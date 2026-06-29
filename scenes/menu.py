"""
scenes/menu.py — Main menu, video intro, and story screen.

Phases:
  menu   → draw_menu / click_menu
  video  → draw_video / update_video  (plays intro_Case_redacted.mp4 with audio)
  intro  → draw_intro / click_intro   (story text, shown if video absent)
  playing → handed back to game.py

SOUND APPROACH: mirrors the working pygame version exactly.
  - moviepy extracts the audio track to temp_audio.mp3 (same as Case_redacted_pygame)
  - pygame.mixer loads and plays that mp3 alongside the video frames
  - _try_load_video() is called LAZILY from reset_video(), which runs AFTER
    pygame.init() — so pygame.surfarray and mixer are both ready.
"""
from __future__ import annotations

import os
import pygame
from settings import GAME_W, GAME_H, ACCENT, DIM, PAPER, RED, BLACK
from entities.rain import draw_rain
from systems.utils import wrap_text
from assets.fonts import font

# ── Video state ───────────────────────────────────────────────────────────────
_VIDEO_AVAILABLE  = False
_VIDEO_LOADED     = False   # True after _try_load_video() has been attempted
_video_frame_idx  = 0
_video_frames: list[pygame.Surface] = []
_VIDEO_FPS        = 24
_next_frame_at    = 0
_AUDIO_TMP        = "temp_audio.mp3"   # same filename the pygame version uses

# Video file search order
_VIDEO_CANDIDATES = [
    os.path.join("assets", "videos", "intro_Case_redacted.mp4"),
    os.path.join("assets", "videos", "intro_case_redacted.mp4"),
    os.path.join("assets", "videos", "intro_Case_redacted.avi"),
    os.path.join("assets", "videos", "intro_case_redacted.avi"),
    os.path.join("assets", "videos", "intro_Case_redacted.mov"),
    os.path.join("assets", "videos", "intro_case_redacted.mov"),
    "intro_Case_redacted.mp4",
    "intro_case_redacted.mp4",
]

_show_credits_screen = False

def _try_load_video() -> bool:
    """Load video frames and extract audio to temp_audio.mp3 via moviepy.

    MUST be called after pygame.init() — pygame.surfarray.make_surface()
    requires pygame to be initialised.  Call via reset_video(), never at
    module import time.
    """
    global _VIDEO_AVAILABLE, _VIDEO_LOADED, _video_frames, _VIDEO_FPS
    _VIDEO_LOADED = True

    try:
        from moviepy.editor import VideoFileClip
        import numpy as np
        import cv2

        for path in _VIDEO_CANDIDATES:
            if not os.path.exists(path):
                continue

            # ── Extract audio to mp3 (exactly like Case_redacted_pygame) ─────
            clip = VideoFileClip(path)
            if clip.audio:
                clip.audio.write_audiofile(
                    _AUDIO_TMP, verbose=False, logger=None
                )
            clip.close()

            # ── Extract frames via cv2 ────────────────────────────────────────
            cap = cv2.VideoCapture(path)
            fps_raw = cap.get(cv2.CAP_PROP_FPS)
            if fps_raw and fps_raw > 0:
                _VIDEO_FPS = fps_raw

            frames = []
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # pygame is initialised here so surfarray is safe to use
                frames.append(
                    pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                )
            cap.release()

            if not frames:
                continue

            _video_frames    = frames
            _VIDEO_AVAILABLE = True
            return True

    except Exception:
        pass

    return False


# ── Audio helpers ─────────────────────────────────────────────────────────────

def _play_video_audio() -> None:
    """Start mp3 audio playback (mirrors Case_redacted_pygame exactly)."""
    if not os.path.exists(_AUDIO_TMP):
        return
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(_AUDIO_TMP)
        pygame.mixer.music.play()
    except Exception:
        pass


def _stop_video_audio() -> None:
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except Exception:
        pass


# ── Geometry helpers ──────────────────────────────────────────────────────────

def start_button_rect() -> pygame.Rect:
    w, h = 300, 60
    return pygame.Rect(GAME_W // 2 - w // 2, 540, w, h)

def exit_button_rect() -> pygame.Rect:
    w, h = 300, 50
    return pygame.Rect(GAME_W // 2 - w // 2, 618, w, h)

def intro_skip_rect() -> pygame.Rect:
    w, h = 380, 50
    return pygame.Rect(GAME_W // 2 - w // 2, 610, w, h)

def intro_exit_rect() -> pygame.Rect:
    w, h = 280, 44
    return pygame.Rect(GAME_W // 2 - w // 2, 676, w, h)

def video_skip_rect() -> pygame.Rect:
    w, h = 240, 42
    return pygame.Rect(GAME_W - 280, GAME_H - 70, w, h)


# ── Draw ──────────────────────────────────────────────────────────────────────

def draw_menu(surf: pygame.Surface, rain: list, mouse: tuple) -> None:
    surf.fill((10, 11, 13))
    draw_rain(surf, rain)

    title_font    = font(64, bold=True)
    subtitle_font = font(16)
    btn_font      = font(20, bold=True)
    exit_font     = font(16)

    title  = title_font.render("CASE ",    True, PAPER)
    title2 = title_font.render("REDACTED", True, RED)
    total_w = title.get_width() + title2.get_width()
    tx, ty  = GAME_W // 2 - total_w // 2, 280
    surf.blit(title,  (tx, ty))
    surf.blit(title2, (tx + title.get_width(), ty))

    sub = subtitle_font.render("A 2D DETECTIVE MYSTERY", True, DIM)
    surf.blit(sub, (GAME_W // 2 - sub.get_width() // 2, ty + 82))

    btn   = start_button_rect()
    hover = btn.collidepoint(mouse)
    if hover:
        pygame.draw.rect(surf, ACCENT, btn)
        txt = btn_font.render("▶ START", True, BLACK)
    else:
        pygame.draw.rect(surf, (10, 11, 13), btn)
        pygame.draw.rect(surf, ACCENT, btn, 1)
        txt = btn_font.render("▶ START", True, ACCENT)
    surf.blit(txt, (btn.centerx - txt.get_width() // 2, btn.centery - txt.get_height() // 2))

    ebtn  = exit_button_rect()
    ehov  = ebtn.collidepoint(mouse)
    pygame.draw.rect(surf, (30, 15, 15) if ehov else (10, 11, 13), ebtn)
    pygame.draw.rect(surf, RED if ehov else (80, 40, 40), ebtn, 1)
    et = exit_font.render("EXIT", True, RED if ehov else (150, 80, 80))
    surf.blit(et, (ebtn.centerx - et.get_width() // 2, ebtn.centery - et.get_height() // 2))


def draw_video(surf: pygame.Surface, mouse: tuple) -> None:
    global _video_frame_idx, _next_frame_at
    now = pygame.time.get_ticks()
    if now >= _next_frame_at:
        _video_frame_idx += 1
        _next_frame_at    = now + int(1000 / _VIDEO_FPS)
    surf.fill(BLACK)
    if _video_frames:
        idx   = min(_video_frame_idx, len(_video_frames) - 1)
        frame = pygame.transform.smoothscale(_video_frames[idx], (GAME_W, GAME_H))
        surf.blit(frame, (0, 0))

    skip = video_skip_rect()
    hov  = skip.collidepoint(mouse)
    pygame.draw.rect(surf, (30, 30, 30) if hov else (0, 0, 0), skip)
    pygame.draw.rect(surf, PAPER if hov else DIM, skip, 1)
    t = font(16).render("SKIP  ▶▶", True, PAPER if hov else DIM)
    surf.blit(t, (skip.centerx - t.get_width() // 2, skip.centery - t.get_height() // 2))


def draw_intro(surf: pygame.Surface, mouse: tuple) -> None:
    intro_font       = font(20)
    intro_small_font = font(16)

    surf.fill(BLACK)
    l1 = intro_small_font.render("— a storm. an abandoned office. one detective. —", True, DIM)
    surf.blit(l1, (GAME_W // 2 - l1.get_width() // 2, 300))

    body = (
        "Detective Arthur Walker was found dead in his own office.\n"
        "The official report has been sealed.\n"
        "You are the one sent to find out why."
    )
    y = 390
    for line in wrap_text(body, intro_font, 680):
        t = intro_font.render(line, True, PAPER)
        surf.blit(t, (GAME_W // 2 - t.get_width() // 2, y))
        y += 38

    rect_ = intro_skip_rect()
    hover = rect_.collidepoint(mouse)
    pygame.draw.rect(surf, (30, 24, 12) if hover else BLACK, rect_)
    pygame.draw.rect(surf, ACCENT, rect_, 1)
    t = intro_small_font.render("ENTER THE OFFICE  →", True, ACCENT)
    surf.blit(t, (rect_.centerx - t.get_width() // 2, rect_.centery - t.get_height() // 2))

    erect = intro_exit_rect()
    ehov  = erect.collidepoint(mouse)
    pygame.draw.rect(surf, (25, 15, 15) if ehov else BLACK, erect)
    pygame.draw.rect(surf, (120, 50, 50) if ehov else (60, 40, 40), erect, 1)
    et = font(14).render("I'm not ready — EXIT", True, (200, 100, 100) if ehov else (140, 80, 80))
    surf.blit(et, (erect.centerx - et.get_width() // 2, erect.centery - et.get_height() // 2))


# ── Click handlers ────────────────────────────────────────────────────────────

def click_menu(pos: tuple) -> str | None:
    if start_button_rect().collidepoint(pos):
        return "video" if _VIDEO_AVAILABLE else "intro"
    if exit_button_rect().collidepoint(pos):
        return "exit"
    return None


def click_video(pos: tuple) -> str | None:
    global _video_frame_idx
    if video_skip_rect().collidepoint(pos):
        _stop_video_audio()
        return "intro"
    if _video_frames and _video_frame_idx >= len(_video_frames) - 1:
        _stop_video_audio()
        return "intro"
    return None


def video_finished() -> bool:
    finished = bool(_video_frames) and _video_frame_idx >= len(_video_frames) - 1
    if finished:
        _stop_video_audio()
    return finished

# ── Cutscene video player (case_redact_2 → case_redact_3) ────────────────────

_CUTSCENE_FRAMES: list[pygame.Surface] = []
_CUTSCENE_FPS    = 24.0
_cutscene_idx    = 0
_next_cutscene_at= 0
_cutscene_queue: list[str] = []

def _load_cutscene(filepath: str) -> bool:
    global _CUTSCENE_FRAMES, _CUTSCENE_FPS, _cutscene_idx, _next_cutscene_at
    _CUTSCENE_FRAMES = []
    _cutscene_idx    = 0
    _next_cutscene_at= 0
    try:
        import cv2

        # ── Extract audio using unique filename ───────────────────
        audio_tmp = filepath.replace(".mp4", "_audio.mp3").replace("assets/videos/", "")
        try:
            from moviepy.editor import VideoFileClip
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            clip = VideoFileClip(filepath)
            if clip.audio:
                clip.audio.write_audiofile(audio_tmp, verbose=False, logger=None)
            clip.close()
        except Exception as e:
            print(f"[cutscene] audio extract failed: {e}")
            audio_tmp = None

        # ── Extract frames via cv2 ────────────────────────────────
        cap = cv2.VideoCapture(filepath)
        fps_raw = cap.get(cv2.CAP_PROP_FPS)
        if fps_raw and fps_raw > 0:
            _CUTSCENE_FPS = fps_raw
        frames = []
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(pygame.surfarray.make_surface(frame.swapaxes(0, 1)))
        cap.release()

        if not frames:
            return False

        _CUTSCENE_FRAMES = frames

        # ── Play audio ────────────────────────────────────────────
        if audio_tmp and os.path.exists(audio_tmp):
            try:
                pygame.mixer.music.load(audio_tmp)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"[cutscene] audio play failed: {e}")

        return True
    except Exception as e:
        print(f"[cutscene] failed to load {filepath}: {e}")
        return False

def start_cutscene_queue(paths: list[str]) -> bool:
    """Load and begin playing the first video in paths; queue the rest."""
    global _cutscene_queue
    _cutscene_queue = list(paths)
    return _advance_cutscene_queue()

def _advance_cutscene_queue() -> bool:
    global _cutscene_queue
    while _cutscene_queue:
        p = _cutscene_queue.pop(0)
        if _load_cutscene(p):
            return True
    return False

def draw_cutscene(surf: pygame.Surface) -> None:
    global _cutscene_idx, _next_cutscene_at
    now = pygame.time.get_ticks()
    if now >= _next_cutscene_at:
        _cutscene_idx   += 1
        _next_cutscene_at = now + int(1000 / _CUTSCENE_FPS)
    if _CUTSCENE_FRAMES:
        idx   = min(_cutscene_idx, len(_CUTSCENE_FRAMES) - 1)
        frame = pygame.transform.smoothscale(_CUTSCENE_FRAMES[idx], (GAME_W, GAME_H))
        surf.blit(frame, (0, 0))

def cutscene_finished() -> bool:
    if not _CUTSCENE_FRAMES:
        return True
    if _cutscene_idx >= len(_CUTSCENE_FRAMES) - 1:
        if _cutscene_queue:
            pygame.mixer.music.stop()
            _advance_cutscene_queue()
            return False
        pygame.mixer.music.stop()
        return True
    return False

def click_intro(pos: tuple) -> str | None:
    if intro_skip_rect().collidepoint(pos):
        return "playing"
    if intro_exit_rect().collidepoint(pos):
        return "exit"
    return None


def reset_video() -> None:
    """Reset frame index and start audio. Called by Game after pygame.init()."""
    global _video_frame_idx, _next_frame_at
    _video_frame_idx = 0
    _next_frame_at   = 0

    # Lazy-load on first call only — pygame is guaranteed to be up by now
    if not _VIDEO_LOADED:
        _try_load_video()

    _play_video_audio()

def draw_credits_menu(surf: pygame.Surface, rain: list) -> None:
    surf.fill((10, 11, 13))
    draw_rain(surf, rain)
    title_font = font(64, bold=True)
    title  = title_font.render("CASE ",    True, PAPER)
    title2 = title_font.render("REDACTED", True, RED)
    total_w = title.get_width() + title2.get_width()
    tx = GAME_W // 2 - total_w // 2
    ty = GAME_H // 2 - title.get_height() // 2
    surf.blit(title,  (tx, ty))
    surf.blit(title2, (tx + title.get_width(), ty))