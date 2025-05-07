import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget
from frontend.login import LoginWindow
from frontend.registro import RegistroWindow
from frontend.recuperar import RecuperarPasswordWindow
from frontend.panel_principal import PanelAdmin
from frontend.panel_usuario import PanelUsuario
from frontend.portada import Portada


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Tareas")
        self.setMinimumSize(1000, 600)

        self.stacked_widget = QStackedWidget()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked_widget)

        # Instancias de vistas
        self.portada_view = Portada()
        self.login_view = LoginWindow()
        self.registro_view = RegistroWindow()
        self.recuperar_view = RecuperarPasswordWindow()

        # Conexiones de navegación
        self.portada_view.navegar.connect(self.ir_a_pantalla)
        self.login_view.login_exitoso.connect(self.abrir_panel_por_rol)
        self.login_view.navegar_registro.connect(lambda: self.stacked_widget.setCurrentWidget(self.registro_view))
        self.login_view.navegar_recuperar.connect(lambda: self.stacked_widget.setCurrentWidget(self.recuperar_view))
        self.registro_view.registro_exitoso.connect(lambda: self.stacked_widget.setCurrentWidget(self.login_view))
        self.recuperar_view.recuperacion_exitosa.connect(lambda: self.stacked_widget.setCurrentWidget(self.login_view))

        # Agregar vistas al stack
        self.stacked_widget.addWidget(self.portada_view)
        self.stacked_widget.addWidget(self.login_view)
        self.stacked_widget.addWidget(self.registro_view)
        self.stacked_widget.addWidget(self.recuperar_view)

        # Mostrar portada al inicio
        self.stacked_widget.setCurrentWidget(self.portada_view)

        print("✅ Aplicación cargada correctamente.")

    def ir_a_pantalla(self, destino: str):
        print(f"📌 Navegando a pantalla: {destino}")
        if destino == "login":
            self.stacked_widget.setCurrentWidget(self.login_view)
        elif destino == "registro":
            self.stacked_widget.setCurrentWidget(self.registro_view)

    def abrir_panel_por_rol(self, usuario):
        print(f"📌 Abriendo panel para rol: {usuario.rol.value}")
        if hasattr(self, "panel_actual"):
            self.stacked_widget.removeWidget(self.panel_actual)
            self.panel_actual.deleteLater()

        if usuario.rol.value == "admin":
            self.panel_actual = PanelAdmin(usuario, cerrar_callback=self.volver_al_login)
        else:
             self.panel_actual = PanelUsuario(usuario, cerrar_callback=self.volver_al_login)

        self.stacked_widget.addWidget(self.panel_actual)
        self.stacked_widget.setCurrentWidget(self.panel_actual)

    def volver_al_login(self):
        print("📌 Volviendo al login.")
        self.stacked_widget.setCurrentWidget(self.login_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 🔥 Carga del estilo corregido
    base_dir = os.path.dirname(os.path.abspath(__file__))
    style_path = os.path.join(base_dir, "style.qss")

    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        print("✅ Estilo cargado desde style.qss.")
    else:
        print("⚠️ Archivo style.qss no encontrado. Usando estilo por defecto.")

    ventana = MainApp()
    ventana.show()
    print("✅ Ventana principal mostrada.")

    # ⚡ Aquí está el cambio importante:
    try:
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌ Error detectado en la aplicación: {e}")
