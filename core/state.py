"""
core/state.py — All mutable runtime state, collected in one place.

GameState is instantiated once by Game and passed (by reference) into
every system, scene, and overlay that needs to read or write it.
No logic lives here — it is a pure data container.
"""

from __future__ import annotations
import pygame

from settings import GAME_W, GAME_H, SCALE_X, SCALE_Y, DIM
from entities.player import Player
from entities.rain import make_rain
from systems.utils import (
    precompute_floor_surface,
    make_vignette_sprite,
    make_circle_mask,
)
from data.rooms import ROOM_A


class GameState:
    def __init__(self):
        # ── Display ───────────────────────────────────────────────────────────
        self.screen: pygame.Surface = None   # set by Game.__init__
        self.surf   = pygame.Surface((GAME_W, GAME_H))

        # ── Pre-baked surfaces ────────────────────────────────────────────────
        self.floor_surface  = precompute_floor_surface()
        self.vignette_sprite= make_vignette_sprite()
        self.mag_mask       = make_circle_mask(70)
        self.uv_mask        = make_circle_mask(90)

        # ── Initial State ─────────────────────────────────────────────────────
        self.reset()
        
        # ── Flags (Now correctly indented inside __init__) ───────────────────
        self.flags: dict = {
            "readNewspaper": False,
            "sawWhiteboard": False,
            "sawDesk":       False,
            "doorUnlocked":  False,
            "foundCassette": False,
            "foundDocs":     False,
            
            "uvFound":       set(),
            "evidenceCount": 0,
            "photoSolved":   False,
            "docSolved":     False,
            
            "deskVerified":    False,
            "hallwayVerified": False,
            "chairVerified":   False,
            
            "theoryFormed":    False,
            "terminalUnlocked": False,
        }

        self.player = Player(x=1300.0, y=760.0)
        self.rain   = make_rain(90)

        # overlay: None | 'reading' | 'keypad' | 'tool' | 'doc' | 'end'
        self.active_overlay: str | None = None

        self.reading: dict = {"title": "", "meta": "", "body": ""}

        self.keypad: dict = {
            "code": "", "hint": "", "submit_at": None,
            "close_at": None, "clear_at": None, "shake_until": 0,
        }

        self.tool: dict = {"mode": None, "mag_idx": 0, "reveal": ""}

        self.doc_selected: set = set()
        self.doc_msg:       str  = ""
        self.doc_msg_color: tuple = DIM

        self.journal_page: int = 0

        self.flash_until: int = 0
        self.shake_until: int = 0
        self.end_card_at: int | None = None
        self.pending_cutscene = False

    def reset(self) -> None:
        """Return everything to its start-of-game defaults."""
        self.phase        = "menu"
        self.current_room = ROOM_A
        self.input_locked = False

    # ── Convenience ───────────────────────────────────────────────────────────

    def get_mouse(self) -> tuple[float, float]:
        """Return mouse position scaled to internal game resolution."""
        mx, my = pygame.mouse.get_pos()
        return mx / SCALE_X, my / SCALE_Y
    