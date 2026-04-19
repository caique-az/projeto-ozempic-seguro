import customtkinter

from ...core.base_views import AdminView
from ...core.logger import logger
from ...services.user_management_service import get_user_management_service
from ..components import Header, VoltarButton


class UsuariosView(AdminView):
    def _setup_view(self):
        """Setup específico da view de usuários"""
        self.pack_full_screen()
        self.create_interface()

    def create_interface(self):
        # Cabeçalho
        self.header = Header(self, "Gerenciamento de Usuários")

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

        # Linhas da tabela
        self.load_data()

        # Botão voltar usando método da classe base
        back_btn = VoltarButton(self.content_frame, command=self.handle_back)
        back_btn.pack(side="bottom", anchor="w", pady=(20, 0))

    def create_table_headers(self):
        # Frame para os cabeçalhos
        header_frame = customtkinter.CTkFrame(
            self.table_frame, fg_color="#f0f0f0", corner_radius=10
        )
        header_frame.pack(fill="x", padx=10, pady=10)

        # Cabeçalhos
        headers = ["ID", "Usuário", "Nome Completo", "Tipo", "Status", "Data de Criação"]
        widths = [0.1, 0.15, 0.25, 0.15, 0.1, 0.25]  # Proporções de largura

        for i, (text, width) in enumerate(zip(headers, widths, strict=False)):
            # Cria um frame para cada cabeçalho para melhor controle
            header_cell = customtkinter.CTkFrame(header_frame, fg_color="transparent")
            header_cell.pack(side="left", fill="x", expand=True)

            lbl = customtkinter.CTkLabel(
                header_cell, text=text, font=("Arial", 14, "bold"), text_color="black", anchor="w"
            )
            lbl.pack(side="left", padx=10, pady=5)

            # Define o peso da coluna
            header_frame.columnconfigure(i, weight=int(width * 100))

    def load_data(self):
        # Frame rolável para os itens
        scrollable_frame = customtkinter.CTkScrollableFrame(self.table_frame, fg_color="white")
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        try:
            # Obter usuários usando UserManagementService
            management_service = get_user_management_service()
            usuarios = management_service.get_all_users()

            # Adicionar itens
            for idx, user in enumerate(usuarios):
                self.add_row(
                    scrollable_frame,
                    user.id,
                    user.username,
                    user.full_name,
                    user.user_type,
                    user.active,
                    user.created_at,
                    idx % 2 == 0,  # Alternar cor de fundo
                )
        except Exception as e:
            logger.error(f"Error loading users: {e}")

    def add_row(self, parent, user_id, username, full_name, user_type, active, created_at, par):
        # Format data
        status = "Ativo" if active else "Inativo"
        formatted_date = created_at.split(" ")[0]  # Get date only

        # Frame para uma linha da tabela
        row_frame = customtkinter.CTkFrame(
            parent, fg_color="#f9f9f9" if par else "white", corner_radius=8
        )
        row_frame.pack(fill="x", padx=5, pady=2)

        # Row data
        row_data = [
            str(user_id),
            username,
            full_name,
            user_type.capitalize(),
            status,
            formatted_date,
        ]

        for text in row_data:
            lbl = customtkinter.CTkLabel(
                row_frame, text=str(text), font=("Arial", 12), text_color="black", anchor="w"
            )
            lbl.pack(side="left", padx=10, pady=8, fill="x", expand=True)

    def handle_back(self):
        """Returns to previous screen"""
        if self.back_callback:
            self.back_callback()
