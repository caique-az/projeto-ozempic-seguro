"""
Gerenciador de conexão com banco de dados.

Responsabilidade única: gerenciar conexão SQLite e executar migrations.
"""

import os
import sqlite3
import threading
from typing import Optional

from ..config import Config
from ..core.logger import DatabaseException, log_exceptions, logger


class DatabaseConnection:
    """
    Singleton thread-safe para gerenciar conexão com banco de dados.

    Responsabilidades:
    - Criar e manter conexão SQLite
    - Executar migrations
    - Fornecer cursor para operações

    Uso:
        conn = DatabaseConnection.get_instance()
        cursor = conn.cursor
        cursor.execute("SELECT * FROM usuarios")

    Context Manager:
        with DatabaseConnection.get_instance() as conn:
            conn.execute("SELECT * FROM usuarios")
    """

    _instance: Optional["DatabaseConnection"] = None
    _lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls) -> "DatabaseConnection":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    @classmethod
    def get_instance(cls) -> "DatabaseConnection":
        """Retorna a instância singleton"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize(self) -> None:
        """Inicializa conexão e executa migrations"""
        logger.info("Initializing database connection")

        db_path = self._get_db_path()
        self._is_new_db = not os.path.exists(db_path)

        self._conn = sqlite3.connect(
            db_path,
            timeout=Config.Database.DB_TIMEOUT,
            check_same_thread=Config.Database.DB_CHECK_SAME_THREAD,
        )
        self._conn.row_factory = sqlite3.Row
        self._cursor = self._conn.cursor()

        self._configure_pragmas()
        self._run_migrations()

        logger.info("Database connection initialized successfully")

    def _get_db_path(self) -> str:
        """Retorna caminho do arquivo do banco"""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(base_dir, Config.App.DATA_DIR)
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, Config.Database.DB_NAME)

    def _configure_pragmas(self) -> None:
        """Configura pragmas de performance"""
        if Config.Database.ENABLE_FOREIGN_KEYS:
            self._cursor.execute("PRAGMA foreign_keys = ON;")
        if Config.Database.ENABLE_WAL_MODE:
            self._cursor.execute("PRAGMA journal_mode = WAL;")
        self._cursor.execute(f"PRAGMA cache_size = {Config.Database.CACHE_SIZE};")
        self._conn.commit()

    @log_exceptions("Database Migrations")
    def _run_migrations(self) -> None:
        """Executa scripts SQL de migrations"""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        migrations_dir = os.path.join(base_dir, Config.App.MIGRATIONS_DIR)
        os.makedirs(migrations_dir, exist_ok=True)

        # Cria tabela de controle
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        self._conn.commit()

        # Detecta versões aplicadas
        applied = {row[0] for row in self._cursor.execute("SELECT version FROM migrations")}

        # Aplica novos scripts
        if not os.path.exists(migrations_dir):
            return

        migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith(".sql")])

        for fname in migration_files:
            version = int(fname.split("_")[0])
            if version in applied:
                continue

            logger.info(f"Applying migration: {fname}")
            path = os.path.join(migrations_dir, fname)

            try:
                with open(path, encoding="utf-8") as f:
                    self._conn.executescript(f.read())
                self._cursor.execute(
                    "INSERT INTO migrations (version, name) VALUES (?, ?)", (version, fname)
                )
                self._conn.commit()
                logger.info(f"Migration applied: {fname}")
            except Exception as e:
                logger.error(f"Migration failed {fname}: {e}")
                raise DatabaseException(f"Migration failed: {fname}")

    @property
    def conn(self) -> sqlite3.Connection:
        """Retorna conexão SQLite"""
        return self._conn

    @property
    def cursor(self) -> sqlite3.Cursor:
        """Retorna cursor SQLite"""
        return self._cursor

    @property
    def is_new_database(self) -> bool:
        """Retorna True se é um banco novo"""
        return self._is_new_db

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Executa query e retorna cursor"""
        return self._cursor.execute(query, params)

    def executemany(self, query: str, params_list: list) -> sqlite3.Cursor:
        """Executa query para múltiplos registros"""
        return self._cursor.executemany(query, params_list)

    def commit(self) -> None:
        """Confirma transação"""
        self._conn.commit()

    def rollback(self) -> None:
        """Reverte transação"""
        self._conn.rollback()

    def fetchone(self):
        """Retorna um registro"""
        return self._cursor.fetchone()

    def fetchall(self) -> list:
        """Retorna todos os registros"""
        return self._cursor.fetchall()

    def lastrowid(self) -> int:
        """Retorna ID do último registro inserido"""
        return self._cursor.lastrowid

    def close(self) -> None:
        """Fecha conexão"""
        if hasattr(self, "_conn") and self._conn:
            try:
                self._conn.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.warning(f"Error closing database connection: {e}")
            finally:
                self._conn = None
                self._cursor = None

    def __del__(self) -> None:
        """Destrutor - garante fechamento da conexão"""
        self.close()

    def __enter__(self) -> "DatabaseConnection":
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - não fecha conexão singleton"""
        # Não fechamos a conexão aqui pois é singleton
        # Apenas fazemos commit ou rollback
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reseta a instância singleton (apenas para testes).
        Fecha a conexão existente antes de resetar.
        """
        with cls._lock:
            if cls._instance is not None:
                cls._instance.close()
                cls._instance = None
                cls._initialized = False
