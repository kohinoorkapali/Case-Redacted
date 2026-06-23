"""
assets/fonts.py — Font loading and caching.

All font sizes used in the game are initialised here through font().
Call font(size, bold=False) anywhere in the project to get a cached
pygame.font.Font object without worrying about re-loading from disk.
"""

import pygame

pygame.font.init()

_FONT_PATH = (
    pygame.font.match_font("couriernew")
    or pygame.font.match_font("monospace")
    or pygame.font.match_font("dejavusansmono")
)
_FONT_CACHE: dict = {}


def font(size: int, bold: bool = False) -> pygame.font.Font:
    """Return a cached monospace Font at *size* pixels, optionally bold."""
    key = (size, bold)
    if key not in _FONT_CACHE:
        f = pygame.font.Font(_FONT_PATH, size)
        f.set_bold(bold)
        _FONT_CACHE[key] = f
    return _FONT_CACHE[key]
