import customtkinter
import tkinter as tk
from ..components import (
    Header,
    VoltarButton,
    TecladoVirtual,
    ModernConfirmDialog,
    ToastNotification,
)
from ...services.user_registration_service import get_user_registration_service


class CadastroUsuarioFrame(customtkinter.CTkFrame):
    BG_COLOR = "#3B6A7D"

    def __init__(self, master, back_callback=None, *args, **kwargs):
        self.back_callback = back_callback
        self.registration_service = get_user_registration_service()
        super().__init__(master, fg_color=self.BG_COLOR, *args, **kwargs)

        # Create overlay to hide construction
        self._overlay = customtkinter.CTkFrame(master, fg_color=self.BG_COLOR)
        self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._overlay.lift()
        master.update_idletasks()

        self.pack(fill="both", expand=True)

        # Input validation configuration
        self.vcmd_name = (self.register(self.validate_name_input), "%P")
        self.vcmd_numeric = (self.register(self.validate_numeric_input), "%P")

        # Initialize timers
        self.error_timer = None
        self.message_timer = None

        self.create_header()
        self.create_registration_interface()
        self.create_back_button()
        self.create_virtual_keyboard()

        # Variable to control which field is active
        self.current_input_field = None

        # Remove overlay after everything is ready
        self.update_idletasks()
        self._overlay.destroy()

    def validate_numeric_input(self, value):
        """Validates if input contains only numbers and has at most 8 characters"""
        if len(value) > 8:  # 8 character limit
            return False
        if value == "":  # Allow empty field for deletion
            return True
        return value.isdigit()

    def validate_name_input(self, value):
        """Validates if name has at most 26 characters"""
        return len(value) <= 26

    def create_header(self):
        Header(self, "Cadastro de Usuário")

    def create_registration_interface(self):
        # Main frame containing the form
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(side="left", fill="both", expand=True, padx=20, pady=(10, 20))

        # Frame for registration form
        registration_frame = customtkinter.CTkFrame(main_frame, fg_color="#3B6A7D")
        registration_frame.pack(pady=(0, 20), padx=20, fill="x")

        # Function to set current input field when clicked
        def set_current_field(entry):
            self.current_input_field = entry
            if hasattr(self, "teclado"):
                self.teclado.set_entry(entry)

        # Campo de Nome (aceita letras)
        customtkinter.CTkLabel(
            registration_frame,
            text="Nome (máx. 26 caracteres)",
            font=("Arial", 16, "bold"),
            text_color="white",
        ).pack(anchor="w", pady=(10, 5), padx=20)

        self.name_entry = customtkinter.CTkEntry(
            registration_frame,
            width=300,
            height=40,
            font=("Arial", 14),
            validate="key",
            validatecommand=self.vcmd_name,
        )
        self.name_entry.pack(pady=(0, 10), padx=20)
        self.name_entry.bind("<Button-1>", lambda e: set_current_field(self.name_entry))

        # Campo de Usuário (aceita apenas números)
        customtkinter.CTkLabel(
            registration_frame,
            text="Usuário (máx. 8 dígitos)",
            font=("Arial", 16, "bold"),
            text_color="white",
        ).pack(anchor="w", pady=(10, 5), padx=20)

        self.username_entry = customtkinter.CTkEntry(
            registration_frame,
            width=300,
            height=40,
            font=("Arial", 14),
            validate="key",
            validatecommand=self.vcmd_numeric,
        )
        self.username_entry.pack(pady=(0, 10), padx=20)
        self.username_entry.bind("<Button-1>", lambda e: set_current_field(self.username_entry))

        # Campo de senha com mensagem de erro abaixo
        customtkinter.CTkLabel(
            registration_frame,
            text="Senha (máx. 8 dígitos)",
            font=("Arial", 16, "bold"),
            text_color="white",
        ).pack(anchor="w", pady=(10, 5), padx=20)

        self.password_entry = customtkinter.CTkEntry(
            registration_frame,
            width=300,
            height=40,
            font=("Arial", 14),
            show="•",  # Mostra bolinhas no lugar dos caracteres
            validate="key",
            validatecommand=self.vcmd_numeric,
        )
        self.password_entry.pack(pady=(0, 5), padx=20)
        self.password_entry.bind("<Button-1>", lambda e: set_current_field(self.password_entry))

        # Label for error message (initially empty)
        self.lbl_password_error = customtkinter.CTkLabel(
            registration_frame,
            text="",
            text_color="red",
            font=("Arial", 12, "bold"),
            fg_color="transparent",
        )
        self.lbl_password_error.pack(
            anchor="w", padx=20, pady=(0, 5)
        )  # Reduzido o padding vertical inferior

        # User type
        user_type_frame = customtkinter.CTkFrame(registration_frame, fg_color="transparent")
        user_type_frame.pack(
            anchor="w", fill="x", padx=20, pady=(0, 10)
        )  # Ajustado o padding vertical

        customtkinter.CTkLabel(
            user_type_frame,
            text="Tipo de Usuário",
            font=("Arial", 16, "bold"),
            text_color="white",
        ).pack(anchor="w", pady=(0, 5), padx=20)

        self.type_var = customtkinter.StringVar(value="vendedor")
        user_types = [
            ("Vendedor", "vendedor"),
            ("Repositor", "repositor"),
            ("Administrador", "administrador"),
            ("Técnico", "tecnico"),
        ]

        for label, value in user_types:
            customtkinter.CTkRadioButton(
                user_type_frame,
                text=label,
                variable=self.type_var,
                value=value,
                text_color="white",
            ).pack(anchor="w", padx=20, pady=2)

        # Status message (for success/info messages)
        self.message_label = customtkinter.CTkLabel(
            registration_frame, text="", text_color="yellow", font=("Arial", 12)
        )
        self.message_label.pack(pady=10, padx=20)

        # Set first field as active by default
        if hasattr(self, "name_entry"):
            set_current_field(self.name_entry)

    def create_virtual_keyboard(self):
        # Frame for keyboard
        keyboard_frame = customtkinter.CTkFrame(
            self, fg_color="transparent", width=600, height=750
        )  # Fixed width and height
        keyboard_frame.pack(side="right", fill="y", padx=20, pady=20)
        keyboard_frame.pack_propagate(False)  # Prevents frame from auto-resizing

        # Keyboard title
        customtkinter.CTkLabel(keyboard_frame, text="").pack(pady=(0, 10))

        # Creates virtual keyboard inside frame with scroll if needed
        container = customtkinter.CTkFrame(keyboard_frame, fg_color="transparent")
        container.pack(fill="both", expand=True)

        self.teclado = TecladoVirtual(
            container, current_entry=self.current_input_field, save_command=self.save_user
        )
        self.teclado.pack(fill="both", expand=True, pady=10)

    def create_back_button(self):
        # Creates frame for back button in bottom left corner
        back_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        back_frame.pack(side="bottom", anchor="sw", padx=20, pady=20)
        VoltarButton(back_frame, self.back_callback)

    def save_user(self):
        """Saves user using UserRegistrationService"""
        name = self.name_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        user_type = self.type_var.get()

        # Clear previous error messages
        self.lbl_password_error.configure(text="")

        # Confirm before saving
        if not ModernConfirmDialog.ask(
            self,
            "Confirmar Cadastro",
            f"Deseja cadastrar o usuário '{name}' do tipo '{user_type}'?",
            icon="question",
            confirm_text="Cadastrar",
            cancel_text="Cancelar",
        ):
            return

        # Use service to register (validation + creation)
        result = self.registration_service.register(name, username, password, user_type)

        if result.success:
            ToastNotification.show(self, result.message, "success")
            self.clear_fields()
        else:
            # Show first error
            error_msg = result.errors[0] if result.errors else result.message
            self.show_message(error_msg, "erro")

    def show_message(self, message, msg_type):
        colors = {"erro": "red", "sucesso": "green", "info": "yellow"}

        # Cancel previous timer if exists
        if msg_type == "erro":
            if self.error_timer is not None:
                self.after_cancel(self.error_timer)
        else:
            if self.message_timer is not None:
                self.after_cancel(self.message_timer)

        if msg_type == "erro":
            # Display error message in appropriate label
            self.lbl_password_error.configure(text=message, text_color=colors[msg_type])
            # Set a new timer
            self.error_timer = self.after(5000, self.clear_error_message)
        else:
            # For other message types (success, info), use normal label
            self.message_label.configure(text=message, text_color=colors.get(msg_type, "white"))
            self.message_timer = self.after(5000, self.clear_normal_message)

    def clear_error_message(self):
        self.lbl_password_error.configure(text="")
        self.error_timer = None

    def clear_normal_message(self):
        self.message_label.configure(text="")
        self.message_timer = None

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.type_var.set("vendedor")
        # Return focus to first field
        if hasattr(self, "name_entry"):
            self.name_entry.focus_set()
            self.current_input_field = self.name_entry
            if hasattr(self, "teclado"):
                self.teclado.set_entry(self.name_entry)
