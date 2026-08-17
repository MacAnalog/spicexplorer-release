# KLayout GUI cheatsheet (for tweaking the 5T-OTA layout)

Default keyboard shortcuts, extracted from the KLayout 0.30.5 source. They are configurable
under **File → Setup → Key Bindings** (or Edit → Key Bindings), so your build may differ.
Open the layout with [`5t_ota/open_in_klayout.sh`](5t_ota/open_in_klayout.sh) (edit mode + IHP
colors + live PyCells).

## The one workflow you came for — edit a PyCell

1. Make sure you're in **edit mode** (the launcher passes `-e`; otherwise Edit → Editable).
2. **Click** the device (an `nmos`/`pmos`/`via_stack` instance) once to select it. Press
   **`Space`** to cycle if several objects sit under the cursor.
3. Press **`Q`** (Properties) → **PCell** tab → change `w` / `l` / `ng` → **Apply**. The
   geometry regenerates live.
4. Re-run signoff after edits: `python 5t_ota/signoff.py` (KLayout) and/or
   `python 5t_ota/signoff_magic_netgen.py` (Magic+netgen). If you changed *connectivity*,
   update `5t_ota/ota_5t_lvs.spice` to match or LVS will (correctly) fail.

> Live PyCells need the Python-3.11 KLayout build (`~/local/klayout-py311`); the launcher uses
> it automatically. With the stock py3.6 KLayout the instances are baked geometry — editable
> as plain shapes but without the PCell parameter dialog.

## View & navigation

| Action | Key |
|---|---|
| Zoom fit (whole layout) | `F2` |
| Zoom fit selection | `Shift+F2` |
| Zoom in / out | `Ctrl++` / `Ctrl+-` |
| Pan | drag scrollbars, or arrow keys |
| Zoom | mouse wheel |
| Cancel current operation / deselect | `Esc` |

## Hierarchy

| Action | Key |
|---|---|
| Show more hierarchy levels | `+` |
| Show fewer hierarchy levels | `-` |
| Show full hierarchy | `*` |
| Descend into / set cell as top | `Ctrl+S` (Show As New Top) |
| Go to coordinate | `Ctrl+G` |

## Selecting & editing

| Action | Key |
|---|---|
| Object **Properties** (incl. PCell params) | `Q` |
| Select next item under cursor | `Space` |
| Add next item to selection | `Shift+Space` |
| Copy / Cut / Paste | `Ctrl+C` / `Ctrl+X` / `Ctrl+V` |
| Duplicate | `Ctrl+B` |
| Delete selected | `Del` |
| Undo / Redo | `Ctrl+Z` / `Ctrl+Y` |
| Editor options (grid, snapping) | `F3` |

Drawing tools (box, polygon, path, instance, text) are on the toolbar / **Edit → Modes**;
they don't have default single-key bindings — assign your own in Key Bindings if you want them.

## Rulers / measuring

| Action | Key |
|---|---|
| Ruler tool | toolbar (the ruler icon) — click-drag to measure |
| Clear all rulers/annotations | `Ctrl+K` |

## Files

| Action | Key |
|---|---|
| Open in new panel / same panel | `Ctrl+O` / `Shift+Ctrl+O` |
| Reload from disk | `Ctrl+R` |
| Close / Close all | `Ctrl+W` / `Shift+Ctrl+W` |
| Print / export image | `Ctrl+P` |
| Macro Development IDE (Ruby/Python console) | `F5` |
| Exit | `Ctrl+Q` |

## Running DRC / LVS from inside the GUI (optional)

The GUI can run the IHP KLayout decks via **Tools → DRC** / **Tools → LVS** when the sg13g2
technology is loaded (it is, via `KLAYOUT_PATH`). For scripted/repeatable signoff, prefer the
command-line runners in `5t_ota/` (`signoff.py`, `signoff_magic_netgen.py`) — they're what the
example documents as passing.
