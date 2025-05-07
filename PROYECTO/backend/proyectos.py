from backend.database import SessionLocal, Proyecto

def obtener_proyectos_activos(usuario_id=None):
    db = SessionLocal()
    try:
        query = db.query(Proyecto).filter(Proyecto.estado == "activo")
        if usuario_id:
            query = query.filter(Proyecto.id_usuario_creador == usuario_id)
        return query.order_by(Proyecto.fecha_inicio).all()
    except Exception as e:
        print("Error al obtener proyectos:", e)
        return []
    finally:
        db.close()
