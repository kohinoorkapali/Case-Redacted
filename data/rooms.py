"""
data/rooms.py — Static room layouts.

Each room dict contains:
  name    : displayed in the HUD
  walls   : list of pygame.Rect used for collision
  door    : pygame.Rect for the exit/entry doorway
  objects : interactive items (id, x, y, w, h, label, color, kind, …)
  deco    : purely visual blocks (no interaction)

Add new rooms here; reference them in scenes/ to wire up transitions.
"""

import pygame

def R(x, y, w, h):
    return pygame.Rect(x, y, w, h)


ROOM_A = {
    "name": "ROOM A \u2014 MAIN OFFICE",
    "walls": [
        R(0, 0, 1600, 80), R(0, 860, 1600, 40),
        R(0, 0, 40, 900),  R(1560, 0, 40, 900),
        # Computer desk — top-left against both walls
        R(50,  80, 200, 100),   # left desk
        R(200, 80, 200, 100),   # center desk
        R(325, 80, 200, 100),   # right desk
        # Whiteboard — top wall, center-left
        R(600, 0, 200, 80),
        # Printer — top wall, right of whiteboard
        R(980, 30, 130, 120),
        # File cabinets — top-right
        R(1400, 0, 130, 130),
        # Table/desk collision — center
        R(650, 380, 180, 110),
        # Sofa — bottom center
        R(395, 750, 155, 30),    # sofa down
        R(395, 580, 155, 30),    # sofa up
        # Water cooler — bottom right area (old printer spot)
        R(920, 690, 80, 140), 
        # Stacked Boxes — bottom left
        R(170, 690, 110, 120),
        R(1490, 300, 60, 80),   # plant right wall
        R(1490, 500, 60, 80),   # plant right wall
        R(870, 60, 60, 80),   # plant left wall
        R(50,   720, 60, 80),   # plant bottom left
        R(670, 690, 170, 160),
    ],
    "door": R(40, 380, 30, 140),
    "objects": [
        {
            "id": "newspaper", "x": 1250, "y": 400, "w": 100, "h": 60,
            "label": "Newspaper", "color": (207, 201, 176), "kind": "paper-floor",
        },
        {
            # Whiteboard — top of room, against top wall
            "id": "whiteboard", "x": 600, "y": 0, "w": 200, "h": 80,
            "label": "Whiteboard", "color": (233, 236, 239), "kind": "whiteboard",
        },
        {
            # Arthur's desk — center of room
            "id": "desk", "x": 650, "y": 380, "w": 360, "h": 165,
            "label": "Arthur's Desk", "color": (90, 70, 50), "kind": "desk",
        },
    ],
    "deco": [
        # Computer desk — top-left corner, against left + top walls
        {"x": 50, "y": 80, "w": 120, "h": 110, "color": (44, 51, 61), "label": "Computer Desk"},
        # Printer — right side of whiteboard, against top wall
        {"x": 980, "y": 70, "w": 170, "h": 120, "color": (35, 38, 43), "label": "Printer"},
        # File cabinets — top-right, against top wall
        {"x": 1400, "y": 0, "w": 130, "h": 130, "color": (51, 39, 30), "label": "File Cabinets"},
        # Sofa — bottom center
        {"x": 380, "y": 710, "w": 220, "h": 75, "color": (58, 37, 48), "label": "Sofa"},  # down
        {"x": 380, "y": 560, "w": 220, "h": 75, "color": (58, 37, 48), "label": "Sofa"}, 
        # Water cooler — bottom right (where printer used to be)
        {"x": 900, "y": 640, "w": 150, "h": 200, "color": (38, 65, 74), "label": "Water Cooler"},
        # Stacked boxes — bottom left
        {"x": 120, "y": 680, "w": 220, "h": 140, "color": (61, 52, 36), "label": "Stacked Boxes"},
        # Coffee station — between sofas and water cooler
        {"x": 680, "y": 690, "w": 220, "h": 160, "color": (60, 40, 20), "label": "Coffee Station"},
        # Plants — scattered
        {"x": 1490, "y": 300, "w": 60, "h": 80, "color": (30, 80, 30), "label": "Plant", "variant": 0},
        {"x": 1490, "y": 500, "w": 60, "h": 80, "color": (30, 80, 30), "label": "Plant", "variant": 2},
        {"x": 870, "y": 60, "w": 60, "h": 80, "color": (30, 80, 30), "label": "Plant", "variant": 4},
        {"x": 50,   "y": 720, "w": 60, "h": 80, "color": (30, 80, 30), "label": "Plant", "variant": 1},

    ],
}

ROOM_B = {
    "name": "ROOM B \u2014 EVIDENCE ROOM",
    "walls": [
        R(0, 0, 1600, 40), R(0, 860, 1600, 40),
        R(0, 0, 40, 900),  R(1560, 0, 40, 900),
        R(120, 140, 420, 60),
        R(620, 140, 260, 70),
        R(1000, 150, 90, 90),
        R(1200, 150, 90, 90),
        R(1320, 400, 160, 90),
        R(120, 650, 160, 90),
    ],
    "door": R(1530, 380, 30, 140),
    "objects": [
        {
            "id": "photoboard", "x": 560, "y": 560, "w": 230, "h": 130,
            "label": "Photo Board (Magnifier)", "color": (202, 168, 107), "kind": "photoboard",
        },
        {
            "id": "uvdesk", "x": 900, "y": 560, "w": 200, "h": 130,
            "label": "UV Inspection Desk", "color": (39, 56, 74), "kind": "uv",
        },
        {
            "id": "cassette", "x": 1260, "y": 600, "w": 160, "h": 90,
            "label": "Cassette Table", "color": (58, 42, 29), "kind": "cassette",
        },
        {
            "id": "docfiles", "x": 200, "y": 560, "w": 200, "h": 120,
            "label": "Document Files", "color": (64, 74, 58), "kind": "docfiles",
        },
        {
            "id": "terminal", "x": 650, "y": 160, "w": 200, "h": 50,
            "label": "Broken Terminal", "color": (34, 34, 34), "kind": "herring",
            "text": "SYSTEM OFFLINE. No data recoverable.",
        },
        {
            "id": "cabinet1", "x": 1010, "y": 160, "w": 70, "h": 70,
            "label": "File Cabinet", "color": (42, 33, 24), "kind": "herring",
            "text": "Locked. Not your case.",
        },
        {
            "id": "cabinet2", "x": 1210, "y": 160, "w": 70, "h": 70,
            "label": "File Cabinet", "color": (42, 33, 24), "kind": "herring",
            "text": "Locked. Rust on the hinges.",
        },
        {
            "id": "storage", "x": 1340, "y": 410, "w": 120, "h": 70,
            "label": "Chairs / Storage", "color": (38, 38, 38), "kind": "herring",
            "text": "Old furniture. Nothing of interest.",
        },
        {
            "id": "coffee", "x": 140, "y": 660, "w": 120, "h": 70,
            "label": "Coffee Cups", "color": (59, 42, 26), "kind": "herring",
            "text": "Cold coffee. Work left unfinished.",
        },
    ],
    "deco": [],
}
