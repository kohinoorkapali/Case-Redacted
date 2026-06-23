"""
entities/rain.py — Rain particle system (used on the menu screen).
"""
from __future__ import annotations

import random
import pygame
from settings import GAME_W, GAME_H


class RainDrop:
    __slots__ = ("x", "y", "length", "speed")

    def __init__(self):
        self.x      = random.uniform(0, GAME_W)
        self.y      = random.uniform(-GAME_H, 0)
        self.length = random.uniform(70, 160)
        self.speed  = random.uniform(900, 1700)

    def update(self, dt: float) -> None:
        self.y += self.speed * dt
        if self.y > GAME_H:
            self.y = random.uniform(-300, -10)
            self.x = random.uniform(0, GAME_W)


def make_rain(count: int = 90) -> list[RainDrop]:
    return [RainDrop() for _ in range(count)]


def draw_rain(surf: pygame.Surface, drops: list[RainDrop]) -> None:
    color = (150, 180, 200, 90)
    for d in drops:
        line_surf = pygame.Surface((2, int(d.length)), pygame.SRCALPHA)
        pygame.draw.line(line_surf, color, (0, 0), (0, d.length), 1)
        surf.blit(line_surf, (d.x, d.y))
