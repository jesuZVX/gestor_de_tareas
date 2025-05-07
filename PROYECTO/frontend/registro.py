# frontend/registro.py
import os
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QMessageBox, QComboBox, QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import pyqtSignal, Qt
from backend.auth import crear_usuario

class RegistroWindow(QWidget):
    registro_exitoso = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f0f0f0;")
        self._build_ui()

    def _build_ui(self):
        form = QFrame(self)
        form.setFixedSize(420, 680)
        form.setStyleSheet("background:white; border-radius:12px;")
        f = QVBoxLayout(form)
        f.setContentsMargins(40, 40, 40, 40)
        f.setSpacing(20)

        self.nombre = QLineEdit(); self.nombre.setPlaceholderText("Nombre completo")
        self.nombre_usuario = QLineEdit(); self.nombre_usuario.setPlaceholderText("Nombre de usuario")
        self.documento = QLineEdit(); self.documento.setPlaceholderText("Documento de identidad")
        self.correo = QLineEdit(); self.correo.setPlaceholderText("Correo electrónico")
        self.password = QLineEdit(); self.password.setPlaceholderText("Contraseña")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.rol_combo = QComboBox()
        self.rol_combo.addItems(["colaborador", "admin"])
        self.rol_combo.setStyleSheet("padding:12px; border:1px solid #BDBDBD; border-radius:8px;")
        self.rol_combo.setFont(QFont("Segoe UI", 12))

        for w in [self.nombre, self.nombre_usuario, self.documento, self.correo, self.password, self.rol_combo]:
            w.setFont(QFont("Segoe UI", 12))
            f.addWidget(w)

        btn_register = QPushButton("🎯 Registrarse")
        btn_register.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_register.setStyleSheet("background:#4CAF50; color:white; padding:12px; border-radius:8px;")
        btn_register.clicked.connect(self.registrar)
        f.addWidget(btn_register)

        f.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        main = QVBoxLayout(self)
        main.addStretch()
        main.addWidget(form, alignment=Qt.AlignmentFlag.AlignCenter)
        main.addStretch()

    def registrar(self):
        rol_seleccionado = self.rol_combo.currentText()
        ok, mensaje = crear_usuario(
            self.nombre.text().strip(),
            self.nombre_usuario.text().strip(),
            self.documento.text().strip(),
            self.correo.text().strip(),
            self.password.text().strip(),
            rol_seleccionado
        )
        if ok:
            QMessageBox.information(self, "Éxito", mensaje)
            self.registro_exitoso.emit()
        else:
            QMessageBox.critical(self, "Error", mensaje)
