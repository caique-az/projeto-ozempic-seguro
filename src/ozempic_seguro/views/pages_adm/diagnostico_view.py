"""
Tela de Diagnóstico - Mostruário de gavetas conectadas.
Mostra status de até 8 gavetas (conectadas/vazias, abertas/fechadas, funcionamento).
"""

import customtkinter

from ..components import Header, VoltarButton


class DiagnosticoFrame(customtkinter.CTkFrame):
    BG_COLOR = "#3B6A7D"

    def __init__(self, master, back_callback=None, *args, **kwargs):
        self.back_callback = back_callback
        super().__init__(master, fg_color=self.BG_COLOR, *args, **kwargs)

        # Criar overlay para esconder construção
        self._overlay = customtkinter.CTkFrame(master, fg_color=self.BG_COLOR)
        self._overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._overlay.lift()
        master.update_idletasks()

        self.pack(fill="both", expand=True)

        # Criar header primeiro
        self.header = Header(self, "Diagnóstico de Gavetas")

        # Frame principal para o conteúdo abaixo do header
        self.main_content = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=40, pady=(20, 100))

        # Dados simulados das gavetas (para demonstração)
        self.simulated_drawers = [
            {"id": 1, "connected": True, "open": True, "working": True},
            {"id": 2, "connected": True, "open": True, "working": False},
            {"id": 3, "connected": True, "open": False, "working": True},
            {"id": 4, "connected": True, "open": False, "working": True},
            {"id": 5, "connected": False, "open": False, "working": True},
            {"id": 6, "connected": False, "open": False, "working": True},
            {"id": 7, "connected": False, "open": False, "working": True},
            {"id": 8, "connected": False, "open": False, "working": True},
        ]

        # Criar elementos restantes
        self.create_content()
        self.create_back_button()

        # Remover overlay após tudo estar pronto
        self.update_idletasks()
        self._overlay.destroy()

    def create_content(self):
        # Frame para o conteúdo
        content_frame = customtkinter.CTkFrame(
            self.main_content, fg_color="white", corner_radius=15
        )
        content_frame.pack(fill="both", expand=True)

        # Título
        lbl_titulo = customtkinter.CTkLabel(
            content_frame,
            text="Status das Gavetas",
            font=("Arial", 20, "bold"),
            text_color="#333333",
        )
        lbl_titulo.pack(pady=(20, 10))

        # Informação do sistema
        info_frame = customtkinter.CTkFrame(content_frame, fg_color="#f0f0f0", corner_radius=10)
        info_frame.pack(pady=10, padx=20, fill="x")

        lbl_info = customtkinter.CTkLabel(
            info_frame,
            text="💻 Mini PC - Capacidade: 8 gavetas | Conectadas: 4 | Disponíveis: 4",
            font=("Arial", 12),
            text_color="#555555",
        )
        lbl_info.pack(pady=10)

        # Grid de gavetas (2x4)
        self.create_drawer_grid(content_frame)

        # Legenda
        self.create_legend(content_frame)

    def create_drawer_grid(self, parent):
        """Creates the 2x4 drawer grid"""
        grid_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        grid_frame.pack(pady=20, padx=20, expand=True)

        # Configurar grid 2x4
        for i in range(2):
            grid_frame.rowconfigure(i, weight=1)
        for j in range(4):
            grid_frame.columnconfigure(j, weight=1)

        # Criar as 8 gavetas
        for i in range(8):
            row = i // 4
            col = i % 4
            drawer_data = self.simulated_drawers[i]

            self.create_drawer_widget(grid_frame, drawer_data, row, col)

    def create_drawer_widget(self, parent, drawer_data, row, col):
        """Creates an individual drawer widget"""
        # Frame da gaveta
        if drawer_data["connected"]:
            # Gaveta conectada - cor baseada no status
            if not drawer_data["working"]:
                bg_color = "#FFEBEE"  # Vermelho claro para mau funcionamento
                border_color = "#F44336"
            elif drawer_data["open"]:
                bg_color = "#FFF3E0"  # Laranja claro para aberta
                border_color = "#FF9800"
            else:
                bg_color = "#E8F5E9"  # Verde claro para fechada e funcionando
                border_color = "#4CAF50"
        else:
            # Espaço vazio
            bg_color = "#F5F5F5"
            border_color = "#CCCCCC"

        # Frame da gaveta com altura mínima
        drawer_frame = customtkinter.CTkFrame(
            parent,
            fg_color=bg_color,
            corner_radius=10,
            border_width=2,
            border_color=border_color,
            height=140,  # Altura mínima
        )
        drawer_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Conteúdo da gaveta
        if drawer_data["connected"]:
            # Número da gaveta
            lbl_numero = customtkinter.CTkLabel(
                drawer_frame,
                text=f"Gaveta {drawer_data['id']}",
                font=("Arial", 14, "bold"),
                text_color="#333333",
            )
            lbl_numero.pack(pady=(20, 8))

            # Status
            if drawer_data["open"]:
                status_text = "🔓 ABERTA"
                status_color = "#FF6B35"
            else:
                status_text = "🔒 FECHADA"
                status_color = "#2E7D32"

            lbl_status = customtkinter.CTkLabel(
                drawer_frame, text=status_text, font=("Arial", 12, "bold"), text_color=status_color
            )
            lbl_status.pack(pady=(0, 8))

            # Funcionamento
            if not drawer_data["working"]:
                lbl_erro = customtkinter.CTkLabel(
                    drawer_frame,
                    text="⚠️ DEFEITO",
                    font=("Arial", 10, "bold"),
                    text_color="#D32F2F",
                )
                lbl_erro.pack(pady=(0, 20))
            else:
                lbl_ok = customtkinter.CTkLabel(
                    drawer_frame, text="✅ Funcionando", font=("Arial", 10), text_color="#388E3C"
                )
                lbl_ok.pack(pady=(0, 20))
        else:
            # Espaço vazio
            lbl_vazio = customtkinter.CTkLabel(
                drawer_frame, text="➕", font=("Arial", 24), text_color="#999999"
            )
            lbl_vazio.pack(pady=(25, 8))

            lbl_texto = customtkinter.CTkLabel(
                drawer_frame, text="Espaço Disponível", font=("Arial", 11), text_color="#666666"
            )
            lbl_texto.pack(pady=(0, 5))

            lbl_info = customtkinter.CTkLabel(
                drawer_frame, text="Conecte uma gaveta", font=("Arial", 9), text_color="#999999"
            )
            lbl_info.pack(pady=(0, 20))

    def create_legend(self, parent):
        """Creates the status legend"""
        legenda_frame = customtkinter.CTkFrame(parent, fg_color="#f9f9f9", corner_radius=10)
        legenda_frame.pack(pady=(10, 20), padx=20, fill="x")

        lbl_titulo = customtkinter.CTkLabel(
            legenda_frame, text="Legenda:", font=("Arial", 12, "bold"), text_color="#333333"
        )
        lbl_titulo.pack(side="left", padx=(20, 10), pady=10)

        # Items da legenda
        legendas = [
            ("🟢", "Fechada/Funcionando"),
            ("🟠", "Aberta/Funcionando"),
            ("🔴", "Mau Funcionamento"),
            ("⬜", "Espaço Disponível"),
        ]

        for cor, texto in legendas:
            item_frame = customtkinter.CTkFrame(legenda_frame, fg_color="transparent")
            item_frame.pack(side="left", padx=15, pady=10)

            lbl_item = customtkinter.CTkLabel(
                item_frame, text=f"{cor} {texto}", font=("Arial", 11), text_color="#555555"
            )
            lbl_item.pack()

    def create_back_button(self):
        VoltarButton(self, self.back_callback)
