"""
core/interactions.py — Interaction and puzzle logic.

Handles what happens when the player presses E near an object, what
each puzzle does when a button is clicked, etc.

Functions receive *state* (GameState) and mutate it directly.
"""
from __future__ import annotations

import math
import pygame

import systems.sound as sound

from settings import DOOR_CODE, ACCENT2, RED, DIM
from data.rooms import ROOM_A, ROOM_B
from data.puzzle_data import MAG_IMAGES, UV_SPOTS, DOC_LINES, READINGS
from ui.overlays import keypad_button_layout, doc_line_layout, tool_close_rect



# ── Overlay open/close ────────────────────────────────────────────────────────

def open_reading(state, title: str, meta: str, body: str) -> None:
    state.reading       = {"title": title, "meta": meta, "body": body}
    state.active_overlay= "reading"
    state.input_locked  = True


def close_any_overlay(state) -> None:
    if state.tool.get("mode") == "uv":
        sound.stop_loop()
    if state.active_overlay == "journal":
        sound.stop_journal()
    state.active_overlay = None
    state.input_locked   = False

# ── Collision + room transitions ──────────────────────────────────────────────

def can_move(state, nx: float, ny: float) -> bool:
    p   = state.player
    box = pygame.Rect(int(nx), int(ny), p.w, p.h)
    for w in state.current_room["walls"]:
        if box.colliderect(w):
            return False
    if state.current_room is ROOM_A and not state.flags["doorUnlocked"]:
        if box.colliderect(state.current_room["door"]):
            return False
    if state.current_room is ROOM_B:
        if box.colliderect(state.current_room["door"]):
            return False
    return True


def check_room_transitions(state) -> None:
    p     = state.player
    prect = p.rect
    if state.current_room is ROOM_A and state.flags["doorUnlocked"]:
        if prect.colliderect(pygame.Rect(0, 380, 60, 140)):
            _enter_room_b(state)
    elif state.current_room is ROOM_B:
        if prect.colliderect(pygame.Rect(1540, 380, 60, 140)):
            state.current_room = ROOM_A
            state.player.teleport(100.0, 430.0)


def _enter_room_b(state) -> None:
    state.player.teleport(80.0, 430.0)
    state.flags["doorUnlocked"] = True
    state.current_room          = ROOM_B
    sound.play("dooropen")

# ── Nearby object detection ───────────────────────────────────────────────────

def find_nearby(state) -> dict | None:
    reach = state.player.reach_rect
    for o in state.current_room["objects"]:
        if reach.colliderect(pygame.Rect(o["x"], o["y"], o["w"], o["h"])):
            return o
    if state.current_room is ROOM_A and reach.colliderect(state.current_room["door"]):
        return {
            "id":    "doorA",
            "label": "Open Door" if state.flags["doorUnlocked"] else "Locked Door",
            "kind":  "doorA",
        }
    if state.current_room is ROOM_B and reach.colliderect(state.current_room["door"]):
        return {"id": "doorB", "label": "Return to Office", "kind": "doorB"}
    return None


# ── Interact dispatcher ───────────────────────────────────────────────────────

def try_interact(state) -> None:
    if state.input_locked:
        return
    o = find_nearby(state)
    if not o:
        return
    if state.current_room is ROOM_A:
        _handle_room_a(state, o)
    elif state.current_room is ROOM_B:
        _handle_room_b(state, o)


def _handle_room_a(state, o: dict) -> None:
    kind = o["kind"]
    if kind == "paper-floor":
        r = READINGS["newspaper"]
        open_reading(state, r["title"], r["meta"], r["body"])
        state.flags["readNewspaper"] = True
        sound.play("newspaper")
    elif kind == "whiteboard":
        r = READINGS["whiteboard"]
        open_reading(state, r["title"], r["meta"], r["body"])
        state.flags["sawWhiteboard"] = True
    elif kind == "desk":
        state.flags["sawDesk"] = True
        open_journal(state)
        sound.play_once_on_channel("journal", channel_id=6, volume=0.7)
        
    elif kind == "doorA":
        if state.flags["doorUnlocked"]:
            _enter_room_b(state)
        else:
            _open_keypad(state)


def _handle_room_b(state, o: dict) -> None:
    kind = o["kind"]
    
    if kind == "photoboard":
        # Look for the identifier we know exists in our UV_SPOTS text
        signature_found = any("KILLER'S SIGNATURE" in s for s in state.flags["uvFound"])
        
        if signature_found:
            state.tool           = {"mode": "magnifier", "mag_idx": 0, "reveal": ""}
            state.active_overlay = "tool"
            state.input_locked   = True
        else:
            open_reading(state, "EVIDENCE BOARD", "LOCKED", 
                         "The board is a mess. I need to find the killer's signature under UV light first.")
    elif kind == "uv":
        state.tool           = {"mode": "uv", "mag_idx": 0, "reveal": ""}
        state.active_overlay = "tool"
        state.input_locked   = True
        sound.start_loop("static", volume=0.4)

    elif kind == "docfiles":
        # Standard doc puzzle flow
        state.doc_selected   = set()
        state.doc_msg        = "Checking files..."
        state.active_overlay = "doc"
        state.input_locked   = True
        
    elif kind == "cassette":
        r = READINGS["cassette"]
        open_reading(state, r["title"], r["meta"], r["body"])
        
        
    elif kind == "herring":
        open_reading(state, o["label"].upper(), "NOTHING USEFUL", o["text"])
    elif kind == "doorB":
        state.current_room = ROOM_A
        state.player.teleport(100.0, 430.0)
     
    elif kind == "terminal":
        # Final Forensic Integrity Check
        theory_verified = state.flags.get("docSolved")
        all_evidence = state.flags.get("evidenceCount", 0) >= 3
        
        if theory_verified and all_evidence:
            state.active_overlay = "ending"
        else:
            msg = "Access Denied: Forensic verification incomplete."
            if not theory_verified: msg += " Need to establish theory."
            else: msg += f" Evidence missing ({state.flags.get('evidenceCount', 0)}/3)."
            open_reading(state, "SYSTEM INTEGRITY", "LOCKED", msg)


# ── Keypad puzzle ─────────────────────────────────────────────────────────────

def _open_keypad(state) -> None:
    state.keypad = {
        "code":       "",
        "hint":       "" if state.flags["sawDesk"] else "Something feels inverted\u2026",
        "submit_at":  None,
        "close_at":   None,
        "clear_at":   None,
        "shake_until":0,
    }
    state.active_overlay = "keypad"
    state.input_locked   = True


def click_keypad(state, pos: tuple) -> None:
    for label, rect_ in keypad_button_layout():
        if rect_.collidepoint(pos):
            if label == "C":
                state.keypad["code"] = ""
            elif label == "OK":
                _submit_code(state)
            else:
                _press_digit(state, label)
            return
    cancel = pygame.Rect(GAME_W // 2 - 70, 740, 140, 36)
    if cancel.collidepoint(pos):
        close_any_overlay(state)


def _press_digit(state, d: str) -> None:
    kp = state.keypad
    if len(kp["code"]) >= 3:
        return
    kp["code"] += d
    sound.play("click")
    if len(kp["code"]) == 3:
        kp["submit_at"] = pygame.time.get_ticks() + 150


def _submit_code(state) -> None:
    kp  = state.keypad
    now = pygame.time.get_ticks()
    if kp["code"] == DOOR_CODE:
        kp["hint"]                  = "CLICK."
        state.flash_until            = now + 90
        kp["close_at"]              = now + 350
        state.flags["doorUnlocked"] = True
        sound.play("confirm")
    else:
        kp["shake_until"] = now + 400
        kp["hint"]        = "Something feels inverted\u2026"
        kp["clear_at"]    = now + 400
        sound.play("error")


# ── Tool panel clicks ─────────────────────────────────────────────────────────

def click_tool(state, pos: tuple) -> None:
    if tool_close_rect().collidepoint(pos):
        close_any_overlay(state)
        return

    if state.tool["mode"] == "magnifier":
        from ui.overlays import mag_nav_rects
        from data.puzzle_data import MAG_IMAGES
        prev_r, next_r = mag_nav_rects()
        if prev_r.collidepoint(pos) and state.tool["mag_idx"] > 0:
            state.tool["mag_idx"] -= 1
            state.tool["reveal"] = ""
            sound.play("click")
            return
        if next_r.collidepoint(pos) and state.tool["mag_idx"] < len(MAG_IMAGES) - 1:
            state.tool["mag_idx"] += 1
            state.tool["reveal"] = ""
            sound.play("click")
            return

    from data.puzzle_data import TOOL_RECT
    if not TOOL_RECT.collidepoint(pos):
        return
    mx = pos[0] - TOOL_RECT.x
    my = pos[1] - TOOL_RECT.y
    if state.tool["mode"] == "magnifier":
        _click_magnifier(state, mx, my)
    elif state.tool["mode"] == "uv":
        _click_uv(state, mx, my)
        
        
def _click_magnifier(state, mx: float, my: float) -> None:
    from data.puzzle_data import MAG_IMAGES, TOOL_RECT

    idx  = state.tool["mag_idx"]
    data = MAG_IMAGES[idx]

   
    inner = pygame.Rect(60, 40, 780, 440)
    if not inner.collidepoint(mx, my):
        return

    # Need the photo's real size to map coordinates correctly
    from ui.overlays import _load_mag_photo
    photo = _load_mag_photo(idx)
    if photo is None:
        return
    src_w, src_h = photo.get_size()

    rel_x = (mx - inner.x) / inner.width
    rel_y = (my - inner.y) / inner.height
    click_src_x = rel_x * src_w
    click_src_y = rel_y * src_h

    dist = math.hypot(click_src_x - data["spot_x"], click_src_y - data["spot_y"])
    if dist <= data["spot_r"]:
        state.tool["reveal"]  = data["reveal"]
        state.flags[data["flag"]] = True
        sound.play("magnifier")

    evidence_found = [
        state.flags.get("deskVerified"),
        state.flags.get("hallwayVerified"),
        state.flags.get("chairVerified"),
    ]
    state.flags["evidenceCount"] = evidence_found.count(True)

    if state.flags["evidenceCount"] >= 3:
        state.flags["photoSolved"] = True
        
        
def _click_uv(state, mx: float, my: float) -> None:
    for s in UV_SPOTS:
        d = math.hypot(mx - s["x"], my - s["y"])
        if d < 60 and s["text"] not in state.flags["uvFound"]:
            state.flags["uvFound"].add(s["text"])
            
            # This logic needs to trigger the flag the photoboard looks for
            prefix = "[TRUE] " if s["true"] else "[UNCONFIRMED] "
            state.tool["reveal"] = prefix + "\u201c" + s["text"] + "\u201d"
            
# ── Document puzzle ───────────────────────────────────────────────────────────

def click_doc(state, pos: tuple) -> None:
    panel, rects = doc_line_layout(state)
    for d, rect_, _lines in rects:
        if rect_.collidepoint(pos):
            if d["id"] in state.doc_selected:
                state.doc_selected.discard(d["id"])
            else:
                state.doc_selected.add(d["id"])
            sound.play("click")
            return
    submit = pygame.Rect(panel.x + 36, panel.bottom - 70, 240, 40)
    if submit.collidepoint(pos):
        _submit_doc(state)


def _submit_doc(state) -> None:
    correct_ids = {d["id"] for d in DOC_LINES if d["correct"]}
    if state.doc_selected == correct_ids:
        state.doc_msg_color = ACCENT2
        state.doc_msg = "Files verified. Official theory established. Accessing photo board..."
        state.flags["docSolved"] = True
        state.flags["theoryFormed"] = True
        sound.play("confirm")
    else:
        state.doc_msg_color = RED
        state.doc_msg = "These don't add up. Re-read the notes."
        sound.play("error")
        
# ── Reading panel click ───────────────────────────────────────────────────────

def click_reading(state, pos: tuple) -> None:
    from settings import GAME_W
    panel     = pygame.Rect(GAME_W // 2 - 380, 130, 760, 560)
    close_btn = pygame.Rect(panel.x + 36, panel.bottom - 76, 170, 40)
    if close_btn.collidepoint(pos):
        close_any_overlay(state)

# ── Ending overlay click ──────────────────────────────────────────────────────

def click_ending(state, pos: tuple) -> None:
    # Trigger the end of the game
    state.active_overlay = None
    state.input_locked = False
   
    print("Investigation terminated. The culprit is watching.")
    
    
# ── Local import needed for keypad cancel rect ────────────────────────────────
from settings import GAME_W


# ── Journal overlay ────────────────────────────────────────────────────────────

def open_journal(state) -> None:
    state.journal_page   = 0
    state.active_overlay = "journal"
    state.input_locked   = True


def click_journal(state, pos: tuple) -> None:
    from ui.overlays import journal_nav_rects
    from data.puzzle_data import JOURNAL_PAGES
    prev_r, next_r, close_r = journal_nav_rects()
    total = len(JOURNAL_PAGES)
    if prev_r.collidepoint(pos) and state.journal_page > 0:
        state.journal_page -= 1
    elif next_r.collidepoint(pos) and state.journal_page < total - 1:
        state.journal_page += 1
    elif close_r.collidepoint(pos):
        close_any_overlay(state)
