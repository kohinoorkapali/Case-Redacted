"""
scenes/room_renderer.py — Draws the game world for a given room.

Responsibilities:
  • Floor, decorations, objects, door
  • Player vignette / torch light
  • HUD (room name, tracker, controls hint)
  • Interaction prompt ("E  label")

All draw_* functions take (surf, state) where *state* is the GameState
dataclass defined in core/state.py — no direct Game references here.
"""

import pygame
from settings import (
    GAME_W, GAME_H,
    ACCENT, ACCENT2, DIM, PAPER, TEXT, BLACK,
    DOOR_UNLOCKED_FILL, DOOR_UNLOCKED_STROKE,
    DOOR_LOCKED_FILL, DOOR_LOCKED_STROKE,
)
from data.rooms import ROOM_A
from data.puzzle_data import TRACKER_ITEMS
from systems.utils import draw_block, draw_panel_box, kbd_box_surface, wrap_text
from assets.fonts import font


def draw_room(surf: pygame.Surface, state) -> None:
    """Top-level call: floor → deco → door → objects → player → vignette."""
    surf.blit(state.floor_surface, (0, 0))
    _draw_deco(surf, state)
    _draw_door(surf, state)
    _draw_objects(surf, state)
    state.player.draw(surf)
    _draw_vignette(surf, state)


def draw_hud(surf: pygame.Surface, state) -> None:
    room_label_font = font(16, bold=True)
    sub_font        = font(12)
    tracker_font    = font(13)

    tag = room_label_font.render(state.current_room["name"], True, ACCENT)
    sub = sub_font.render("CASE REDACTED", True, DIM)
    surf.blit(tag, (26, 18))
    surf.blit(sub, (26, 18 + tag.get_height() + 2))

    y = 18
    for flag_name, label in TRACKER_ITEMS:
        done   = state.flags[flag_name]
        prefix = "\u25cf " if done else "\u25cb "
        color  = ACCENT2 if done else DIM
        t = tracker_font.render(prefix + label, True, color)
        surf.blit(t, (GAME_W - 26 - t.get_width(), y))
        y += t.get_height() + 4

    hint = font(12).render("WASD/Arrows: Move   E: Interact   ESC: Close", True, DIM)
    surf.blit(hint, (26, GAME_H - 30))


def draw_prompt(surf: pygame.Surface, state, nearby_obj) -> None:
    if state.input_locked or nearby_obj is None:
        return

    kbd_font    = font(14, bold=True)
    prompt_font = font(16)

    label   = nearby_obj.get("label", "Inspect")
    kbd     = kbd_font.render("E", True, ACCENT)
    txt     = prompt_font.render(label, True, PAPER)
    pad_x, pad_y, gap = 22, 10, 12

    kbd_box = pygame.Rect(0, 0, kbd.get_width() + 14, kbd.get_height() + 8)
    total_w = kbd_box.width + gap + txt.get_width() + pad_x * 2
    total_h = max(kbd_box.height, txt.get_height()) + pad_y * 2
    box     = pygame.Rect(GAME_W // 2 - total_w // 2, int(GAME_H * 0.92) - total_h, total_w, total_h)

    panel = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
    panel.fill((10, 11, 13, 235))
    pygame.draw.rect(panel, ACCENT, panel.get_rect(), 1)
    panel.blit(kbd_box_surface(kbd, kbd_box), (pad_x, pad_y))
    panel.blit(txt, (pad_x + kbd_box.width + gap, (panel.get_height() - txt.get_height()) // 2))
    surf.blit(panel, box.topleft)


# ── Private helpers ───────────────────────────────────────────────────────────

def _draw_deco(surf: pygame.Surface, state) -> None:
    lbl_font = font(12)
    for d in state.current_room.get("deco", []):
        draw_block(surf, d["x"], d["y"], d["w"], d["h"], d["color"], d["label"], lbl_font)


def _draw_objects(surf: pygame.Surface, state) -> None:
    lbl_font = font(12)
    for o in state.current_room["objects"]:
        draw_block(surf, o["x"], o["y"], o["w"], o["h"], o["color"], o["label"], lbl_font)
        if o["kind"] == "whiteboard":
            _draw_whiteboard_doodles(surf, o)
        if o["id"] == "desk" and not state.flags["doorUnlocked"]:
            t = font(11).render("journal", True, (202, 162, 75))
            surf.blit(t, (o["x"] + 8, o["y"] + 14))


def _draw_whiteboard_doodles(surf: pygame.Surface, o: dict) -> None:
    col = (34, 34, 34)
    pygame.draw.circle(surf, col, (o["x"] + 60, o["y"] + 70), 16, 1)
    pygame.draw.rect(surf,   col, (o["x"] + 150, o["y"] + 55, 30, 30), 1)
    pygame.draw.polygon(surf, col, [
        (o["x"] + 250, o["y"] + 90),
        (o["x"] + 280, o["y"] + 50),
        (o["x"] + 310, o["y"] + 90),
    ], 1)
    pygame.draw.line(surf, col, (o["x"] + 76, o["y"] + 70), (o["x"] + 150, o["y"] + 70), 1)
    pygame.draw.line(surf, col, (o["x"] + 180, o["y"] + 70), (o["x"] + 265, o["y"] + 75), 1)


def _draw_door(surf: pygame.Surface, state) -> None:
    d        = state.current_room["door"]
    unlocked = state.flags["doorUnlocked"] if state.current_room is ROOM_A else True
    fill     = DOOR_UNLOCKED_FILL   if unlocked else DOOR_LOCKED_FILL
    stroke   = DOOR_UNLOCKED_STROKE if unlocked else DOOR_LOCKED_STROKE
    pygame.draw.rect(surf, fill,   d)
    pygame.draw.rect(surf, stroke, d, 2)
    if not unlocked and state.current_room is ROOM_A:
        pygame.draw.circle(surf, (202, 162, 75), (d.centerx, d.centery), 5)


def _draw_vignette(surf: pygame.Surface, state) -> None:
    p  = state.player
    cx = p.x + p.w / 2
    cy = p.y + p.h / 2
    overlay = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 127))
    sw, sh = state.vignette_sprite.get_size()
    overlay.blit(state.vignette_sprite, (cx - sw / 2, cy - sh / 2),
                 special_flags=pygame.BLEND_RGBA_SUB)
    surf.blit(overlay, (0, 0))
