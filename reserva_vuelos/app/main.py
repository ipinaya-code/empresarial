from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database
import datetime
import asyncio

app = FastAPI(title="Prototipo de Reserva de Vuelos BoA - Transaccionalidad")

models.Base.metadata.create_all(bind=database.engine)

@app.post("/seed")
def seed_data(db: Session = Depends(database.get_db)):
    vuelo = db.query(models.Vuelo).first()
    if vuelo:
        asiento = db.query(models.Asiento).first()
        return {"msg": "Ya hay datos", "vuelo_id": vuelo.id, "asiento_id": asiento.id}
    
    # Crear vuelo
    vuelo = models.Vuelo(origen="La Paz", destino="Santa Cruz", fecha=datetime.datetime.now(), capacidad=100)
    db.add(vuelo)
    db.commit()
    db.refresh(vuelo)
    
    # Crear asiento
    asiento = models.Asiento(vuelo_id=vuelo.id, numero="1A", estado=models.EstadoAsiento.DISPONIBLE)
    db.add(asiento)
    
    # Crear usuarios
    for i in range(10):
        usuario = models.Usuario(nombre=f"Usuario {i}", email=f"user{i}@test.com")
        db.add(usuario)
        
    db.commit()
    return {"msg": "Datos inicializados", "vuelo_id": vuelo.id, "asiento_id": asiento.id}

@app.post("/reset")
def reset_data(db: Session = Depends(database.get_db)):
    db.query(models.Reserva).delete()
    db.query(models.Asiento).update({"estado": models.EstadoAsiento.DISPONIBLE})
    db.commit()
    return {"msg": "Datos reseteados"}

@app.post("/reservar/inseguro", response_model=schemas.ReservaResponse)
def reservar_inseguro(reserva: schemas.ReservaCreate, db: Session = Depends(database.get_db)):
    # Simular latencia de procesamiento
    asiento = db.query(models.Asiento).filter(models.Asiento.id == reserva.asiento_id).first()
    
    if not asiento:
        raise HTTPException(status_code=404, detail="Asiento no encontrado")
        
    if asiento.estado != models.EstadoAsiento.DISPONIBLE:
        raise HTTPException(status_code=400, detail="Asiento no disponible")
    
    import time
    time.sleep(0.5) # Simular procesamiento
    
    asiento.estado = models.EstadoAsiento.CONFIRMADO
    nueva_reserva = models.Reserva(usuario_id=reserva.usuario_id, asiento_id=reserva.asiento_id, estado=models.EstadoReserva.CONFIRMADA)
    
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    
    return nueva_reserva

@app.post("/reservar/seguro", response_model=schemas.ReservaResponse)
def reservar_seguro(reserva: schemas.ReservaCreate, db: Session = Depends(database.get_db)):
    try:
        # Bloqueo pesimista con FOR UPDATE
        asiento = db.query(models.Asiento).filter(models.Asiento.id == reserva.asiento_id).with_for_update().first()
        
        if not asiento:
            raise HTTPException(status_code=404, detail="Asiento no encontrado")
            
        if asiento.estado != models.EstadoAsiento.DISPONIBLE:
            db.rollback()
            raise HTTPException(status_code=400, detail="Asiento no disponible")
        
        import time
        time.sleep(0.5) # Simular procesamiento
        
        asiento.estado = models.EstadoAsiento.CONFIRMADO
        nueva_reserva = models.Reserva(usuario_id=reserva.usuario_id, asiento_id=reserva.asiento_id, estado=models.EstadoReserva.CONFIRMADA)
        
        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)
        
        return nueva_reserva
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
