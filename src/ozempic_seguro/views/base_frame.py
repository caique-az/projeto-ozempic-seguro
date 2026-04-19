"""
BaseFrameView - Base class for frames with smooth transitions
"""

import customtkinter

from .components import FinalizarSessaoButton, Header, ModernConfirmDialog, ToastNotification


class BaseFrameView(customtkinter.CTkFrame):
    """
    Classe base para views que precisam de:
    - Transição suave entre telas internas
    - Header padrão
    - Botão de finalizar sessão
    """

    # Cor de fundo padrão - pode ser sobrescrita
    BG_COLOR = "#3B6A7D"

    def __init__(self, master, end_session_callback=None, *args, **kwargs):
        super().__init__(master, fg_color=self.BG_COLOR, *args, **kwargs)
        self.end_session_callback = end_session_callback
        self._master = master

        # Create overlay to hide construction
        self._init_overlay = customtkinter.CTkFrame(master, fg_color=self.BG_COLOR)
        self._init_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._init_overlay.lift()
        master.update_idletasks()

        self.pack(fill="both", expand=True)

        # Schedule overlay removal after complete initialization
        self.after(1, self._hide_init_overlay)

    def _hide_init_overlay(self):
        """Removes initialization overlay after screen is ready"""
        if self._init_overlay:
            self.update_idletasks()
            self._init_overlay.destroy()
            self._init_overlay = None

    def _transition_screen(self, create_frame_func):
        """
        Executes smooth transition between internal screens.
        Uses overlay to hide component rendering.

        Args:
            create_frame_func: Function that creates the new frame/content
        """
        # Create overlay to hide rendering
        overlay = customtkinter.CTkFrame(self, fg_color=self.BG_COLOR)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.update()

        # Destroy old widgets (except overlay)
        for widget in self.winfo_children():
            if widget != overlay:
                widget.destroy()

        # Create new content
        create_frame_func()

        # Force complete rendering
        self.update_idletasks()

        # Remove overlay
        overlay.destroy()

    def create_header_widget(self, title: str):
        """Creates standard header with title"""
        Header(self, title)

    def create_finish_button(self):
        """Creates standard end session button"""
        FinalizarSessaoButton(self, self.end_session)

    def end_session(self):
        """Standard session finalization logic with confirmation"""
        if ModernConfirmDialog.ask(
            self,
            "Finalizar Sessão",
            "Tem certeza que deseja sair do sistema?",
            icon="question",
            confirm_text="Sair",
            cancel_text="Cancelar",
        ):
            ToastNotification.show(self, "Sessão finalizada com sucesso", "success")
            if self.end_session_callback:
                self.after(1000, self._execute_logout)

    def _execute_logout(self):
        """Executes logout after notification delay"""
        self.pack_forget()
        if self.end_session_callback:
            self.end_session_callback()
