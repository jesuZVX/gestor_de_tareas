import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QSizePolicy, QLineEdit, QTextEdit,
    QDateEdit, QFormLayout, QMessageBox, QProgressBar,
    QComboBox, QFileDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QDate
from backend.database import SessionLocal, Proyecto, Tarea, Usuario
from backend.database import RolUsuario
from datetime import date
from backend.database import Notificacion
from backend.admin_service import eliminar_proyecto

class PanelAdmin(QWidget):
    def __init__(self, usuario, cerrar_callback=None):
        super().__init__()
        self.usuario = usuario
        self.cerrar_callback = cerrar_callback

        self.setMinimumSize(1100, 650)
        self.setStyleSheet("background-color: #f9f9f9;")
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.crear_barra_lateral())
        self.contenedor_contenido = QScrollArea()
        self.contenedor_contenido.setWidgetResizable(True)
        main_layout.addWidget(self.contenedor_contenido)
        self.crear_contenido_bienvenida()

    def limpiar_contenedor_contenido(self):
        widget_anterior = self.contenedor_contenido.widget()
        if widget_anterior is not None:
            widget_anterior.deleteLater()
            self.contenedor_contenido.setWidget(None)

    def crear_barra_lateral(self):
        barra = QFrame()
        barra.setFixedWidth(240)
        barra.setStyleSheet("background-color: #e8f5e9;")
        v = QVBoxLayout(barra)
        v.setContentsMargins(10, 30, 10, 10)
        v.setSpacing(15)

        botones = [
            ("\U0001f4c1 Proyectos", self.abrir_proyectos),
            ("\u2705 Tareas", self.abrir_tareas),
            ("\U0001f514 Notificaciones", self.abrir_notificaciones),
            ("\U0001f513 Cerrar sesión", self.cerrar_sesion)
        ]
        for texto, accion in botones:
            btn = QPushButton(texto)
            btn.setStyleSheet(
                "QPushButton { padding: 12px; font-size: 15px; "
                "border-radius: 10px; background-color: #4CAF50; color: white; text-align: left; }"
                "QPushButton:hover { background-color: #388e3c; }"
            )
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(accion)
            v.addWidget(btn)

        v.addStretch()
        return barra

    def crear_contenido_bienvenida(self):
        self.limpiar_contenedor_contenido()
        cont = QWidget()
        layout = QVBoxLayout(cont)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel(f"Bienvenido {self.usuario.nombre} (Administrador)")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2e7d32;")
        layout.addWidget(title)

        self.contenedor_contenido.setWidget(cont)

    def cerrar_sesion(self):
        if self.cerrar_callback:
            self.cerrar_callback()

    # --- Proyectos ---

    def abrir_proyectos(self):
        self.limpiar_contenedor_contenido()

        cont = QWidget()
        layout = QVBoxLayout(cont)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("\U0001f4c1 Gestión de Proyectos")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2e7d32;")
        layout.addWidget(title)

    # === Resumen ===
        resumen = self.crear_resumen_admin()
        layout.addWidget(resumen)

    # === Botón Crear nuevo proyecto ===
        btn_nuevo = QPushButton("\u2795 Crear nuevo proyecto")
        btn_nuevo.setStyleSheet(
        "background-color: #4CAF50; color: white; padding: 10px; "
        "font-size: 14px; border-radius: 8px;"
        )
        btn_nuevo.clicked.connect(lambda: self.mostrar_formulario_proyecto())
        layout.addWidget(btn_nuevo)

    # === Listar proyectos ===
        self.lista_proyectos = QVBoxLayout()
        db = SessionLocal()
        proyectos = db.query(Proyecto).filter(
        Proyecto.estado == "activo",
        Proyecto.id_usuario_creador == self.usuario.id
        ).all()
        db.close()
        for p in proyectos:
            self.agregar_proyecto_a_lista(p)

        layout.addLayout(self.lista_proyectos)
        self.contenedor_contenido.setWidget(cont)


    def agregar_proyecto_a_lista(self, proyecto):
        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px;")
        v = QVBoxLayout(card)

        lbl_t = QLabel(proyecto.nombre)
        lbl_t.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_d = QLabel(proyecto.descripcion or "")
        lbl_d.setFont(QFont("Segoe UI", 11))
        lbl_d.setWordWrap(True)

        prog = self.calcular_progreso_proyecto(proyecto.id)
        pb = QProgressBar()
        pb.setValue(prog)
        pb.setFormat(f"{prog}% Completado")
        pb.setStyleSheet("QProgressBar { height: 15px; border-radius: 5px; }")

        btn_ed = QPushButton("✏️ Editar")
        btn_ed.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px; border-radius: 6px;")
        btn_ed.clicked.connect(lambda _, p=proyecto: self.mostrar_formulario_proyecto(p))

        btn_del = QPushButton("🗑 Eliminar")
        btn_del.setStyleSheet("background-color: red; color: white; padding: 6px; border-radius: 6px;")
        btn_del.clicked.connect(lambda _, p=proyecto: self.eliminar_proyecto(p.id))


        v.addWidget(lbl_t)
        v.addWidget(lbl_d)
        v.addWidget(pb)
        h = QHBoxLayout()
        h.addWidget(btn_ed)
        h.addWidget(btn_del)
        v.addLayout(h)

        self.lista_proyectos.addWidget(card)

    def calcular_progreso_proyecto(self, proyecto_id):
        db = SessionLocal()
        tareas = db.query(Tarea).filter(
            Tarea.id_proyecto == proyecto_id,
            Tarea.estado != "inactivo"
        ).all()
        db.close()
        if not tareas:
            return 0
        return int(sum(1 for t in tareas if t.estado == "completada") / len(tareas) * 100)

    def eliminar_proyecto(self, proyecto_id):
        try:
            exito, mensaje = eliminar_proyecto(proyecto_id)
            if exito:
                QMessageBox.information(self, "Éxito", mensaje)
                self.actualizar_vista_proyectos()  # Método para recargar la lista sin el proyecto eliminado
            else:
                QMessageBox.warning(self, "Advertencia", mensaje)
        except Exception as e:
            print(f"Error eliminando proyecto desde la interfaz: {e}")
            QMessageBox.critical(self, "Error", "Ocurrió un error inesperado al eliminar el proyecto.")


    def mostrar_formulario_proyecto(self, proyecto=None):
        try:
            self.limpiar_contenedor_contenido()

            self.formulario_widget = QWidget()
            form = QFormLayout()
            self.formulario_widget.setLayout(form)

            form.setContentsMargins(30, 30, 30, 30)

            # Campos del proyecto
            self.input_nombre = QLineEdit(proyecto.nombre if proyecto else "")
            self.input_descripcion = QTextEdit(proyecto.descripcion if proyecto else "")
            self.input_inicio = QDateEdit(calendarPopup=True)
            self.input_fin = QDateEdit(calendarPopup=True)

            if proyecto and proyecto.fecha_inicio:
                d = proyecto.fecha_inicio
                self.input_inicio.setDate(QDate(d.year, d.month, d.day))
            else:
                self.input_inicio.setDate(QDate.currentDate())

            if proyecto and proyecto.fecha_fin:
                d = proyecto.fecha_fin
                self.input_fin.setDate(QDate(d.year, d.month, d.day))
            else:
                self.input_fin.setDate(QDate.currentDate())

            form.addRow("📌 Nombre:", self.input_nombre)
            form.addRow("📝 Descripción:", self.input_descripcion)
            form.addRow("📅 Inicio:", self.input_inicio)
            form.addRow("📆 Fin:", self.input_fin)

            # ===== TAREAS DINÁMICAS =====
            self.tareas_fields = []
            self.bloque_tareas = QVBoxLayout()
            self.colaboradores = []

            self.cargar_colaboradores()

            if not self.colaboradores:
                QMessageBox.warning(self, "⚠️ Advertencia", "No puedes crear tareas porque no hay colaboradores registrados.")
                return
            else:
                self.añadir_campo_tarea()
                btn_add = QPushButton("➕ Añadir otra tarea")
                btn_add.setStyleSheet("background-color: #81c784; padding: 6px; border-radius: 6px;")
                btn_add.clicked.connect(lambda: self.añadir_campo_tarea())
                self.bloque_tareas.addWidget(btn_add)

            contenedor_tareas = QWidget()
            contenedor_tareas.setLayout(self.bloque_tareas)
            form.addRow(QLabel("🧩 Tareas:"), contenedor_tareas)

            btn_guardar = QPushButton("💾 Guardar Proyecto")
            btn_guardar.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 8px;")
            btn_guardar.clicked.connect(lambda _, p=proyecto: self.guardar_proyecto(p))
            form.addRow(btn_guardar)

            self.contenedor_contenido.setWidget(self.formulario_widget)

        except Exception as e:
            print(f"❌ Error en mostrar_formulario_proyecto: {e}")
    

    def cargar_colaboradores(self):
        db = SessionLocal()
        try:
            self.colaboradores = db.query(Usuario).filter(
                Usuario.rol == RolUsuario.colaborador,
                Usuario.activo == 1
            ).all()
        except Exception as e:
            print(f"⚠️ Error cargando colaboradores: {e}")
            self.colaboradores = []
        finally:
            db.close()

    def añadir_campo_tarea(self):
        grupo = QFrame()
        layout = QFormLayout(grupo)

        titulo = QLineEdit()
        descripcion = QTextEdit()
        fecha = QDateEdit(calendarPopup=True)
        fecha.setDate(QDate.currentDate())

        combo_colab = QComboBox()
        for c in self.colaboradores:
            combo_colab.addItem(f"{c.nombre} ({c.correo})", c.id)

        layout.addRow("📌 Título:", titulo)
        layout.addRow("📝 Descripción:", descripcion)
        layout.addRow("📅 Vence:", fecha)
        layout.addRow("👤 Colaborador:", combo_colab)

        self.tareas_fields.append((titulo, descripcion, fecha, combo_colab))
        self.bloque_tareas.insertWidget(len(self.tareas_fields) - 1, grupo)

    # --- Tareas ---

    def abrir_tareas(self):
        self.limpiar_contenedor_contenido()

        cont = QWidget()
        self.layout_tareas = QVBoxLayout(cont)
        self.layout_tareas.setContentsMargins(30, 30, 30, 30)
        self.layout_tareas.setSpacing(20)

        title = QLabel("✅ Tareas creadas por ti")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2e7d32;")
        self.layout_tareas.addWidget(title)

    # Resumen de proyectos/tareas
        resumen = self.crear_resumen_admin()
        self.layout_tareas.addWidget(resumen)

    # Barra de búsqueda
        self.barra_busqueda_tareas = QLineEdit()
        self.barra_busqueda_tareas.setPlaceholderText("🔎 Buscar tarea...")
        self.barra_busqueda_tareas.setStyleSheet("padding: 8px; font-size: 14px; border-radius: 8px; border: 1px solid #ccc;")
        self.barra_busqueda_tareas.textChanged.connect(self.actualizar_lista_tareas)
        self.layout_tareas.addWidget(self.barra_busqueda_tareas)

    # Cargar tareas
        db = SessionLocal()
        tareas = db.query(Tarea).join(Proyecto).filter(
        Proyecto.id_usuario_creador == self.usuario.id,
        Tarea.estado != "inactivo"
        ).all()
        self.proyectos_dict = {p.id: p.nombre for p in db.query(Proyecto).all()}
        db.close()

        self.tareas_originales = tareas

        self.contenedor_tareas_cards = QVBoxLayout()
        self.layout_tareas.addLayout(self.contenedor_tareas_cards)

        self.mostrar_tarjetas_tareas(tareas)

        self.contenedor_contenido.setWidget(cont)



    def mostrar_tarjetas_tareas(self, tareas):
    # Limpiar tarjetas anteriores
        count = self.contenedor_tareas_cards.count()
        if count > 0:
            for i in reversed(range(count)):
                item = self.contenedor_tareas_cards.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)
                        widget.deleteLater()

    # Mostrar tareas
        for tarea in tareas:
            card = QFrame()

        # Color según estado
            if tarea.estado == "completada":
                color_fondo = "#c8e6c9"
            elif tarea.estado == "pendiente":
                color_fondo = "#fff9c4"
            else:
                color_fondo = "#ffcdd2"

            card.setStyleSheet(f"""
            QFrame {{
            background-color: {color_fondo};
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #ddd;
            }}
            """)

            v = QVBoxLayout(card)

            lbl_titulo = QLabel(f"📝 {tarea.titulo}")
            lbl_titulo.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))

            lbl_info = QLabel(
                f"📁 Proyecto: {self.proyectos_dict.get(tarea.id_proyecto, '')}\n"
                f"📅 Vence: {tarea.fecha_vencimiento}\n"
                f"🔧 Estado: {tarea.estado.capitalize()}"
            )
            lbl_info.setFont(QFont("Segoe UI", 11))
            lbl_info.setStyleSheet("color: #555;")

            lbl_desc = QLabel(tarea.descripcion or "")
            lbl_desc.setWordWrap(True)
            lbl_desc.setFont(QFont("Segoe UI", 11))

            progreso = self.calcular_progreso_por_fecha(date.today(), tarea.fecha_vencimiento)

            pb = QProgressBar()
            pb.setValue(progreso)
            pb.setFormat(f"{progreso}% del tiempo transcurrido")
            pb.setStyleSheet("QProgressBar { height: 15px; border-radius: 5px; }")

        # 🔵 Calcular y mostrar contador regresivo
            hoy = date.today()
            dias_restantes = (tarea.fecha_vencimiento - hoy).days

            if dias_restantes >= 0:
                lbl_contador = QLabel(f"⏳ Días restantes: {dias_restantes}")
                lbl_contador.setStyleSheet("color: #555; font-size: 11px;")
            else:
                lbl_contador = QLabel(f"❗ Vencida hace {abs(dias_restantes)} días")
                lbl_contador.setStyleSheet("color: red; font-size: 11px; font-weight: bold;")

            lbl_contador.setFont(QFont("Segoe UI", 10))

        # --- Armado visual ---
            v.addWidget(lbl_titulo)
            v.addWidget(lbl_info)
            v.addWidget(lbl_desc)
            v.addWidget(pb)
            v.addWidget(lbl_contador)

        # 🔵 Mostrar botón para abrir archivo o mensaje si no existe
            if tarea.ruta_archivo:
                btn_ver_archivo = QPushButton("📂 Ver Archivo")
                btn_ver_archivo.setStyleSheet("background-color: #1976d2; color: white; padding: 6px; border-radius: 6px;")
                btn_ver_archivo.clicked.connect(lambda _, ruta=tarea.ruta_archivo: self.abrir_archivo(ruta))
                v.addWidget(btn_ver_archivo)
            else:
                lbl_sin_archivo = QLabel("📂 Sin archivo adjunto")
                lbl_sin_archivo.setFont(QFont("Segoe UI", 10))
                v.addWidget(lbl_sin_archivo)

        # --- Botones de acción ---
            h_buttons = QHBoxLayout()
            btn_editar = QPushButton("✏️ Editar")
            btn_editar.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px; border-radius: 6px;")

            btn_eliminar = QPushButton("🗑 Eliminar")
            btn_eliminar.setStyleSheet("background-color: red; color: white; padding: 6px; border-radius: 6px;")
            btn_eliminar.clicked.connect(lambda _, t=tarea: self.eliminar_tarea(t))

            h_buttons.addWidget(btn_editar)
            h_buttons.addWidget(btn_eliminar)
            v.addLayout(h_buttons)

            self.contenedor_tareas_cards.addWidget(card)
            
    def abrir_archivo(self, ruta):
        if ruta and os.path.exists(ruta):
            try:
                os.startfile(ruta)  # Para Windows, abrir archivo con la app asociada
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo.\n{e}")
        else:
            QMessageBox.warning(self, "Advertencia", "El archivo no existe.")

    def actualizar_lista_tareas(self):
        texto = self.barra_busqueda_tareas.text().lower()
        filtradas = [t for t in self.tareas_originales if texto in t.titulo.lower()]
        self.mostrar_tarjetas_tareas(filtradas)


    # --- Notificaciones ---

    def abrir_notificaciones(self):
        self.limpiar_contenedor_contenido()
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
        Notificacion.id_usuario == self.usuario.id
        ).order_by(Notificacion.fecha.desc()).all()

        if not notificaciones:
            msg = QLabel("Actualmente no tienes notificaciones.")
            msg.setFont(QFont("Segoe UI", 12))
            layout.addWidget(msg)
        else:
            for noti in notificaciones:
                card = QFrame()
                card.setStyleSheet("""
                background-color: white;
                border-radius: 10px;
                padding: 10px;
                """)
                v = QVBoxLayout(card)

                lbl_mensaje = QLabel(f"🔔 {noti.mensaje}")
                lbl_mensaje.setFont(QFont("Segoe UI", 12))
                if not noti.leido:
                    lbl_mensaje.setStyleSheet("color: #000000; font-weight: bold;")
                else:
                    lbl_mensaje.setStyleSheet("color: #555555;")
                    v.addWidget(lbl_mensaje)

                if not noti.leido:
                    btn_leer = QPushButton("✅ Marcar como leído")
                    btn_leer.setStyleSheet("background-color: #81c784; padding: 5px; border-radius: 5px;")
                    btn_leer.clicked.connect(lambda _, n_id=noti.id: self.marcar_notificacion_leida(n_id))
                    v.addWidget(btn_leer)

                layout.addWidget(card)

        db.close()
        self.contenedor_contenido.setWidget(cont)

    def guardar_proyecto(self, proyecto=None):
        nombre = self.input_nombre.text().strip()
        descripcion = self.input_descripcion.toPlainText().strip()
        fecha_inicio = self.input_inicio.date().toPyDate()
        fecha_fin = self.input_fin.date().toPyDate()

        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre del proyecto no puede estar vacío.")
            return
        if fecha_inicio > fecha_fin:
            QMessageBox.warning(self, "Error", "La fecha de inicio no puede ser posterior a la de fin.")
            return

        db = SessionLocal()
        try:
            if proyecto:
                pj = db.get(Proyecto, proyecto.id)
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
                    id_usuario_creador=self.usuario.id
                )
                db.add(pj)
                db.flush()  # Para obtener el id del nuevo proyecto

            # ✅ Guardar tareas dinámicas
            for titulo, descripcion, fecha, combo_colab in self.tareas_fields:
                t = titulo.text().strip()
                d = descripcion.toPlainText().strip()
                f = fecha.date().toPyDate()
                colaborador_id = combo_colab.currentData()

                if t:
                    nueva_tarea = Tarea(
                        titulo=t,
                        descripcion=d,
                        fecha_vencimiento=f,
                        estado="pendiente",
                        id_proyecto=pj.id,
                        id_usuario_asignado=colaborador_id
                    )
                    db.add(nueva_tarea)

                    # ✅ Enviar correo de asignación
                    from backend.auth import enviar_correo_asignacion
                    colaborador = db.query(Usuario).get(colaborador_id)
                    if colaborador and colaborador.correo:
                        enviar_correo_asignacion(colaborador.correo, colaborador.nombre, t, pj.nombre)

            db.commit()
            QMessageBox.information(self, "✅ Éxito", "Proyecto y tareas guardados correctamente.")
            self.abrir_proyectos()

        except Exception as e:
            db.rollback()
            print(f"❌ Error al guardar proyecto: {e}")
            QMessageBox.critical(self, "❌ Error", "No se pudo guardar el proyecto.")
        finally:
            db.close()

    def crear_resumen_admin(self):
        resumen = QFrame()
        resumen.setStyleSheet("""
        QFrame {
            background-color: #e8f5e9;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #c8e6c9;
        }
        """)
        layout = QHBoxLayout(resumen)
        layout.setSpacing(30)

        db = SessionLocal()
        proyectos_activos = db.query(Proyecto).filter(
        Proyecto.estado == "activo",
        Proyecto.id_usuario_creador == self.usuario.id
        ).count()

        tareas_pendientes = db.query(Tarea).join(Proyecto).filter(
        Proyecto.id_usuario_creador == self.usuario.id,
        Tarea.estado == "pendiente"
        ).count()
        db.close()

        label_proyectos = QLabel(f"📁 Proyectos activos: {proyectos_activos}")
        label_proyectos.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        label_tareas = QLabel(f"📝 Tareas pendientes: {tareas_pendientes}")
        label_tareas.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))

        layout.addWidget(label_proyectos)
        layout.addWidget(label_tareas)

        return resumen

    def calcular_progreso_por_fecha(self, fecha_inicio, fecha_fin):
        if fecha_inicio > fecha_fin:
            return 0

        today = date.today()

        dias_totales = (fecha_fin - fecha_inicio).days
        dias_transcurridos = (today - fecha_inicio).days

        if dias_totales <= 0:
            return 100

        progreso = int((dias_transcurridos / dias_totales) * 100)
        progreso = max(0, min(progreso, 100))
        return progreso

    def eliminar_tarea(self, tarea):
        try:
            session = SessionLocal()
            tarea_db = session.query(Tarea).get(tarea.id)
            if tarea_db:
                tarea_db.estado = 'inactivo'
                session.commit()
                QMessageBox.information(self, "Eliminado", "La tarea fue eliminada correctamente.")
                self.actualizar_tarjetas_tareas()
            else:
                QMessageBox.warning(self, "Error", "La tarea no fue encontrada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar la tarea: {e}")
        finally:
            session.close()


    def actualizar_tarjetas_tareas(self):
        try:
            session = SessionLocal()
            tareas = session.query(Tarea).filter(Tarea.estado != "inactivo").all()
            self.mostrar_tarjetas_tareas(tareas)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron actualizar las tareas: {e}")
        finally:
            session.close()

