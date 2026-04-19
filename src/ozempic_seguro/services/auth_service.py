"""
Serviço de autenticação - Lógica de login separada das views.

Responsabilidades:
- Verificar bloqueio de usuário
- Autenticar usuário
- Registrar tentativas de login
- Determinar tipo de painel a abrir
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..core.exceptions import (
    InvalidCredentialsError,
)
from ..core.logger import logger
from ..session.session_manager import SessionManager
from .user_service import UserService


class UserPanel(Enum):
    """Tipos de painel disponíveis"""

    ADMIN = "administrador"
    VENDEDOR = "vendedor"
    REPOSITOR = "repositor"
    TECNICO = "tecnico"
    UNKNOWN = "unknown"


@dataclass
class LoginResult:
    """Resultado de uma tentativa de login"""

    success: bool
    user: dict[str, Any] | None = None
    panel: UserPanel | None = None
    error_message: str | None = None
    is_locked: bool = False
    remaining_attempts: int = 0
    lockout_seconds: int = 0


class AuthService:
    """
    Serviço de autenticação.

    Encapsula toda a lógica de login que estava na LoginView.
    """

    def __init__(self):
        self._session_manager = SessionManager.get_instance()
        self._user_service = UserService()

    def login(self, username: str, password: str) -> LoginResult:
        """
        Realiza tentativa de login.

        Args:
            username: Nome de usuário
            password: Senha

        Returns:
            LoginResult com o resultado da tentativa
        """
        username = username.strip()

        # Verifica se usuário está bloqueado
        if self._session_manager.is_user_locked(username):
            status = self._session_manager.get_login_status_message(username)
            remaining_seconds = self._session_manager.get_lockout_remaining_seconds(username)

            logger.warning(f"Login attempt for locked user: {username}")

            return LoginResult(
                success=False,
                is_locked=True,
                error_message=status.get("detailed_message", "Conta bloqueada"),
                lockout_seconds=remaining_seconds,
            )

        # Tenta autenticar
        try:
            user = self._user_service.authenticate(username, password)

            # Sucesso - registra e configura sessão
            self._session_manager.record_login_attempt(username, success=True)
            self._session_manager.set_current_user(user)

            panel = self._get_user_panel(user)

            logger.info(f"Login successful for user: {username}, panel: {panel.value}")

            return LoginResult(success=True, user=user, panel=panel)

        except InvalidCredentialsError:
            # Falha - registra tentativa
            self._session_manager.record_login_attempt(username, success=False)
            status = self._session_manager.get_login_status_message(username)

            logger.warning(f"Login failed for user: {username}")

            return LoginResult(
                success=False,
                is_locked=status.get("locked", False),
                error_message=status.get(
                    "detailed_message", status.get("message", "Credenciais inválidas")
                ),
                remaining_attempts=status.get("remaining_attempts", 0),
                lockout_seconds=(
                    self._session_manager.get_lockout_remaining_seconds(username)
                    if status.get("locked")
                    else 0
                ),
            )

    def logout(self) -> None:
        """Realiza logout do usuário atual"""
        current_user = self._session_manager.get_current_user()
        if current_user:
            logger.info(f"Logout for user: {current_user.get('username')}")

        self._session_manager.logout()

    def get_login_status(self, username: str) -> dict[str, Any]:
        """
        Obtém status de login para um usuário.

        Args:
            username: Nome de usuário

        Returns:
            Dict com status (locked, remaining_attempts, message)
        """
        result = self._session_manager.get_login_status_message(username)
        return dict(result) if result else {}

    def get_lockout_remaining_seconds(self, username: str) -> int:
        """
        Obtém segundos restantes de bloqueio.

        Args:
            username: Nome de usuário

        Returns:
            Segundos restantes ou 0 se não bloqueado
        """
        result = self._session_manager.get_lockout_remaining_seconds(username)
        return int(result) if result else 0

    def is_user_locked(self, username: str) -> bool:
        """
        Verifica se usuário está bloqueado.

        Args:
            username: Nome de usuário

        Returns:
            True se bloqueado
        """
        return bool(self._session_manager.is_user_locked(username))

    def get_current_user(self) -> dict[str, Any] | None:
        """Retorna usuário atual logado"""
        result = self._session_manager.get_current_user()
        return dict(result) if result else None

    def is_logged_in(self) -> bool:
        """Verifica se há usuário logado"""
        return bool(self._session_manager.is_logged_in())

    def _get_user_panel(self, user: dict[str, Any]) -> UserPanel:
        """
        Determina qual painel o usuário deve acessar.

        Args:
            user: Dados do usuário

        Returns:
            UserPanel correspondente ao tipo
        """
        tipo = user.get("tipo", "").lower()

        panel_map = {
            "administrador": UserPanel.ADMIN,
            "vendedor": UserPanel.VENDEDOR,
            "repositor": UserPanel.REPOSITOR,
            "tecnico": UserPanel.TECNICO,
        }

        return panel_map.get(tipo, UserPanel.UNKNOWN)


def get_auth_service() -> AuthService:
    """Returns singleton AuthService instance via ServiceFactory."""
    from .service_factory import ServiceFactory

    service: AuthService = ServiceFactory.get_auth_service()
    return service
