"""
Serviço de auditoria: camada de negócio isolada para logs de auditoria.
"""
from typing import Optional, List, Dict, Any

from ..repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self):
        self.audit_repo = AuditRepository()

    def get_logs(
        self,
        offset: int = 0,
        limit: int = 50,
        user_filter: Optional[int] = None,
        action_filter: Optional[str] = None,
        table_filter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[Any, Any]]:
        """Returns audit logs with filters and pagination."""
        result = self.audit_repo.get_logs(
            offset, limit, user_filter, action_filter, table_filter, start_date, end_date
        )
        return list(result) if result else []

    def count_logs(
        self,
        user_filter: Optional[int] = None,
        action_filter: Optional[str] = None,
        table_filter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> int:
        """Returns the total number of logs matching the filters."""
        result = self.audit_repo.count_logs(
            user_filter, action_filter, table_filter, start_date, end_date
        )
        return int(result) if result is not None else 0

    def create_log(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        affected_table: Optional[str] = None,
        id_afetado: Optional[int] = None,
        previous_data: Optional[Dict] = None,
        new_data: Optional[Dict] = None,
        ip_address: Optional[str] = None,
    ) -> Optional[int]:
        """Records an audit log entry and returns the record ID."""
        result = self.audit_repo.create_log(
            user_id, action, affected_table, id_afetado, previous_data, new_data, ip_address
        )
        return int(result) if result is not None else None
