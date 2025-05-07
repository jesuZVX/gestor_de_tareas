import os
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QTextEdit, QDateEdit, QComboBox, QPushButton, QFormLayout, QHBoxLayout, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from backend.database import SessionLocal, Proyecto

class ProyectoDialog(QDialog):
    proyecto_guardado = pyqtSignal()
    def __init__(self, usuario, parent=None, proyecto=None):
        super().__init__(parent)
        self.usuario = usuario
        self.proyecto = proyecto
        self.setWindowTitle("Editar Proyecto" if proyecto else "Crear Proyecto")
        self.setFixedSize(400,450)
        self._build_ui()
        if proyecto:
            self._load_data()

    def _build_ui(self):
        font = QFont("Segoe UI",10)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.nombre_edit = QLineEdit(); self.nombre_edit.setFont(font)
        form.addRow("Nombre:", self.nombre_edit)
        self.descripcion_edit = QTextEdit(); self.descripcion_edit.setFont(font); self.descripcion_edit.setFixedHeight(100)
        form.addRow("Descripción:", self.descripcion_edit)
        self.fecha_inicio = QDateEdit(calendarPopup=True); self.fecha_inicio.setFont(font); self.fecha_inicio.setDate(QDate.currentDate())
        form.addRow("Fecha de inicio:", self.fecha_inicio)
        self.fecha_fin = QDateEdit(calendarPopup=True); self.fecha_fin.setFont(font); self.fecha_fin.setDate(QDate.currentDate())
        form.addRow("Fecha de fin:", self.fecha_fin)
        self.estado_combo = QComboBox(); self.estado_combo.addItems(["activo","inactivo"])
        form.addRow("Estado:", self.estado_combo)
        btn_guardar = QPushButton("💾 Guardar"); btn_cancel = QPushButton("✖ Cancelar")
        btn_guardar.clicked.connect(self._on_guardar); btn_cancel.clicked.connect(self.reject); btn_guardar.setDefault(True)
        h = QHBoxLayout(); h.addStretch(); h.addWidget(btn_cancel); h.addWidget(btn_guardar)
        v = QVBoxLayout(self); v.addLayout(form); v.addStretch(); v.addLayout(h)

    def _load_data(self):
        p = self.proyecto
        self.nombre_edit.setText(p.nombre)
        self.descripcion_edit.setPlainText(p.descripcion or "")
        if p.fecha_inicio: self.fecha_inicio.setDate(p.fecha_inicio)
        if p.fecha_fin:    self.fecha_fin.setDate(p.fecha_fin)
        idx = self.estado_combo.findText(p.estado or "activo")
        if idx>=0: self.estado_combo.setCurrentIndex(idx)

    def _on_guardar(self):
        n = self.nombre_edit.text().strip()
        if not n:
            QMessageBox.warning(self, "Validación","El nombre no puede quedar vacío.")
            return
        fi = self.fecha_inicio.date().toPyDate()
        ff = self.fecha_fin.date().toPyDate()
        if fi>ff:
            QMessageBox.warning(self, "Validación","La fecha final no puede ser anterior.")
            return
        db = SessionLocal()
        try:
            if self.proyecto:
                pj = db.query(Proyecto).get(self.proyecto.id)
                pj.nombre = n; pj.descripcion = self.descripcion_edit.toPlainText().strip()
                pj.fecha_inicio = fi; pj.fecha_fin = ff; pj.estado = self.estado_combo.currentText()
            else:
                nuevo = Proyecto(
                    nombre=n,
                    descripcion=self.descripcion_edit.toPlainText().strip(),
                    fecha_inicio=fi,
                    fecha_fin=ff,
                    estado=self.estado_combo.currentText(),
                    id_usuario_creador=self.usuario.id
                )
                db.add(nuevo)
            db.commit()
            self.proyecto_guardado.emit()
            self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self,"Error",f"No se pudo guardar:\n{e}")
        finally:
            db.close()
