"""
Repositor view - allows opening and closing drawers.
"""

from .base_user_view import BaseUserFrame
from .components import GavetaButton


class RepositorFrame(BaseUserFrame):
    """Frame for repositor type users."""

    TITLE = "Repositor"
    USER_TYPE = "repositor"

    def show_drawer_history(self, gaveta_id):
        """Shows the history of a specific drawer"""
        button = GavetaButton(
            self,
            text=gaveta_id,
            command=None,
            name="gaveta_black.png",
            user_type=self.USER_TYPE,
        )
        button.show_history()
        button.destroy()
