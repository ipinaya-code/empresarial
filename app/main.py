from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app import models, schemas, database
import datetime
import logging
import time
import json

def clear_cache(vuelo_id: int):
    r = database.get_redis()
    if r:
        try:
            r.delete(f"vuelo:{vuelo_id}:disponibilidad")
        except Exception as e:
            logger.error(f"Error borrando cache: {e}")

def clear_all_cache():
    r = database.get_redis()
    if r:
        try:
            r.flushdb()
        except Exception as e:
            logger.error(f"Error limpiando cache: {e}")

app = FastAPI(title="Prototipo de Reserva de Vuelos BoA - Transaccionalidad")
logger = logging.getLogger(__name__)
INSECURE_PROCESSING_DELAY_SECONDS = 0.5
SECURE_PROCESSING_DELAY_SECONDS = 60

models.Base.metadata.create_all(bind=database.engine)

@app.post("/seed")
def seed_data(db: Session = Depends(database.get_db)):
    vuelo = db.query(models.Vuelo).first()
    if vuelo:
        asiento = db.query(models.Asiento).first()
        if not asiento:
            raise HTTPException(status_code=409, detail="El vuelo no tiene asientos configurados")
        return {"msg": "Ya hay datos", "vuelo_id": vuelo.id, "asiento_id": asiento.id}
    
    # Crear vuelo
    vuelo = models.Vuelo(origen="La Paz", destino="Santa Cruz", fecha=datetime.datetime.now(), capacidad=100)
    db.add(vuelo)
    db.flush()

    asientos = []
    for fila in range(1, 11):
        for letra in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J"):
            asientos.append(models.Asiento(vuelo_id=vuelo.id, numero=f"{fila}{letra}"))
    db.add_all(asientos)

    for i in range(10):
        usuario = models.Usuario(nombre=f"Usuario {i}", email=f"user{i}@test.com")
        db.add(usuario)

    db.commit()
    db.refresh(vuelo)
    asiento = asientos[0]
    clear_all_cache()
    return {"msg": "Datos inicializados", "vuelo_id": vuelo.id, "asiento_id": asiento.id}

@app.post("/reset")
def reset_data(db: Session = Depends(database.get_db)):
    db.query(models.Reserva).delete(synchronize_session=False)
    db.query(models.Asiento).update(
        {"estado": models.EstadoAsiento.DISPONIBLE, "fecha_expiracion": None},
        synchronize_session=False,
    )
    db.commit()
    clear_all_cache()
    return {"msg": "Datos reseteados"}

@app.post("/reservar/inseguro", response_model=schemas.ReservaResponse)
def reservar_inseguro(reserva: schemas.ReservaCreate, db: Session = Depends(database.get_db)):
    # Simular latencia de procesamiento
    asiento = db.query(models.Asiento).filter(models.Asiento.id == reserva.asiento_id).first()
    
    if not asiento:
        raise HTTPException(status_code=404, detail="Asiento no encontrado")

    if not db.query(models.Usuario).filter(models.Usuario.id == reserva.usuario_id).first():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    if asiento.estado != models.EstadoAsiento.DISPONIBLE:
        raise HTTPException(status_code=400, detail="Asiento no disponible")
    
    time.sleep(INSECURE_PROCESSING_DELAY_SECONDS)
    
    asiento.estado = models.EstadoAsiento.CONFIRMADO
    nueva_reserva = models.Reserva(usuario_id=reserva.usuario_id, asiento_id=reserva.asiento_id, estado=models.EstadoReserva.CONFIRMADA)
    
    db.add(nueva_reserva)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El asiento ya tiene una reserva activa")
    db.refresh(nueva_reserva)
    
    clear_cache(asiento.vuelo_id)
    return nueva_reserva

@app.post("/reservar/seguro", response_model=schemas.ReservaResponse)
def reservar_seguro(reserva: schemas.ReservaCreate, db: Session = Depends(database.get_db)):
    try:
        # Bloqueo pesimista con FOR UPDATE
        asiento = db.query(models.Asiento).filter(models.Asiento.id == reserva.asiento_id).with_for_update().first()
        
        if not asiento:
            raise HTTPException(status_code=404, detail="Asiento no encontrado")

        if not db.query(models.Usuario).filter(models.Usuario.id == reserva.usuario_id).first():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        if asiento.estado != models.EstadoAsiento.DISPONIBLE:
            db.rollback()
            raise HTTPException(status_code=400, detail="Asiento no disponible")
        
        time.sleep(SECURE_PROCESSING_DELAY_SECONDS)
        
        asiento.estado = models.EstadoAsiento.CONFIRMADO
        nueva_reserva = models.Reserva(usuario_id=reserva.usuario_id, asiento_id=reserva.asiento_id, estado=models.EstadoReserva.CONFIRMADA)
        
        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)
        
        clear_cache(asiento.vuelo_id)
        return nueva_reserva
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El asiento ya tiene una reserva activa")
    except Exception as e:
        db.rollback()
        logger.exception("Error inesperado al reservar asiento")
        raise HTTPException(status_code=500, detail="Error interno al procesar la reserva")


@app.post("/reservar/provisional", response_model=schemas.ReservaResponse)
def reservar_provisional(reserva: schemas.ReservaCreate, db: Session = Depends(database.get_db)):
    """Aparta un asiento temporalmente hasta que se confirme o expire."""
    try:
        asiento = (
            db.query(models.Asiento)
            .filter(models.Asiento.id == reserva.asiento_id)
            .with_for_update()
            .first()
        )
        if not asiento:
            raise HTTPException(status_code=404, detail="Asiento no encontrado")
        if not db.query(models.Usuario).filter(models.Usuario.id == reserva.usuario_id).first():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if asiento.estado != models.EstadoAsiento.DISPONIBLE:
            raise HTTPException(status_code=409, detail="Asiento no disponible")

        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        asiento.estado = models.EstadoAsiento.RESERVADO_PROVISIONAL
        asiento.fecha_expiracion = expiration
        nueva_reserva = models.Reserva(
            usuario_id=reserva.usuario_id,
            asiento_id=reserva.asiento_id,
            estado=models.EstadoReserva.PENDIENTE,
            fecha_expiracion=expiration,
        )
        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)
        clear_cache(asiento.vuelo_id)
        return nueva_reserva
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El asiento ya tiene una reserva activa")
    except Exception:
        db.rollback()
        logger.exception("Error inesperado al crear reserva provisional")
        raise HTTPException(status_code=500, detail="Error interno al procesar la reserva")


@app.post("/reservar/{reserva_id}/confirmar", response_model=schemas.ReservaResponse)
def confirmar_reserva(reserva_id: int, db: Session = Depends(database.get_db)):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).with_for_update().first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    if reserva.estado != models.EstadoReserva.PENDIENTE:
        raise HTTPException(status_code=409, detail="La reserva ya no está pendiente")

    asiento = db.query(models.Asiento).filter(models.Asiento.id == reserva.asiento_id).with_for_update().first()
    if reserva.fecha_expiracion and reserva.fecha_expiracion <= datetime.datetime.utcnow():
        reserva.estado = models.EstadoReserva.CANCELADA
        asiento.estado = models.EstadoAsiento.DISPONIBLE
        asiento.fecha_expiracion = None
        db.commit()
        raise HTTPException(status_code=409, detail="La reserva provisional expiró")

    reserva.estado = models.EstadoReserva.CONFIRMADA
    asiento.estado = models.EstadoAsiento.CONFIRMADO
    asiento.fecha_expiracion = None
    db.commit()
    db.refresh(reserva)
    clear_cache(asiento.vuelo_id)
    return reserva


@app.post("/reservar/expirar")
def expirar_reservas(db: Session = Depends(database.get_db)):
    ahora = datetime.datetime.utcnow()
    pendientes = (
        db.query(models.Reserva)
        .filter(
            models.Reserva.estado == models.EstadoReserva.PENDIENTE,
            models.Reserva.fecha_expiracion <= ahora,
        )
        .with_for_update()
        .all()
    )
    for reserva in pendientes:
        asiento = db.query(models.Asiento).filter(models.Asiento.id == reserva.asiento_id).with_for_update().first()
        reserva.estado = models.EstadoReserva.CANCELADA
        if asiento and asiento.estado == models.EstadoAsiento.RESERVADO_PROVISIONAL:
            asiento.estado = models.EstadoAsiento.DISPONIBLE
            asiento.fecha_expiracion = None
    db.commit()
    if pendientes:
        clear_all_cache()
    return {"expiradas": len(pendientes)}


# ==========================================
# CQRS: LECTURAS (QUERIES) 
# ==========================================
@app.get("/vuelos/{vuelo_id}/disponibilidad", response_model=schemas.VueloDisponibilidadResponse)
def consultar_disponibilidad(vuelo_id: int, db: Session = Depends(database.get_db)):
    """
    Endpoint de lectura optimizado.
    En una arquitectura CQRS completa, esta lectura podría venir de una 
    réplica de lectura o de una caché (Redis) para evitar carga en el maestro.
    No utiliza bloqueos (Locks).
    """
    redis_client = database.get_redis()
    cache_key = f"vuelo:{vuelo_id}:disponibilidad"
    
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info("Cache hit")
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error leyendo de Redis: {e}")

    logger.info("Cache miss")
    vuelo = db.query(models.Vuelo).filter(models.Vuelo.id == vuelo_id).first()
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")

    asientos = db.query(models.Asiento).filter(models.Asiento.vuelo_id == vuelo_id).all()
    
    asientos_disponibles = [a for a in asientos if a.estado == models.EstadoAsiento.DISPONIBLE]
    
    response_data = {
        "vuelo_id": vuelo.id,
        "origen": vuelo.origen,
        "destino": vuelo.destino,
        "capacidad_total": vuelo.capacidad,
        "asientos_disponibles": len(asientos_disponibles),
        "asientos": [{"id": a.id, "numero": a.numero, "estado": a.estado.value} for a in asientos]
    }

    if redis_client:
        try:
            # TTL de 10 minutos
            redis_client.setex(cache_key, 600, json.dumps(response_data))
        except Exception as e:
            logger.error(f"Error escribiendo en Redis: {e}")

    return response_data
