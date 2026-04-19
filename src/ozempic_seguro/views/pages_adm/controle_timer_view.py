"""
Tela de Controle de Timer - Exclusiva para usuários técnicos.
Permite desativar temporariamente o timer enquanto o técnico está logado.
"""
import customtkinter
from ..components import Header, VoltarButton, ModernConfirmDialog, ToastNotification
from ...services.timer_control_service import get_timer_control_service
from ...services.auth_service import get_auth_service


class ControleTimerFrame(customtkinter.CTkFrame):
    BG_COLOR = "#3B6A7D"

    def __init__(self, master, back_callback=None, *args, **kwargs):
        self.back_callback = back_callback
        self.timer_service = get_timer_control_service()
        self.auth_service = get_auth_service()
        super().__init__(master, fg_color=self.BG_COLOR, *args, **kwargs)

        # Criar overlay para esconder construção
        self._overlay = customtkinter.CTkFrame(master, fg_color=self.BG_COLOR)
        self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._overlay.lift()
        master.update_idletasks()

        self.pack(fill="both", expand=True)

        # Criar header
        self.header = Header(self, "Controle de Timer")

        # Frame principal para o conteúdo
        self.main_content = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=20, pady=(20, 80))

        # Criar controle de timer
        self.create_timer_control()

        # Criar botão voltar
        self.create_back_button()

        # Remover overlay após tudo estar pronto
        self.update_idletasks()
        self._overlay.destroy()

    def create_timer_control(self):
        """Creates control to enable/disable timer"""
        # Frame central para o controle
        frame_central = customtkinter.CTkFrame(
            self.main_content, fg_color="white", corner_radius=15
        )
        frame_central.pack(expand=True, fill="both", pady=20)

        # Título
        lbl_titulo = customtkinter.CTkLabel(
            frame_central,
            text="Controle de Timer de Sessão",
            font=("Arial", 20, "bold"),
            text_color="#333333",
        )
        lbl_titulo.pack(pady=(30, 10))

        # Descrição
        lbl_descricao = customtkinter.CTkLabel(
            frame_central,
            text="Quando desativado, o sistema não bloqueará automaticamente por inatividade.\nO timer será reativado automaticamente ao fazer logout.",
            font=("Arial", 12),
            text_color="#666666",
            justify="center",
        )
        lbl_descricao.pack(pady=(0, 30))

        # Frame para status
        self.frame_status = customtkinter.CTkFrame(
            frame_central, fg_color="#E8F5E9", corner_radius=10
        )
        self.frame_status.pack(pady=20, padx=40)

        # Indicador de status
        self.lbl_status = customtkinter.CTkLabel(
            self.frame_status, text="", font=("Arial", 18, "bold"), text_color="#333333"
        )
        self.lbl_status.pack(padx=50, pady=25)

        # Botão de controle
        self.btn_controle = customtkinter.CTkButton(
            frame_central,
            text="",
            width=200,
            height=50,
            font=("Arial", 14, "bold"),
            command=self.toggle_timer,
        )
        self.btn_controle.pack(pady=20)

        # Informação adicional
        lbl_info = customtkinter.CTkLabel(
            frame_central,
            text="⚠️ Esta configuração é temporária e válida\napenas durante esta sessão",
            font=("Arial", 11),
            text_color="#FF6B6B",
            justify="center",
        )
        lbl_info.pack(pady=(10, 20), padx=20)

        # Atualizar estado inicial
        self.update_state()

    def toggle_timer(self):
        """Toggles the timer state using TimerControlService"""
        # Verifica se o usuário é técnico
        user = self.auth_service.get_current_user()
        if not user or user.get("tipo") != "tecnico":
            ToastNotification.show(self, "Acesso negado! Apenas técnicos podem alterar.", "error")
            return

        status = self.timer_service.get_status()

        if status.enabled:
            # Vai desativar - pedir confirmação
            if ModernConfirmDialog.ask(
                self,
                "Desativar Timer",
                "Tem certeza que deseja DESATIVAR o timer?\n\nO sistema não bloqueará por inatividade.",
                icon="warning",
                confirm_text="Desativar",
                cancel_text="Cancelar",
            ):
                success, msg = self.timer_service.disable_timer()
                if success:
                    ToastNotification.show(self, "Timer DESATIVADO!", "warning")
                self.update_state()
        else:
            # Vai ativar - sem confirmação necessária
            success, msg = self.timer_service.enable_timer()
            if success:
                ToastNotification.show(self, "Timer ATIVADO com sucesso!", "success")
            self.update_state()

    def update_state(self):
        """Updates interface according to timer state"""
        status = self.timer_service.get_status()
        timer_active = status.enabled

        if timer_active:
            # Timer enabled - light green background
            self.frame_status.configure(fg_color="#E8F5E9")
            self.lbl_status.configure(text="🟢 Timer ATIVADO", text_color="#2E7D32")
            self.btn_controle.configure(
                text="Desativar Timer", fg_color="#F44336", hover_color="#D32F2F"
            )
        else:
            # Timer disabled - light red background
            self.frame_status.configure(fg_color="#FFEBEE")
            self.lbl_status.configure(text="🔴 Timer DESATIVADO", text_color="#C62828")
            self.btn_controle.configure(
                text="Ativar Timer", fg_color="#4CAF50", hover_color="#388E3C"
            )

        # Force visual update
        self.frame_status.update()
        self.lbl_status.update()
        self.btn_controle.update()

    def create_back_button(self):
        """Creates back button"""
        VoltarButton(self, self.back_callback)
