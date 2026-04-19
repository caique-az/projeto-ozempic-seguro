"""
Serviço de auditoria: camada de negócio isolada para logs de auditoria.
"""

from typing import Any

from ..repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self):
        self.audit_repo = AuditRepository()

    def get_logs(
        self,
        offset: int = 0,
        limit: int = 50,
        user_filter: int | None = None,
        action_filter: str | None = None,
        table_filter: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[Any, Any]]:
        """Returns audit logs with filters and pagination."""
        result = self.audit_repo.get_logs(
            offset, limit, user_filter, action_filter, table_filter, start_date, end_date
        )
        return list(result) if result else []

    def count_logs(
        self,
        user_filter: int | None = None,
        action_filter: str | None = None,
        table_filter: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> int:
        """Returns the total number of logs matching the filters."""
        result = self.audit_repo.count_logs(
            user_filter, action_filter, table_filter, start_date, end_date
        )
        return int(result) if result is not None else 0

    def create_log(
        self,
        user_id: int | None = None,
        action: str | None = None,
        affected_table: str | None = None,
        id_afetado: int | None = None,
        previous_data: dict | None = None,
        new_data: dict | None = None,
        ip_address: str | None = None,
    ) -> int | None:
        """Records an audit log entry and returns the record ID."""
        result = self.audit_repo.create_log(
            user_id, action, affected_table, id_afetado, previous_data, new_data, ip_address
        )
        return int(result) if result is not None else None
