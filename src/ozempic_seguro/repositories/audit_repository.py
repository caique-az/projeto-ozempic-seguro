"""
Repositório de auditoria: registros de ações do sistema.

Implementa IAuditRepository com lógica de persistência para logs de auditoria.
"""

import json
import sqlite3
from datetime import datetime
from typing import Any

from ..core.logger import logger
from .connection import DatabaseConnection
from .interfaces import IAuditRepository


class AuditRepository(IAuditRepository):
    """
    Repositório para operações de auditoria no banco de dados.

    Responsabilidades:
    - Registrar logs de auditoria
    - Buscar e filtrar logs
    - Contagem de registros
    """

    def __init__(self):
        self._db = DatabaseConnection.get_instance()

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
        """
        Records an audit log entry and returns the record ID.

        Args:
            user_id: ID of the user who performed the action
            action: Action type (LOGIN, LOGOUT, CRIAR, ATUALIZAR, EXCLUIR, etc.)
            affected_table: Name of the affected table
            id_afetado: ID of the affected record
            previous_data: Data before the change
            new_data: Data after the change
            ip_address: User's IP address

        Returns:
            ID do registro criado ou None se falhar
        """
        try:
            prev_json = json.dumps(previous_data, ensure_ascii=False) if previous_data else None
            new_json = json.dumps(new_data, ensure_ascii=False) if new_data else None

            self._db.execute(
                """
                INSERT INTO auditoria
                (usuario_id, acao, tabela_afetada, id_afetado, dados_anteriores, dados_novos, endereco_ip)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (user_id, action, affected_table, id_afetado, prev_json, new_json, ip_address),
            )

            self._db.commit()
            return self._db.lastrowid()

        except sqlite3.Error as e:
            logger.error(f"Database error creating audit log: {e}")
            self._db.rollback()
            return None

    def get_logs(
        self,
        offset: int = 0,
        limit: int = 50,
        user_filter: int | None = None,
        action_filter: str | None = None,
        table_filter: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Returns audit logs with filters and pagination.

        Args:
            offset: Number of records to skip
            limit: Maximum number of records
            user_filter: Filter by user ID
            action_filter: Filter by action type
            table_filter: Filter by affected table
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Lista de dicionários com os logs
        """
        try:
            query = """
                SELECT
                    a.id, a.acao, a.tabela_afetada, a.id_afetado,
                    a.dados_anteriores, a.dados_novos, a.data_hora,
                    u.username as usuario
                FROM auditoria a
                LEFT JOIN usuarios u ON a.usuario_id = u.id
                WHERE 1=1
            """
            params: list[Any] = []

            if user_filter is not None:
                query += " AND a.usuario_id = ?"
                params.append(user_filter)
            if action_filter:
                query += " AND a.acao = ?"
                params.append(action_filter)
            if table_filter:
                query += " AND a.tabela_afetada = ?"
                params.append(table_filter)
            if start_date:
                query += " AND DATE(a.data_hora) >= ?"
                params.append(start_date)
            if end_date:
                query += " AND DATE(a.data_hora) <= ?"
                params.append(end_date)

            query += " ORDER BY a.data_hora DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            self._db.execute(query, tuple(params))
            columns = [desc[0] for desc in self._db.cursor.description]

            results = []
            for row in self._db.fetchall():
                result = dict(zip(columns, row, strict=False))

                # Parse JSON fields
                if result.get("dados_anteriores"):
                    result["dados_anteriores"] = json.loads(result["dados_anteriores"])
                if result.get("dados_novos"):
                    result["dados_novos"] = json.loads(result["dados_novos"])

                # Format date
                if result.get("data_hora"):
                    try:
                        dt = datetime.strptime(result["data_hora"], "%Y-%m-%d %H:%M:%S")
                        result["data_formatada"] = dt.strftime("%d/%m/%Y %H:%M:%S")
                    except ValueError:
                        result["data_formatada"] = result["data_hora"]

                results.append(result)

            return results

        except sqlite3.Error as e:
            logger.error(f"Database error fetching audit logs: {e}")
            return []

    def count_logs(
        self,
        user_filter: int | None = None,
        action_filter: str | None = None,
        table_filter: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> int:
        """
        Returns the total number of logs matching the filters.

        Args:
            user_filter: Filter by user ID
            action_filter: Filter by action type
            table_filter: Filter by affected table
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Número total de registros
        """
        try:
            query = "SELECT COUNT(*) FROM auditoria a WHERE 1=1"
            params: list[Any] = []

            if user_filter is not None:
                query += " AND a.usuario_id = ?"
                params.append(user_filter)
            if action_filter:
                query += " AND a.acao = ?"
                params.append(action_filter)
            if table_filter:
                query += " AND a.tabela_afetada = ?"
                params.append(table_filter)
            if start_date:
                query += " AND DATE(a.data_hora) >= ?"
                params.append(start_date)
            if end_date:
                query += " AND DATE(a.data_hora) <= ?"
                params.append(end_date)

            self._db.execute(query, tuple(params))
            return self._db.fetchone()[0]

        except sqlite3.Error as e:
            logger.error(f"Database error counting audit logs: {e}")
            return 0

    # Métodos da interface IRepository
    def find_by_id(self, entity_id: int) -> dict[str, Any] | None:
        """Implementação de IRepository.find_by_id"""
        self._db.execute("SELECT * FROM auditoria WHERE id = ?", (entity_id,))
        row = self._db.fetchone()
        if row:
            return {"id": row[0], "usuario_id": row[1], "acao": row[2], "data_hora": row[3]}
        return None

    def find_all(self) -> list[dict[str, Any]]:
        """Implementação de IRepository.find_all"""
        return self.get_logs(limit=1000)

    def save(self, entity: dict[str, Any]) -> bool:
        """Implementação de IRepository.save"""
        result = self.create_log(
            user_id=entity.get("usuario_id"),
            action=entity.get("acao"),
            affected_table=entity.get("tabela_afetada"),
            previous_data=entity.get("dados_anteriores"),
        )
        return result is not None

    def delete(self, entity_id: int) -> bool:
        """Implementação de IRepository.delete - Logs não devem ser deletados"""
        return False

    def exists(self, entity_id: int) -> bool:
        """Implementação de IRepository.exists"""
        return self.find_by_id(entity_id) is not None

    # Métodos da interface IAuditRepository
    def log_action(
        self,
        user_id: int | None,
        action: str,
        details: str | None = None,
        ip_address: str | None = None,
    ) -> bool:
        """Implementação de IAuditRepository.log_action"""
        result = self.create_log(
            user_id=user_id,
            action=action,
            previous_data={"details": details} if details else None,
            ip_address=ip_address,
        )
        return result is not None

    def find_by_user(self, user_id: int) -> list[dict[str, Any]]:
        """Implementação de IAuditRepository.find_by_user"""
        return self.get_logs(user_filter=user_id)

    def find_by_action(self, action: str) -> list[dict[str, Any]]:
        """Implementação de IAuditRepository.find_by_action"""
        return self.get_logs(action_filter=action)

    def find_by_date_range(self, start_date: str, end_date: str) -> list[dict[str, Any]]:
        """Implementação de IAuditRepository.find_by_date_range"""
        return self.get_logs(start_date=start_date, end_date=end_date)
