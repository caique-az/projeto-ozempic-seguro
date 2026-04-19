"""
Base view for operational users (vendedor/repositor).

Extracts common code to reduce duplication.
"""

from tkinter import messagebox

import customtkinter

from .components import (
    FinalizarSessaoButton,
    GavetaButton,
    GavetaButtonGrid,
    Header,
    ModernConfirmDialog,
    ToastNotification,
)


class BaseUserFrame(customtkinter.CTkFrame):
    """
    Frame base para views de usuários operacionais.

    Subclasses devem definir:
        - TITULO: str - título exibido no header
        - TIPO_USUARIO: str - tipo de usuário para permissões
    """

    BG_COLOR = "#3B6A7D"
    TITLE: str = ""
    USER_TYPE: str = ""

    def __init__(self, master, end_session_callback=None, *args, **kwargs):
        super().__init__(master, fg_color=self.BG_COLOR, *args, **kwargs)
        self.end_session_callback = end_session_callback

        # Create overlay to hide construction
        self._overlay = customtkinter.CTkFrame(master, fg_color=self.BG_COLOR)
        self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._overlay.lift()
        master.update_idletasks()

        self.pack(fill="both", expand=True)
        self.create_header()
        self.create_button_grid()
        self.create_finish_button()

        # Remove overlay after everything is ready
        self.update_idletasks()
        self._overlay.destroy()

    def create_header(self):
        Header(self, self.TITLE)

    def create_button_grid(self):
        button_data = []
        # Create 15 drawers to test pagination
        for i in range(1, 16):
            gaveta_id = f"100{i}"
            button_data.append(
                {
                    "text": gaveta_id,
                    "command": lambda x=gaveta_id: self.show_drawer_history(x),
                    "name": "gaveta_black.png",
                    "user_type": self.USER_TYPE,
                }
            )

        self.button_grid = GavetaButtonGrid(self, button_data)

    def show_drawer_history(self, gaveta_id):
        """Shows the history of a specific drawer"""
        button = GavetaButton(
            self,
            text=gaveta_id,
            command=None,
            name="gaveta_black.png",
            user_type=self.USER_TYPE,
        )
        button.show_history()
        # Subclasses can override for additional behavior

    def create_finish_button(self):
        FinalizarSessaoButton(self, self.end_session)

    def end_session(self):
        # Use modern visual confirmation
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
                self.after(1000, lambda: self._execute_logout())
            else:
                messagebox.showinfo("Sessão", "Sessão finalizada!")

    def _execute_logout(self):
        """Executes logout after notification delay"""
        self.pack_forget()
        self.end_session_callback()
