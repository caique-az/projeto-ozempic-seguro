"""
Gerenciador de timer e bloqueio do sistema.
"""

from datetime import datetime, timedelta


class TimerManager:
    """
    Gerencia timer do sistema e bloqueios temporários.

    Responsabilidades:
    - Controlar bloqueio temporário do sistema
    - Gerenciar estado do timer (ativado/desativado)
    """

    def __init__(self):
        self._blocked_until: datetime | None = None
        self._timer_enabled: bool = True

    def is_blocked(self) -> bool:
        """Verifica se o sistema está bloqueado"""
        if not self._timer_enabled:
            return False

        if self._blocked_until is None:
            return False

        if datetime.now() >= self._blocked_until:
            self._blocked_until = None
            return False

        return True

    def get_remaining_time(self) -> int:
        """Retorna o tempo restante de bloqueio em segundos"""
        if not self._blocked_until or not self._timer_enabled:
            return 0

        remaining = (self._blocked_until - datetime.now()).total_seconds()
        return max(0, int(remaining))

    def block_for_minutes(self, minutes: int = 5) -> bool:
        """Bloqueia o sistema por um número específico de minutos"""
        if not self._timer_enabled:
            return False

        self._blocked_until = datetime.now() + timedelta(minutes=minutes)
        return True

    def clear_block(self) -> None:
        """Remove o bloqueio do sistema"""
        self._blocked_until = None

    def set_enabled(self, enabled: bool) -> None:
        """Ativa ou desativa a função de timer"""
        self._timer_enabled = enabled

    def is_enabled(self) -> bool:
        """Verifica se a função de timer está ativada"""
        return self._timer_enabled
