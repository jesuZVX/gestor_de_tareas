import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QPushButton, QFileDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from backend.database import SessionLocal, Tarea, Proyecto, Notificacion

class PanelUsuario(QWidget):
    def __init__(self, usuario, cerrar_callback=None):
        super().__init__()
        self.usuario = usuario
        self.cerrar_callback = cerrar_callback

        self.setMinimumSize(1000, 600)
        self.setStyleSheet("background-color: #fdfdfd;")
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("background-color: #e8f5e9;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 30, 10, 10)
        sidebar_layout.setSpacing(15)

        self.btn_notificaciones = QPushButton("🔔 Notificaciones")
        self.btn_notificaciones.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_notificaciones.setStyleSheet("""
            QPushButton { 
                padding: 12px; font-size: 15px; 
                border-radius: 10px; background-color: #4CAF50; color: white; text-align: left; 
            }
            QPushButton:hover { background-color: #388e3c; }
        """)
        self.btn_notificaciones.clicked.connect(self.abrir_notificaciones)
        sidebar_layout.addWidget(self.btn_notificaciones)

        self.btn_tareas = QPushButton("📝 Tareas Asignadas")
        self.btn_tareas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_tareas.setStyleSheet("""
            QPushButton { 
                padding: 12px; font-size: 15px; 
                border-radius: 10px; background-color: #4CAF50; color: white; text-align: left; 
            }
            QPushButton:hover { background-color: #388e3c; }
        """)
        self.btn_tareas.clicked.connect(self.abrir_tareas)
        sidebar_layout.addWidget(self.btn_tareas)

        self.btn_cerrar_sesion = QPushButton("🔒 Cerrar Sesión")
        self.btn_cerrar_sesion.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_cerrar_sesion.setStyleSheet("""
            QPushButton { 
                padding: 12px; font-size: 15px; 
                border-radius: 10px; background-color: #4CAF50; color: white; text-align: left; 
            }
            QPushButton:hover { background-color: #388e3c; }
        """)
        self.btn_cerrar_sesion.clicked.connect(self.cerrar_sesion)
        sidebar_layout.addWidget(self.btn_cerrar_sesion)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        self.contenedor_contenido = QScrollArea()
        self.contenedor_contenido.setWidgetResizable(True)
        main_layout.addWidget(self.contenedor_contenido)

        self.crear_bienvenida()

    def limpiar_contenedor(self):
        widget_anterior = self.contenedor_contenido.widget()
        if widget_anterior is not None:
            widget_anterior.deleteLater()
            self.contenedor_contenido.setWidget(None)

    def crear_bienvenida(self):
        self.limpiar_contenedor()
        cont = QWidget()
        layout = QVBoxLayout(cont)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel(f"👤 Bienvenido {self.usuario.nombre} (Colaborador)")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2e7d32;")
        layout.addWidget(title)

        self.contenedor_contenido.setWidget(cont)

    def abrir_tareas(self):
        self.limpiar_contenedor()
        cont = QWidget()
        layout = QVBoxLayout(cont)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("📝 Tareas Asignadas")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2e7d32;")
        layout.addWidget(title)

        db = SessionLocal()
        tareas = db.query(Tarea).filter(
            Tarea.id_usuario_asignado == self.usuario.id,
            Tarea.estado != "inactivo"
        ).all()
        db.close()

        if not tareas:
            msg = QLabel("No tienes tareas asignadas.")
            msg.setFont(QFont("Segoe UI", 12))
            layout.addWidget(msg)
        else:
            for tarea in tareas:
                card = QFrame()
                card.setStyleSheet("background-color: white; border-radius: 10px; padding: 12px;")
                cv = QVBoxLayout(card)

                lbl = QLabel(f"📝 {tarea.titulo}")
                lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
                cv.addWidget(lbl)

                db = SessionLocal()
                proyecto = db.query(Proyecto).get(tarea.id_proyecto)
                db.close()

                info = QLabel(
                    f"📁 Proyecto: {proyecto.nombre}\n"
                    f"📅 Vence: {tarea.fecha_vencimiento}\n"
                    f"🔧 Estado: {tarea.estado}"
                )
                info.setFont(QFont("Segoe UI", 11))
                info.setStyleSheet("color: #555;")
                cv.addWidget(info)

                if proyecto.descripcion:
                    descripcion_proy = QLabel(f"📝 Descripción del proyecto: {proyecto.descripcion}")
                    descripcion_proy.setFont(QFont("Segoe UI", 10))
                    descripcion_proy.setWordWrap(True)
                    cv.addWidget(descripcion_proy)

                if tarea.descripcion:
                    desc = QLabel(tarea.descripcion)
                    desc.setFont(QFont("Segoe UI", 10))
                    desc.setWordWrap(True)
                    cv.addWidget(desc)

                btn_subir = QPushButton("📤 Subir archivo")
                btn_subir.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px; border-radius: 6px;")
                btn_subir.clicked.connect(lambda _, t=tarea: self.subir_archivo(t))
                cv.addWidget(btn_subir)

                # 🔵 Mostrar botón Ver Archivo si existe
                if tarea.ruta_archivo:
                    btn_ver_archivo = QPushButton("📂 Ver Archivo")
                    btn_ver_archivo.setStyleSheet("background-color: #1976d2; color: white; padding: 6px; border-radius: 6px;")
                    btn_ver_archivo.clicked.connect(lambda _, ruta=tarea.ruta_archivo: self.abrir_archivo(ruta))
                    cv.addWidget(btn_ver_archivo)
                else:
                    lbl_sin_archivo = QLabel("📂 Sin archivo adjunto")
                    lbl_sin_archivo.setFont(QFont("Segoe UI", 10))
                    cv.addWidget(lbl_sin_archivo)

                layout.addWidget(card)

        self.contenedor_contenido.setWidget(cont)

    def abrir_notificaciones(self):
        self.limpiar_contenedor()
        cont = QWidget()
        layout = QVBoxLayout(cont)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("🔔 Notificaciones")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2e7d32;")
        layout.addWidget(title)

        db = SessionLocal()
        notificaciones = db.query(Notificacion).filter(
            Notificacion.id_usuario == self.usuario.id,
            Notificacion.leido == 0
        ).order_by(Notificacion.fecha.desc()).all()

        if not notificaciones:
            msg = QLabel("Actualmente no tienes nuevas notificaciones.")
            msg.setFont(QFont("Segoe UI", 12))
            layout.addWidget(msg)
        else:
            for n in notificaciones:
                card = QFrame()
                card.setStyleSheet("background-color: white; border-radius: 10px; padding: 10px;")
                cv = QVBoxLayout(card)

                mensaje = QLabel(f"🔔 {n.mensaje}")
                mensaje.setFont(QFont("Segoe UI", 12))
                cv.addWidget(mensaje)

                layout.addWidget(card)

            for n in notificaciones:
                n.leido = 1
            db.commit()

        db.close()
        self.contenedor_contenido.setWidget(cont)

    def cerrar_sesion(self):
        if self.cerrar_callback:
            self.cerrar_callback()
        else:
            QMessageBox.information(self, "Cerrar Sesión", "No se definió acción de cierre de sesión.")

    def subir_archivo(self, tarea):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo",
            "",
            "Documentos (*.pdf *.doc *.docx *.png *.jpg *.jpeg)"
        )
        if archivo:
            try:
                dest_dir = os.path.join("archivos_tareas", f"tarea_{tarea.id}")
                os.makedirs(dest_dir, exist_ok=True)
                nombre = os.path.basename(archivo)
                dst = os.path.join(dest_dir, nombre)
                shutil.copy(archivo, dst)

                # 🔵 Actualizar en la base de datos
                session = SessionLocal()
                tarea_db = session.query(Tarea).get(tarea.id)
                if tarea_db:
                    tarea_db.ruta_archivo = dst
                    session.commit()
                session.close()

                QMessageBox.information(self, "Éxito", f"Archivo subido:\n{nombre}")
                self.abrir_tareas()  # Refrescar vista
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo subir el archivo:\n{e}")

    def abrir_archivo(self, ruta):
        if ruta and os.path.exists(ruta):
            try:
                os.startfile(ruta)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo.\n{e}")
        else:
            QMessageBox.warning(self, "Advertencia", "El archivo no existe.")
