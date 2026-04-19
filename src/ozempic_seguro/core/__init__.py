"""
Módulo core - Componentes fundamentais do sistema.

Fornece utilitários, validadores, cache, logging e exceções customizadas.
"""

from .cache import MemoryCache, cached
from .exceptions import (
    AccountLockedError,
    # Audit
    AuditError,
    AuditLogError,
    # Authentication
    AuthenticationError,
    # Configuration
    ConfigurationError,
    # Database
    DatabaseError,
    # Drawer
    DrawerError,
    DrawerNotFoundError,
    DrawerStateError,
    InsufficientPermissionsError,
    IntegrityError,
    InvalidConfigError,
    InvalidCredentialsError,
    InvalidInputError,
    InvalidUserDataError,
    InvalidUsernameError,
    LastAdminError,
    MigrationError,
    MissingConfigError,
    # Base
    OzempicError,
    SessionExpiredError,
    UserAlreadyExistsError,
    # User
    UserError,
    UserNotFoundError,
    # Validation
    ValidationError,
    WeakPasswordError,
)
from .logger import logger
from .validators import ValidationResult, Validators

__all__ = [
    # Validators
    "Validators",
    "ValidationResult",
    # Cache
    "MemoryCache",
    "cached",
    # Logger
    "logger",
    # Exceptions - Base
    "OzempicError",
    # Exceptions - Auth
    "AuthenticationError",
    "InvalidCredentialsError",
    "SessionExpiredError",
    "AccountLockedError",
    "InsufficientPermissionsError",
    # Exceptions - User
    "UserError",
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "LastAdminError",
    "InvalidUserDataError",
    # Exceptions - Validation
    "ValidationError",
    "InvalidUsernameError",
    "WeakPasswordError",
    "InvalidInputError",
    # Exceptions - Database
    "DatabaseError",
    "MigrationError",
    "IntegrityError",
    # Exceptions - Drawer
    "DrawerError",
    "DrawerNotFoundError",
    "DrawerStateError",
    # Exceptions - Audit
    "AuditError",
    "AuditLogError",
    # Exceptions - Config
    "ConfigurationError",
    "MissingConfigError",
    "InvalidConfigError",
]
