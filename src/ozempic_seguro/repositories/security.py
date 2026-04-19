"""
Módulo de segurança: funções de hash e verificação de senha com bcrypt.
Sistema 100% bcrypt - sem suporte legacy.
"""

import bcrypt


def hash_password(password: str, rounds: int = 12) -> str:
    """
    Generates a secure hash for the password using bcrypt.

    Args:
        password (str): Password to hash
        rounds (int): Número de rounds para bcrypt (padrão: 12)

    Returns:
        str: Hash da senha
    """
    # Converte senha para bytes
    password_bytes = password.encode("utf-8")
    # Gera salt e hash com bcrypt
    salt = bcrypt.gensalt(rounds=rounds)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifies if the password matches the provided hash.
    Uses bcrypt only for maximum security.

    Args:
        password (str): Plain text password
        password_hash (str): Hash stored in the database

    Returns:
        bool: True se a senha corresponde ao hash
    """
    try:
        # Verifica se é bcrypt (começa com $2a$, $2b$, $2x$ ou $2y$)
        if not password_hash.startswith(("$2a$", "$2b$", "$2x$", "$2y$")):
            # Hash inválido ou formato desconhecido
            return False

        # Sistema bcrypt apenas
        password_bytes = password.encode("utf-8")
        hash_bytes = password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except (ValueError, TypeError):
        # Invalid hash format or encoding error
        return False


def is_bcrypt_hash(password_hash: str) -> bool:
    """
    Checks if a hash is bcrypt format.

    Args:
        password_hash (str): Hash to verify

    Returns:
        bool: True se for bcrypt, False caso contrário
    """
    return password_hash.startswith(("$2a$", "$2b$", "$2x$", "$2y$"))
