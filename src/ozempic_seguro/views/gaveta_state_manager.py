"""
Módulo de compatibilidade para GavetaStateManager.

DEPRECATED: Use services.gaveta_service.GavetaService diretamente.
"""

from ..services.gaveta_service import GavetaService

# Re-export para compatibilidade
GavetaStateManager = GavetaService
