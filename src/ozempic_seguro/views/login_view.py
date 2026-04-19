import tkinter as tk
from tkinter import messagebox

import customtkinter

from ..config import UIConfig
from ..services.auth_service import UserPanel, get_auth_service
from .components import Header, ModernButton, VoltarButton
from .pages_adm.painel_administrador_view import PainelAdministradorFrame
from .repositor_view import RepositorFrame
from .tecnico_view import TecnicoFrame
from .vendedor_view import VendedorFrame


class LoginFrame(customtkinter.CTkFrame):
    def __init__(self, master, show_iniciar_callback, *args, **kwargs):
        super().__init__(master, fg_color=UIConfig.LOGIN_FRAME_COLOR, *args, **kwargs)
        self.show_iniciar_callback = show_iniciar_callback
        self.auth_service = get_auth_service()
        self.timer_job = None
        # Não fazer pack aqui - NavigationController gerencia
        self.create_header()
        self.create_login_interface()
        self.create_numeric_keyboard()
        self.create_back_button()

    def create_header(self):
        Header(self, "Login")

    def create_login_interface(self):
        frame_login = customtkinter.CTkFrame(self, fg_color=UIConfig.LOGIN_FRAME_COLOR)
        frame_login.place(x=UIConfig.LOGIN_FRAME_X, y=UIConfig.LOGIN_FRAME_Y)

        # Campo de usuário
        customtkinter.CTkLabel(
            frame_login, text="Usuário", font=("Arial", 16, "bold"), text_color="white"
        ).pack(anchor="w", pady=(0, 5))
        self.username_entry = customtkinter.CTkEntry(
            frame_login, width=UIConfig.LOGIN_ENTRY_WIDTH, height=UIConfig.LOGIN_ENTRY_HEIGHT
        )
        self.username_entry.pack(pady=UIConfig.LOGIN_ENTRY_PADY)
        self.username_entry.bind("<Button-1>", lambda e: self.set_active_field(self.username_entry))

        # Campo de senha
        customtkinter.CTkLabel(
            frame_login, text="Senha", font=("Arial", 16, "bold"), text_color="white"
        ).pack(anchor="w", pady=(20, 5))
        self.password_entry = customtkinter.CTkEntry(frame_login, width=300, height=40, show="*")
        self.password_entry.pack(pady=10)
        self.password_entry.bind("<Button-1>", lambda e: self.set_active_field(self.password_entry))

        # Label de status/avisos
        self.status_label = customtkinter.CTkLabel(
            frame_login,
            text="Digite suas credenciais para acessar o sistema",
            font=("Arial", 12),
            text_color="#90EE90",
            wraplength=280,
        )
        self.status_label.pack(pady=(10, 0))

        # Campo ativo por padrão
        self.active_field = self.username_entry

        # Bind para atualizar status quando usuário digita
        self.username_entry.bind("<KeyRelease>", self.update_login_status)

        # Define o foco no campo de usuário
        self.after(100, lambda: self.username_entry.focus_set())

    def create_back_button(self):
        VoltarButton(self, self.show_iniciar_callback)

    def create_numeric_keyboard(self):
        keyboard_frame = customtkinter.CTkFrame(self, fg_color=UIConfig.WHITE, corner_radius=20)
        keyboard_frame.place(x=UIConfig.LOGIN_KEYBOARD_X, y=UIConfig.LOGIN_KEYBOARD_Y)
        buttons = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["", "0", ""]]

        # Create numeric buttons
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                if text:
                    btn = ModernButton(
                        keyboard_frame,
                        text=text,
                        command=lambda t=text: self.key_press(t),
                        style="secondary",
                        width=90,
                        height=50,
                        font=("Arial", 16, "bold"),
                    )
                    btn.grid(row=i, column=j, padx=8, pady=8)

        # Action buttons at the bottom
        action_frame = customtkinter.CTkFrame(keyboard_frame, fg_color="transparent")
        action_frame.grid(row=4, column=0, columnspan=3, pady=15)

        ModernButton(
            action_frame,
            text="🗑️ Apagar",
            command=lambda: self.key_press("Apagar"),
            style="warning",
            width=120,
            height=45,
        ).pack(side="left", padx=5)

        ModernButton(
            action_frame,
            text="❌ Cancelar",
            command=lambda: self.key_press("Cancelar"),
            style="danger",
            width=120,
            height=45,
        ).pack(side="left", padx=5)

        ModernButton(
            action_frame,
            text="✅ Confirmar",
            command=lambda: self.key_press("Confirmar"),
            style="success",
            width=120,
            height=45,
        ).pack(side="left", padx=5)

    def verify_login(self):
        """Verifica credenciais usando AuthService"""
        usuario = self.username_entry.get().strip()
        senha = self.password_entry.get()

        # Usa AuthService para toda a lógica de login
        result = self.auth_service.login(usuario, senha)

        if result.success:
            # Sucesso - abre painel apropriado
            self._open_panel(result.panel)
        else:
            # Falha - mostra mensagem de erro
            if result.is_locked:
                messagebox.showerror("Conta Bloqueada", result.error_message)
                self.start_lockout_timer(usuario)
            else:
                messagebox.showerror("Login Inválido", result.error_message)

            # Atualiza status visual
            self.update_login_status()

    def _open_panel(self, panel: UserPanel):
        """Abre o painel apropriado baseado no tipo de usuário"""
        panel_handlers = {
            UserPanel.ADMIN: self.open_admin_panel,
            UserPanel.REPOSITOR: self.open_stocker_panel,
            UserPanel.VENDEDOR: self.open_seller_panel,
            UserPanel.TECNICO: self.open_technician_panel,
        }

        handler = panel_handlers.get(panel)
        if handler:
            handler()
        else:
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")

    def open_technician_panel(self):
        """Abre o painel do técnico"""
        self.pack_forget()
        TecnicoFrame(self.master, end_session_callback=self.show_iniciar_callback)

    def open_seller_panel(self):
        self.pack_forget()
        VendedorFrame(self.master, end_session_callback=self.show_iniciar_callback)

    def open_stocker_panel(self):
        self.pack_forget()
        RepositorFrame(self.master, end_session_callback=self.show_iniciar_callback)

    def open_admin_panel(self):
        self.pack_forget()
        # Get the current user from AuthService
        logged_in_user = self.auth_service.get_current_user()
        PainelAdministradorFrame(
            self.master,
            end_session_callback=self.show_iniciar_callback,
            logged_in_user=logged_in_user,
        )

    def set_active_field(self, field):
        """Sets which field is active to receive keyboard input"""
        self.active_field = field

    def key_press(self, valor):
        if valor == "Apagar":
            if self.active_field == self.username_entry:
                self.username_entry.delete(len(self.username_entry.get()) - 1, tk.END)
            else:
                self.password_entry.delete(len(self.password_entry.get()) - 1, tk.END)
        elif valor == "Cancelar":
            if self.active_field == self.username_entry:
                self.username_entry.delete(0, tk.END)
            else:
                self.password_entry.delete(0, tk.END)
        elif valor == "Confirmar":
            self.verify_login()
        else:
            # Incrementa entrada no campo ativo
            if self.active_field == self.username_entry:
                self.username_entry.insert(tk.END, valor)
            else:
                self.password_entry.insert(tk.END, valor)

    def update_login_status(self, event=None):
        """Atualiza o status de login baseado no usuário digitado"""
        usuario = self.username_entry.get().strip()

        if not usuario:
            self.status_label.configure(
                text="Digite suas credenciais para acessar o sistema", text_color="#90EE90"
            )
            return

        status = self.auth_service.get_login_status(usuario)

        if status["locked"]:
            self.status_label.configure(text=status["message"], text_color="#FF6B6B")
            self.start_lockout_timer(usuario)
        elif status["remaining_attempts"] < 3:
            self.status_label.configure(text=status["message"], text_color="#FFA500")
        else:
            self.status_label.configure(text=status["message"], text_color="#90EE90")

    def start_lockout_timer(self, usuario):
        """Inicia timer visual para conta bloqueada"""
        if self.timer_job:
            self.after_cancel(self.timer_job)

        self.update_lockout_timer(usuario)

    def update_lockout_timer(self, usuario):
        """Atualiza o timer de bloqueio em tempo real"""
        remaining_seconds = self.auth_service.get_lockout_remaining_seconds(usuario)

        if remaining_seconds <= 0:
            # Bloqueio expirou
            self.status_label.configure(
                text="Bloqueio expirado. Você pode tentar fazer login novamente",
                text_color="#90EE90",
            )
            self.timer_job = None
            return

        # Formatar tempo restante
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60

        self.status_label.configure(
            text=f" Conta bloqueada - Restam {minutes}:{seconds:02d}", text_color="#FF6B6B"
        )

        # Agenda próxima atualização
        self.timer_job = self.after(1000, lambda: self.update_lockout_timer(usuario))
