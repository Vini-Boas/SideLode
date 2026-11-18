#!/bin/bash
# Regenerates SideLode.ico and SideLode.icns from logo.svg. Needs Python 3 with Pillow (pip install pillow).
# See genicons.py for what logo.svg may contain.
exec python3 "$(dirname "$0")/genicons.py" "$@"
