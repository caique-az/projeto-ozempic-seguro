from ..base_frame import BaseFrameView
from ..components import ResponsiveButtonGrid
from .admin_gavetas_view import AdminGavetasFrame
from .auditoria_view import AuditoriaFrame
from .cadastro_usuario_view import CadastroUsuarioFrame
from .diagnostico_view import DiagnosticoFrame
from .gerenciamento_usuarios_view import GerenciamentoUsuariosFrame
from .historico_view import HistoricoView


class PainelAdministradorFrame(BaseFrameView):
    """Painel do administrador - herda de BaseFrameView"""

    def __init__(self, master, end_session_callback=None, logged_in_user=None, *args, **kwargs):
        self.logged_in_user = logged_in_user
        super().__init__(master, end_session_callback, *args, **kwargs)
        self.create_main_screen()

    def create_main_screen(self):
        """Creates the administrator main screen"""
        for widget in self.winfo_children():
            widget.destroy()

        self.create_header_widget("Administrador")
        self.create_buttons()
        self.create_finish_button()

    def create_buttons(self):
        buttons_data = [
            {
                "text": "👥 Gerenciar Usuários",
                "command": self.manage_users,
                "style": "primary",
            },
            {"text": "🗄️ Gerenciar Gavetas", "command": self.manage_drawers, "style": "primary"},
            {"text": "➕ Cadastro de Usuário", "command": self.register_user, "style": "success"},
            {
                "text": "📋 Registro de Auditoria",
                "command": self.audit_registry,
                "style": "secondary",
            },
            {"text": "🔧 Diagnóstico", "command": self.diagnostics, "style": "warning"},
            {"text": "📊 Histórico", "command": self.show_history, "style": "secondary"},
        ]
        self.button_grid = ResponsiveButtonGrid(self, buttons_data, max_cols=3)

    def manage_drawers(self):
        self._transition_screen(lambda: AdminGavetasFrame(self, back_callback=self.back_to_main))

    def show_history(self):
        self._transition_screen(lambda: HistoricoView(self, back_callback=self.back_to_main))

    def audit_registry(self):
        self._transition_screen(lambda: AuditoriaFrame(self, back_callback=self.back_to_main))

    def manage_users(self):
        def create():
            if hasattr(self, "logged_in_user"):
                GerenciamentoUsuariosFrame(
                    self, back_callback=self.back_to_main, logged_in_user=self.logged_in_user
                )
            else:
                GerenciamentoUsuariosFrame(
                    self, back_callback=self.back_to_main, logged_in_user=None
                )

        self._transition_screen(create)

    def register_user(self):
        self._transition_screen(lambda: CadastroUsuarioFrame(self, back_callback=self.back_to_main))

    def diagnostics(self):
        self._transition_screen(lambda: DiagnosticoFrame(self, back_callback=self.back_to_main))

    def back_to_main(self):
        """Returns to main screen with transition"""
        self._transition_screen(self.create_main_screen)
