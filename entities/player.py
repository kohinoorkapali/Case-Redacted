"""
entities/player.py — Player state, movement, collision, and rendering.

The Player class is intentionally free of game-phase logic.
It receives a collision callback (can_move_fn) so it doesn't need to
import the room data directly — the Game class wires that up.
"""

import math
import pygame

from settings import PLAYER_SPEED, PLAYER_BODY, PLAYER_SKIN, PLAYER_HAIR, PLAYER_EYE

def _load_frames(sheet: pygame.Surface, row: int, num_cols: int):
    fw = sheet.get_width() // num_cols
    fh = sheet.get_height() // 4
    frames = []
    for col in range(num_cols):
        frame = pygame.Surface((fw, fh), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (col * fw, row * fh, fw, fh))
        frames.append(frame)
    return frames
class Player:
    _DIR_ROW = {"down": 0, "up": 1, "right": 2, "left": 3}

    def __init__(self, x: float = 1300.0, y: float = 760.0):
        self.x      = x
        self.y      = y
        self.w      = 96
        self.h      = 96
        self.speed  = PLAYER_SPEED
        self.dir    = "down"
        self.moving = False
        self.frame  = 0.0
        self._sprites_loaded = False
        self._walk_frames  = {}
        self._idle_frames  = {}
    

    def load_sprites(self, walk_path="assets/walk.png", idle_path="assets/idle.png"):
        walk_sheet = pygame.image.load(walk_path).convert_alpha()
        idle_sheet = pygame.image.load(idle_path).convert_alpha()
        for direction, row in self._DIR_ROW.items():
            self._walk_frames[direction] = _load_frames(walk_sheet, row, 4)
            self._idle_frames[direction] = _load_frames(idle_sheet, row, 1)
        for d in self._DIR_ROW:
            self._walk_frames[d] = [pygame.transform.scale(f, (self.w, self.h)) for f in self._walk_frames[d]]
            self._idle_frames[d] = [pygame.transform.scale(f, (self.w, self.h)) for f in self._idle_frames[d]]
        self._sprites_loaded = True

    # ── Movement ──────────────────────────────────────────────────────────────

    def update(self, input_locked: bool, can_move_fn) -> None:
        """Read keyboard, apply movement with collision, animate walk cycle."""
        if input_locked:
            self.moving = False
            return

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += 1
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1

        self.moving = dx != 0 or dy != 0

        # normalise diagonal speed
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        # update facing direction
        if   dx > 0: self.dir = "right"
        elif dx < 0: self.dir = "left"
        elif dy > 0: self.dir = "down"
        elif dy < 0: self.dir = "up"

        nx = self.x + dx * self.speed
        ny = self.y + dy * self.speed
        if can_move_fn(nx, self.y): self.x = nx
        if can_move_fn(self.x, ny): self.y = ny

        if self.moving:
            self.frame += 0.18

    def teleport(self, x: float, y: float) -> None:
        self.x, self.y = x, y

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    @property
    def reach_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - 18), int(self.y - 18), self.w + 36, self.h + 36)

    # ── Rendering ─────────────────────────────────────────────────────────────

    def draw(self, surf: pygame.Surface) -> None:
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2

        # drop shadow
        shadow = pygame.Surface((int(self.w * 1.2), 16), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), shadow.get_rect())
        surf.blit(shadow, (cx - shadow.get_width() / 2, self.y + self.h - 6))

        if self._sprites_loaded:
            frames = self._walk_frames[self.dir] if self.moving else self._idle_frames[self.dir]
            surf.blit(frames[int(self.frame) % len(frames)], (int(self.x), int(self.y)))
        else:
            bob = math.sin(self.frame * 6) * 2 if self.moving else 0
            pygame.draw.rect(surf, PLAYER_BODY, (self.x, self.y + 6 + bob, self.w, self.h - 10))
            pygame.draw.circle(surf, PLAYER_SKIN, (int(cx), int(self.y + 8 + bob)), 9)
            pygame.draw.rect(surf, PLAYER_HAIR, (cx - 11, self.y - 2 + bob, 22, 6))
            pygame.draw.rect(surf, PLAYER_HAIR, (cx - 7,  self.y - 7 + bob, 14, 6))
            lx, ly = cx, cy
            if   self.dir == "up":    ly -= 16
            elif self.dir == "down":  ly += 16
            elif self.dir == "left":  lx -= 16
            elif self.dir == "right": lx += 16
            pygame.draw.circle(surf, PLAYER_EYE, (int(lx), int(ly)), 3)
