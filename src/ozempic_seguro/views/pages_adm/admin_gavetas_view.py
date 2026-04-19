import customtkinter

from ..components import (
    GavetaButton,
    GavetaButtonGrid,
    Header,
    ToastNotification,
    VoltarButton,
)


class AdminGavetasFrame(customtkinter.CTkFrame):
    BG_COLOR = "#3B6A7D"

    def __init__(self, master, back_callback=None, *args, **kwargs):
        super().__init__(master, fg_color=self.BG_COLOR, *args, **kwargs)
        self.back_callback = back_callback

        # Criar overlay para esconder construção
        self._overlay = customtkinter.CTkFrame(master, fg_color=self.BG_COLOR)
        self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._overlay.lift()
        master.update_idletasks()

        self.pack(fill="both", expand=True)
        self.create_header()
        self.create_button_grid()
        self.create_back_button()

        # Remover overlay após tudo estar pronto
        self.update_idletasks()
        self._overlay.destroy()

    def create_header(self):
        """Creates the screen header"""
        Header(self, "Administrador - Gerenciar Gavetas")

    def create_button_grid(self):
        """Creates the drawer buttons grid"""
        button_data = []
        # Criar 15 gavetas para testar a paginação
        for i in range(1, 16):
            gaveta_id = f"100{i}"
            button_data.append(
                {
                    "text": gaveta_id,
                    "command": lambda x=gaveta_id: self.show_drawer_history(x),
                    "name": "gaveta_black.png",
                    "user_type": "administrador",  # Permite abrir e fechar
                }
            )

        self.button_grid = GavetaButtonGrid(self, button_data)

    def show_drawer_history(self, gaveta_id):
        """Shows the history of a specific drawer"""
        ToastNotification.show(self, f"Carregando histórico da gaveta {gaveta_id}...", "info")
        temp_button = GavetaButton(
            self,
            text=gaveta_id,
            command=None,
            name="gaveta_black.png",
            user_type="administrador",
        )
        temp_button.show_history()

    def create_back_button(self):
        """Creates back button using VoltarButton component"""
        self.back_btn = VoltarButton(self, command=self.back_to_panel)

    def back_to_panel(self):
        """Returns to the administrator main panel"""
        if self.back_callback:
            self.pack_forget()
            self.back_callback()
