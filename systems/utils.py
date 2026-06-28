"""
systems/utils.py — Shared utility functions used across the whole project.

Covers:
  • Text wrapping
  • Generic panel / block drawing helpers
  • Pre-baked surface generators (floor, vignette, circle masks)
"""
from __future__ import annotations

import pygame
from settings import (
    GAME_W, GAME_H,
    FLOOR_BG, FLOOR_BORDER_BG, FLOOR_BORDER_STROKE, GRID_LINE,
    PANEL, DIM, PAPER, TEXT, ACCENT, BLACK,
)


# ── Text ──────────────────────────────────────────────────────────────────────

def wrap_text(text: str, fnt: pygame.font.Font, max_width: int) -> list[str]:
    """Word-wrap *text* (honouring explicit \\n breaks) to fit *max_width* px."""
    lines = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            lines.append("")
            continue
        words = paragraph.split(" ")
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if fnt.size(test)[0] <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


# ── Drawing helpers ───────────────────────────────────────────────────────────

def draw_panel_box(
    surf: pygame.Surface,
    rect_: pygame.Rect,
    fill: tuple,
    border_color: tuple | None = None,
    border_w: int = 1,
    accent_left: tuple | None = None,
    accent_w: int = 4,
) -> None:
    """Fill a rect, draw an optional left accent stripe and border."""
    pygame.draw.rect(surf, fill, rect_)
    if accent_left:
        pygame.draw.rect(surf, accent_left, (rect_.x, rect_.y, accent_w, rect_.height))
    if border_color:
        pygame.draw.rect(surf, border_color, rect_, border_w)


def draw_block(
    surf: pygame.Surface,
    x: int, y: int, w: int, h: int,
    color: tuple,
    label: str | None = None,
    label_font: pygame.font.Font | None = None,
) -> None:
    """Draw a coloured rectangle with a soft drop-shadow and optional label."""
    # shadow
    shadow = pygame.Surface((w, 10), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 90))
    surf.blit(shadow, (x + 6, y + h - 6))
    # body
    pygame.draw.rect(surf, color, (x, y, w, h))
    # subtle highlight border
    border = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(border, (255, 255, 255, 18), border.get_rect(), 1)
    surf.blit(border, (x, y))
    # label
    if label and label_font:
        t = label_font.render(label, True, (255, 255, 255))
        t.set_alpha(140)
        surf.blit(t, (x + 8, y + 4))


def kbd_box_surface(kbd_text_surf: pygame.Surface, box_rect: pygame.Rect) -> pygame.Surface:
    """Return a small keyboard-key surface (black + accent border)."""
    surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(surf, BLACK, surf.get_rect())
    pygame.draw.rect(surf, ACCENT, surf.get_rect(), 1)
    surf.blit(
        kbd_text_surf,
        (
            (box_rect.width  - kbd_text_surf.get_width())  // 2,
            (box_rect.height - kbd_text_surf.get_height()) // 2,
        ),
    )
    return surf


# ── Pre-baked surfaces ────────────────────────────────────────────────────────

def precompute_floor_surface() -> pygame.Surface:
    """Build the static grid floor once; blit every frame."""
    surf = pygame.Surface((GAME_W, GAME_H))
    surf.fill(FLOOR_BG)

    grid = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
    x = 40
    while x < GAME_W - 40:
        pygame.draw.line(grid, GRID_LINE, (x, 40), (x, GAME_H - 40), 1)
        x += 64
    y = 40
    while y < GAME_H - 40:
        pygame.draw.line(grid, GRID_LINE, (40, y), (GAME_W - 40, y), 1)
        y += 64
    surf.blit(grid, (0, 0))

    pygame.draw.rect(surf, FLOOR_BORDER_BG, (0, 0, GAME_W, 150))        # top wall — was 40
    pygame.draw.rect(surf, FLOOR_BORDER_BG, (0, GAME_H - 40, GAME_W, 40))
    pygame.draw.rect(surf, FLOOR_BORDER_BG, (0, 0, 40, GAME_H))
    pygame.draw.rect(surf, FLOOR_BORDER_BG, (GAME_W - 40, 0, 40, GAME_H))
    pygame.draw.rect(surf, FLOOR_BORDER_STROKE, (2, 2, GAME_W - 4, GAME_H - 4), 2)
    return surf


def make_circle_mask(radius: int) -> pygame.Surface:
    """White filled circle (alpha=255) on transparent bg for BLEND_RGBA_MULT clipping."""
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 255, 255, 255), (radius, radius), radius)
    return surf


def make_vignette_sprite(
    radius_inner: int = 40,
    radius_outer: int = 420,
    max_alpha: int = 127,
) -> pygame.Surface:
    """
    Radial 'darkness subtraction' sprite.

    Combined with a flat dark overlay and BLEND_RGBA_SUB this reproduces
    the torchlight vignette from the original JS version.
    """
    size = radius_outer * 2 + 20
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    center = size // 2
    r = radius_outer
    while r >= 0:
        d = r
        if d <= radius_inner:
            a = max_alpha
        elif d >= radius_outer:
            a = 0
        else:
            a = max_alpha * (1 - (d - radius_inner) / (radius_outer - radius_inner))
        a = max(0, min(max_alpha, int(a)))
        pygame.draw.circle(surf, (0, 0, 0, a), (center, center), r)
        r -= 2
    return surf
