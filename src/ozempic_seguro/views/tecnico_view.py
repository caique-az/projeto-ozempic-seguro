import customtkinter
from .base_frame import BaseFrameView
from .components import ModernButton, ToastNotification
from .pages_adm.diagnostico_view import DiagnosticoFrame
from .pages_adm.controle_timer_view import ControleTimerFrame
from ..services.timer_control_service import get_timer_control_service


class TecnicoFrame(BaseFrameView):
    """Tela principal do técnico - herda de BaseFrameView"""

    def __init__(self, master, end_session_callback=None, *args, **kwargs):
        super().__init__(master, end_session_callback, *args, **kwargs)
        self.create_main_screen()

    def create_main_screen(self):
        """Creates the technician main screen"""
        for widget in self.winfo_children():
            widget.destroy()

        self.create_header_widget("Técnico")
        self.create_buttons()
        self.create_finish_button()

    def create_buttons(self):
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, pady=30)

        ModernButton(
            main_frame,
            text="🔧 Diagnóstico",
            command=self.open_diagnostics,
            style="warning",
            width=280,
            height=60,
        ).pack(pady=15)

        ModernButton(
            main_frame,
            text="⏱️ Controle de Timer",
            command=self.open_timer_control,
            style="secondary",
            width=280,
            height=60,
        ).pack(pady=15)

    def end_session(self):
        """Overrides to reactivate timer on exit using TimerControlService"""
        from .components import ModernConfirmDialog

        if ModernConfirmDialog.ask(
            self,
            "Finalizar Sessão",
            "Tem certeza que deseja sair do sistema?",
            icon="question",
            confirm_text="Sair",
            cancel_text="Cancelar",
        ):
            # Reactivate timer when logging out of technician using the service
            timer_service = get_timer_control_service()
            if not timer_service.is_timer_enabled():
                timer_service.enable_timer()
                ToastNotification.show(self, "Timer reativado automaticamente", "info")

            ToastNotification.show(self, "Sessão finalizada com sucesso", "success")
            if self.end_session_callback:
                self.after(1000, self._execute_logout)

    def open_diagnostics(self):
        """Opens the diagnostics screen"""
        self._transition_screen(lambda: DiagnosticoFrame(self, self.back_to_main))

    def open_timer_control(self):
        """Opens the timer control screen"""
        self._transition_screen(lambda: ControleTimerFrame(self, self.back_to_main))

    def back_to_main(self):
        """Returns to the technician main screen"""
        self._transition_screen(self.create_main_screen)
