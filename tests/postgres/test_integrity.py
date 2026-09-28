"""Invariantes bajo transacciones independientes: jamás validar locks con SQLite."""

import datetime
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import AsientoNoDisponibleError, ReservaExpiradaError
from app.models import Asiento, EstadoAsiento, EstadoReserva, Reserva
from app.services.reserva_service import confirmar_reserva, expirar_reservas, reservar_provisional, reservar_seguro

pytestmark = pytest.mark.postgres


@pytest.fixture(autouse=True)
def require_postgres(db_session):
    if db_session.bind.dialect.name != "postgresql":
        pytest.skip("Requiere TEST_DATABASE_URL PostgreSQL; SQLite no prueba bloqueo de filas")


@pytest.mark.parametrize("participants", [5, 10])
@pytest.mark.parametrize("operation", [reservar_seguro, reservar_provisional])
def test_same_seat_one_winner(seed_data, session_factory, operation, participants):
    barrier = Barrier(participants)

    def attempt(_):
        with session_factory() as db:
            barrier.wait(timeout=10)
            try:
                operation(db, seed_data["primer_usuario_id"], seed_data["primer_asiento_id"])
                return "accepted"
            except AsientoNoDisponibleError:
                return "conflict"

    with ThreadPoolExecutor(max_workers=participants) as executor:
        results = list(executor.map(attempt, range(participants)))
    assert results.count("accepted") == 1
    assert results.count("conflict") == participants - 1
    with session_factory() as db:
        assert (
            db.query(Reserva).filter(Reserva.estado.in_([EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA])).count()
            == 1
        )
        assert db.get(Asiento, seed_data["primer_asiento_id"]).estado != EstadoAsiento.DISPONIBLE


def test_unique_index_protects_even_without_service_lock(seed_data, db_session):
    args = dict(usuario_id=seed_data["primer_usuario_id"], asiento_id=seed_data["primer_asiento_id"])
    db_session.add(Reserva(**args, codigo_reserva="TEST-A", estado=EstadoReserva.CONFIRMADA))
    db_session.commit()
    db_session.add(Reserva(**args, codigo_reserva="TEST-B", estado=EstadoReserva.PENDIENTE))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
    assert db_session.query(Reserva).count() == 1


def test_expired_seat_can_be_reserved_again(seed_data, db_session):
    reservation = reservar_provisional(db_session, seed_data["primer_usuario_id"], seed_data["primer_asiento_id"])
    reservation.fecha_expiracion = datetime.datetime.now(datetime.UTC).replace(tzinfo=None) - datetime.timedelta(
        seconds=1
    )
    db_session.commit()
    assert expirar_reservas(db_session)["expiradas"] == 1
    replacement = reservar_seguro(db_session, seed_data["primer_usuario_id"], seed_data["primer_asiento_id"])
    assert replacement.estado == EstadoReserva.CONFIRMADA
    assert db_session.query(Reserva).count() == 2


def test_confirm_expired_invalidates_cache(seed_data, db_session, monkeypatch):
    reservation = reservar_provisional(db_session, seed_data["primer_usuario_id"], seed_data["primer_asiento_id"])
    reservation.fecha_expiracion = datetime.datetime.now(datetime.UTC).replace(tzinfo=None) - datetime.timedelta(
        seconds=1
    )
    db_session.commit()
    invalidations = []
    monkeypatch.setattr("app.services.reserva_service.cache_delete", invalidations.append)
    with pytest.raises(ReservaExpiradaError):
        confirmar_reserva(db_session, reservation.id)
    assert invalidations == [f"vuelo:{seed_data['primer_vuelo_id']}:disponibilidad"]
    assert db_session.get(Asiento, seed_data["primer_asiento_id"]).estado == EstadoAsiento.DISPONIBLE


def test_read_does_not_wait_for_seat_lock(seed_data, session_factory):
    from app.services.disponibilidad_service import consultar_disponibilidad

    with session_factory() as writer, session_factory() as reader:
        writer.query(Asiento).filter_by(id=seed_data["primer_asiento_id"]).with_for_update().one()
        reader.execute(text("SET LOCAL statement_timeout = '500ms'"))
        result = consultar_disponibilidad(reader, seed_data["primer_vuelo_id"])
        assert result["asientos_disponibles"] > 0
        writer.rollback()


def test_unprotected_control_reproduces_race(session_factory):
    """Control negativo en tabla aislada; jamás retirar índices del esquema de la app."""
    with session_factory() as db:
        db.execute(text("CREATE TABLE laboratorio_sin_control (seat_id integer, passenger_id integer)"))
        db.commit()
    barrier = Barrier(5)

    def attempt(passenger):
        with session_factory() as db:
            count = db.execute(text("SELECT count(*) FROM laboratorio_sin_control WHERE seat_id=1")).scalar_one()
            barrier.wait(timeout=10)
            assert count == 0
            db.execute(text("INSERT INTO laboratorio_sin_control VALUES (1, :passenger)"), {"passenger": passenger})
            db.commit()

    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            list(executor.map(attempt, range(5)))
        with session_factory() as db:
            assert db.execute(text("SELECT count(*) FROM laboratorio_sin_control")).scalar_one() == 5
    finally:
        with session_factory() as db:
            db.execute(text("DROP TABLE laboratorio_sin_control"))
            db.commit()
