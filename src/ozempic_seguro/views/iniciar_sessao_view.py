from tkinter import messagebox

import customtkinter

from .components import Header, VoltarButton


class IniciarSessaoFrame(customtkinter.CTkFrame):
    def __init__(self, master, show_login_callback, back_callback=None, *args, **kwargs):
        super().__init__(master, fg_color="#346172", *args, **kwargs)
        self.show_login_callback = show_login_callback
        self.back_callback = back_callback
        # Não fazer pack aqui - NavigationController gerencia
        self.create_header()
        self.create_login_button()
        self.create_back_button()

    def create_header(self):
        Header(self, "Iniciar Sessão")

    def create_login_button(self):
        main_frame = customtkinter.CTkFrame(self, fg_color="#346172")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        btn_login = customtkinter.CTkButton(
            main_frame,
            text="Iniciar Sessão",
            font=("Arial", 16, "bold"),
            width=300,
            height=60,
            corner_radius=15,
            fg_color="white",
            text_color="black",
            hover_color="#e0e0e0",
            command=self.show_login_callback,
        )
        btn_login.pack(pady=20)

    def create_back_button(self):
        VoltarButton(self, self.back_callback)

    def employee_registration(self):
        messagebox.showinfo("Cadastro", "Você clicou em Cadastro de Funcionário")
