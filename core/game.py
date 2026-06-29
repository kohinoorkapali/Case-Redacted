"""
core/game.py — Main game loop, event routing, update, and draw orchestration.
"""

import random
import sys
import pygame

from settings import GAME_W, GAME_H, WINDOW_W, WINDOW_H, FPS, SCALE_X, SCALE_Y, BLACK
from core.state import GameState
from data.rooms import ROOM_A

import core.interactions as interactions
import scenes.menu as menu_scene
import scenes.room_renderer as room_renderer
import ui.overlays as overlays


class Game:
    def __init__(self):
        # pygame.init() is called in main.py (with mixer pre_init before it).
        # A second pygame.init() here would reset mixer settings and break audio.
        pygame.display.set_caption("CASE REDACTED")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock  = pygame.time.Clock()

        self.state        = GameState()
        self.state.screen = self.screen

        from entities.player import Player
        self.state.player = Player()
        self.state.player.load_sprites("assets/images/Walk.png", "assets/images/idle_1.png")

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            self._present()

    def _present(self) -> None:
        now = pygame.time.get_ticks()
        ox = oy = 0
        if now < self.state.shake_until:
            ox = random.uniform(-5, 5)
            oy = random.uniform(-5, 5)
        scaled = pygame.transform.smoothscale(self.state.surf, (WINDOW_W, WINDOW_H))
        self.screen.fill(BLACK)
        self.screen.blit(scaled, (ox * SCALE_X, oy * SCALE_Y))
        pygame.display.flip()

    # ── Events ────────────────────────────────────────────────────────────────

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._on_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._on_click(self.state.get_mouse())

    def _on_keydown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            if self.state.phase in ("intro", "video"):
                # ESC on intro/video = exit
                pygame.quit()
                sys.exit()
            interactions.close_any_overlay(self.state)
        if self.state.phase == "playing" and event.key == pygame.K_e:
            interactions.try_interact(self.state)

    def _on_click(self, pos: tuple) -> None:
        s = self.state
        if s.phase == "menu":
            # reset_video() must run BEFORE click_menu() so that
            # _try_load_video() has already set _VIDEO_AVAILABLE = True
            # by the time click_menu() decides whether to go to "video"
            # or fall back to "intro".
            menu_scene.reset_video()
            result = menu_scene.click_menu(pos)
            if result == "exit":
                pygame.quit()
                sys.exit()
            elif result:
                s.phase = result
        elif s.phase == "video":
            result = menu_scene.click_video(pos)
            if result:
                s.phase = result
        elif s.phase == "intro":
            result = menu_scene.click_intro(pos)
            if result == "exit":
                pygame.quit()
                sys.exit()
            elif result:
                s.phase = result
                s.current_room = ROOM_A
        elif s.phase == "playing":
            ov = s.active_overlay
            if   ov == "reading": interactions.click_reading(s, pos)
            elif ov == "keypad":  interactions.click_keypad(s, pos)
            elif ov == "tool":    interactions.click_tool(s, pos)
            elif ov == "doc":     interactions.click_doc(s, pos)
            elif ov == "journal": interactions.click_journal(s, pos)
            elif ov == "end":     interactions.close_any_overlay(s)
            elif ov == "ending":  interactions.click_ending(s, pos)

    # ── Update ────────────────────────────────────────────────────────────────

    def _update(self, dt: float) -> None:
        s   = self.state
        now = pygame.time.get_ticks()

        if s.phase in ("menu", "credits"):
            for drop in s.rain:
                drop.update(dt)
            return
        
        if s.phase == "video":
            if menu_scene.video_finished():
                s.phase = "intro"
            return

        if s.pending_cutscene:
            s.pending_cutscene = False
            s.phase = "cutscene"
            return

        if s.phase == "cutscene":
            if menu_scene.cutscene_finished():
                s.phase = "credits"
                s.active_overlay = None
                s.input_locked   = False
            return

        if s.phase != "playing":
            return
        

        # keypad auto-submit / auto-clear timers
        kp = s.keypad
        if kp["submit_at"] is not None and now >= kp["submit_at"]:
            kp["submit_at"] = None
            interactions._submit_code(s)

        if kp["close_at"] is not None and now >= kp["close_at"]:
            kp["close_at"]    = None
            s.active_overlay  = None
            s.input_locked    = False
            s.shake_until     = now + 360

        if kp["clear_at"] is not None and now >= kp["clear_at"]:
            kp["clear_at"] = None
            kp["code"]     = ""

        # end card after doc solved
        if s.end_card_at is not None and now >= s.end_card_at:
            s.end_card_at    = None
            s.active_overlay = "end"
            s.input_locked   = True

        s.player.update(s.input_locked, lambda nx, ny: interactions.can_move(s, nx, ny))
        interactions.check_room_transitions(s)

   # ── Draw ──────────────────────────────────────────────────────────────────

    # ── Draw ──────────────────────────────────────────────────────────────────

    def _draw(self) -> None:
        s = self.state
        # Clear the surface first
        s.surf.fill(BLACK) 
        
        # 1. Draw the primary game/scene content
        if s.phase == "menu":
            menu_scene.draw_menu(s.surf, s.rain, s.get_mouse())
        elif s.phase == "video":
            menu_scene.draw_video(s.surf, s.get_mouse())
        elif s.phase == "intro":
            menu_scene.draw_intro(s.surf, s.get_mouse())
        elif s.phase == "cutscene":
            menu_scene.draw_cutscene(s.surf)
        elif s.phase == "credits":
            menu_scene.draw_credits_menu(s.surf, s.rain)
        elif s.phase == "playing":
            self._draw_game()
        
        # 2. Draw active overlays on top (Single Source of Truth)
        ov = s.active_overlay
        if   ov == "reading": overlays.draw_reading_panel(s.surf, s)
        elif ov == "keypad":  overlays.draw_keypad(s.surf, s)
        elif ov == "tool":    overlays.draw_tool(s.surf, s)
        elif ov == "doc":     overlays.draw_doc_panel(s.surf, s)
        elif ov == "journal": overlays.draw_journal(s.surf, s)
        elif ov == "end":     overlays.draw_end_card(s.surf, s)
        elif ov == "ending":  overlays.draw_end_card(s.surf, s)
        
        
    def _draw_game(self) -> None:
        s   = self.state
        now = pygame.time.get_ticks()

        nearby = interactions.find_nearby(s)

        room_renderer.draw_room(s.surf, s)
        room_renderer.draw_hud(s.surf, s)
        room_renderer.draw_prompt(s.surf, s, nearby)

        # ov = s.active_overlay
        # if   ov == "reading": overlays.draw_reading_panel(s.surf, s)
        # elif ov == "keypad":  overlays.draw_keypad(s.surf, s)
        # elif ov == "tool":    overlays.draw_tool(s.surf, s)
        # elif ov == "doc":     overlays.draw_doc_panel(s.surf, s)
        # elif ov == "journal": overlays.draw_journal(s.surf, s)
        # elif ov == "end":     overlays.draw_end_card(s.surf, s)

        if now < s.flash_until:
            remaining = s.flash_until - now
            alpha     = int(204 * min(1.0, remaining / 90))
            flash     = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
            flash.fill((255, 255, 255, alpha))
            s.surf.blit(flash, (0, 0))
