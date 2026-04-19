import customtkinter

from ..core.logger import logger
from ..session.session_manager import SessionManager
from ..views.iniciar_sessao_view import IniciarSessaoFrame
from ..views.login_view import LoginFrame
from ..views.pages_iniciais.tela_logo_view import TelaLogoFrame
from ..views.pages_iniciais.tela_toque_view import TelaToqueFrame


class NavigationController:
    def __init__(self, app):
        self.app = app
        self.container = app.container
        self.frames = {}
        self.current_frame = None
        self.screen_index = 0
        self.screens = [self.show_touch_screen, self.show_logo_screen]
        self.after_id = None
        self.is_running = True
        self._transitioning = False

        # Overlay para transições suaves
        self._transition_overlay = customtkinter.CTkFrame(self.container, fg_color="#3B6A7D")

    def preload_frames(self):
        """Pré-carrega os frames iniciais de forma invisível"""
        # Criar frames e renderizar fora da tela visível
        self.frames["toque"] = TelaToqueFrame(
            self.container, on_click_callback=self.show_start_session
        )
        self._prerender_frame(self.frames["toque"])

        self.frames["logo"] = TelaLogoFrame(
            self.container, on_click_callback=self.show_start_session
        )
        self._prerender_frame(self.frames["logo"])

        self.frames["iniciar"] = IniciarSessaoFrame(
            self.container,
            show_login_callback=self.show_login,
            back_callback=self.back_to_initial_screen,
        )
        self._prerender_frame(self.frames["iniciar"])

        self.frames["login"] = LoginFrame(
            self.container, show_iniciar_callback=self.show_start_session
        )
        self._prerender_frame(self.frames["login"])

    def _prerender_frame(self, frame):
        """Pré-renderiza um frame de forma invisível"""
        # Posicionar fora da tela para renderizar sem mostrar
        frame.place(x=-9999, y=-9999)
        self.app.update_idletasks()
        frame.place_forget()

    def show_frame(self, frame_name, animate=True):
        """Mostra um frame específico com transição suave"""
        if self._transitioning:
            return False

        # Verificar se precisa criar o frame
        needs_creation = (
            frame_name not in self.frames
            or not hasattr(self.frames[frame_name], "winfo_exists")
            or not self.frames[frame_name].winfo_exists()
        )

        if needs_creation:
            self._create_frame(frame_name)

        frame = self.frames.get(frame_name)
        if not frame:
            return False

        # Se é o mesmo frame, não fazer nada
        if self.current_frame == frame:
            return True

        self._transitioning = True
        old_frame = self.current_frame

        # 1. Mostrar overlay cobrindo tudo
        self._transition_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._transition_overlay.lift()
        self.app.update_idletasks()

        # 2. Esconder frame antigo
        if old_frame:
            old_frame.place_forget()
            old_frame.pack_forget()

        # 3. Posicionar novo frame
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.app.update_idletasks()

        # 4. Trazer novo frame para frente e esconder overlay
        frame.lift()
        self._transition_overlay.place_forget()

        self.current_frame = frame
        self._transitioning = False
        return True

    def _create_frame(self, frame_name):
        """Cria um frame específico"""
        if frame_name == "toque":
            self.frames[frame_name] = TelaToqueFrame(
                self.container, on_click_callback=self.show_start_session
            )
        elif frame_name == "logo":
            self.frames[frame_name] = TelaLogoFrame(
                self.container, on_click_callback=self.show_start_session
            )
        elif frame_name == "iniciar":
            self.frames[frame_name] = IniciarSessaoFrame(
                self.container,
                show_login_callback=self.show_login,
                back_callback=self.back_to_initial_screen,
            )
        elif frame_name == "login":
            self.frames[frame_name] = LoginFrame(
                self.container, show_iniciar_callback=self.show_start_session
            )

        self.app.update_idletasks()

    def back_to_initial_screen(self):
        if self.after_id:
            self.app.after_cancel(self.after_id)
        if self.current_frame:
            self.current_frame.pack_forget()
        self.show_touch_screen()
        self.start_alternation()

    def show_touch_screen(self):
        self.show_frame("toque")

    def show_logo_screen(self):
        self.show_frame("logo")

    def show_start_session(self):
        if self.after_id:
            self.app.after_cancel(self.after_id)
        if "iniciar" not in self.frames or not self.frames["iniciar"].winfo_exists():
            self.frames["iniciar"] = IniciarSessaoFrame(
                self.container,
                show_login_callback=self.show_login,
                back_callback=self.back_to_initial_screen,
            )
        self.show_frame("iniciar")

    def show_login(self):
        # Limpa a sessão atual
        session_manager = SessionManager.get_instance()
        session_manager.set_current_user(None)

        # Limpa campos do login
        if "login" in self.frames and self.frames["login"].winfo_exists():
            self.frames["login"].username_entry.delete(0, "end")
            self.frames["login"].password_entry.delete(0, "end")
        else:
            self.frames["login"] = LoginFrame(
                self.container, show_iniciar_callback=self.show_start_session
            )
        self.show_frame("login")

    def start_alternation(self):
        """Starts alternation between screens"""
        if self.is_running and len(self.screens) > 1:
            self.after_id = self.app.after(3000, self.alternate_screen)

    def alternate_screen(self):
        """Alternates between screens automatically"""
        if not self.is_running:
            return

        self.screen_index = (self.screen_index + 1) % len(self.screens)
        self.screens[self.screen_index]()

        # Schedule next alternation
        if self.is_running:
            self.after_id = self.app.after(3000, self.alternate_screen)

    def cleanup(self):
        """Cleans up resources when the application is closed"""
        try:
            # Stop screen alternation
            self.is_running = False

            # Cancel pending timer
            if self.after_id:
                self.app.after_cancel(self.after_id)
                self.after_id = None

            # Destroy frames if they exist
            for frame_name, frame in self.frames.items():
                try:
                    if frame and hasattr(frame, "winfo_exists") and frame.winfo_exists():
                        frame.destroy()
                except Exception as e:
                    logger.warning(f"Error destroying frame {frame_name}: {e}")

            # Clear frames dictionary
            self.frames.clear()
            self.current_frame = None

        except Exception as e:
            logger.error(f"Error during NavigationController cleanup: {e}")
