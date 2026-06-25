# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A minimal Windows desktop analog clock widget (`analog_clock.py`) built with Python's `tkinter`. It runs as a frameless, always-on-top transparent overlay. `main.py` is an unrelated stub.

## Running and building

Run directly:
```
python analog_clock.py
```

Build a standalone Windows executable with PyInstaller:
```
pyinstaller analog_clock.spec
```
Output goes to `dist/analog_clock.exe`. The `.gitignore` excludes `build/`, `dist/`, and `*.spec`.

## Architecture

Everything lives in `analog_clock.py` as a single `AnalogClock` class initialized with a `tk.Tk` root window.

**Transparency trick:** The window uses `overrideredirect(True)` (no title bar/border) and sets a near-black color (`#020202`) as the transparent key via `-transparentcolor`. The canvas background is set to that key so it appears invisible.

**Interaction model** (all handled in `_make_draggable`):
- Drag: left-button press + motion moves the window
- Single click (no drag): shows "アイーン♡" text on the clock face for 2 seconds
- Double-click: toggles alpha between 1.0 and 0.3
- Right-click: quits

The single-click vs double-click disambiguation uses Windows' native double-click interval via `ctypes.windll.user32.GetDoubleClickTime()`. A pending single-click job is cancelled when a double-click fires, and `_skip_release` prevents the release event after a double-click from re-scheduling the single-click.

**Draw loop:** `tick()` calls `draw()` then schedules itself again after 1000 ms via `root.after`. `draw()` clears the canvas and redraws everything from scratch each second.

**Clock geometry:** `size=150` px canvas, `radius = size//2 - 10`. An extra `date_area=24` px below the circle shows the current date as `YYYY-MM-DD`.
