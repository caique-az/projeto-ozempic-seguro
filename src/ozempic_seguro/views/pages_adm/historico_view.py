import customtkinter

from ...core.logger import logger
from ...services.gaveta_service import GavetaService
from ..components import Header, VoltarButton


class HistoricoView(customtkinter.CTkFrame):
    BG_COLOR = "#3B6A7D"

    def __init__(self, master, back_callback=None, user_type="administrador", **kwargs):
        super().__init__(master, fg_color=self.BG_COLOR, **kwargs)
        self.back_callback = back_callback
        self.user_type = user_type
        self._gaveta_service = GavetaService.get_instance()
        self.current_page = 1
        self.items_per_page = 20

        # Criar overlay para esconder construção
        self._overlay = customtkinter.CTkFrame(master, fg_color=self.BG_COLOR)
        self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._overlay.lift()
        master.update_idletasks()

        self.pack(fill="both", expand=True)
        self.create_interface()

        # Remover overlay após tudo estar pronto
        self.update_idletasks()
        self._overlay.destroy()

    def create_interface(self):
        # Cabeçalho
        self.header = Header(self, "Histórico de Ações nas Gavetas")

        # Frame para o conteúdo
        self.content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=(20, 100))

        # Frame branco para a tabela
        self.table_frame = customtkinter.CTkFrame(
            self.content_frame, fg_color="white", corner_radius=15
        )
        self.table_frame.pack(fill="both", expand=True, pady=10)

        # Cabeçalhos da tabela
        self.create_table_headers()

        # Frame para os controles de paginação
        self.pagination_frame = customtkinter.CTkFrame(self.content_frame, fg_color="transparent")
        self.pagination_frame.pack(fill="x", pady=(10, 0))

        # Botões de navegação
        self.btn_previous = customtkinter.CTkButton(
            self.pagination_frame,
            text="Anterior",
            command=self.previous_page,
            width=100,
            state="disabled",
        )
        self.btn_previous.pack(side="left", padx=5)

        self.lbl_page = customtkinter.CTkLabel(self.pagination_frame, text="Página 1")
        self.lbl_page.pack(side="left", padx=5)

        self.btn_next = customtkinter.CTkButton(
            self.pagination_frame, text="Próximo", command=self.next_page, width=100
        )
        self.btn_next.pack(side="left", padx=5)

        # Linhas da tabela
        self.load_data()

        # Botão voltar (adicionado por último para ficar por cima)
        self.back_btn = VoltarButton(self, command=self.go_back)

    def create_table_headers(self):
        # Frame para os cabeçalhos
        header_frame = customtkinter.CTkFrame(
            self.table_frame, fg_color="#f0f0f0", corner_radius=10
        )
        header_frame.pack(fill="x", padx=10, pady=10)

        # Cabeçalhos
        headers = ["Data/Hora", "Gaveta", "Ação", "Usuário"]
        widths = [0.3, 0.2, 0.25, 0.25]  # Proporções de largura

        for i, (text, width) in enumerate(zip(headers, widths, strict=False)):
            # Cria um frame para cada cabeçalho para melhor controle
            header_cell = customtkinter.CTkFrame(header_frame, fg_color="transparent")
            header_cell.pack(side="left", fill="x", expand=True)

            # Configura o padding apenas para o cabeçalho "Gaveta"
            padx_left = 65 if text == "Gaveta" else 0

            lbl = customtkinter.CTkLabel(
                header_cell, text=text, font=("Arial", 14, "bold"), text_color="black", anchor="w"
            )
            lbl.pack(side="left", padx=(padx_left, 0), pady=5)

            # Define o peso da coluna
            header_frame.columnconfigure(i, weight=int(width * 100))

    def load_data(self):
        # Clear current table
        for widget in self.table_frame.winfo_children():
            if widget != self.table_frame.winfo_children()[0]:  # Mantém o cabeçalho
                widget.destroy()

        # Frame rolável para os itens
        scrollable_frame = customtkinter.CTkScrollableFrame(self.table_frame, fg_color="white")
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        try:
            # Calculate offset based on current page
            offset = (self.current_page - 1) * self.items_per_page

            # Get paginated data using GavetaService
            history_raw = self._gaveta_service.get_all_history_paginated(
                offset, self.items_per_page
            )
            total = self._gaveta_service.count_all_history()

            # Update pagination controls
            self.update_pagination_controls(total)

            # Add items
            for idx, h in enumerate(history_raw):
                self.add_row(
                    scrollable_frame,
                    h[0],  # data_hora
                    h[1],  # gaveta_id
                    h[2],  # acao
                    h[3],  # usuario
                    idx % 2 == 0,  # Alternar cor de fundo
                )
        except Exception as e:
            logger.error(f"Error loading history: {e}")

    def update_pagination_controls(self, total_items):
        # Calculate total pages
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        total_pages = max(1, total_pages)  # Ensure at least 1 page

        # Update page text
        self.lbl_page.configure(text=f"Página {self.current_page} de {total_pages}")

        # Show or hide pagination controls based on page count
        if total_pages <= 1:
            # Hide pagination controls if only one page
            self.btn_previous.pack_forget()
            self.lbl_page.pack_forget()
            self.btn_next.pack_forget()
        else:
            # Show controls and update button states
            self.btn_previous.pack(side="left", padx=5)
            self.lbl_page.pack(side="left", padx=5)
            self.btn_next.pack(side="left", padx=5)

            # Update button states
            self.btn_previous.configure(state="normal" if self.current_page > 1 else "disabled")
            self.btn_next.configure(
                state="normal" if self.current_page < total_pages else "disabled"
            )

    def next_page(self):
        self.current_page += 1
        self.load_data()

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def add_row(self, parent, data_hora, gaveta_id, acao, usuario, par):
        # Frame para uma linha da tabela
        row_frame = customtkinter.CTkFrame(
            parent, fg_color="#f9f9f9" if par else "white", corner_radius=8
        )
        row_frame.pack(fill="x", padx=5, pady=2)

        # Dados da linha
        row_data = [data_hora, gaveta_id, acao, usuario]

        for text in row_data:
            lbl = customtkinter.CTkLabel(
                row_frame, text=str(text), font=("Arial", 12), text_color="black", anchor="w"
            )
            lbl.pack(side="left", padx=10, pady=8, fill="x", expand=True)

    def go_back(self):
        """Returns to previous screen"""
        if self.back_callback:
            self.back_callback()
