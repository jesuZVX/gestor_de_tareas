# frontend/recuperar.py
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QSpacerItem, QSizePolicy, QFrame
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import pyqtSignal, Qt
from backend.auth import resetear_contraseña

class RecuperarPasswordWindow(QWidget):
    recuperacion_exitosa = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f0f0f0;")
        self._build_ui()

    def _build_ui(self):
        form = QFrame(self)
        form.setFixedSize(420, 500)
        form.setStyleSheet("background:white; border-radius:12px;")
        f = QVBoxLayout(form)
        f.setContentsMargins(40, 40, 40, 40)
        f.setSpacing(20)

        self.correo_edit = QLineEdit()
        self.correo_edit.setPlaceholderText("Correo electrónico")
        self.correo_edit.setFont(QFont("Segoe UI", 12))
        self.correo_edit.setStyleSheet("padding:12px; border:1px solid #BDBDBD; border-radius:8px;")
        f.addWidget(self.correo_edit)

        self.nueva_contraseña_edit = QLineEdit()
        self.nueva_contraseña_edit.setPlaceholderText("Nueva Contraseña")
        self.nueva_contraseña_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.nueva_contraseña_edit.setFont(QFont("Segoe UI", 12))
        self.nueva_contraseña_edit.setStyleSheet("padding:12px; border:1px solid #BDBDBD; border-radius:8px;")
        f.addWidget(self.nueva_contraseña_edit)

        self.confirmar_contraseña_edit = QLineEdit()
        self.confirmar_contraseña_edit.setPlaceholderText("Confirmar Contraseña")
        self.confirmar_contraseña_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirmar_contraseña_edit.setFont(QFont("Segoe UI", 12))
        self.confirmar_contraseña_edit.setStyleSheet("padding:12px; border:1px solid #BDBDBD; border-radius:8px;")
        f.addWidget(self.confirmar_contraseña_edit)

        btn_reset = QPushButton("🔄 Cambiar Contraseña")
        btn_reset.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_reset.setStyleSheet("background:#4CAF50; color:white; padding:12px; border-radius:8px;")
        btn_reset.clicked.connect(self.recuperar)
        f.addWidget(btn_reset)

        f.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        main = QVBoxLayout(self)
        main.addStretch()
        main.addWidget(form, alignment=Qt.AlignmentFlag.AlignCenter)
        main.addStretch()

    def recuperar(self):
        correo = self.correo_edit.text().strip()
        nueva_contra = self.nueva_contraseña_edit.text().strip()
        confirmar_contra = self.confirmar_contraseña_edit.text().strip()

        if not correo or not nueva_contra or not confirmar_contra:
            QMessageBox.warning(self, "Campos Vacíos", "Por favor llena todos los campos.")
            return

        if nueva_contra != confirmar_contra:
            QMessageBox.warning(self, "Contraseñas No Coinciden", "Las contraseñas ingresadas no coinciden.")
            return

        ok, mensaje = resetear_contraseña(correo, nueva_contra)
        if ok:
            QMessageBox.information(self, "Éxito", mensaje)
            self.recuperacion_exitosa.emit()
        else:
            QMessageBox.critical(self, "Error", mensaje)
