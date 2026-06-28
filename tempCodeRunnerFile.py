"""
main.py — Entry point for CASE REDACTED.

Run:
    pip install pygame opencv-python moviepy
    python main.py
"""

import pygame
from core.game import Game


def main() -> None:
    pygame.mixer.pre_init(44100, -16, 2, 2048)  # must be before pygame.init()
    pygame.init()
    Game().run()


if __name__ == "__main__":
    main()
