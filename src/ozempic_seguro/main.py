"""
Módulo principal da aplicação Ozempic Seguro.

Inicializa a interface gráfica e configura os componentes do sistema.
"""

import customtkinter

from .controllers.navigation_controller import NavigationController
from .core.logger import logger


def _preload_images() -> None:
    """Pré-carrega imagens para acelerar a renderização das telas"""
    from .views.components.common import ImageCache
    from .views.components.gavetas import _GavetaImageCache

    # Pré-carregar imagens do header
    ImageCache.get_logo()
    ImageCache.get_digital()

    # Pré-carregar imagens das gavetas
    _GavetaImageCache.get_gaveta_aberta()
    _GavetaImageCache.get_gaveta_fechada()


def _setup_audit_callback() -> None:
    """Configura callback de auditoria para SessionManager (evita import circular)"""
    from .services.audit_service import AuditService
    from .session.session_manager import SessionManager

    audit_service = AuditService()

    def audit_callback(user_id: int, action: str, table: str, data: dict) -> None:
        audit_service.create_log(
            user_id=user_id, action=action, affected_table=table, previous_data=data
        )

    SessionManager.set_audit_callback(audit_callback)


class MainApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        from .config import AppConfig, UIConfig

        # Hide window during initialization
        self.withdraw()

        # Pre-load images to speed up rendering
        _preload_images()

        # Configure audit callback first
        _setup_audit_callback()

        self.title(AppConfig.APP_NAME)
        self.geometry(f"{UIConfig.WINDOW_WIDTH}x{UIConfig.WINDOW_HEIGHT}")
        self.minsize(UIConfig.WINDOW_MIN_WIDTH, UIConfig.WINDOW_MIN_HEIGHT)
        customtkinter.set_appearance_mode(UIConfig.THEME_MODE)
        customtkinter.set_default_color_theme(UIConfig.THEME_COLOR)

        # Main container for all screens
        self.container = customtkinter.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # Navigation controller - direct initialization
        self.nav_controller = NavigationController(self)
        self.nav_controller.preload_frames()
        self.nav_controller.show_touch_screen()

        # Force complete rendering before showing
        self.update_idletasks()
        self.update()

        # Show window after everything is ready
        self.deiconify()

        self.nav_controller.start_alternation()

        # Configure proper application shutdown
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Shuts down the application properly, cleaning all resources"""
        try:
            # Stop navigation controller if exists
            if hasattr(self, "nav_controller") and self.nav_controller:
                self.nav_controller.cleanup()

            # Clean session manager
            from .session.session_manager import SessionManager

            session = SessionManager.get_instance()
            session.cleanup()

            # Destroy main window
            self.destroy()

            # Force shutdown if needed
            import sys

            sys.exit(0)

        except Exception as e:
            logger.error(f"Error closing application: {e}")
            # Force shutdown even with error
            import sys

            sys.exit(1)


def main():
    """Main function to start the application"""
    try:
        app = MainApp()
        app.mainloop()
    except KeyboardInterrupt:
        # Shutdown via Ctrl+C or abrupt close
        pass
    except Exception as e:
        logger.error(f"Fatal application error: {e}")


if __name__ == "__main__":
    main()
