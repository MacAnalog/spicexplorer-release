#!/usr/bin/env bash
# Open the 5T-OTA layout in the KLayout GUI (edit mode) with IHP sg13g2 layer colors AND
# live, editable PyCells — select an nmos/pmos/via_stack and change W/L/fingers in the PCell
# parameter dialog.
#
# This uses a KLayout built against Python 3.11 (~/local/klayout-py311), because the IHP
# PyCell library needs Python >= 3.11 (StrEnum, `from __future__ import annotations`) and the
# stock portable KLayout embeds Python 3.6. Requires an X display (SSH X-forwarding sets
# $DISPLAY). If the py3.11 build is absent, falls back to the plain `klayout` on PATH with
# -rx (baked geometry only, no live PyCells).
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PDK="${PDK_ROOT:?set PDK_ROOT to your PDK install root}/ihp-sg13g2"
LYP="$PDK/libs.tech/klayout/tech/sg13g2.lyp"
GDS="${1:-$HERE/ota_5t.gds}"
PY="${PYTHON:-python3}"
GUI="${KLAYOUT_GUI:-klayout}"

[ -f "$GDS" ] || { echo "generating $GDS ..."; "$PY" "$HERE/gen_5t_ota.py" -o "$GDS"; }
[ -n "$DISPLAY" ] || echo "warning: \$DISPLAY is unset — the GUI needs an X display." >&2

if [ -x "$GUI" ]; then
  # IHP tech on KLAYOUT_PATH so the SG13_dev PyCell library autoloads (works under py3.11).
  export KLAYOUT_PATH="$PDK/libs.tech/klayout:$PDK/libs.tech/klayout/tech"
  exec "$GUI" -e -l "$LYP" "$GDS"
else
  echo "note: py3.11 KLayout build not found — opening without live PyCells." >&2
  export QT_QPA_PLATFORM=xcb
  exec klayout -e -rx -l "$LYP" "$GDS"
fi
