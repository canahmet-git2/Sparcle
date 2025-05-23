#!/usr/bin/env python3
"""diagnose_blend.py

Quick diagnostic for Screen-blend artefacts (white diamonds etc.).
Prints the RGBA values of the centre pixel of the sprite PNG as it exists
on disk and as it is seen by Kivy after loading.  If RGB is non-zero where
alpha is 0 the texture is *not* clean and will break Screen mode.

Run once from the project root:
    python tools/diagnose_blend.py
"""
from __future__ import annotations
import os, sys
from pathlib import Path

PNG_PATH = Path('assets/placeholder_particle.png')
if not PNG_PATH.exists():
    sys.exit(f"❌  {PNG_PATH} not found – run the preview first so it creates the placeholder image, or point PNG_PATH at your sprite.")

try:
    from PIL import Image
except ImportError:
    sys.exit('❌  Pillow not installed –  pip install pillow')

# ------------------------------------------------------------
# 1) What is actually stored on disk?
# ------------------------------------------------------------
with Image.open(PNG_PATH) as im:
    im = im.convert('RGBA')
    on_disk = im.getpixel((im.width // 2, im.height // 2))

# ------------------------------------------------------------
# 2) What does Kivy hand us *after* its internal loading path?
#    (This bypasses the GL upload so it works headless.)
# ------------------------------------------------------------
from kivy.core.image import Image as CoreImage
ci = CoreImage(str(PNG_PATH), nocache=True)
# Attempt to fetch pixel from underlying texture
tex = ci.texture
if tex is None:
    sys.exit('❌  Kivy failed to load the image texture.')
w, h = tex.size
# Kivy stores texture.pixels bottom-left origin, length = w*h*4 bytes
pixels = tex.pixels  # raw RGBA bytes
# If tex.pixels is empty (no readback support), we'll rely only on disk check.
if not pixels:
    print('\n(GPU pixel read-back not available on this driver; using PNG-on-disk only)')
    loaded = (None, None, None, None)
else:
    # centre pixel coordinates
    cx, cy = w // 2, h // 2
    idx = (cy * w + cx) * 4
    loaded = tuple(pixels[idx: idx + 4])

print('\n🖼️  PNG  centre pixel  (disk):', on_disk)
if loaded[0] is not None:
    print('🎨  Kivy centre pixel (load):', loaded)
else:
    print('🎨  Kivy centre pixel (load):  <unavailable>')

r_d, g_d, b_d, a_d = on_disk
if loaded[0] is not None:
    r_k, g_k, b_k, a_k = loaded
else:
    r_k = g_k = b_k = a_k = 0

print('\nInterpretation:')
if a_d == 0 and (r_d or g_d or b_d):
    print(' • The file itself has non-black RGB in transparent area → Clean the PNG.')
elif a_d == 0 and (r_k or g_k or b_k):
    print(' • PNG is clean on disk but Kivy returns RGB≠0 – likely premultiplied or converted on load. Need code fix 2b.')
elif a_d == 0 and a_k == 0 and (r_k or g_k or b_k) == 0:
    print(' • Texture is clean; artefacts likely from region slice, GLES quirk or blend factors – see fixes 3 or 4.')
else:
    print(' • Centre pixel not fully transparent; if this is inside the sprite that is fine. Pick a transparent pixel for the test.') 