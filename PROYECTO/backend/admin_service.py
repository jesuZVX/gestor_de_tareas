# backend/admin_service.py
import os
import shutil
from backend.database import SessionLocal, Proyecto, Tarea, Usuario
from backend.database import Notificacion

def get_active_projects_for_admin(admin_id):
    db = SessionLocal()
    try:
        return db.query(Proyecto)\
                 .filter(Proyecto.estado == "activo",
                         Proyecto.id_usuario_creador == admin_id)\
                 .all()
    finally:
        db.close()

def calculate_project_progress(project_id):
    db = SessionLocal()
    try:
        tareas = db.query(Tarea)\
                   .filter(Tarea.id_proyecto == project_id,
                           Tarea.estado != "inactivo")\
                   .all()
        if not tareas:
            return 0
        completadas = sum(1 for t in tareas if t.estado == "completada")
        return int((completadas / len(tareas)) * 100)
    finally:
        db.close()

def save_project(usuario_id, nombre, descripcion, fecha_inicio, fecha_fin, project_id=None):
    db = SessionLocal()
    try:
        if project_id:
            pj = db.query(Proyecto).get(project_id)
            pj.nombre = nombre
            pj.descripcion = descripcion
            pj.fecha_inicio = fecha_inicio
            pj.fecha_fin = fecha_fin
        else:
            pj = Proyecto(
                nombre=nombre,
                descripcion=descripcion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado="activo",
                id_usuario_creador=usuario_id
            )
            db.add(pj)
        db.commit()
        return pj
    except:
        db.rollback()
        raise
    finally:
        db.close()


def eliminar_proyecto(proyecto_id):
    """Elimina lógicamente un proyecto y todas sus tareas asociadas"""
    session = SessionLocal()
    try:
        proyecto = session.query(Proyecto).filter_by(id=proyecto_id).first()
        if not proyecto:
            return False, "Proyecto no encontrado."

        # Marcar todas las tareas del proyecto como inactivas
        for tarea in proyecto.tareas:
            tarea.estado = 'inactivo'
        
        # Marcar el proyecto como inactivo
        proyecto.estado = 'inactivo'

        session.commit()
        return True, "Este proyecto ha sido eliminado (desactivado), junto con sus tareas asociadas."

    except Exception as e:
        session.rollback()
        print(f"Error eliminando proyecto: {e}")
        return False, "Error interno al eliminar el proyecto."

    finally:
        session.close()


def get_tasks_for_admin(admin_id):
    db = SessionLocal()
    try:
        return db.query(Tarea)\
                 .join(Proyecto, Tarea.id_proyecto == Proyecto.id)\
                 .filter(Proyecto.id_usuario_creador == admin_id,
                         Tarea.estado != "inactivo")\
                 .all()
    finally:
        db.close()

def save_project_with_tasks(usuario_id, project_data, tareas_data):
    db = SessionLocal()
    try:
        # Guardado de proyecto
        if project_data.get("id"):
            pj = db.query(Proyecto).get(project_data["id"])
            pj.nombre = project_data["nombre"]
            pj.descripcion = project_data["descripcion"]
            pj.fecha_inicio = project_data["fecha_inicio"]
            pj.fecha_fin = project_data["fecha_fin"]
        else:
            pj = Proyecto(
                nombre=project_data["nombre"],
                descripcion=project_data["descripcion"],
                fecha_inicio=project_data["fecha_inicio"],
                fecha_fin=project_data["fecha_fin"],
                estado="activo",
                id_usuario_creador=usuario_id
            )
            db.add(pj)
            db.flush()  # Para obtener el id del proyecto

        # Guardado de tareas
        for td in tareas_data:
            if not td["titulo"].strip():
                continue

            tarea = Tarea(
                titulo=td["titulo"].strip(),
                descripcion=td["descripcion"].strip(),
                fecha_vencimiento=td["fecha_vencimiento"],
                estado="pendiente",
                id_proyecto=pj.id,
                id_usuario_asignado=td["id_usuario_asignado"],
                ruta_archivo=td.get("ruta_archivo")
            )
            db.add(tarea)

            # 🔵 Crear notificación para cada tarea asignada
            noti = Notificacion(
                id_usuario=td["id_usuario_asignado"],
                mensaje=f"Te han asignado una nueva tarea: {td['titulo'].strip()}",
                leido=0
            )
            db.add(noti)

        db.commit()
        return pj
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

