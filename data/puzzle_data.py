"""
data/puzzle_data.py — Static content for every puzzle in the game.
"""

from settings import GAME_W, GAME_H
import pygame

# ── HUD tracker ──────────────────────────────────────────────────────────────
TRACKER_ITEMS = [
    ("readNewspaper", "Read the newspaper"),
    ("sawWhiteboard", "Inspect the whiteboard"),
    ("sawDesk",       "Examine Arthur's desk"),
    ("doorUnlocked",  "Unlock the door"),
]

# ── Magnifier (photo board) ───────────────────────────────────────────────────
# Place these photos in your assets/ folder:
#   photo_desk.jpg   — close-up of the desk, timestamp in corner reads 11:47 PM
#   photo_hallway.jpg — hallway shot; a second shadow is visible near the door
#   photo_chair.jpg  — office chair; slightly displaced from the report photograph
#
# If no images are loaded yet the game renders a placeholder rectangle with the
# label and reveal text so the puzzle still works during development.

MAG_IMAGES = [
    {
        "base":     (38, 32, 28),
        "label":    "Crime scene photo #1 — Desk area",
        "reveal":   "Timestamp matches the visitor sign-in sheet exactly.",
        "file":     "assets/images/photo1.jpeg",
        "spot_x":   900,
        "spot_y":   530,
        "spot_r":   70,
        "flag":     "deskVerified",
    },
    {
        "base":     (30, 34, 36),
        "label":    "Crime scene photo #2 — Office chair",
        "reveal":   "Chair position contradicts the official report.",
        "file":     "assets/images/photo2.jpeg",
        "spot_x":   615,
        "spot_y":   270,
        "spot_r":   60,
        "flag":     "chairVerified",
    },
    {
        "base":     (28, 28, 32),
        "label":    "Crime scene photo #3 — Hallway outside office",
        "reveal":   "Arthur was not alone.",
        "file":     "assets/images/photo3.jpeg",
        "spot_x":   125,
        "spot_y":   260,
        "spot_r":   90,
        "flag":     "hallwayVerified",
    },
]

# ── UV inspection desk ────────────────────────────────────────────────────────
# NOTE: "2-4-7 IS THE REAL ORDER" has been removed as requested.
# The two remaining spots are the meaningful verified clues.
UV_SPOTS = [
    {
        "x":    200,
        "y":    150,
        "true": True,
        "text": "CASE WAS ALTERED AFTER CLOSURE",
    },
    {
        "x":    600,
        "y":    380,
        "true": False,
        "text": "ARTHUR WAS CORRUPT",
    },
    {
        "x":    420,
        "y":    260,
        "true": True,
        "text": "VISITOR NEVER SIGNED OUT",
    },
    {
        "x":    270,
        "y":    400,
        "true": True,
        "text": "FILE REMOVED FROM EVIDENCE",
    },
    {
        "x":    540,
        "y":    180,
        "true": False,
        "text": "CASE WAS SUICIDE",
    },
    {
        "x": 590,
        "y": 450,
        "true": True,
        "text": "KILLER'S SIGNATURE: A partial print matches Case 4-7-2.", # The Golden Clue
    },
]

# ── Document file puzzle ──────────────────────────────────────────────────────
DOC_LINES = [
    {"id": 0, "text": "Report: Det. Walker was alone in the office at time of death.",        "correct": True},
    {"id": 1, "text": "Edited line: Walker had 'no visitors logged' that night.",             "correct": False},
    {"id": 2, "text": "Contradiction: Sign-in sheet shows an unnamed visitor at 11:47 PM.",   "correct": True},
    {"id": 3, "text": "Original note: 'Case 4-7-2 reopened without authorization.'",          "correct": True},
    {"id": 4, "text": "Official summary: case closed, no further action required.",           "correct": False},
    {"id": 5, "text": "Margin note in Arthur's hand: 'They came back for the file.'",         "correct": False},
]

# ── Keypad ────────────────────────────────────────────────────────────────────
KEYPAD_KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "C", "0", "OK"]

# ── Tool panel geometry ───────────────────────────────────────────────────────
TOOL_RECT = pygame.Rect((GAME_W - 900) // 2, (GAME_H - 560) // 2, 900, 560)

# ── Journal pages ─────────────────────────────────────────────────────────────
# Pages in order. The last page is the one currently shown when the journal
# is first opened; clicking advances forward, and the last page shows the
# original desk reading (the "current" note).
JOURNAL_PAGES = [
    {
        "day":  "Day 42",
        "text": "Same symbols again.\n\nThree marks on the wall of the storage room — identical to the ones in the Harlow file. Nobody else has noticed. Or nobody wants to.",
    },
    {
        "day":  "Day 67",
        "text": "Nobody believes they're connected.\n\nI brought it to Reeves. He told me I was seeing patterns in noise. But the spacing, the angle — it's deliberate. Someone is leaving a signature.",
    },
    {
        "day":  "Day 94",
        "text": "Evidence disappeared.\n\nThe photographs from the storage room were gone from the archive this morning. Checked the log — no withdrawal recorded. Someone removed them without a trace.",
    },
    {
        "day":  "Final entry",
        "text": (
            "'They don't realize the system they built is being used to hide what happened.'\n"
            "'Case 4-7-2 was never just a case file.'\n"
            "'It was a location where everything started.'\n\n"
            "A second note, scrawled hastily:\n"
            "'If anyone reads this… don't trust the numbering.'"
        ),
        "is_last": True,
    },
]

# ── Reading panel content ─────────────────────────────────────────────────────
READINGS = {
    "newspaper": {
        "title": "NEWSPAPER",
        "meta":  "DETECTIVE FOUND DEAD IN OFFICE — CASE LINKED TO RESIDENTIAL ZONE 4-7-2",
        "body": (
            "Police confirm the body of Detective Arthur Walker was discovered in a private "
            "office located near Road 4, Street 7, House 2.\n\n"
            "The official report has sealed all further details."
        ),
    },
    "whiteboard": {
        "title": "WHITEBOARD",
        "meta":  "A CRYPTIC GRID",
        "body": (
            "Three symbols are drawn: ○  △  □\n"
            "Faint numbers sit beneath each, joined by arrows.\n\n"
            "'Everything is numbered by proximity… not order.'\n"
            "'House follows Road. Street follows House.'\n\n"
            "— It feels like a structured crime grid system."
        ),
    },
    "desk": {
        "title": "ARTHUR'S DESK",
        "meta":  "JOURNAL + LOCKED DRAWER",
        "body":  "(Open the journal on the desk to read Arthur's notes.)",
    },
    "cassette": {
        "title": "CASSETTE TABLE",
        "meta":  "AUDIO LOG (TRANSCRIBED)",
        "body": (
            "'...if you're hearing this, the case file was changed after closure. "
            "I don't know who has access. I only know the numbers are the key. "
            "Don't trust the order they gave you.' — A. Walker, recording cuts off."
        ),
    },
}
