# CASE REDACTED — Pygame Port

A 2D top-down detective mystery.

## Controls

| Key | Action |
|-----|--------|
| WASD / Arrow Keys | Move |
| E | Interact |
| ESC / click CLOSE | Close panel |
| Mouse | Menus & puzzles |

## Run

```bash
pip install pygame
python main.py
```

---

## Project Structure

```
case_redacted/
│
├── main.py                  ← Entry point only (stay thin)
├── settings.py              ← ALL constants: resolution, colours, speed, door code
│
├── assets/
│   └── fonts.py             ← Font loading & caching (font() helper)
│
├── data/
│   ├── rooms.py             ← Room layouts: walls, objects, doors, deco
│   └── puzzle_data.py       ← All puzzle content: clues, UV spots, doc lines, readings
│
├── core/
│   ├── state.py             ← GameState dataclass (all mutable runtime data)
│   ├── game.py              ← Main loop, event routing, update, draw orchestration
│   └── interactions.py      ← Interaction logic & puzzle mechanics
│
├── entities/
│   ├── player.py            ← Player movement, collision rect, drawing
│   └── rain.py              ← Rain particle system (menu screen)
│
├── scenes/
│   ├── menu.py              ← Menu & intro screen draw + click handlers
│   └── room_renderer.py     ← In-game world: floor, deco, door, objects, vignette, HUD
│
└── ui/
    └── overlays.py          ← All overlay panels: reading, keypad, tool, doc, end card
```

---

## Where to make common changes

| What you want to change | File |
|-------------------------|------|
| Window / canvas size, FPS | `settings.py` |
| Colours | `settings.py` |
| Player speed | `settings.py` |
| Door code | `settings.py` → `DOOR_CODE` |
| Room layout (walls, furniture positions) | `data/rooms.py` |
| Clue text / reading panel content | `data/puzzle_data.py` → `READINGS` |
| UV spots | `data/puzzle_data.py` → `UV_SPOTS` |
| Document puzzle lines | `data/puzzle_data.py` → `DOC_LINES` |
| Magnifier images / reveals | `data/puzzle_data.py` → `MAG_IMAGES` |
| Player look / animation | `entities/player.py` |
| Rain behaviour | `entities/rain.py` |
| Menu / intro visuals | `scenes/menu.py` |
| In-game world rendering | `scenes/room_renderer.py` |
| Overlay panel visuals | `ui/overlays.py` |
| Puzzle mechanics | `core/interactions.py` |
| Game loop / event routing | `core/game.py` |
