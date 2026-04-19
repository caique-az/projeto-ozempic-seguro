"""
Componentes UI reutilizáveis do Ozempic Seguro.

Este pacote organiza os componentes em módulos separados por funcionalidade:
- buttons: Botões modernos e especializados
- dialogs: Diálogos e notificações
- layouts: Frames e grids responsivos
- gavetas: Componentes específicos de gavetas
- keyboard: Teclado virtual
- common: Componentes comuns (Header, ImageCache)
- loading: Overlays de carregamento e splash screen
"""

# Importações para manter compatibilidade com código existente
from .buttons import FinalizarSessaoButton, ModernButton, VoltarButton
from .common import Header, ImageCache, MainButton
from .dialogs import ModernConfirmDialog, ToastNotification
from .gavetas import GavetaButton, GavetaButtonGrid
from .keyboard import TecladoVirtual
from .layouts import ResponsiveButtonGrid, ResponsiveFrame
from .loading import LoadingOverlay, SplashScreen, TransitionOverlay

__all__ = [
    # Common
    "Header",
    "ImageCache",
    "MainButton",
    # Buttons
    "ModernButton",
    "VoltarButton",
    "FinalizarSessaoButton",
    # Dialogs
    "ModernConfirmDialog",
    "ToastNotification",
    # Layouts
    "ResponsiveFrame",
    "ResponsiveButtonGrid",
    # Gavetas
    "GavetaButton",
    "GavetaButtonGrid",
    # Keyboard
    "TecladoVirtual",
    # Loading
    "LoadingOverlay",
    "SplashScreen",
    "TransitionOverlay",
]
