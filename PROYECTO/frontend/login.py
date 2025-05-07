import sys, os
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy, QFrame
from PyQt6.QtGui import QFont, QPixmap, QCursor
from PyQt6.QtCore import Qt, pyqtSignal
from backend.auth import verificar_login, crear_usuario, resetear_contraseña

class LoginWindow(QWidget):
    login_exitoso     = pyqtSignal(object)
    navegar_registro  = pyqtSignal()
    navegar_recuperar = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f0f0f0;")
        self._build_ui()

    def _build_ui(self):
        base = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base, "..", "imagenes", "logo.png")
        form = QFrame(self)
        form.setFixedSize(420,580); form.setStyleSheet("background:white; border-radius:12px;")
        f = QVBoxLayout(form)
        f.setContentsMargins(40,40,40,40); f.setSpacing(20)
        logo = QLabel()
        pix = QPixmap(logo_path)
        if not pix.isNull():
            logo.setPixmap(pix.scaled(120,120,Qt.AspectRatioMode.KeepAspectRatio))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f.addWidget(logo)
        title = QLabel("Gestor de Tareas")
        title.setFont(QFont("Segoe UI",20,QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color:#2e7d32;")
        f.addWidget(title)
        self.email = QLineEdit(); self.email.setPlaceholderText("Correo electrónico")
        self.email.setFont(QFont("Segoe UI",12))
        self.email.setStyleSheet("padding:12px; border:1px solid #BDBDBD; border-radius:8px;")
        f.addWidget(self.email)
        self.password = QLineEdit(); self.password.setPlaceholderText("Contraseña")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFont(QFont("Segoe UI",12))
        self.password.setStyleSheet("padding:12px; border:1px solid #BDBDBD; border-radius:8px;")
        f.addWidget(self.password)
        btn_login = QPushButton("🎯 Iniciar Sesión")
        btn_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_login.setStyleSheet("background:#4CAF50; color:white; padding:12px; border-radius:8px;")
        btn_login.clicked.connect(self.iniciar_sesion)
        f.addWidget(btn_login)
        forgot = QPushButton("¿Olvidaste tu contraseña?")
        forgot.setStyleSheet("background:none; color:#E53935; border:none;")
        forgot.clicked.connect(lambda: self.navegar_recuperar.emit())
        register = QPushButton("¿No tienes cuenta? Regístrate")
        register.setStyleSheet("background:none; color:#2e7d32; border:none;")
        register.clicked.connect(lambda: self.navegar_registro.emit())
        f.addWidget(forgot); f.addWidget(register)
        f.addSpacerItem(QSpacerItem(20,20,QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding))
        main = QVBoxLayout(self)
        main.addStretch(); main.addWidget(form, alignment=Qt.AlignmentFlag.AlignCenter); main.addStretch()

    def iniciar_sesion(self):
        ok, user = verificar_login(self.email.text().strip(), self.password.text().strip())
        if ok:
            self.login_exitoso.emit(user)
        else:
            QMessageBox.critical(self, "Error", "Correo o contraseña incorrectos")

class RegistroWindow(QWidget):
    registro_exitoso = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#f0f0f0;")
        self._build_ui()
    def _build_ui(self):
        pass

class RecuperarPasswordWindow(QWidget):
    recuperacion_exitosa = pyqtSignal()
    def __init__(self):
        super().__init__(); self.setWindowTitle("Recuperar Contraseña"); self.setStyleSheet("background:#f0f0f0;"); self._build_ui()
    def _build_ui(self):

        pass
