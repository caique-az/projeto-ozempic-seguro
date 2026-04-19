"""
Componentes de layout: ResponsiveFrame, ResponsiveButtonGrid
"""

import customtkinter

from .buttons import ModernButton


class ResponsiveFrame(customtkinter.CTkFrame):
    """Layout responsivo para painéis"""

    def __init__(self, master, min_width=800, min_height=600, **kwargs):
        super().__init__(master, **kwargs)
        self.min_width = min_width
        self.min_height = min_height
        self.pack(fill="both", expand=True)
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        """Ajusta layout baseado no tamanho da janela"""
        if event.widget == self:
            width = event.width
            height = event.height

            if hasattr(self, "_responsive_components"):
                for component in self._responsive_components:
                    if hasattr(component, "adjust_to_size"):
                        component.adjust_to_size(width, height)


class ResponsiveButtonGrid(customtkinter.CTkFrame):
    """Grid de botões responsivo"""

    def __init__(self, master, buttons_data, max_cols=4, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.pack(expand=True, fill="both", padx=20, pady=20)

        self.buttons_data = buttons_data
        self.max_cols = max_cols
        self.current_cols = max_cols

        self.create_grid()
        self.bind("<Configure>", self._adjust_grid)

    def create_grid(self):
        """Cria a grade de botões"""
        for widget in self.winfo_children():
            widget.destroy()

        for i, btn_data in enumerate(self.buttons_data):
            row = i // self.current_cols
            col = i % self.current_cols

            btn = ModernButton(
                self,
                text=btn_data.get("text", ""),
                command=btn_data.get("command"),
                style=btn_data.get("style", "primary"),
                width=200,
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

        for col in range(self.current_cols):
            self.grid_columnconfigure(col, weight=1)

    def _adjust_grid(self, event):
        """Ajusta número de colunas baseado na largura"""
        if event.widget == self:
            width = event.width
            btn_width = 220
            new_cols = max(1, min(self.max_cols, width // btn_width))

            if new_cols != self.current_cols:
                self.current_cols = new_cols
                self.create_grid()
