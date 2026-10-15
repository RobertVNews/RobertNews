#!/usr/bin/env python3
"""Prueba y render de un Short.

  python3 render.py historias/<nombre> test 1.0 6.5 12 ...   # PNG + build/contacto.png
  python3 render.py historias/<nombre> render                # build/short.mp4
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[2] not in ("test", "render"):
        sys.exit(__doc__)
    lib.run(sys.argv[1], sys.argv[2], [float(x) for x in sys.argv[3:]])
