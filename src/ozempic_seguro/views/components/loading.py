"""
Componentes de Loading/Splash Screen.

Fornece overlay de carregamento para esconder o render das telas.
"""

from collections.abc import Callable

import customtkinter


class LoadingOverlay(customtkinter.CTkFrame):
    """
    Overlay de carregamento que cobre toda a tela.

    Uso:
        loading = LoadingOverlay(parent)
        loading.show("Carregando...")
        # ... operação demorada ...
        loading.hide()
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#1a1a2e", corner_radius=0, **kwargs)

        # Container central
        self.center_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Spinner animado (usando texto rotativo)
        self.spinner_label = customtkinter.CTkLabel(
            self.center_frame, text="⟳", font=("Arial", 48), text_color="#4a90d9"
        )
        self.spinner_label.pack(pady=(0, 20))

        # Texto de loading
        self.message_label = customtkinter.CTkLabel(
            self.center_frame, text="Carregando...", font=("Arial", 18), text_color="white"
        )
        self.message_label.pack()

        # Progress bar opcional
        self.progress_bar = customtkinter.CTkProgressBar(
            self.center_frame, width=300, height=8, progress_color="#4a90d9", fg_color="#2d2d44"
        )
        self.progress_bar.pack(pady=(20, 0))
        self.progress_bar.set(0)

        # Estado de animação
        self._animating = False
        self._rotation = 0
        self._spinner_chars = ["⟳", "↻", "⟲", "↺"]
        self._spinner_index = 0

        # Inicialmente escondido
        self.place_forget()

    def show(self, message: str = "Carregando...", show_progress: bool = True) -> None:
        """
        Mostra o overlay de loading.

        Args:
            message: Mensagem a exibir
            show_progress: Se deve mostrar a barra de progresso
        """
        self.message_label.configure(text=message)

        if show_progress:
            self.progress_bar.pack(pady=(20, 0))
            self.progress_bar.set(0)
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
        else:
            self.progress_bar.pack_forget()

        # Cobrir toda a tela
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()

        # Iniciar animação do spinner
        self._animating = True
        self._animate_spinner()

        # Forçar atualização visual
        self.update()

    def hide(self) -> None:
        """Esconde o overlay de loading."""
        self._animating = False
        self.progress_bar.stop()
        self.place_forget()
        self.update()

    def set_progress(self, value: float) -> None:
        """
        Define o progresso (0.0 a 1.0).

        Args:
            value: Valor do progresso entre 0 e 1
        """
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.stop()
        self.progress_bar.set(min(1.0, max(0.0, value)))

    def set_message(self, message: str) -> None:
        """Atualiza a mensagem de loading."""
        self.message_label.configure(text=message)
        self.update()

    def _animate_spinner(self) -> None:
        """Anima o spinner de loading."""
        if not self._animating:
            return

        self._spinner_index = (self._spinner_index + 1) % len(self._spinner_chars)
        self.spinner_label.configure(text=self._spinner_chars[self._spinner_index])

        # Continuar animação
        self.after(150, self._animate_spinner)


class SplashScreen(customtkinter.CTkToplevel):
    """
    Splash screen que aparece durante a inicialização da aplicação.

    Uso:
        splash = SplashScreen()
        splash.set_status("Inicializando banco de dados...")
        # ... inicialização ...
        splash.destroy()
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Configurações da janela
        self.title("")
        self.geometry("400x300")
        self.resizable(False, False)
        self.overrideredirect(True)  # Remove borda da janela

        # Centralizar na tela
        self.update_idletasks()
        width = 400
        height = 300
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Fundo
        self.configure(fg_color="#1a1a2e")

        # Container
        container = customtkinter.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=40, pady=40)

        # Logo/Título
        self.title_label = customtkinter.CTkLabel(
            container, text="Ozempic Seguro", font=("Arial", 28, "bold"), text_color="white"
        )
        self.title_label.pack(pady=(20, 10))

        # Subtítulo
        self.subtitle_label = customtkinter.CTkLabel(
            container,
            text="Sistema de Controle de Gavetas",
            font=("Arial", 14),
            text_color="#888888",
        )
        self.subtitle_label.pack(pady=(0, 30))

        # Status
        self.status_label = customtkinter.CTkLabel(
            container, text="Iniciando...", font=("Arial", 12), text_color="#4a90d9"
        )
        self.status_label.pack(pady=(0, 10))

        # Progress bar
        self.progress = customtkinter.CTkProgressBar(
            container, width=280, height=6, progress_color="#4a90d9", fg_color="#2d2d44"
        )
        self.progress.pack()
        self.progress.configure(mode="indeterminate")
        self.progress.start()

        # Versão
        self.version_label = customtkinter.CTkLabel(
            container, text="v1.3.2", font=("Arial", 10), text_color="#555555"
        )
        self.version_label.pack(side="bottom", pady=(20, 0))

        # Manter no topo
        self.lift()
        self.attributes("-topmost", True)
        self.update()

    def set_status(self, message: str) -> None:
        """Atualiza o status exibido."""
        self.status_label.configure(text=message)
        self.update()

    def set_progress(self, value: float) -> None:
        """Define progresso determinado (0.0 a 1.0)."""
        self.progress.configure(mode="determinate")
        self.progress.stop()
        self.progress.set(min(1.0, max(0.0, value)))
        self.update()


class TransitionOverlay(customtkinter.CTkFrame):
    """
    Overlay de transição suave entre telas.

    Uso:
        transition = TransitionOverlay(parent)
        transition.fade_out(callback=lambda: show_next_screen())
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#1a1a2e", corner_radius=0, **kwargs)
        self._alpha = 0.0
        self.place_forget()

    def fade_in(self, duration_ms: int = 200, callback: Callable | None = None) -> None:
        """
        Fade in do overlay (escurece a tela).

        Args:
            duration_ms: Duração da animação em ms
            callback: Função a chamar após completar
        """
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        self._animate_fade(0.0, 1.0, duration_ms, callback)

    def fade_out(self, duration_ms: int = 200, callback: Callable | None = None) -> None:
        """
        Fade out do overlay (clareia a tela).

        Args:
            duration_ms: Duração da animação em ms
            callback: Função a chamar após completar
        """
        self._animate_fade(1.0, 0.0, duration_ms, lambda: self._on_fade_out_complete(callback))

    def _on_fade_out_complete(self, callback: Callable | None) -> None:
        """Chamado quando fade out completa."""
        self.place_forget()
        if callback:
            callback()

    def _animate_fade(
        self, start: float, end: float, duration_ms: int, callback: Callable | None
    ) -> None:
        """Anima o fade."""
        steps = 10
        step_duration = duration_ms // steps
        delta = (end - start) / steps

        def step(current_alpha: float, remaining: int):
            if remaining <= 0:
                if callback:
                    callback()
                return

            new_alpha = current_alpha + delta
            # Simular transparência com cor
            gray_value = int(26 + (229 * (1 - new_alpha)))  # 26 = #1a, 255 = white
            color = f"#{gray_value:02x}{gray_value:02x}{int(46 + (209 * (1 - new_alpha))):02x}"
            self.configure(fg_color=color if new_alpha > 0.1 else "#1a1a2e")

            self.after(step_duration, lambda: step(new_alpha, remaining - 1))

        step(start, steps)
