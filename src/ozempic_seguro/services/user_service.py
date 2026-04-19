"""
Serviço de usuários: camada de negócio isolada entre controllers e repositories.

Utiliza exceções customizadas para tratamento de erros consistente.
"""
from typing import Optional, Tuple, List, Dict, Any
import datetime

from ..repositories.user_repository import UserRepository
from ..repositories.audit_repository import AuditRepository
from ..repositories.security_logger import SecurityLogger
from ..core.validators import Validators
from ..config import SecurityConfig
from ..core.base_views import BaseService
from ..core.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    LastAdminError,
    InvalidCredentialsError,
    AccountLockedError,
    WeakPasswordError,
    InvalidUserDataError,
    InsufficientPermissionsError,
)


class UserService(BaseService):
    def __init__(self):
        super().__init__()
        self.user_repo = UserRepository()
        self.audit_repo = AuditRepository()

    def create_user(
        self,
        nome: str,
        username: str,
        senha: str,
        tipo: str,
        usuario_criador_id: Optional[int] = None,
    ) -> Tuple[bool, str]:
        """
        Cadastra um novo usuário com validações robustas e registra log de auditoria.

        Raises:
            InvalidUserDataError: Se os dados de entrada forem inválidos
            UserAlreadyExistsError: Se o username já existir
        """
        # Validação robusta de entrada usando método da classe base
        validation_data = {"username": username, "senha": senha, "nome": nome, "tipo": tipo}

        if not self._validate_input(validation_data):
            raise InvalidUserDataError("input", "Dados de entrada inválidos ou incompletos")

        validation_result = Validators.validate_and_sanitize_user_input(
            username=username, password=senha, name=nome, user_type=tipo
        )

        if not validation_result["valid"]:
            errors = "; ".join(validation_result["errors"])
            raise InvalidUserDataError("validation", errors)

        # Usar dados sanitizados
        sanitized_data = validation_result["sanitized_data"]
        nome_sanitizado = sanitized_data["name"]
        username_sanitizado = sanitized_data["username"]
        tipo_sanitizado = sanitized_data["user_type"]

        try:
            novo_id = self.user_repo.create_user(
                username_sanitizado, senha, nome_sanitizado, tipo_sanitizado
            )
            if not novo_id:
                raise UserAlreadyExistsError(username_sanitizado)

            # Log de criação com contexto de segurança
            security_context = SecurityLogger.log_user_management(
                action="CREATE_USER",
                admin_user_id=usuario_criador_id or novo_id,
                admin_username="system",
                target_user_id=novo_id,
                target_username=username_sanitizado,
                changes={
                    "nome_completo": nome_sanitizado,
                    "tipo": tipo_sanitizado,
                    "data_criacao": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            )
            self.audit_repo.create_log(
                usuario_id=usuario_criador_id or novo_id,
                acao="CRIAR",
                tabela_afetada="USUARIOS",
                id_afetado=novo_id,
                dados_novos=security_context,
                endereco_ip=security_context.get("ip_address"),
            )
            return True, "Usuário cadastrado com sucesso!"

        except (InvalidUserDataError, UserAlreadyExistsError):
            raise
        except Exception as e:
            raise InvalidUserDataError("database", f"Erro ao cadastrar usuário: {str(e)}")

    def _validate_input(self, validation_data: Dict) -> bool:
        """Implementação da validação de entrada obrigatória da classe base"""
        required_fields = ["username", "senha", "nome", "tipo"]

        # Verificar campos obrigatórios
        for field in required_fields:
            if not validation_data.get(field):
                return False

        # Validar tipo de usuário
        if validation_data["tipo"] not in SecurityConfig.VALID_USER_TYPES:
            return False

        return True

    def authenticate(self, username: str, senha: str, endereco_ip: Optional[str] = None) -> Dict[str, Any]:
        """
        Autentica usuário com validação robusta, controle de força bruta e logs detalhados.

        Returns:
            Dict com dados do usuário autenticado

        Raises:
            InvalidCredentialsError: Se credenciais forem inválidas
            AccountLockedError: Se conta estiver bloqueada
        """
        # Validação básica - permite usuário "00" (admin padrão)
        if not username or not senha:
            raise InvalidCredentialsError(username)

        # Sanitiza entrada
        username = username.strip()

        # Permite usuário admin padrão "00" sem validação rigorosa
        if username != "00":
            # Validação robusta apenas para outros usuários
            username_result = Validators.validate_username(username)
            password_result = Validators.validate_password(senha, strict=False)
            username_valid = username_result.is_valid
            username_error = username_result.errors[0] if username_result.errors else ""
            password_valid = password_result.is_valid
            password_error = password_result.errors[0] if password_result.errors else ""

            if not username_valid:
                # Log tentativa com dados inválidos
                security_context = SecurityLogger.log_security_violation(
                    violation_type="INVALID_USERNAME_FORMAT",
                    details={
                        "username": Validators.sanitize_string(username, 50),
                        "error": username_error,
                    },
                )
                self.audit_repo.create_log(
                    usuario_id=None,
                    acao="SECURITY_VIOLATION",
                    tabela_afetada="USUARIOS",
                    dados_anteriores=security_context,
                    endereco_ip=security_context.get("ip_address"),
                )
                raise InvalidCredentialsError(username, "Formato de usuário inválido")

            if not password_valid:
                raise InvalidCredentialsError(username, "Formato de senha inválido")

        # Verificar se usuário está bloqueado por tentativas excessivas
        from ..session.session_manager import SessionManager

        session_manager = SessionManager.get_instance()

        if session_manager.is_user_locked(username):
            remaining_time = session_manager.get_lockout_remaining_time(username)
            security_context = SecurityLogger.log_security_violation(
                violation_type="ACCOUNT_LOCKED",
                username=username,
                details={"remaining_lockout_minutes": remaining_time},
            )
            self.audit_repo.create_log(
                usuario_id=None,
                acao="LOGIN_BLOCKED",
                tabela_afetada="USUARIOS",
                dados_anteriores=security_context,
                endereco_ip=security_context.get("ip_address"),
            )
            raise AccountLockedError(username, locked_until=f"{remaining_time} minutos")

        user = self.user_repo.authenticate_user(username, senha)

        if user:
            # Reset contador de tentativas em caso de sucesso
            session_manager.record_login_attempt(username, success=True)

            # Log de sucesso com contexto de segurança
            security_context = SecurityLogger.log_login_attempt(
                username=username, success=True, user_id=user["id"]
            )

            self.audit_repo.create_log(
                usuario_id=user["id"],
                acao="LOGIN_SUCCESS",
                tabela_afetada="USUARIOS",
                id_afetado=user["id"],
                dados_novos=security_context,
                endereco_ip=security_context.get("ip_address"),
            )
            return dict(user)
        else:
            # Registra tentativa falhada para controle de força bruta
            session_manager.record_login_attempt(username, success=False)

            # Log de tentativa falha com contexto de segurança
            security_context = SecurityLogger.log_login_attempt(
                username=username, success=False, failure_reason="invalid_credentials"
            )

            self.audit_repo.create_log(
                usuario_id=None,
                acao="LOGIN_FAILED",
                tabela_afetada="USUARIOS",
                dados_anteriores=security_context,
                endereco_ip=security_context.get("ip_address"),
            )
            raise InvalidCredentialsError(username)

    def logout(self, usuario_id: int, username: str, endereco_ip: Optional[str] = None) -> None:
        """Registra logout de usuário com contexto de segurança."""
        security_context = SecurityLogger.log_session_event(
            event_type="LOGOUT", user_id=usuario_id, username=username
        )

        self.audit_repo.create_log(
            usuario_id=usuario_id,
            acao="LOGOUT",
            tabela_afetada="USUARIOS",
            id_afetado=usuario_id,
            dados_novos=security_context,
            endereco_ip=security_context.get("ip_address", endereco_ip),
        )

    def delete_user(self, usuario_id: int) -> Tuple[bool, str]:
        """
        Exclui usuário e registra auditoria.

        Raises:
            UserNotFoundError: Se usuário não existir
            InsufficientPermissionsError: Se tentar excluir técnico
            LastAdminError: Se tentar excluir único admin
        """
        # Verificar se usuário existe
        user = self.user_repo.get_user_by_id(usuario_id)
        if not user:
            raise UserNotFoundError(usuario_id)

        # Verificar se é um técnico
        if user.get("tipo") == "tecnico":
            raise InsufficientPermissionsError(
                action="excluir_usuario", required_role="administrador", user_role="tecnico"
            )

        if self.user_repo.is_unique_admin(usuario_id):
            raise LastAdminError()

        sucesso = self.user_repo.delete_user(usuario_id)
        if sucesso:
            self.audit_repo.create_log(
                usuario_id=usuario_id,
                acao="EXCLUIR",
                tabela_afetada="USUARIOS",
                id_afetado=usuario_id,
            )
            return True, "Usuário excluído com sucesso!"
        raise UserNotFoundError(usuario_id)

    def get_all_users(self) -> List[Dict[Any, Any]]:
        """Retorna lista de todos os usuários."""
        result = self.user_repo.get_users()
        return list(result) if result else []

    def update_password(
        self, usuario_id: int, nova_senha: str, admin_user_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Atualiza senha de usuário com validação robusta e registra auditoria.

        Raises:
            UserNotFoundError: Se usuário não existir
            InsufficientPermissionsError: Se tentar alterar senha de técnico
            WeakPasswordError: Se senha não atender requisitos
        """
        # Verificar se usuário existe
        user = self.user_repo.get_user_by_id(usuario_id)
        if not user:
            raise UserNotFoundError(usuario_id)

        # Verificar se é um técnico
        if user.get("tipo") == "tecnico":
            raise InsufficientPermissionsError(
                action="alterar_senha", required_role="administrador", user_role="tecnico"
            )

        # Validação robusta da nova senha
        password_result = Validators.validate_password(nova_senha, strict=False)
        password_valid = password_result.is_valid
        password_error = password_result.errors[0] if password_result.errors else ""

        if not password_valid:
            raise WeakPasswordError([password_error])

        try:
            sucesso = self.user_repo.update_password(usuario_id, nova_senha)
            if sucesso:
                # Log com contexto de segurança
                security_context = SecurityLogger.log_user_management(
                    action="UPDATE_PASSWORD",
                    admin_user_id=admin_user_id or usuario_id,
                    admin_username="system",
                    target_user_id=usuario_id,
                    changes={"password_updated": True},
                )

                self.audit_repo.create_log(
                    usuario_id=admin_user_id or usuario_id,
                    acao="ATUALIZAR_SENHA",
                    tabela_afetada="USUARIOS",
                    id_afetado=usuario_id,
                    dados_novos=security_context,
                    endereco_ip=security_context.get("ip_address"),
                )
                return True, "Senha atualizada com sucesso"
            raise UserNotFoundError(usuario_id)
        except (UserNotFoundError, InsufficientPermissionsError, WeakPasswordError):
            raise
        except Exception as e:
            # Log erro de segurança
            security_context = SecurityLogger.log_security_violation(
                violation_type="PASSWORD_UPDATE_ERROR",
                user_id=admin_user_id or usuario_id,
                details={"error": str(e), "target_user_id": usuario_id},
            )
            self.audit_repo.create_log(
                usuario_id=admin_user_id or usuario_id,
                acao="ERRO_ATUALIZAR_SENHA",
                tabela_afetada="USUARIOS",
                id_afetado=usuario_id,
                dados_anteriores=security_context,
                endereco_ip=security_context.get("ip_address"),
            )
            raise InvalidUserDataError("password", f"Erro ao atualizar senha: {str(e)}")
