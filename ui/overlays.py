"""
ui/overlays.py — All overlay / panel draw functions.
"""
from __future__ import annotations

import math
import random
import pygame

from settings import (
    GAME_W, GAME_H,
    PANEL, PANEL2, ACCENT, ACCENT2, RED, DIM, PAPER, TEXT, BLACK,
)
from data.puzzle_data import (
    TOOL_RECT, MAG_IMAGES, UV_SPOTS, DOC_LINES, KEYPAD_KEYS, JOURNAL_PAGES,
)
from systems.utils import draw_panel_box, wrap_text
from assets.fonts import font


# ── Shared scrim ──────────────────────────────────────────────────────────────

def _scrim(surf: pygame.Surface, alpha: int = 240) -> None:
    s = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
    s.fill((2, 2, 3, alpha))
    surf.blit(s, (0, 0))


# ── Reading panel ─────────────────────────────────────────────────────────────

def draw_reading_panel(surf: pygame.Surface, state) -> None:
    _scrim(surf)
    panel = pygame.Rect(GAME_W // 2 - 380, 130, 760, 560)
    draw_panel_box(surf, panel, PANEL, border_color=(51, 54, 61), accent_left=ACCENT)

    f_title = font(24, bold=True)   # bigger
    f_meta  = font(15)              # bigger
    f_body  = font(19)              # bigger
    f_close = font(16, bold=True)   # bigger

    title = f_title.render(state.reading["title"], True, ACCENT)
    surf.blit(title, (panel.x + 36, panel.y + 28))
    meta = f_meta.render(state.reading["meta"], True, DIM)
    surf.blit(meta, (panel.x + 36, panel.y + 28 + title.get_height() + 8))

    body_y = panel.y + 28 + title.get_height() + 8 + meta.get_height() + 22
    for line in wrap_text(state.reading["body"], f_body, panel.width - 72):
        t = f_body.render(line, True, PAPER)
        surf.blit(t, (panel.x + 36, body_y))
        body_y += 32

    close_btn = pygame.Rect(panel.x + 36, panel.bottom - 76, 180, 44)
    mouse     = state.get_mouse()
    hover     = close_btn.collidepoint(mouse)
    pygame.draw.rect(surf, (40, 40, 42) if hover else PANEL, close_btn)
    pygame.draw.rect(surf, PAPER if hover else DIM, close_btn, 1)
    t = f_close.render("CLOSE [ESC]", True, PAPER if hover else TEXT)
    surf.blit(t, (close_btn.centerx - t.get_width() // 2, close_btn.centery - t.get_height() // 2))


# ── Keypad ────────────────────────────────────────────────────────────────────

def keypad_button_layout() -> list[tuple[str, pygame.Rect]]:
    cols, rows  = 3, 4
    bw, bh, gap = 70, 58, 10
    grid_w      = cols * bw + (cols - 1) * gap
    ox, oy      = GAME_W // 2 - grid_w // 2, 470
    rects = []
    for i, label in enumerate(KEYPAD_KEYS):
        col = i % cols
        row = i // cols
        rects.append((label, pygame.Rect(ox + col * (bw + gap), oy + row * (bh + gap), bw, bh)))
    return rects


def draw_keypad(surf: pygame.Surface, state) -> None:
    _scrim(surf)
    kp    = state.keypad
    panel = pygame.Rect(GAME_W // 2 - 220, 280, 440, 510)
    draw_panel_box(surf, panel, PANEL2, border_color=(58, 62, 70))

    f_kp_title = font(20, bold=True)   # bigger
    f_code     = font(42, bold=True)   # bigger
    f_key      = font(26, bold=True)   # bigger
    f_hint     = font(16)              # bigger

    title = f_kp_title.render("LOCKED DOOR — ENTER CODE", True, ACCENT)
    surf.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 24))

    now     = pygame.time.get_ticks()
    shaking = now < kp["shake_until"]
    disp    = pygame.Rect(panel.centerx - 130, panel.y + 80, 260, 58)
    ox      = random.uniform(-8, 8) if shaking else 0
    disp.x += int(ox)
    pygame.draw.rect(surf, BLACK, disp)
    pygame.draw.rect(surf, RED if shaking else (58, 62, 70), disp, 1)
    code_str = " ".join(list((kp["code"] + "___")[:3]))
    t = f_code.render(code_str, True, PAPER)
    surf.blit(t, (disp.centerx - t.get_width() // 2, disp.centery - t.get_height() // 2))

    mouse = state.get_mouse()
    for label, rect_ in keypad_button_layout():
        hover = rect_.collidepoint(mouse)
        pygame.draw.rect(surf, (14, 16, 20), rect_)
        pygame.draw.rect(surf, ACCENT if hover else (58, 62, 70), rect_, 1)
        t = f_key.render(label, True, ACCENT if hover else PAPER)
        surf.blit(t, (rect_.centerx - t.get_width() // 2, rect_.centery - t.get_height() // 2))

    hint = f_hint.render(kp["hint"], True, DIM)
    surf.blit(hint, (panel.centerx - hint.get_width() // 2, 706))

    cancel = pygame.Rect(GAME_W // 2 - 70, 742, 140, 38)
    hover  = cancel.collidepoint(mouse)
    pygame.draw.rect(surf, (40, 40, 42) if hover else PANEL, cancel)
    pygame.draw.rect(surf, PAPER if hover else DIM, cancel, 1)
    t = font(14, bold=True).render("CANCEL [ESC]", True, PAPER if hover else TEXT)
    surf.blit(t, (cancel.centerx - t.get_width() // 2, cancel.centery - t.get_height() // 2))


# ── Tool panel (magnifier + UV) ───────────────────────────────────────────────

def tool_close_rect() -> pygame.Rect:
    return pygame.Rect(TOOL_RECT.right - 120, TOOL_RECT.top - 36, 120, 28)


def draw_tool(surf: pygame.Surface, state) -> None:
    _scrim(surf)
    pygame.draw.rect(surf, (8, 9, 11), TOOL_RECT)
    pygame.draw.rect(surf, (51, 54, 61), TOOL_RECT, 1)

    header_txt = (
        "PHOTO BOARD — MAGNIFYING GLASS"
        if state.tool["mode"] == "magnifier"
        else "UV INSPECTION DESK"
    )
    header = font(18, bold=True).render(header_txt, True, ACCENT)   # bigger
    surf.blit(header, (TOOL_RECT.x, TOOL_RECT.y - 36))

    close_btn = tool_close_rect()
    mouse     = state.get_mouse()
    hover     = close_btn.collidepoint(mouse)
    pygame.draw.rect(surf, (40, 40, 42) if hover else PANEL, close_btn)
    pygame.draw.rect(surf, PAPER if hover else DIM, close_btn, 1)
    t = font(13, bold=True).render("CLOSE [ESC]", True, PAPER if hover else TEXT)
    surf.blit(t, (close_btn.centerx - t.get_width() // 2, close_btn.centery - t.get_height() // 2))

    canvas = pygame.Surface((900, 560))
    mx = max(0, min(900, mouse[0] - TOOL_RECT.x))
    my = max(0, min(560, mouse[1] - TOOL_RECT.y))
    if state.tool["mode"] == "magnifier":
        _draw_magnifier_frame(canvas, mx, my, state)
    else:
        _draw_uv_frame(canvas, mx, my, state)
    surf.blit(canvas, TOOL_RECT.topleft)

    reveal = font(16).render(state.tool["reveal"], True, ACCENT2)   # bigger
    surf.blit(reveal, (TOOL_RECT.centerx - reveal.get_width() // 2, TOOL_RECT.bottom + 14))


# ── Magnifier images cache ─────────────────────────────────────────────────────
_mag_photo_cache: dict[int, pygame.Surface | None] = {}

def _load_mag_photo(idx: int) -> pygame.Surface | None:
    if idx in _mag_photo_cache:
        return _mag_photo_cache[idx]
    try:
        path = MAG_IMAGES[idx].get("file", "")
        if path:
            img = pygame.image.load(path).convert()
            _mag_photo_cache[idx] = img
            return img
    except Exception:
        pass
    _mag_photo_cache[idx] = None
    return None


def _draw_magnifier_frame(canvas: pygame.Surface, mx: int, my: int, state) -> None:
    canvas.fill((12, 13, 15))
    inner = pygame.Rect(60, 40, 780, 440)
    idx   = state.tool["mag_idx"] % len(MAG_IMAGES)
    data  = MAG_IMAGES[idx]

    # Try to draw the actual photo; fall back to coloured placeholder
    photo = _load_mag_photo(idx)
    if photo:
        scaled = pygame.transform.smoothscale(photo, (inner.width, inner.height))
        canvas.blit(scaled, inner.topleft)
    else:
        pygame.draw.rect(canvas, data["base"], inner)
        # Draw placeholder film-grain
        for _ in range(60):
            px = inner.x + random.uniform(0, inner.width)
            py = inner.y + random.uniform(0, inner.height)
            canvas.fill((80, 80, 80), (px, py, 2, 2))
        # Placeholder label in center
        lbl_c = font(20).render("[ " + data["label"] + " ]", True, (140, 140, 140))
        canvas.blit(lbl_c, (inner.centerx - lbl_c.get_width() // 2,
                             inner.centery - lbl_c.get_height() // 2))

    pygame.draw.rect(canvas, (51, 51, 51), inner, 1)
    lbl = font(16).render(data["label"], True, (160, 160, 160))   # bigger
    canvas.blit(lbl, (70, 48))

    # Magnifying glass circle content
    content = pygame.Surface((140, 140), pygame.SRCALPHA)
    content.fill((26, 59, 26, 255))
    pygame.draw.line(content, (153, 204, 51, 255), (0, 70),  (140, 70),  2)
    pygame.draw.line(content, (153, 204, 51, 255), (70, 0),  (70, 140), 2)
    lbl2 = font(15, bold=True).render("ANOMALY", True, (207, 238, 238))
    content.blit(lbl2, (40, 18))
    content.blit(state.mag_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    canvas.blit(content, (mx - 70, my - 70))
    pygame.draw.circle(canvas, (202, 168, 107), (int(mx), int(my)), 70, 3)


def _draw_uv_frame(canvas: pygame.Surface, mx: int, my: int, state) -> None:
    canvas.fill((5, 5, 7))
    inner = pygame.Rect(60, 40, 780, 440)
    pygame.draw.rect(canvas, (34, 34, 34), inner, 1)
    pygame.draw.rect(canvas, (12, 14, 16), inner)
    lbl = font(16).render(
        "Document surface — move the UV light to reveal hidden text", True, (80, 80, 80)
    )
    canvas.blit(lbl, (70, 48))

    content = pygame.Surface((180, 180), pygame.SRCALPHA)
    content.fill((21, 5, 42, 255))
    for s in UV_SPOTS:
        d = math.hypot(mx - s["x"], my - s["y"])
        if d < 90:
            already = s["text"] in state.flags["uvFound"]
            color   = (138, 92, 255, 255) if already else (184, 140, 255, 255)
            t       = font(15, bold=True).render(s["text"], True, color)   # bigger
            local_x = (s["x"] - mx) + 90 - 70
            local_y = (s["y"] - my) + 90
            content.blit(t, (local_x, local_y))
    content.blit(state.uv_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    canvas.blit(content, (mx - 90, my - 90))
    pygame.draw.circle(canvas, (111, 168, 201), (int(mx), int(my)), 90, 2)


# ── Document puzzle panel ─────────────────────────────────────────────────────

def doc_line_layout(state) -> tuple[pygame.Rect, list]:
    panel  = pygame.Rect(GAME_W // 2 - 410, 160, 820, 560)
    f_line = font(17)   # bigger
    rects  = []
    y = panel.y + 90
    for d in DOC_LINES:
        lines = wrap_text(d["text"], f_line, panel.width - 80)
        h     = 18 + len(lines) * 24 + 8
        rects.append((d, pygame.Rect(panel.x + 36, y, panel.width - 72, h), lines))
        y += h + 8
    return panel, rects


def draw_doc_panel(surf: pygame.Surface, state) -> None:
    _scrim(surf)
    panel, rects = doc_line_layout(state)
    draw_panel_box(surf, panel, PANEL, border_color=(51, 54, 61), accent_left=ACCENT2)

    f_title = font(22, bold=True)   # bigger
    f_meta  = font(14)              # bigger
    f_line  = font(17)              # bigger
    f_msg   = font(15)              # bigger

    title = f_title.render("DOCUMENT FILES — SELECT THE TRUTH", True, ACCENT2)
    surf.blit(title, (panel.x + 36, panel.y + 24))
    meta = f_meta.render(
        "Choose the 3 lines that form a consistent account. Click to select, click again to deselect.",
        True, DIM,
    )
    surf.blit(meta, (panel.x + 36, panel.y + 24 + title.get_height() + 6))

    mouse = state.get_mouse()
    for d, rect_, lines in rects:
        selected = d["id"] in state.doc_selected
        hover    = rect_.collidepoint(mouse)
        if selected:
            bg = pygame.Surface(rect_.size, pygame.SRCALPHA)
            bg.fill((111, 168, 201, 30))
            surf.blit(bg, rect_.topleft)
        border_color = ACCENT2 if (selected or hover) else (51, 54, 61)
        pygame.draw.rect(surf, border_color, rect_, 1)
        ty = rect_.y + 10
        for line in lines:
            t = f_line.render(line, True, PAPER if selected else TEXT)
            surf.blit(t, (rect_.x + 14, ty))
            ty += 24

    submit = pygame.Rect(panel.x + 36, panel.bottom - 70, 260, 44)
    hover  = submit.collidepoint(mouse)
    pygame.draw.rect(surf, (40, 40, 30) if hover else PANEL, submit)
    pygame.draw.rect(surf, ACCENT, submit, 1)
    t = font(15, bold=True).render("CONFIRM SELECTION", True, ACCENT)
    surf.blit(t, (submit.centerx - t.get_width() // 2, submit.centery - t.get_height() // 2))

    if state.doc_msg:
        my_ = submit.bottom + 10
        for line in wrap_text(state.doc_msg, f_msg, panel.width - 72):
            t = f_msg.render(line, True, state.doc_msg_color)
            surf.blit(t, (panel.x + 36, my_))
            my_ += 22


# ── Journal overlay ───────────────────────────────────────────────────────────

def journal_nav_rects() -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
    """Return (prev_rect, next_rect, close_rect)."""
    prev  = pygame.Rect(GAME_W // 2 - 410 + 36,     730, 130, 44)
    next_ = pygame.Rect(GAME_W // 2 + 410 - 36 - 130, 730, 130, 44)
    close = pygame.Rect(GAME_W // 2 - 65,            730,  130, 44)
    return prev, next_, close


def draw_journal(surf: pygame.Surface, state) -> None:
    _scrim(surf)
    panel = pygame.Rect(GAME_W // 2 - 410, 120, 820, 640)
    draw_panel_box(surf, panel, (18, 16, 12), border_color=(90, 75, 50), accent_left=(160, 130, 70))

    page_idx = state.journal_page
    page     = JOURNAL_PAGES[page_idx]
    total    = len(JOURNAL_PAGES)
    is_last  = page.get("is_last", False)

    f_header = font(14)
    f_day    = font(28, bold=True)    # bigger
    f_body   = font(20)               # bigger
    f_nav    = font(16, bold=True)    # bigger
    f_page   = font(14)

    # Header
    hdr = f_header.render("ARTHUR WALKER'S JOURNAL", True, (140, 115, 65))
    surf.blit(hdr, (panel.x + 36, panel.y + 18))
    pygame.draw.line(surf, (90, 75, 50), (panel.x + 36, panel.y + 44), (panel.right - 36, panel.y + 44), 1)

    # Day heading
    day_txt = f_day.render(page["day"], True, (220, 195, 130))
    surf.blit(day_txt, (panel.x + 36, panel.y + 58))

    # Body text
    body_y = panel.y + 58 + day_txt.get_height() + 18
    for line in wrap_text(page["text"], f_body, panel.width - 72):
        t = f_body.render(line, True, (210, 200, 175))
        surf.blit(t, (panel.x + 36, body_y))
        body_y += 34

    if is_last:
        note = f_header.render("— written the night Arthur died", True, (140, 100, 80))
        surf.blit(note, (panel.x + 36, body_y + 14))

    # Page indicator
    pg = f_page.render(f"Page {page_idx + 1} / {total}", True, (100, 90, 65))
    surf.blit(pg, (panel.centerx - pg.get_width() // 2, panel.bottom - 70))

    # Nav buttons
    prev_r, next_r, close_r = journal_nav_rects()
    mouse = state.get_mouse()

    def _nav_btn(rect_, label, enabled):
        hov = rect_.collidepoint(mouse) and enabled
        col_bg = (40, 35, 20) if hov else (18, 16, 12)
        col_bd = (180, 150, 80) if (hov and enabled) else ((80, 68, 44) if enabled else (40, 38, 32))
        col_tx = (220, 190, 100) if (hov and enabled) else ((140, 120, 70) if enabled else (60, 58, 48))
        pygame.draw.rect(surf, col_bg, rect_)
        pygame.draw.rect(surf, col_bd, rect_, 1)
        t = f_nav.render(label, True, col_tx)
        surf.blit(t, (rect_.centerx - t.get_width() // 2, rect_.centery - t.get_height() // 2))

    _nav_btn(prev_r,  "◀ PREV",   page_idx > 0)
    _nav_btn(close_r, "CLOSE",    True)
    _nav_btn(next_r,  "NEXT ▶",   page_idx < total - 1)


# ── End card ──────────────────────────────────────────────────────────────────

def draw_end_card(surf: pygame.Surface, state) -> None:
    _scrim(surf, alpha=250)
    f_big  = font(60, bold=True)   # bigger
    f_body = font(19)              # bigger

    t1 = f_big.render("TO BE CONTINUED", True, ACCENT)
    surf.blit(t1, (GAME_W // 2 - t1.get_width() // 2, 330))

    body = (
        "Arthur reopened the case alone, the night someone else came for the file. "
        "The numbers were never just a filing system — they were the key.\n\n"
        "Click anywhere or press ESC to keep investigating."
    )
    y = 440
    for line in wrap_text(body, f_body, 720):
        t = f_body.render(line, True, PAPER)
        surf.blit(t, (GAME_W // 2 - t.get_width() // 2, y))
        y += 34
