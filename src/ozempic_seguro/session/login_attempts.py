"""
Gerenciador de tentativas de login para controle de força bruta.
"""

from datetime import datetime, timedelta
from typing import Any

from ..config import Config


class LoginAttemptsManager:
    """
    Gerencia tentativas de login e bloqueios por força bruta.

    Responsabilidades:
    - Registrar tentativas de login
    - Controlar bloqueio por tentativas excessivas
    - Fornecer status de bloqueio
    """

    def __init__(self):
        self._login_attempts: dict[str, dict] = {}
        self._max_login_attempts: int = Config.Security.MAX_LOGIN_ATTEMPTS
        self._lockout_duration: int = Config.Security.LOCKOUT_DURATION_MINUTES

    def record_attempt(self, username: str, success: bool = True) -> None:
        """Registra tentativa de login"""
        now = datetime.now()

        if username not in self._login_attempts:
            self._login_attempts[username] = {"count": 0, "last_attempt": now, "locked_until": None}

        attempt_data = self._login_attempts[username]

        if success:
            attempt_data["count"] = 0
            attempt_data["locked_until"] = None
        else:
            attempt_data["count"] += 1
            attempt_data["last_attempt"] = now

            if attempt_data["count"] >= self._max_login_attempts:
                attempt_data["locked_until"] = now + timedelta(minutes=self._lockout_duration)

    def is_locked(self, username: str) -> bool:
        """Verifica se usuário está bloqueado"""
        if username not in self._login_attempts:
            return False

        attempt_data = self._login_attempts[username]

        if attempt_data["locked_until"] is None:
            return False

        if datetime.now() >= attempt_data["locked_until"]:
            attempt_data["locked_until"] = None
            attempt_data["count"] = 0
            return False

        return True

    def get_remaining_time_minutes(self, username: str) -> int:
        """Retorna tempo restante de bloqueio em minutos"""
        if username not in self._login_attempts:
            return 0

        attempt_data = self._login_attempts[username]

        if attempt_data["locked_until"] is None:
            return 0

        remaining = attempt_data["locked_until"] - datetime.now()
        return max(0, int(remaining.total_seconds() / 60))

    def get_remaining_time_seconds(self, username: str) -> int:
        """Retorna tempo restante de bloqueio em segundos"""
        if username not in self._login_attempts:
            return 0

        attempt_data = self._login_attempts[username]

        if attempt_data["locked_until"] is None:
            return 0

        remaining = attempt_data["locked_until"] - datetime.now()
        return max(0, int(remaining.total_seconds()))

    def get_remaining_attempts(self, username: str) -> int:
        """Retorna número de tentativas restantes"""
        if username not in self._login_attempts:
            return self._max_login_attempts

        attempt_data = self._login_attempts[username]
        used_attempts = attempt_data["count"]
        remaining = self._max_login_attempts - used_attempts
        return max(0, remaining)

    def get_status_message(self, username: str) -> dict[str, Any]:
        """Retorna mensagem personalizada sobre o status de login"""
        if self.is_locked(username):
            remaining_time = self.get_remaining_time_minutes(username)
            remaining_seconds = self.get_remaining_time_seconds(username)

            if remaining_time > 0:
                return {
                    "locked": True,
                    "message": f"Conta bloqueada por {remaining_time} minuto(s)",
                    "detailed_message": f"Muitas tentativas incorretas. Tente novamente em {remaining_time}:{remaining_seconds % 60:02d}",
                    "remaining_seconds": remaining_seconds,
                    "remaining_attempts": 0,
                }

        remaining_attempts = self.get_remaining_attempts(username)
        if remaining_attempts < self._max_login_attempts:
            return {
                "locked": False,
                "message": f"Atenção: {remaining_attempts} tentativa(s) restante(s)",
                "remaining_attempts": remaining_attempts,
            }

        return {"locked": False, "message": "", "remaining_attempts": remaining_attempts}

    def reset(self, username: str) -> None:
        """Reseta tentativas de login de um usuário"""
        if username in self._login_attempts:
            self._login_attempts[username] = {
                "count": 0,
                "last_attempt": None,
                "locked_until": None,
            }
