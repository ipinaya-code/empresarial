"""initial_schema

Revision ID: 0001
Revises:
Create Date: 2026-09-27 00:37:14.746098

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False, comment="Nombre completo del pasajero"),
        sa.Column("apellido", sa.String(length=100), nullable=False, comment="Apellido del pasajero"),
        sa.Column("email", sa.String(length=255), nullable=False, comment="Correo electrónico único"),
        sa.Column(
            "documento_tipo", sa.String(length=20), nullable=False, comment="Tipo de documento: CI, PASAPORTE, DNI"
        ),
        sa.Column("documento_numero", sa.String(length=20), nullable=False, comment="Número de documento de identidad"),
        sa.Column("telefono", sa.String(length=20), nullable=True, comment="Teléfono de contacto"),
        sa.Column("nacionalidad", sa.String(length=3), nullable=False, comment="Código ISO 3166-1 alpha-3"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_usuarios_apellido"), "usuarios", ["apellido"], unique=False)
    op.create_index(op.f("ix_usuarios_documento_numero"), "usuarios", ["documento_numero"], unique=True)
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True)
    op.create_index(op.f("ix_usuarios_id"), "usuarios", ["id"], unique=False)
    op.create_index(op.f("ix_usuarios_nombre"), "usuarios", ["nombre"], unique=False)
    op.create_table(
        "vuelos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(length=10), nullable=False, comment="Código de vuelo IATA (ej: OB-101)"),
        sa.Column(
            "origen_iata", sa.String(length=3), nullable=False, comment="Código IATA del aeropuerto de origen (ej: VVI)"
        ),
        sa.Column(
            "origen_nombre", sa.String(length=100), nullable=False, comment="Nombre completo del aeropuerto de origen"
        ),
        sa.Column(
            "destino_iata",
            sa.String(length=3),
            nullable=False,
            comment="Código IATA del aeropuerto de destino (ej: LPB)",
        ),
        sa.Column(
            "destino_nombre", sa.String(length=100), nullable=False, comment="Nombre completo del aeropuerto de destino"
        ),
        sa.Column("fecha_salida", sa.DateTime(), nullable=False, comment="Fecha y hora de salida programada"),
        sa.Column("fecha_llegada", sa.DateTime(), nullable=False, comment="Fecha y hora de llegada estimada"),
        sa.Column("aeronave", sa.String(length=50), nullable=False, comment="Tipo de aeronave asignada"),
        sa.Column("capacidad", sa.Integer(), nullable=False, comment="Capacidad total de asientos"),
        sa.Column(
            "estado",
            sa.String(length=20),
            nullable=False,
            comment="Estado: PROGRAMADO, ABORDANDO, EN_VUELO, ATERRIZADO, CANCELADO",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vuelos_codigo"), "vuelos", ["codigo"], unique=True)
    op.create_index(op.f("ix_vuelos_destino_iata"), "vuelos", ["destino_iata"], unique=False)
    op.create_index(op.f("ix_vuelos_estado"), "vuelos", ["estado"], unique=False)
    op.create_index(op.f("ix_vuelos_fecha_salida"), "vuelos", ["fecha_salida"], unique=False)
    op.create_index(op.f("ix_vuelos_id"), "vuelos", ["id"], unique=False)
    op.create_index(op.f("ix_vuelos_origen_iata"), "vuelos", ["origen_iata"], unique=False)
    op.create_table(
        "asientos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vuelo_id", sa.Integer(), nullable=False),
        sa.Column("numero", sa.String(length=5), nullable=False, comment="Identificador del asiento (ej: 1A, 14F)"),
        sa.Column("fila", sa.Integer(), nullable=False, comment="Número de fila (1-22)"),
        sa.Column("columna", sa.String(length=1), nullable=False, comment="Letra de columna (A-F)"),
        sa.Column(
            "clase",
            sa.Enum("EJECUTIVA", "ECONOMICA", name="claseservicio"),
            nullable=False,
            comment="Clase de servicio: ejecutiva o económica",
        ),
        sa.Column(
            "estado",
            sa.Enum("DISPONIBLE", "RESERVADO_PROVISIONAL", "CONFIRMADO", "BLOQUEADO", name="estadoasiento"),
            nullable=False,
        ),
        sa.Column(
            "fecha_expiracion",
            sa.DateTime(),
            nullable=True,
            comment="Límite de reserva provisional (NULL si no aplica)",
        ),
        sa.ForeignKeyConstraint(["vuelo_id"], ["vuelos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vuelo_id", "numero", name="uq_asiento_vuelo_numero"),
    )
    op.create_index(op.f("ix_asientos_estado"), "asientos", ["estado"], unique=False)
    op.create_index(op.f("ix_asientos_id"), "asientos", ["id"], unique=False)
    op.create_index(op.f("ix_asientos_numero"), "asientos", ["numero"], unique=False)
    op.create_index(op.f("ix_asientos_vuelo_id"), "asientos", ["vuelo_id"], unique=False)
    op.create_table(
        "reservas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "codigo_reserva", sa.String(length=10), nullable=False, comment="Código PNR de la reserva (ej: BOA-A1B2C3)"
        ),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("asiento_id", sa.Integer(), nullable=False),
        sa.Column("fecha_reserva", sa.DateTime(), nullable=False, comment="Fecha y hora de creación de la reserva"),
        sa.Column(
            "fecha_expiracion",
            sa.DateTime(),
            nullable=True,
            comment="Fecha límite para confirmar una reserva provisional",
        ),
        sa.Column("estado", sa.Enum("PENDIENTE", "CONFIRMADA", "CANCELADA", name="estadoreserva"), nullable=False),
        sa.ForeignKeyConstraint(["asiento_id"], ["asientos.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reservas_asiento_id"), "reservas", ["asiento_id"], unique=False)
    op.create_index(op.f("ix_reservas_codigo_reserva"), "reservas", ["codigo_reserva"], unique=True)
    op.create_index(op.f("ix_reservas_estado"), "reservas", ["estado"], unique=False)
    op.create_index(op.f("ix_reservas_id"), "reservas", ["id"], unique=False)
    op.create_index(op.f("ix_reservas_usuario_id"), "reservas", ["usuario_id"], unique=False)
    op.create_index(
        "uq_reserva_asiento_activa",
        "reservas",
        ["asiento_id"],
        unique=True,
        postgresql_where=sa.text("estado IN ('PENDIENTE', 'CONFIRMADA')"),
        sqlite_where=sa.text("estado IN ('PENDIENTE', 'CONFIRMADA')"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "uq_reserva_asiento_activa",
        table_name="reservas",
        postgresql_where=sa.text("estado IN ('PENDIENTE', 'CONFIRMADA')"),
        sqlite_where=sa.text("estado IN ('PENDIENTE', 'CONFIRMADA')"),
    )
    op.drop_index(op.f("ix_reservas_usuario_id"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_id"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_estado"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_codigo_reserva"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_asiento_id"), table_name="reservas")
    op.drop_table("reservas")
    op.drop_index(op.f("ix_asientos_vuelo_id"), table_name="asientos")
    op.drop_index(op.f("ix_asientos_numero"), table_name="asientos")
    op.drop_index(op.f("ix_asientos_id"), table_name="asientos")
    op.drop_index(op.f("ix_asientos_estado"), table_name="asientos")
    op.drop_table("asientos")
    op.drop_index(op.f("ix_vuelos_origen_iata"), table_name="vuelos")
    op.drop_index(op.f("ix_vuelos_id"), table_name="vuelos")
    op.drop_index(op.f("ix_vuelos_fecha_salida"), table_name="vuelos")
    op.drop_index(op.f("ix_vuelos_estado"), table_name="vuelos")
    op.drop_index(op.f("ix_vuelos_destino_iata"), table_name="vuelos")
    op.drop_index(op.f("ix_vuelos_codigo"), table_name="vuelos")
    op.drop_table("vuelos")
    op.drop_index(op.f("ix_usuarios_nombre"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_id"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_documento_numero"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_apellido"), table_name="usuarios")
    op.drop_table("usuarios")
    if op.get_bind().dialect.name == "postgresql":
        for enum_name in ("estadoreserva", "estadoasiento", "claseservicio"):
            sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
