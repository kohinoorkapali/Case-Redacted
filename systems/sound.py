"""
systems/sound.py — Centralized SFX loading and playback.
"""
from __future__ import annotations
import pygame

_SFX_DIR = "assets/sfx"

_FILES = {
    "click":      "click.mp3",
    "confirm":    "confirm.wav",
    "error":      "error.mp3",
    "dooropen":   "dooropen.wav",
    "newspaper":  "newspaper.mp3",
    "magnifier":  "magnifier.wav",
    "static":     "Static.mp3",
    "journal":    "journal.mp3",
}

_cache: dict[str, pygame.mixer.Sound | None] = {}
_static_channel: pygame.mixer.Channel | None = None
_journal_channel: pygame.mixer.Channel | None = None


def _load(name: str) -> pygame.mixer.Sound | None:
    if name in _cache:
        return _cache[name]
    path = f"{_SFX_DIR}/{_FILES[name]}"
    snd = None
    try:
        snd = pygame.mixer.Sound(path)
    except Exception as e:
        print(f"[sound] failed to load {path!r}: {e}")
    _cache[name] = snd
    return snd


def play(name: str, volume: float = 1.0) -> None:
    """Fire-and-forget one-shot sound effect."""
    snd = _load(name)
    if snd:
        snd.set_volume(volume)
        snd.play()


def start_loop(name: str, volume: float = 0.5) -> None:
    """Start a looping sound on its own channel (e.g. UV static)."""
    global _static_channel
    snd = _load(name)
    if not snd:
        return
    if _static_channel is None:
        _static_channel = pygame.mixer.Channel(7)
    snd.set_volume(volume)
    _static_channel.play(snd, loops=-1)


def stop_loop() -> None:
    global _static_channel
    if _static_channel is not None:
        _static_channel.stop()


def play_once_on_channel(name: str, channel_id: int, volume: float = 1.0) -> None:
    """Play a one-shot sound on a specific channel, so it can be stopped later."""
    global _journal_channel
    snd = _load(name)
    if not snd:
        return
    ch = pygame.mixer.Channel(channel_id)
    ch.set_volume(volume)
    ch.play(snd)
    if channel_id == 6:
        _journal_channel = ch


def stop_journal() -> None:
    global _journal_channel
    if _journal_channel is not None:
        _journal_channel.stop()