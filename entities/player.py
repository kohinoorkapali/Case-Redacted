"""
entities/player.py — Player state, movement, collision, and rendering.
"""

import math
import pygame
from settings import PLAYER_SPEED

class Player:
    def __init__(self, x: float = 1300.0, y: float = 760.0):
        self.x      = x
        self.y      = y
        self.w      = 40 
        self.h      = 60 
        self.speed  = PLAYER_SPEED
        self.dir    = "down"
        self.moving = False
        self.frame  = 0.0

    # ── Movement ──────────────────────────────────────────────────────────────

    def update(self, input_locked: bool, can_move_fn) -> None:
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

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        if   dx > 0: self.dir = "right"
        elif dx < 0: self.dir = "left"
        elif dy > 0: self.dir = "down"
        elif dy < 0: self.dir = "up"

        nx = self.x + dx * self.speed
        ny = self.y + dy * self.speed
        if can_move_fn(nx, self.y): self.x = nx
        if can_move_fn(self.x, ny): self.y = ny

        if self.moving:
            self.frame += 0.2

    @property
    def reach_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - 18), int(self.y - 18), self.w + 36, self.h + 36)
    
    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    # ── Rendering ─────────────────────────────────────────────────────────────

    def draw(self, surf: pygame.Surface) -> None:
        # 1. Bigger Surface (Increased size by 1.5x)
        self.w, self.h = 60, 90 
        char_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        
        # 2. Animation Math
        bob = math.sin(self.frame * 5) * 4 if self.moving else 0
        leg_spread = math.sin(self.frame * 5) * 12 if self.moving else 0
        
        # 3. Shadow
        pygame.draw.ellipse(char_surf, (0, 0, 0, 60), (10, self.h - 10, self.w - 20, 8))
        
        # 4. Legs
        leg_color = (40, 35, 30)
        pygame.draw.line(char_surf, leg_color, (self.w // 2 - 8, self.h - 25 + bob), (self.w // 2 - 8 + leg_spread, self.h - 5), 6)
        pygame.draw.line(char_surf, leg_color, (self.w // 2 + 8, self.h - 25 + bob), (self.w // 2 + 8 - leg_spread, self.h - 5), 6)
        
        # 5. Torso (Trench coat)
        pygame.draw.rect(char_surf, (70, 60, 50), (12, 25 + bob, self.w - 24, self.h - 50), border_radius=8)
        
        # 6. Arms
        arm_color = (60, 50, 40)
        pygame.draw.line(char_surf, arm_color, (12, 30 + bob), (5, 50 + bob), 5)
        pygame.draw.line(char_surf, arm_color, (self.w - 12, 30 + bob), (self.w - 5, 50 + bob), 5)
        
        # 7. Head
        pygame.draw.circle(char_surf, (255, 220, 180), (self.w // 2, 25 + bob), 15)
        
        # 8. Fedora
        pygame.draw.ellipse(char_surf, (40, 40, 40), (self.w // 2 - 20, 10 + bob, 40, 10))
        pygame.draw.rect(char_surf, (50, 50, 50), (self.w // 2 - 12, 2 + bob, 24, 10), border_radius=4)
        
        # 9. TWO EYES (Dynamic based on direction)
        eye_y = 25 + bob
        eye_offset = 6 # Distance between eyes
        if self.dir == "up":
            pass # Eyes hidden by hat brim
        elif self.dir == "left":
            pygame.draw.circle(char_surf, (20, 20, 20), (self.w // 2 - 8, eye_y), 3)
        elif self.dir == "right":
            pygame.draw.circle(char_surf, (20, 20, 20), (self.w // 2 + 8, eye_y), 3)
        else: # Down/Forward
            pygame.draw.circle(char_surf, (20, 20, 20), (self.w // 2 - 6, eye_y), 3)
            pygame.draw.circle(char_surf, (20, 20, 20), (self.w // 2 + 6, eye_y), 3)
        
        # 10. Draw to main screen
        surf.blit(char_surf, (int(self.x), int(self.y)))