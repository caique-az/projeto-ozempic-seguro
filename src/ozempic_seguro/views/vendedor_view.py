"""
Vendor view - allows only opening drawers.
"""
from .base_user_view import BaseUserFrame


class VendedorFrame(BaseUserFrame):
    """Frame for vendor type users."""

    TITLE = "Vendedor"
    USER_TYPE = "vendedor"
