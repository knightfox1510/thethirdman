#!/bin/bash
# One-time setup for The Third Man video engine.
set -e
pip install --break-system-packages -q skia-python numpy scipy fonttools pillow 2>/dev/null || pip install -q skia-python numpy scipy fonttools pillow
command -v ffmpeg >/dev/null || { echo "ffmpeg is required"; exit 1; }
python3 -c "import skia, scipy; print('engine ready: skia', skia.__version__)"
