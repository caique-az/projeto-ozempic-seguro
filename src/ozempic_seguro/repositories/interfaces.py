"""
Interfaces e abstrações para o padrão Repository.
Define contratos para implementações concretas.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """Interface base para todos os repositórios"""

    @abstractmethod
    def find_by_id(self, entity_id: int) -> T | None:
        """Busca entidade por ID"""

    @abstractmethod
    def find_all(self) -> list[T]:
        """Busca todas as entidades"""

    @abstractmethod
    def save(self, entity: T) -> bool:
        """Salva ou atualiza entidade"""

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """Remove entidade por ID"""

    @abstractmethod
    def exists(self, entity_id: int) -> bool:
        """Verifica se entidade existe"""


class IUserRepository(IRepository[dict[str, Any]]):
    """Interface específica para repositório de usuários"""

    @abstractmethod
    def find_by_username(self, username: str) -> dict[str, Any] | None:
        """Busca usuário por username"""

    @abstractmethod
    def find_by_type(self, user_type: str) -> list[dict[str, Any]]:
        """Busca usuários por tipo"""

    @abstractmethod
    def find_active_users(self) -> list[dict[str, Any]]:
        """Busca apenas usuários ativos"""

    @abstractmethod
    def update_password(self, user_id: int, password_hash: str) -> bool:
        """Atualiza senha do usuário"""

    @abstractmethod
    def update_status(self, user_id: int, active: bool) -> bool:
        """Atualiza status ativo/inativo do usuário"""


class IAuditRepository(IRepository[dict[str, Any]]):
    """Interface para repositório de auditoria"""

    @abstractmethod
    def log_action(
        self,
        user_id: int | None,
        action: str,
        details: str | None = None,
        ip_address: str | None = None,
    ) -> bool:
        """Registra ação de auditoria"""

    @abstractmethod
    def find_by_user(self, user_id: int) -> list[dict[str, Any]]:
        """Busca logs por usuário"""

    @abstractmethod
    def find_by_action(self, action: str) -> list[dict[str, Any]]:
        """Busca logs por tipo de ação"""

    @abstractmethod
    def find_by_date_range(self, start_date: str, end_date: str) -> list[dict[str, Any]]:
        """Busca logs por período"""


class IGavetaRepository(IRepository[dict[str, Any]]):
    """Interface para repositório de gavetas"""

    @abstractmethod
    def find_by_numero(self, numero: int) -> dict[str, Any] | None:
        """Busca gaveta por número"""

    @abstractmethod
    def find_by_status(self, status: str) -> list[dict[str, Any]]:
        """Busca gavetas por status"""

    @abstractmethod
    def find_by_user(self, user_id: int) -> list[dict[str, Any]]:
        """Busca gavetas de um usuário"""

    @abstractmethod
    def update_status(self, gaveta_id: int, status: str) -> bool:
        """Atualiza status da gaveta"""

    @abstractmethod
    def assign_to_user(self, gaveta_id: int, user_id: int) -> bool:
        """Atribui gaveta a um usuário"""


class IService(ABC):
    """Interface base para serviços"""

    @abstractmethod
    def validate_input(self, data: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Valida dados de entrada.

        Returns:
            Tuple (válido, lista_de_erros)
        """


class IUserService(IService):
    """Interface para serviço de usuários"""

    @abstractmethod
    def authenticate(self, username: str, password: str) -> dict[str, Any] | None:
        """Autentica usuário"""

    @abstractmethod
    def create_user(
        self, username: str, password: str, nome_completo: str, tipo: str
    ) -> tuple[bool, str | None]:
        """
        Cria novo usuário.

        Returns:
            Tuple (sucesso, mensagem_erro)
        """

    @abstractmethod
    def update_password(self, user_id: int, new_password: str) -> bool:
        """Atualiza senha do usuário"""

    @abstractmethod
    def toggle_user_status(self, user_id: int) -> bool:
        """Alterna status ativo/inativo"""

    @abstractmethod
    def delete_user(self, user_id: int) -> tuple[bool, str | None]:
        """
        Remove usuário.

        Returns:
            Tuple (sucesso, mensagem_erro)
        """

    @abstractmethod
    def get_all_users(self) -> list[dict[str, Any]]:
        """Lista todos os usuários"""

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        """Busca usuário por ID"""

    @abstractmethod
    def is_admin(self, user_id: int) -> bool:
        """Verifica se usuário é administrador"""


class IAuditService(IService):
    """Interface para serviço de auditoria"""

    @abstractmethod
    def log_action(self, user_id: int | None, action: str, details: str | None = None) -> bool:
        """Registra ação para auditoria"""

    @abstractmethod
    def get_user_logs(self, user_id: int) -> list[dict[str, Any]]:
        """Obtém logs de um usuário"""

    @abstractmethod
    def get_recent_logs(self, limit: int = 100) -> list[dict[str, Any]]:
        """Obtém logs recentes"""

    @abstractmethod
    def get_logs_by_action(self, action: str) -> list[dict[str, Any]]:
        """Obtém logs por tipo de ação"""

    @abstractmethod
    def export_logs(self, format: str = "json") -> str:
        """Exporta logs em formato específico"""
