#!/bin/bash
# Build each spec in turn (voice, long, Short, outro, subtitles, covers). One failure doesn't stop the rest.
cd /home/claude/video
for s in "$@"; do
  echo "=== $s $(date +%H:%M:%S)"
  python3 engine.py build "specs/$s.json" both 2>&1 | grep -v Fontconfig
  if [ "${PIPESTATUS[0]}" = "0" ]; then
    echo "OK $s"
  else
    echo "FAIL $s"
  fi
done
echo "ALL DONE $(date +%H:%M:%S)"
