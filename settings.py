"""
settings.py — Global constants and configuration for CASE REDACTED.

Change game resolution, speed, colours, and the door code here.
Anything that might need tweaking between playtests lives in this file.
"""

# ── Resolution / window ──────────────────────────────────────────────────────
GAME_W, GAME_H   = 1600, 900   # internal canvas size (matches original HTML5 canvas)
WINDOW_W, WINDOW_H = 1280, 720  # OS window (scaled down for typical screens)
FPS              = 60

SCALE_X = WINDOW_W / GAME_W
SCALE_Y = WINDOW_H / GAME_H

# ── Gameplay ──────────────────────────────────────────────────────────────────
PLAYER_SPEED = 3.4
DOOR_CODE    = "247"           # the code the player must enter at the keypad

# ── Colour palette ────────────────────────────────────────────────────────────
INK    = (60,  65,  72)
PANEL  = (75,  82,  92)
PANEL2 = (90,  98,  108)
ACCENT = (201, 162, 75)
ACCENT2= (111, 168, 201)
RED    = (179, 70,  63)
PAPER  = (232, 221, 194)
TEXT   = (207, 211, 216)
DIM    = (107, 114, 128)
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)

FLOOR_BG = (48, 52, 60) 
FLOOR_BORDER_BG    = (8,  9,  11)   # was (12, 14, 17) — darker wall
FLOOR_BORDER_STROKE= (30, 33, 38)   # was (42, 46, 53)
GRID_LINE          = (255, 255, 255, 20)

PLAYER_BODY = (43,  51,  64)
PLAYER_SKIN = (202, 169, 135)
PLAYER_HAIR = (27,  33,  43)
PLAYER_EYE  = (202, 162, 75)

DOOR_UNLOCKED_FILL   = (36,  53,  40)
DOOR_UNLOCKED_STROKE = (63,  94,  68)
DOOR_LOCKED_FILL     = (58,  34,  34)
DOOR_LOCKED_STROKE   = (107, 48,  48)
