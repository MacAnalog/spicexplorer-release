#!/usr/bin/env bash
# Open the gdsfactory-lane 5T-OTA layout in the KLayout GUI (edit mode) with IHP sg13g2
# layer colors. Requires an X display (SSH X-forwarding sets $DISPLAY).
#
# Unlike the PyCell lane, this GDS contains no live PCells — the ihp-gdsfactory cells are
# baked geometry (hierarchical cells, editable as plain shapes). Hand edits are fine; to
# change W/L/nf, edit SIZING in gen_5t_ota_gf.py and regenerate (then re-run signoff.py).
# Any KLayout works here; the py3.11 build is preferred only for consistency with the
# PyCell lane's workflow.
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PDK="${PDK_ROOT:?set PDK_ROOT to your PDK install root}/ihp-sg13g2"
LYP="$PDK/libs.tech/klayout/tech/sg13g2.lyp"
GDS="${1:-$HERE/ota_5t_gf.gds}"
PY="${PYTHON:-python3}"
GUI="${KLAYOUT_GUI:-klayout}"

[ -f "$GDS" ] || { echo "generating $GDS ..."; "$PY" "$HERE/gen_5t_ota_gf.py" -o "$GDS"; }
[ -n "$DISPLAY" ] || echo "warning: \$DISPLAY is unset — the GUI needs an X display." >&2

if [ -x "$GUI" ]; then
  export KLAYOUT_PATH="$PDK/libs.tech/klayout:$PDK/libs.tech/klayout/tech"
  exec "$GUI" -e -l "$LYP" "$GDS"
else
  export QT_QPA_PLATFORM=xcb
  exec klayout -e -rx -l "$LYP" "$GDS"
fi
