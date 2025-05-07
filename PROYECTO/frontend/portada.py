from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, pyqtSignal
import os

class Portada(QWidget):
    navegar = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._setup_background()
        self._build_ui()


    def _setup_background(self):
        base = os.path.dirname(os.path.abspath(__file__))
        ruta = os.path.abspath(os.path.join(base, "..", "imagenes", "fondo_inicio.png"))

        self.fondo = QLabel(self)
        self.fondo.setGeometry(0, 0, 1100, 650) 

        if os.path.exists(ruta):
            pixmap = QPixmap(ruta)
            if not pixmap.isNull():
                self.fondo.setPixmap(pixmap)
                self.fondo.setScaledContents(True)
                print("✅ Fondo cargado correctamente.")
            else:
                print("⚠️ Fondo encontrado pero inválido:", ruta)
                self.setStyleSheet("background-color: white;")
        else:
            print("⚠️ No se encontró el fondo:", ruta)
            self.setStyleSheet("background-color: white;")

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.addStretch()
        overlay = QFrame()
        overlay.setMaximumSize(800, 500)
        overlay.setStyleSheet("QFrame{ background-color: rgba(255,255,255,0.9); border-radius:20px; }")
        overlay.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=30))
        v = QVBoxLayout(overlay)
        v.setContentsMargins(30,30,30,30)
        # logo
        logo = QLabel()
        lp = os.path.join(os.path.dirname(__file__), "..", "imagenes", "logo.png")
        pix = QPixmap(lp)
        if not pix.isNull():
            logo.setPixmap(pix.scaled(100,100,Qt.AspectRatioMode.KeepAspectRatio))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(logo)
        # título
        title = QLabel("Bienvenido al Gestor de Tareas")
        title.setFont(QFont("Arial",24,QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color:#2e7d32;")
        v.addWidget(title)
        subtitle = QLabel("Organiza tus proyectos y tareas con inspiración 💡")
        subtitle.setFont(QFont("Arial",12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color:#555;")
        v.addWidget(subtitle)
        v.addSpacerItem(QSpacerItem(20,20,QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding))
        h = QHBoxLayout()
        btn_login = QPushButton("🎯 Iniciar Sesión")
        btn_login.setStyleSheet("background:#4CAF50; color:white; padding:10px 20px; border-radius:8px;")
        btn_login.clicked.connect(lambda: self.navegar.emit("login"))
        h.addWidget(btn_login)
        btn_reg = QPushButton("✍️ Registrarse")
        btn_reg.setStyleSheet("background:#2e7d32; color:white; padding:10px 20px; border-radius:8px;")
        btn_reg.clicked.connect(lambda: self.navegar.emit("registro"))
        h.addWidget(btn_reg)
        v.addLayout(h)
        v.addSpacerItem(QSpacerItem(20,20,QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding))
        wrapper = QHBoxLayout()
        wrapper.addStretch(); wrapper.addWidget(overlay); wrapper.addStretch()
        main.addLayout(wrapper)
        main.addStretch()
