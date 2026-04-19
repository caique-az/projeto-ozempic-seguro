from tkinter import messagebox

import customtkinter

from ...services.timer_control_service import get_timer_control_service
from ..components import Header, VoltarButton


class ParametroSistemasFrame(customtkinter.CTkFrame):
    BG_COLOR = "#3B6A7D"

    def __init__(self, master, back_callback=None, *args, **kwargs):
        self.back_callback = back_callback
        self.timer_service = get_timer_control_service()
        super().__init__(master, fg_color=self.BG_COLOR, *args, **kwargs)

        # Criar overlay para esconder construção
        self._overlay = customtkinter.CTkFrame(master, fg_color=self.BG_COLOR)
        self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._overlay.lift()
        master.update_idletasks()

        self.pack(fill="both", expand=True)

        # Criar header primeiro
        self.header = Header(self, "Parâmetro de Sistemas")

        # Frame principal para o conteúdo abaixo do header
        self.main_content = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=40, pady=(20, 100))

        # Criar elementos restantes
        self.create_timer_control()
        self.create_parameters_table()
        self.create_back_button()

        # Remover overlay após tudo estar pronto
        self.update_idletasks()
        self._overlay.destroy()

    def create_timer_control(self):
        """Creates control to enable/disable drawer opening timer function"""
        frame_controle = customtkinter.CTkFrame(
            self.main_content, fg_color="white", corner_radius=15, height=100
        )
        frame_controle.pack(fill="x", pady=(10, 20))
        frame_controle.pack_propagate(False)

        # Título
        lbl_titulo = customtkinter.CTkLabel(
            frame_controle,
            text="Controle de Timer de Abertura de Gavetas",
            font=("Arial", 14, "bold"),
            text_color="#333333",
        )
        lbl_titulo.pack(side="left", padx=20, pady=10, anchor="n")

        # Frame para o status e botão
        frame_status = customtkinter.CTkFrame(frame_controle, fg_color="transparent")
        frame_status.pack(side="right", padx=20, pady=10, fill="y")

        # Status atual
        self.lbl_status = customtkinter.CTkLabel(
            frame_status,
            text="Status: "
            + ("Ativado" if self.timer_service.is_timer_enabled() else "Desativado"),
            font=("Arial", 12),
            text_color="#333333",
        )
        self.lbl_status.pack(pady=(0, 5))

        # Botão de controle
        self.btn_timer_control = customtkinter.CTkButton(
            frame_status,
            text="",
            width=120,
            command=self.toggle_timer,
            fg_color="#4CAF50" if self.timer_service.is_timer_enabled() else "#F44336",
        )
        self.btn_timer_control.pack()

        # Atualiza o texto do botão
        self.update_button_state()

    def toggle_timer(self):
        """Toggles timer function state using TimerControlService"""
        success, msg, new_state = self.timer_service.toggle_timer()

        if success:
            state_text = "ativado" if new_state else "desativado"
            messagebox.showinfo(
                "Sucesso", f"Timer de abertura de gavetas {state_text} com sucesso!"
            )

            # Se estiver ativando e houver um bloqueio ativo, mostra o tempo restante
            if new_state and self.timer_service.is_blocked():
                segundos = self.timer_service.get_remaining_time()
                minutos = segundos // 60
                segundos_restantes = segundos % 60
                messagebox.showinfo(
                    "Informação",
                    f"O sistema está bloqueado por mais {minutos} minutos e {segundos_restantes} segundos.",
                )
        else:
            messagebox.showerror("Erro", msg)

        # Atualiza o estado do botão
        self.update_button_state()

    def update_button_state(self):
        """Updates button text and color according to timer state"""
        if self.timer_service.is_timer_enabled():
            self.btn_timer_control.configure(
                text="Desativar Timer", fg_color="#4CAF50", hover_color="#388E3C"
            )
            self.lbl_status.configure(text="Status: Ativado", text_color="#2E7D32")
        else:
            self.btn_timer_control.configure(
                text="Ativar Timer", fg_color="#F44336", hover_color="#D32F2F"
            )
            self.lbl_status.configure(text="Status: Desativado", text_color="#C62828")

    def create_parameters_table(self):
        # Frame para a tabela
        self.table_frame = customtkinter.CTkFrame(
            self.main_content,
            fg_color="white",
            corner_radius=15,
        )
        self.table_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Configurar grid da tabela
        self.table_frame.columnconfigure(0, weight=1)

        # Cabeçalhos da tabela
        self.create_table_headers()

        # Frame rolável para os itens
        scrollable_frame = customtkinter.CTkScrollableFrame(self.table_frame, fg_color="white")
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Mensagem de tabela vazia
        lbl_vazio = customtkinter.CTkLabel(
            scrollable_frame,
            text="Nenhum parâmetro encontrado.",
            text_color="#666666",
            font=("Arial", 12),
        )
        lbl_vazio.pack(pady=20)

    def create_table_headers(self):
        # Frame para os cabeçalhos
        header_frame = customtkinter.CTkFrame(
            self.table_frame, fg_color="#f0f0f0", corner_radius=10
        )
        header_frame.pack(fill="x", padx=10, pady=10)

        # Cabeçalhos
        headers = ["Parâmetro", "Valor", "Descrição", "Atualizado em"]

        for text in headers:
            # Cria um frame para cada cabeçalho para melhor controle
            header_cell = customtkinter.CTkFrame(header_frame, fg_color="transparent")
            header_cell.pack(side="left", fill="x", expand=True)

            lbl = customtkinter.CTkLabel(
                header_cell, text=text, font=("Arial", 14, "bold"), text_color="black", anchor="w"
            )
            lbl.pack(side="left", padx=10, pady=5)

    def create_back_button(self):
        VoltarButton(self, self.back_callback)
