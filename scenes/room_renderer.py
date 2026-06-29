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

from os import path

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

_DESK_IMGS = {}
_ASSET_IMGS = {}
_SOFA_IMGS = {}
_PLANT_IMGS = {}

def _get_desk(variant: str):
    if variant not in _DESK_IMGS:
        sheet = pygame.image.load("assets/images/computer_desk.png").convert_alpha()
        sw = sheet.get_width() // 2
        sh = sheet.get_height() // 2
        coords = {
            "top_left":     (0,  0),
            "top_right":    (sw, 0),
            "bottom_left":  (0,  sh),
            "bottom_right": (sw, sh),
        }
        cx, cy = coords[variant]
        frame = pygame.Surface((sw, sh), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (cx, cy, sw, sh))
        _DESK_IMGS[variant] = pygame.transform.scale(frame, (200, 180))
    return _DESK_IMGS[variant]

def _get_asset(name: str, w: int, h: int):
    key = (name, w, h)
    if key not in _ASSET_IMGS:
        path = f"assets/images/{name}" if "." in name else f"assets/images/{name}.png"
        img = pygame.image.load(path).convert_alpha()
        # Scale to height, preserve aspect ratio
        orig_w, orig_h = img.get_size()
        scale = h / orig_h
        new_w = int(orig_w * scale)
        _ASSET_IMGS[key] = pygame.transform.scale(img, (new_w, h))
    return _ASSET_IMGS[key]

def _get_sofa(variant: str):
    if variant not in _SOFA_IMGS:
        sheet = pygame.image.load("assets/images/sofa.png").convert_alpha()
        sw = sheet.get_width() // 2
        sh = sheet.get_height()
        col = 0 if variant == "down" else 1
        frame = pygame.Surface((sw, sh), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (col * sw, 0, sw, sh))
        _SOFA_IMGS[variant] = pygame.transform.scale(frame, (280, int(sh * 280 / sw)))
    return _SOFA_IMGS[variant]

def _get_plant(index: int):
    if index not in _PLANT_IMGS:
        sheet = pygame.image.load("assets/images/plants.png").convert_alpha()
        sw = sheet.get_width() // 6
        sh = sheet.get_height()
        frame = pygame.Surface((sw, sh), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (index * sw, 0, sw, sh))
        frame.set_colorkey(frame.get_at((0, 0)))
        _PLANT_IMGS[index] = pygame.transform.scale(frame, (60, 160))
    return _PLANT_IMGS[index]

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
    sofa_down_drawn = False
    for d in state.current_room.get("deco", []):
        if d["label"] == "Computer Desk":
            surf.blit(_get_desk("top_left"), (d["x"], d["y"]))
        elif d["label"] == "File Cabinets":
            surf.blit(_get_asset("file_cabinet", 240, 220), (d["x"], d["y"]))
        elif d["label"] == "Water Cooler":
            surf.blit(_get_asset("water_cooler", d["w"], d["h"]), (d["x"], d["y"]))
        elif d["label"] == "Printer":
            surf.blit(_get_asset("printer", d["w"], d["h"]), (d["x"], d["y"]))
        elif d["label"] == "Sofa":
            variant = "down" if not sofa_down_drawn else "up"
            sofa_down_drawn = True
            surf.blit(_get_sofa(variant), (d["x"], d["y"]))
        elif d["label"] == "Coffee Station":
            surf.blit(_get_asset("coffee.png", d["w"], d["h"]), (d["x"], d["y"]))
        elif d["label"] == "Plant":
            surf.blit(_get_plant(d["variant"]), (d["x"], d["y"]))
        elif d["label"] == "Stacked Boxes":
            surf.blit(_get_asset("stacked_boxes.png", d["w"], d["h"]), (d["x"], d["y"]))
        elif d["label"] == "AC Side":
            surf.blit(_get_asset("side.png", d["w"], d["h"]), (d["x"], d["y"]))
        elif d["label"] == "AC":
            surf.blit(_get_asset("Ac.png", d["w"], d["h"]), (d["x"], d["y"]))
        elif d["label"] == "Locker":
            surf.blit(_get_asset("locker.png", d["w"], d["h"]), (d["x"], d["y"]))
        elif d["label"] == "Small Locker":
            surf.blit(_get_asset("small_locker.png", d["w"], d["h"]), (d["x"], d["y"]))
        else:
            draw_block(surf, d["x"], d["y"], d["w"], d["h"], d["color"], d["label"], lbl_font)

    # Extra desks only in Room A
    if state.current_room is ROOM_A:
        surf.blit(_get_desk("bottom_right"), (200, 90))
        surf.blit(_get_desk("top_right"),    (325, 80))

        _dark = pygame.Surface((475, 180), pygame.SRCALPHA)
        _dark.fill((0, 0, 0, 40))
        surf.blit(_dark, (50, 40))


def _draw_objects(surf: pygame.Surface, state) -> None:
    lbl_font = font(12)
    for o in state.current_room["objects"]:
        if o["kind"] == "whiteboard":
            surf.blit(_get_asset("whiteboard", 660, 120), (o["x"], o["y"]))
        elif o["id"] in ("cabinet1", "cabinet2"):
            surf.blit(_get_asset("file_cabinet", o["w"], o["h"]), (o["x"], o["y"]))
        elif o["id"] == "newspaper":
            surf.blit(_get_asset("newspaper_2.png", o["w"], o["h"]), (o["x"], o["y"]))
        elif o["id"] == "desk":
            img = _get_asset("authur_chair.png", o["w"], o["h"])
            scaled = pygame.transform.scale(img, (int(img.get_width() * 1.5), int(img.get_height() * 1.5)))
            surf.blit(scaled, (o["x"], o["y"] - 40))
        elif o["id"] == "terminal":
            surf.blit(_get_asset("broken_terminal.png", o["w"], o["h"]), (o["x"], o["y"]))
        elif o["id"] == "photoboard":
            surf.blit(_get_asset("Magnifier.png", o["w"], o["h"]), (o["x"], o["y"]))
        elif o["id"] == "uvdesk":
            surf.blit(_get_asset("uv-desk.png", o["w"], o["h"]), (o["x"], o["y"]))
        elif o["id"] == "cassette":
            surf.blit(_get_asset("cassete_desk.png", o["w"], o["h"]), (o["x"], o["y"]))
        elif o["id"] == "docfiles":
            surf.blit(_get_asset("scattere_table.png", o["w"], o["h"]), (o["x"], o["y"]))
        else:
            draw_block(surf, o["x"], o["y"], o["w"], o["h"], o["color"], o["label"], lbl_font)
        if o["id"] == "desk" and not state.flags["doorUnlocked"]:
            t = font(11).render("journal", True, (202, 162, 75))
            surf.blit(t, (o["x"] + 8, o["y"] + 14))


# def _draw_whiteboard_doodles(surf: pygame.Surface, o: dict) -> None:
#     col = (34, 34, 34)
#     pygame.draw.circle(surf, col, (o["x"] + 60, o["y"] + 70), 16, 1)
#     pygame.draw.rect(surf,   col, (o["x"] + 150, o["y"] + 55, 30, 30), 1)
#     pygame.draw.polygon(surf, col, [
#         (o["x"] + 250, o["y"] + 90),
#         (o["x"] + 280, o["y"] + 50),
#         (o["x"] + 310, o["y"] + 90),
#     ], 1)
#     pygame.draw.line(surf, col, (o["x"] + 76, o["y"] + 70), (o["x"] + 150, o["y"] + 70), 1)
#     pygame.draw.line(surf, col, (o["x"] + 180, o["y"] + 70), (o["x"] + 265, o["y"] + 75), 1)


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
