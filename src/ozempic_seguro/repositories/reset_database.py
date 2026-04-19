"""
Script para resetar o banco de dados.

ATENÇÃO: Este script remove TODOS os dados existentes!
Use apenas em ambiente de desenvolvimento ou para recuperação.
"""

import os
import sqlite3

from .security import hash_password


def reset_database():
    """
    Remove o banco de dados existente e cria um novo com as configurações iniciais,
    incluindo um usuário administrador padrão.

    Returns:
        bool: True se sucesso, False se erro
    """
    # Obtém o caminho do banco de dados
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, "ozempic_seguro.db")

    # Remove o banco de dados existente, se existir
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Banco de dados antigo removido: {db_path}")
        except Exception as e:
            print(f"Erro ao remover o banco de dados existente: {e}")
            return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Tabela de usuários
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            nome_completo TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK (tipo IN ('administrador', 'vendedor', 'repositor', 'tecnico')),
            ativo BOOLEAN DEFAULT 1,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # Tabela de gavetas
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS gavetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_gaveta TEXT NOT NULL UNIQUE,
            esta_aberta BOOLEAN NOT NULL DEFAULT 0,
            ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # Tabela de histórico de gavetas
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS historico_gavetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gaveta_id INTEGER,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acao TEXT NOT NULL,
            usuario_id INTEGER,
            FOREIGN KEY (gaveta_id) REFERENCES gavetas (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
        """
        )

        # Tabela de auditoria
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            acao TEXT NOT NULL,
            tabela_afetada TEXT,
            id_afetado INTEGER,
            dados_anteriores TEXT,
            dados_novos TEXT,
            endereco_ip TEXT,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
        """
        )

        # Tabela de migrations
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # Cria usuário administrador padrão com bcrypt
        admin_username = os.getenv("OZEMPIC_ADMIN_USERNAME", "00")
        admin_password = os.getenv("OZEMPIC_ADMIN_PASSWORD", "admin@2025")
        password_hash = hash_password(admin_password)
        cursor.execute(
            "INSERT INTO usuarios (username, senha_hash, nome_completo, tipo) VALUES (?, ?, ?, ?)",
            (admin_username, password_hash, "ADMINISTRADOR", "administrador"),
        )

        # Cria usuário técnico padrão
        technician_username = os.getenv("OZEMPIC_TECNICO_USERNAME", "01")
        technician_password = os.getenv("OZEMPIC_TECNICO_PASSWORD", "tecnico@2025")
        technician_password_hash = hash_password(technician_password)
        cursor.execute(
            "INSERT INTO usuarios (username, senha_hash, nome_completo, tipo) VALUES (?, ?, ?, ?)",
            (technician_username, technician_password_hash, "TÉCNICO", "tecnico"),
        )

        conn.commit()

        print("\nBanco de dados recriado com sucesso!")
        print("\nCredenciais de acesso (conforme variáveis de ambiente):")
        print(f"  Administrador: {admin_username} / {admin_password}")
        print(f"  Técnico: {technician_username} / {technician_password}")
        print("\nPor segurança, altere as senhas após o primeiro login.")

        return True

    except Exception as e:
        print(f"Erro ao recriar o banco de dados: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    print("=== RECRIAÇÃO DO BANCO DE DADOS ===\n")
    print("ATENÇÃO: Este processo irá APAGAR todos os dados existentes!\n")
    print("Este processo irá:")
    print("  1. Remover o banco de dados existente")
    print("  2. Criar um novo banco de dados")
    print("  3. Adicionar usuários padrão (admin: 00/1234, técnico: 01/1234)\n")

    confirmation = input("Deseja continuar? (s/n): ").strip().lower()

    if confirmation == "s":
        if reset_database():
            print("\nOperação concluída com sucesso!")
        else:
            print("\nOcorreu um erro durante a operação.")
    else:
        print("\nOperação cancelada pelo usuário.")
