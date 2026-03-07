# -*- coding: utf-8 -*-
"""Chaos Vis - Image Gen Interface (Gradio App)"""

import os
import warnings
import logging

import gradio as gr
from PIL import Image

# ── Defaults ──────────────────────────────────────────────────────────────────

HASH_TEXT = "AQIDBAUGBwgJEBESExQVFgECAwQFBgcICRAREtT7Uvq9jkUEsEMVYLWQTLY6F-A7bi4zy9sEW0N7nP8HPA-nV2sBP_l27UVxXGyJc7cU8sMVeLuV_7RXBVL_VglIq-0xY0w5_e1GvsusCnCfm9zGXTza8rxgVFyzoUIl8wFajhE79ZXMgpjLGN5axmzntljO6cqz-x5f0NYpdNeyqYH43HvmuwLX8rMkK1tkfT1-e04tywyzdtjgiCFWS1I1TflsMy3V3sWflEaiHDEau6FDCMq9PHEXAN7oaVmdGcspnitgyGo493wfH7R2Jjcy0mFICp0XV1jd4rBzE3PakHcNKTmzHv4KGsWSEt0CEYNKZydwP88w43_4yhWcQnwCjjpLJiIuYdBnNcp0G84O4e3ZqM8I-THu1h3gXh-z3vY8qaHLJIiwnTgDoDrS5Arzx40WK8_TQvP8O7Zemh6e0gg7iBqOUT4zpKD8-5wsRLwat0M7CA6MGlE80de56Vl-4LNt5bKErjER6sC7lw7TzFKa_nA0zprp21kzHmgcJ1p0QZa4ilF3hOAyD1TxYVF94rInoMbSTf4O7oynMkSyEn5LiAISmThxBJ93NwC-5oG7kw6GNYMpbQSoxM8QaVTLcr4nAJXwj-gMyg=="
CMAP = "inferno"
MAX_ITERATIONS = 100000000
WIDTH = 2400
HEIGHT = 1600
BACKGROUND = "default"
DENSITY = 15
LEFT_PADDING = 0.36
RIGHT_PADDING = 0.36
TOP_PADDING = 0.05
BOTTOM_PADDING = 0.05
REVERSE_IMAGE = False

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CMAP_CHOICES = [
    "Greys", "Blues", "Reds", "Oranges", "Purples", "inferno",
    "hot", "afmhot", "copper", "viridis", "gist_earth",
    "pink", "summer", "winter", "cool", "Wistia",
]

ITERATION_CHOICES = [10_000, 100_000, 1_000_000, 10_000_000, 100_000_000, 1_000_000_000]

BACKGROUND_CHOICES = ["default", "force_white", "force_black"]

GRADIO_CSS = """
/* ── GLOBAL RESET & DARK BASE ── */
*, *::before, *::after {
  box-sizing: border-box;
}

.gradio-container .main,
.gradio-container .wrap,
.gradio-container .contain,
.gradio-container > div {
  background: transparent !important;
}

body {
  background: #07080f !important;
}

/* Kill all Gradio gray/white wrapper backgrounds */
.gradio-container .block,
.gradio-container .form,
.gradio-container .row,
.gradio-container .col,
.gradio-container .styler,
.gradio-container .padded,
.gradio-container .container,
.gradio-container .prose,
.gradio-container .svelte-1svsvh2,
.gradio-container .svelte-1vd8eap,
.gradio-container .svelte-1xp0cw7,
.gradio-container .svelte-1nguped,
.gradio-container .svelte-lag733,
.gradio-container .svelte-vuh1yp,
.gradio-container .svelte-1jkmaen,
.gradio-container .svelte-7ddecg,
.gradio-container [class*="svelte-"] {
  background: transparent !important;
  background-color: transparent !important;
}
/* Kill all Gradio borders, outlines, and box-shadows on wrappers */
.gradio-container .block,
.gradio-container .form,
.gradio-container .padded,
.gradio-container .container,
.gradio-container .styler,
.gradio-container [class*="svelte-"] {
  border: none !important;
  border-width: 0 !important;
  border-color: transparent !important;
  box-shadow: none !important;
  outline: none !important;
}

/* Reset the inline CSS variable borders Gradio injects */
.gradio-container .styler {
  --block-border-width: 0px !important;
  --button-border-width: 0px !important;
  --form-gap-width: 0px !important;
  --layout-gap: 0px !important;
}

/* Remove the 1px form divider lines between stacked inputs */
.gradio-container .form {
  gap: 0 !important;
  border: none !important;
}

.gradio-container .form > .block {
  border: none !important;
  border-bottom: none !important;
  border-top: none !important;
}

/* Re-apply borders ONLY where you want them */
.cyber-panel {
  border: 1px solid rgba(0, 255, 200, 0.12) !important;
  box-shadow:
    0 0 20px rgba(0, 0, 0, 0.5),
    0 0 10px rgba(0, 255, 200, 0.04),
    inset 0 1px 0 rgba(0, 255, 200, 0.06) !important;
}

.gradio-container .gr-group,
.gradio-container .group {
  border: 1px solid rgba(0, 255, 200, 0.08) !important;
  box-shadow: none !important;
}

.gradio-container input[type="text"],
.gradio-container input[type="number"],
.gradio-container textarea,
.gradio-container select {
  border: 1px solid rgba(0, 255, 200, 0.12) !important;
}

.gradio-container input:focus,
.gradio-container textarea:focus,
.gradio-container select:focus {
  border: 1px solid rgba(0, 255, 200, 0.4) !important;
  box-shadow: 0 0 12px rgba(0, 255, 200, 0.1) !important;
}

#title-bar {
  border: 1px solid rgba(0, 255, 200, 0.2) !important;
  box-shadow:
    0 0 15px rgba(0, 255, 200, 0.07),
    inset 0 1px 0 rgba(0, 255, 200, 0.08) !important;
}

#render-btn {
  border: none !important;
  box-shadow:
    0 0 20px rgba(0, 255, 200, 0.2),
    0 0 40px rgba(0, 180, 216, 0.1) !important;
}

#output-box {
  border: 1px solid rgba(0, 255, 200, 0.1) !important;
}

/* Re-apply dark bg only to actual input fields */
.gradio-container input[type="text"],
.gradio-container input[type="number"],
.gradio-container textarea,
.gradio-container select {
  background: rgba(5, 8, 18, 0.8) !important;
  background-color: rgba(5, 8, 18, 0.8) !important;
}

/* Re-apply panel backgrounds (these are your intentional styled panels) */
.cyber-panel {
  background: linear-gradient(180deg, rgba(10, 14, 24, 0.92), rgba(8, 10, 18, 0.96)) !important;
}

/* Re-apply group backgrounds */
.gradio-container .gr-group,
.gradio-container .group {
  background: rgba(5, 10, 20, 0.4) !important;
}

.gradio-container {
  background: #07080f !important;
  background-color: #07080f !important;
  color: #e0e6f0 !important;
  font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
  min-height: 100vh;
}

/* Subtle grid pattern overlay */
.gradio-container::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    linear-gradient(rgba(0, 255, 200, 0.015) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 255, 200, 0.015) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

/* Radial glow accents */
.gradio-container::after {
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse 600px 400px at 10% 10%, rgba(0, 255, 200, 0.06), transparent),
    radial-gradient(ellipse 500px 500px at 90% 80%, rgba(255, 0, 120, 0.05), transparent),
    radial-gradient(ellipse 400px 300px at 50% 0%, rgba(100, 120, 255, 0.04), transparent);
  pointer-events: none;
  z-index: 0;
}

/* Make content sit above overlays */
.gradio-container > * {
  position: relative;
  z-index: 1;
}

/* ── TITLE BAR ── */
#title-bar {
  margin: 0 0 10px 0 !important;
  padding: 14px 20px !important;
  background: linear-gradient(135deg, rgba(10, 12, 22, 0.95), rgba(15, 18, 30, 0.9)) !important;
  border: 1px solid rgba(0, 255, 200, 0.2) !important;
  border-radius: 12px !important;
  box-shadow:
    0 0 15px rgba(0, 255, 200, 0.07),
    inset 0 1px 0 rgba(0, 255, 200, 0.08) !important;
  text-align: left;
}

#title-bar h1 {
  margin: 0 !important;
  padding: 0 !important;
  font-size: 22px !important;
  font-weight: 800 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  background: linear-gradient(90deg, #00ffc8, #00b4d8 40%, #ff006e 100%) !important;
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  background-clip: text !important;
  line-height: 1.3 !important;
}

#title-bar p {
  margin: 2px 0 0 0 !important;
  padding: 0 !important;
  font-size: 11px !important;
  color: #5a7a8a !important;
  letter-spacing: 0.15em !important;
  text-transform: uppercase !important;
}

/* ── PANEL CARDS ── */
.cyber-panel {
  background: linear-gradient(180deg, rgba(10, 14, 24, 0.92), rgba(8, 10, 18, 0.96)) !important;
  border: 1px solid rgba(0, 255, 200, 0.12) !important;
  border-radius: 14px !important;
  padding: 16px !important;
  box-shadow:
    0 0 20px rgba(0, 0, 0, 0.5),
    0 0 10px rgba(0, 255, 200, 0.04),
    inset 0 1px 0 rgba(0, 255, 200, 0.06) !important;
}

/* ── SECTION HEADERS ── */
.section-label {
  font-size: 10px !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  color: #00ffc8 !important;
  font-weight: 700 !important;
  margin: 0 0 6px 2px !important;
  padding: 0 !important;
  line-height: 1 !important;
  text-shadow: 0 0 12px rgba(0, 255, 200, 0.3) !important;
}

.section-label span {
  color: #00ffc8 !important;
}

/* ── GENERAL BLOCK OVERRIDES ── */
.gradio-container .block {
  background: transparent !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 0 !important;
}

/* ── ALL FORM LABELS ── */
.gradio-container label,
.gradio-container .label-wrap span,
.gradio-container .gr-form .wrap .label {
  color: #6b8a99 !important;
  font-size: 10px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
}

/* ── TEXT INPUTS & TEXTAREAS ── */
.gradio-container input[type="text"],
.gradio-container input[type="number"],
.gradio-container textarea,
.gradio-container .wrap input,
.gradio-container .wrap textarea {
  background: rgba(5, 8, 18, 0.8) !important;
  color: #c8dce8 !important;
  border: 1px solid rgba(0, 255, 200, 0.12) !important;
  border-radius: 8px !important;
  font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace !important;
  font-size: 13px !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}

.gradio-container input:focus,
.gradio-container textarea:focus {
  border-color: rgba(0, 255, 200, 0.4) !important;
  box-shadow: 0 0 12px rgba(0, 255, 200, 0.1) !important;
  outline: none !important;
}

/* ── HASH BOX ── */
#hash-box textarea {
  min-height: 40px !important;
  max-height: 40px !important;
  line-height: 1.2 !important;
  padding: 10px 12px !important;
  resize: none !important;
}

/* ── DROPDOWNS ── */
.gradio-container .wrap.svelte-1kyjfya,
.gradio-container .secondary-wrap,
.gradio-container .wrap[data-testid] {
  background: rgba(5, 8, 18, 0.8) !important;
  border: 1px solid rgba(0, 255, 200, 0.12) !important;
  border-radius: 8px !important;
}

.gradio-container .wrap.svelte-1kyjfya input,
.gradio-container .secondary-wrap input {
  color: #c8dce8 !important;
}

/* Dropdown list */
.gradio-container ul[role="listbox"],
.gradio-container .dropdown-menu,
.gradio-container ul.options {
  background: #0a0e1a !important;
  border: 1px solid rgba(0, 255, 200, 0.15) !important;
  border-radius: 8px !important;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6) !important;
}

.gradio-container ul[role="listbox"] li,
.gradio-container .dropdown-menu li,
.gradio-container ul.options li {
  color: #a0b8c8 !important;
}

.gradio-container ul[role="listbox"] li:hover,
.gradio-container ul[role="listbox"] li.selected,
.gradio-container .dropdown-menu li:hover {
  background: rgba(0, 255, 200, 0.1) !important;
  color: #00ffc8 !important;
}

/* ── NUMBER INPUTS ── */
.gradio-container input[type="number"] {
  background: rgba(5, 8, 18, 0.8) !important;
  color: #c8dce8 !important;
  border: 1px solid rgba(0, 255, 200, 0.12) !important;
  border-radius: 8px !important;
}

/* ── SLIDERS ── */
.gradio-container input[type="range"] {
  accent-color: #00ffc8 !important;
}

.gradio-container .range-slider input[type="number"] {
  background: rgba(5, 8, 18, 0.9) !important;
  color: #c8dce8 !important;
  border: 1px solid rgba(0, 255, 200, 0.12) !important;
}

/* ── CHECKBOX ── */
.gradio-container input[type="checkbox"] {
  accent-color: #00ffc8 !important;
}

.gradio-container .gr-check-radio label {
  color: #8aa0b0 !important;
}

/* ── RENDER BUTTON ── */
#render-btn {
  background: linear-gradient(135deg, #00ffc8 0%, #00b4d8 50%, #006eff 100%) !important;
  border: none !important;
  color: #030a08 !important;
  font-weight: 800 !important;
  font-size: 13px !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  padding: 10px 24px !important;
  border-radius: 8px !important;
  box-shadow:
    0 0 20px rgba(0, 255, 200, 0.2),
    0 0 40px rgba(0, 180, 216, 0.1) !important;
  transition: all 0.2s ease !important;
  cursor: pointer !important;
}

#render-btn:hover {
  filter: brightness(1.1) !important;
  box-shadow:
    0 0 25px rgba(0, 255, 200, 0.3),
    0 0 50px rgba(0, 180, 216, 0.15) !important;
  transform: translateY(-1px) !important;
}

#render-btn:active {
  transform: translateY(0) !important;
  filter: brightness(0.95) !important;
}

/* ── OUTPUT IMAGE ── */
#output-box {
  background: rgba(5, 8, 18, 0.6) !important;
  border: 1px solid rgba(0, 255, 200, 0.1) !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}

#output-box img {
  border-radius: 8px !important;
}

/* ── GROUP STYLING ── */
.gradio-container .gr-group,
.gradio-container .group {
  background: rgba(5, 10, 20, 0.4) !important;
  border: 1px solid rgba(0, 255, 200, 0.08) !important;
  border-radius: 10px !important;
  padding: 10px !important;
  margin-bottom: 6px !important;
}

/* ── COMPACT SPACING ── */
.compact-gap {
  gap: 10px !important;
}

.tight-col > .block,
.tight-col > div {
  margin-bottom: 2px !important;
  padding-bottom: 0 !important;
}

.tight-col .gr-group,
.tight-col .group {
  margin-bottom: 6px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #07080f;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 255, 200, 0.15);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 255, 200, 0.3);
}

/* ── HIDE FOOTER ── */
footer {
  display: none !important;
}

/* ── FIX GRADIO DARK OVERRIDES ── */
.gradio-container .gr-box {
  background: transparent !important;
  border: none !important;
}

.gradio-container .gr-padded {
  padding: 0 !important;
}

.gradio-container .gr-form {
  background: transparent !important;
  border: none !important;
}

/* Ensure all text on dark bg is light */
.gradio-container span,
.gradio-container p,
.gradio-container div {
  color: inherit;
}

/* Fix Markdown rendered inside panels */
.gradio-container .md h3,
.gradio-container .prose h3,
.gradio-container .markdown-text h3 {
  color: #00ffc8 !important;
  font-size: 10px !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  font-weight: 700 !important;
  margin: 0 0 4px 0 !important;
  text-shadow: 0 0 12px rgba(0, 255, 200, 0.3) !important;
}

.gradio-container .md strong,
.gradio-container .prose strong {
  color: #ff006e !important;
  font-size: 10px !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  text-shadow: 0 0 8px rgba(255, 0, 110, 0.2) !important;
}

/* Reverse Image checkbox - make it a toggle button style */
.gradio-container input[type="checkbox"] {
  appearance: none !important;
  -webkit-appearance: none !important;
  width: 40px !important;
  height: 22px !important;
  background: rgba(255, 0, 110, 0.15) !important;
  border: 2px solid rgba(255, 0, 110, 0.4) !important;
  border-radius: 12px !important;
  position: relative !important;
  cursor: pointer !important;
  transition: all 0.3s ease !important;
  vertical-align: middle !important;
}

.gradio-container input[type="checkbox"]::after {
  content: '' !important;
  position: absolute !important;
  top: 2px !important;
  left: 2px !important;
  width: 14px !important;
  height: 14px !important;
  background: #ff006e !important;
  border-radius: 50% !important;
  transition: all 0.3s ease !important;
  opacity: 0.5 !important;
  box-shadow: none !important;
}

.gradio-container input[type="checkbox"]:checked {
  background: rgba(0, 255, 200, 0.2) !important;
  border-color: #00ffc8 !important;
  box-shadow:
    0 0 12px rgba(0, 255, 200, 0.3),
    0 0 30px rgba(0, 255, 200, 0.1) !important;
}

.gradio-container input[type="checkbox"]:checked::after {
  left: 20px !important;
  background: #00ffc8 !important;
  opacity: 1 !important;
  box-shadow: 0 0 8px rgba(0, 255, 200, 0.6) !important;
}

/* Make the checkbox label text react too */
.gradio-container input[type="checkbox"] + span,
.gradio-container input[type="checkbox"] ~ span {
  color: #5a4050 !important;
  transition: all 0.3s ease !important;
}

.gradio-container input[type="checkbox"]:checked + span,
.gradio-container input[type="checkbox"]:checked ~ span {
  color: #00ffc8 !important;
  text-shadow: 0 0 10px rgba(0, 255, 200, 0.3) !important;
}

/* Remove inner outline on dropdown listbox inputs */
.gradio-container input[role="listbox"],
.gradio-container input.svelte-1hfxrpf {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

.gradio-container input[role="listbox"]:focus,
.gradio-container input.svelte-1hfxrpf:focus {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}

/* ── MOBILE RESPONSIVE ── */
@media (max-width: 768px) {
  #title-bar h1 {
    font-size: 16px !important;
  }
}
"""

# ── Library ───────────────────────────────────────────────────────────────────

import base64
import binascii
import datetime as dt
import hashlib
import json
import pickle
import struct
import warnings
from pathlib import Path
from typing import Iterable

import imageio.v2 as imageio
import matplotlib.cm as cm
import numpy as np
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from numba import njit


DEFAULT_MAX_ITERATIONS = 100_000_000
DEFAULT_HEIGHT = 476
DEFAULT_WIDTH = 690
DEFAULT_DENSITY = 15
DEFAULT_CMAP = "inferno"
DEFAULT_LEFT_PADDING = 0.35
DEFAULT_RIGHT_PADDING = 0.35
DEFAULT_TOP_PADDING = 0.05
DEFAULT_BOTTOM_PADDING = 0.05
DEFAULT_PASSWORD = "cha0tic"
DEFAULT_SHOW_PROGRESS = True
DEFAULT_PROGRESS_DESC = "Rendering attractor"
DEFAULT_BACKGROUND_COLOR = ""
DEFAULT_FLIP = False
DEFAULT_SOURCE_HASH = None
DEFAULT_SECRET_NOTE = ""
DEFAULT_TITLE = ""
DEFAULT_URL = ""
DEFAULT_USE_CACHE = False
CACHE_SCHEMA_VERSION = "grid-cache.v1"
CACHE_ALGO_VERSION = "attractor-grid.v1"


def _parse_hex_color(hex_color: str) -> np.ndarray:
    """Convert a hex color string into an RGB uint8 array.

    Accepted formats: #RRGGBB, RRGGBB, #RGB, RGB.
    """
    s = (hex_color or "").strip()
    if s.startswith("#"):
        s = s[1:]

    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)

    if len(s) != 6:
        raise ValueError(f"Invalid hex color '{hex_color}'. Use #RRGGBB, RRGGBB, #RGB, or RGB.")

    try:
        rgb = np.array([int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)], dtype=np.uint8)
    except ValueError as exc:
        raise ValueError(f"Invalid hex color '{hex_color}'. Contains non-hex characters.") from exc

    return rgb


def _progress_range(total: int, show_progress: bool, progress_desc: str) -> Iterable[int]:
    """Return an iterator for chunk progress, optionally with tqdm output."""
    if total <= 0:
        return range(0)

    if not show_progress:
        return range(total)

    try:
        from tqdm.auto import trange

        return trange(total, desc=progress_desc, unit="chunk")
    except Exception:
        print(f"{progress_desc}: tqdm unavailable, running without visual bar")
        return range(total)


def hash_to_args(hash_text: str, password: str = DEFAULT_PASSWORD) -> dict:
    """Decrypt an encrypted hash string into attractor arguments."""
    combined = base64.urlsafe_b64decode(hash_text.encode("utf-8"))
    salt, nonce, tag, ciphertext = combined[:16], combined[16:28], combined[28:44], combined[44:]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = kdf.derive(password.encode())

    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    serialized = decryptor.update(ciphertext) + decryptor.finalize()
    values = pickle.loads(serialized)

    return {
        **{f"a_{i + 1}": values[i] for i in range(6)},
        **{f"b_{i + 1}": values[i + 6] for i in range(6)},
        "x_0": values[-6],
        "y_0": values[-5],
        "x_min": values[-4],
        "y_min": values[-3],
        "x_max": values[-2],
        "y_max": values[-1],
    }


def _png_text_chunk(chunk_key: str, text_value: str) -> bytes:
    """Build a PNG tEXt chunk with the given key/value pair."""
    if "\x00" in chunk_key:
        raise ValueError("PNG tEXt key cannot contain NUL")

    chunk_type = b"tEXt"
    data = chunk_key.encode("latin-1") + b"\x00" + text_value.encode("utf-8")
    length = struct.pack(">I", len(data))
    crc = struct.pack(">I", binascii.crc32(chunk_type + data) & 0xFFFFFFFF)
    return length + chunk_type + data + crc


def _embed_png_text_chunk(png_path: Path, key: str, value: str) -> None:
    """Embed one tEXt chunk into a PNG file before IEND."""
    raw = png_path.read_bytes()
    signature = b"\x89PNG\r\n\x1a\n"
    if not raw.startswith(signature):
        raise ValueError(f"Not a PNG file: {png_path}")

    iend_chunk = b"\x00\x00\x00\x00IEND\xaeB`\x82"
    idx = raw.rfind(iend_chunk)
    if idx == -1:
        raise ValueError("Invalid PNG: IEND chunk not found")

    text_chunk = _png_text_chunk(key, value)
    png_path.write_bytes(raw[:idx] + text_chunk + raw[idx:])


def _build_json_payload(
    hash_text: str,
    args: dict,
    render_config: dict,
    output_path: Path,
    variant: str,
    secret_note: str = "",
    title: str = "",
    url: str = "",
) -> dict:
    """Create the JSON payload stored as sidecar and embedded PNG metadata."""
    json_payload = {
        "schema": "chaos-vis-image-gen.json-payload.v1",
        "created_at_utc": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "output_file": output_path.name,
        "variant": variant,
        "hash": hash_text.strip(),
        "args": args,
        "render_config": render_config,
    }
    if title:
        json_payload["title"] = title
    if url:
        json_payload["url"] = url
    if secret_note:
        json_payload["secret_note"] = secret_note
    return json_payload


def _generated_hash_from_args(args: dict) -> str:
    """Build a stable synthetic hash when no source hash is provided."""
    canonical = json.dumps(args, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"generated:{digest}"


def _default_cache_dir() -> Path:
    """Return ~/.cache/<repository-name> as the default cache directory."""
    repository_name = Path(__file__).resolve().parents[2].name
    return Path.home() / ".cache" / repository_name


def _cache_key_for_grid(
    args: dict,
    max_iterations: int,
    width: int,
    height: int,
    left_padding: float,
    right_padding: float,
    top_padding: float,
    bottom_padding: float,
) -> str:
    """Build a deterministic cache key for raw simulation grid output."""
    cache_input = {
        "cache_schema": CACHE_SCHEMA_VERSION,
        "cache_algo": CACHE_ALGO_VERSION,
        "args": args,
        "max_iterations": max_iterations,
        "width": width,
        "height": height,
        "left_padding": left_padding,
        "right_padding": right_padding,
        "top_padding": top_padding,
        "bottom_padding": bottom_padding,
    }
    canonical = json.dumps(cache_input, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _load_cached_grid(cache_dir: Path, cache_key: str) -> tuple[np.ndarray, bool]:
    """Load cached raw grid if present. Returns (grid, loaded)."""
    cache_file = cache_dir / f"{cache_key}.npz"
    if not cache_file.exists():
        return np.empty((0, 0), dtype=np.float32), False

    data = np.load(cache_file)
    grid = data["grid"].astype(np.float32, copy=False)
    return grid, True


def _save_cached_grid(cache_dir: Path, cache_key: str, grid: np.ndarray) -> None:
    """Persist raw simulation grid to cache directory."""
    cache_file = cache_dir / f"{cache_key}.npz"
    np.savez_compressed(cache_file, grid=grid.astype(np.float32, copy=False))


def _write_image_and_json_payload(output_path: Path, rgb_image: np.ndarray, json_payload: dict) -> None:
    """Write PNG output, JSON sidecar, and embedded JSON payload."""
    imageio.imwrite(str(output_path), rgb_image, format="png")

    json_payload_text = json.dumps(json_payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

    sidecar_path = output_path.with_suffix(".json")
    sidecar_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    _embed_png_text_chunk(output_path, "chaos_vis_image_gen", json_payload_text)


def extract_json_payload_from_image(image_path: str | Path, print_detail: bool = True) -> dict:
    """Read and return the embedded JSON payload from a PNG file."""
    image_path = Path(image_path)
    raw = image_path.read_bytes()
    signature = b"\x89PNG\r\n\x1a\n"
    if not raw.startswith(signature):
        raise ValueError(f"Not a PNG file: {image_path}")

    offset = len(signature)
    while offset + 8 <= len(raw):
        length = int.from_bytes(raw[offset : offset + 4], "big")
        chunk_type = raw[offset + 4 : offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        if data_end + 4 > len(raw):
            raise ValueError("Invalid PNG: chunk length exceeds file size")

        data = raw[data_start:data_end]

        if chunk_type == b"tEXt":
            nul_idx = data.find(b"\x00")
            if nul_idx != -1:
                key = data[:nul_idx].decode("latin-1")
                value = data[nul_idx + 1 :].decode("utf-8")
                if key == "chaos_vis_image_gen":
                    json_payload = json.loads(value)
                    title = str(json_payload.get("title", "") or "")
                    url = str(json_payload.get("url", "") or "")
                    secret_note = str(json_payload.get("secret_note", "") or "")
                    if print_detail:
                        if title:
                            print(f"Title: {title}")
                        if url:
                            print(f"URL: {url}")
                        if secret_note:
                            print("Found a secret note in the image!\n")
                            print(secret_note)
                    return json_payload

        offset = data_end + 4

    raise ValueError(f"No embedded chaos_vis_image_gen JSON payload found in {image_path}")


def _assert_embedded_json_payload_matches(image_path: Path, expected_json_payload: dict) -> None:
    """Assert that extracted embedded payload matches the payload we wrote."""
    actual_json_payload = extract_json_payload_from_image(image_path)
    expected_canonical = json.dumps(expected_json_payload, sort_keys=True, ensure_ascii=False, default=str)
    actual_canonical = json.dumps(actual_json_payload, sort_keys=True, ensure_ascii=False, default=str)
    assert (
        actual_canonical == expected_canonical
    ), "Embedded JSON payload mismatch: extracted PNG payload != expected payload"


@njit
def _compute_grid_and_last_position(x0, y0, ax, ay, xmin, xmax, ymin, ymax, x_scale, y_scale, grid, num_iterations):
    """Accumulate attractor visit counts and return updated grid and final position."""
    x, y = x0, y0
    for _ in range(num_iterations):
        ix = int((x - xmin) * x_scale)
        iy = int((y - ymin) * y_scale)
        if 0 <= ix < grid.shape[1] and 0 <= iy < grid.shape[0]:
            grid[grid.shape[0] - iy - 1, ix] += 1.0

        x_next = ax[0] + ax[1] * x + ax[2] * x * x + ax[3] * x * y + ax[4] * y + ax[5] * y * y
        y_next = ay[0] + ay[1] * x + ay[2] * x * x + ay[3] * x * y + ay[4] * y + ay[5] * y * y
        x, y = x_next, y_next

    return grid, x, y


def render_cover_from_args(
    args: dict,
    output_path: str | Path,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    left_padding: float = DEFAULT_LEFT_PADDING,
    right_padding: float = DEFAULT_RIGHT_PADDING,
    top_padding: float = DEFAULT_TOP_PADDING,
    bottom_padding: float = DEFAULT_BOTTOM_PADDING,
    density: int = DEFAULT_DENSITY,
    cmap: str = DEFAULT_CMAP,
    source_hash: str | None = DEFAULT_SOURCE_HASH,
    show_progress: bool = DEFAULT_SHOW_PROGRESS,
    progress_desc: str = DEFAULT_PROGRESS_DESC,
    background_color: str = DEFAULT_BACKGROUND_COLOR,
    flip: bool = DEFAULT_FLIP,
    secret_note: str = DEFAULT_SECRET_NOTE,
    title: str = DEFAULT_TITLE,
    url: str = DEFAULT_URL,
    use_cache: bool = DEFAULT_USE_CACHE,
) -> Path:
    """Render one cover image from attractor arguments and write JSON payload metadata."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if width <= 1 or height <= 1:
        raise ValueError("width and height must both be greater than 1")

    ax = [args[f"a_{i}"] for i in range(1, 7)]
    ay = [args[f"b_{i}"] for i in range(1, 7)]
    x0, y0 = args["x_0"], args["y_0"]
    xmin, ymin, xmax, ymax = args["x_min"], args["y_min"], args["x_max"], args["y_max"]

    x_span = xmax - xmin
    y_span = ymax - ymin
    xmin -= left_padding * x_span
    xmax += right_padding * x_span
    ymin -= bottom_padding * y_span
    ymax += top_padding * y_span

    if xmax <= xmin or ymax <= ymin:
        raise ValueError("Padding resulted in invalid bounds (xmax<=xmin or ymax<=ymin)")

    x_scale = (width - 1) / (xmax - xmin)
    y_scale = (height - 1) / (ymax - ymin)

    grid = np.zeros((height, width), dtype=np.float32)

    grid_loaded_from_cache = False
    if use_cache:
        try:
            cache_dir = _default_cache_dir()
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_key = _cache_key_for_grid(
                args=args,
                max_iterations=max_iterations,
                width=width,
                height=height,
                left_padding=left_padding,
                right_padding=right_padding,
                top_padding=top_padding,
                bottom_padding=bottom_padding,
            )
            cached_grid, grid_loaded_from_cache = _load_cached_grid(cache_dir, cache_key)
            if grid_loaded_from_cache:
                grid = cached_grid
        except Exception as exc:
            warnings.warn(f"Cache unavailable, continuing without cache: {exc}", stacklevel=2)
            grid_loaded_from_cache = False

    if not grid_loaded_from_cache:
        chunk_size = 2_000_000
        chunks = max_iterations // chunk_size
        remainder = max_iterations % chunk_size

        if show_progress:
            print("Preparing JIT kernel (first chunk may take longer)...")

        for _ in _progress_range(chunks, show_progress=show_progress, progress_desc=progress_desc):
            grid, x0, y0 = _compute_grid_and_last_position(
                x0, y0, ax, ay, xmin, xmax, ymin, ymax, x_scale, y_scale, grid, chunk_size
            )
        if remainder:
            if show_progress:
                print(f"Processing remainder chunk ({remainder} iterations)...")
            grid, x0, y0 = _compute_grid_and_last_position(
                x0, y0, ax, ay, xmin, xmax, ymin, ymax, x_scale, y_scale, grid, remainder
            )

        if use_cache:
            try:
                cache_dir = _default_cache_dir()
                cache_dir.mkdir(parents=True, exist_ok=True)
                cache_key = _cache_key_for_grid(
                    args=args,
                    max_iterations=max_iterations,
                    width=width,
                    height=height,
                    left_padding=left_padding,
                    right_padding=right_padding,
                    top_padding=top_padding,
                    bottom_padding=bottom_padding,
                )
                _save_cached_grid(cache_dir, cache_key, grid)
            except Exception as exc:
                warnings.warn(f"Failed to write cache, continuing: {exc}", stacklevel=2)

    zero_mask = grid == 0

    grid_min, grid_max = float(grid.min()), float(grid.max())
    if grid_max > grid_min:
        grid = (grid - grid_min) / (grid_max - grid_min)

    epsilon = 1e-10
    for _ in range(density):
        grid = np.log1p(grid + epsilon) / np.log1p(1 + epsilon)

    cmap_func = cm.get_cmap(cmap)
    rgba_image = cmap_func(grid)
    rgb_image = (np.delete(rgba_image, 3, 2) * 255).astype(np.uint8)

    final_image = (255 - rgb_image).astype(np.uint8) if flip else rgb_image
    if background_color.strip():
        final_image[zero_mask] = _parse_hex_color(background_color)
    effective_hash = source_hash.strip() if (source_hash and source_hash.strip()) else _generated_hash_from_args(args)

    render_config = {
        "max_iterations": max_iterations,
        "width": width,
        "height": height,
        "left_padding": left_padding,
        "right_padding": right_padding,
        "top_padding": top_padding,
        "bottom_padding": bottom_padding,
        "density": density,
        "cmap": cmap,
        "background_color": background_color,
        "flip": flip,
        "use_cache": use_cache,
    }

    json_payload = _build_json_payload(
        hash_text=effective_hash,
        args=args,
        render_config=render_config,
        output_path=output_path,
        variant="inverted" if flip else "normal",
        secret_note=secret_note,
        title=title,
        url=url,
    )
    _write_image_and_json_payload(output_path, final_image, json_payload)
    _assert_embedded_json_payload_matches(output_path, json_payload)

    return output_path


def render_cover_from_json_payload(json_payload: dict, output_path: str | Path | None = None) -> Path:
    """Render a cover image from a previously stored JSON payload."""
    args = json_payload["args"]
    render_config = json_payload.get("render_config", {})

    output_target = output_path or json_payload.get("output_file")
    if not output_target:
        raise ValueError("output_path is required when json_payload has no output_file")

    return render_cover_from_args(
        args=args,
        output_path=output_target,
        max_iterations=int(render_config.get("max_iterations", DEFAULT_MAX_ITERATIONS)),
        width=int(render_config.get("width", DEFAULT_WIDTH)),
        height=int(render_config.get("height", DEFAULT_HEIGHT)),
        left_padding=float(render_config.get("left_padding", render_config.get("x_padding", DEFAULT_LEFT_PADDING))),
        right_padding=float(render_config.get("right_padding", render_config.get("x_padding", DEFAULT_RIGHT_PADDING))),
        top_padding=float(render_config.get("top_padding", render_config.get("y_padding", DEFAULT_TOP_PADDING))),
        bottom_padding=float(render_config.get("bottom_padding", render_config.get("y_padding", DEFAULT_BOTTOM_PADDING))),
        density=int(render_config.get("density", DEFAULT_DENSITY)),
        cmap=str(render_config.get("cmap", DEFAULT_CMAP)),
        source_hash=str(json_payload.get("hash", "")),
        show_progress=bool(render_config.get("show_progress", DEFAULT_SHOW_PROGRESS)),
        progress_desc=str(render_config.get("progress_desc", DEFAULT_PROGRESS_DESC)),
        background_color=str(render_config.get("background_color", DEFAULT_BACKGROUND_COLOR)),
        flip=bool(render_config.get("flip", DEFAULT_FLIP)),
        secret_note=str(json_payload.get("secret_note", DEFAULT_SECRET_NOTE)),
        title=str(json_payload.get("title", DEFAULT_TITLE)),
        url=str(json_payload.get("url", DEFAULT_URL)),
        use_cache=bool(render_config.get("use_cache", DEFAULT_USE_CACHE)),
    )


def render_cover_from_hash(
    hash_text: str,
    output_path: str | Path,
    password: str = DEFAULT_PASSWORD,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    left_padding: float = DEFAULT_LEFT_PADDING,
    right_padding: float = DEFAULT_RIGHT_PADDING,
    top_padding: float = DEFAULT_TOP_PADDING,
    bottom_padding: float = DEFAULT_BOTTOM_PADDING,
    density: int = DEFAULT_DENSITY,
    cmap: str = DEFAULT_CMAP,
    show_progress: bool = DEFAULT_SHOW_PROGRESS,
    progress_desc: str = DEFAULT_PROGRESS_DESC,
    background_color: str = DEFAULT_BACKGROUND_COLOR,
    flip: bool = DEFAULT_FLIP,
    secret_note: str = DEFAULT_SECRET_NOTE,
    title: str = DEFAULT_TITLE,
    url: str = DEFAULT_URL,
    use_cache: bool = DEFAULT_USE_CACHE,
) -> Path:
    """Decrypt a hash and render a cover image using the resolved attractor arguments."""
    args = hash_to_args(hash_text.strip(), password=password)
    return render_cover_from_args(
        args=args,
        output_path=output_path,
        max_iterations=max_iterations,
        width=width,
        height=height,
        left_padding=left_padding,
        right_padding=right_padding,
        top_padding=top_padding,
        bottom_padding=bottom_padding,
        density=density,
        cmap=cmap,
        source_hash=hash_text,
        show_progress=show_progress,
        progress_desc=progress_desc,
        background_color=background_color,
        flip=flip,
        secret_note=secret_note,
        title=title,
        url=url,
        use_cache=use_cache,
    )

# ── Helper ────────────────────────────────────────────────────────────────────

def render_image(
    hash_text,
    cmap,
    max_iterations,
    width,
    height,
    background,
    density,
    left_padding,
    right_padding,
    top_padding,
    bottom_padding,
    reverse_image,
):
    background_color = ""
    if background == "force_white":
        background_color = "#FFFFFF"
    elif background == "force_black":
        background_color = "#000000"

    output_path = os.path.join(OUTPUT_DIR, "cover.png")

    render_cover_from_hash(
        hash_text=hash_text.strip(),
        max_iterations=int(max_iterations),
        output_path=output_path,
        width=int(width),
        height=int(height),
        left_padding=float(left_padding),
        right_padding=float(right_padding),
        top_padding=float(top_padding),
        bottom_padding=float(bottom_padding),
        density=int(density),
        background_color=background_color,
        cmap=cmap,
        flip=reverse_image,
        use_cache=True,
    )

    return Image.open(output_path)


# ── UI ────────────────────────────────────────────────────────────────────────

def launch_ui(
    hash_text,
    cmap,
    max_iterations,
    width,
    height,
    background,
    density,
    left_padding,
    right_padding,
    top_padding,
    bottom_padding,
    reverse_image,
    css,
):
    warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"gradio\..*")
    warnings.filterwarnings("ignore", message=r".*parameter in the Blocks constructor.*")
    logging.getLogger("gradio").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.ERROR)

    with gr.Blocks(css=css, fill_height=True, theme=gr.themes.Base()) as demo:
        with gr.Column(elem_id="app-shell"):
            gr.HTML("""
            <div id="title-bar">
              <h1>⬡ Chaos Vis - Image Gen Interface</h1>
              <p>Visualize Random Attractors</p>
            </div>
            """)

            with gr.Row(equal_height=True, elem_classes=["compact-gap"]):
                # ── LEFT: Input + Output ──
                with gr.Column(scale=11, min_width=540, elem_classes=["cyber-panel"]):
                    gr.Markdown("### ◈ Input · Paste a hash from [@bo_is_coding](https://instagram.com/bo_is_coding)")

                    hash_text_box = gr.Textbox(
                        value=hash_text,
                        label="Hash",
                        lines=1,
                        max_lines=1,
                        elem_id="hash-box",
                        container=True,
                    )

                    render_button = gr.Button("◆ Render", variant="primary", elem_id="render-btn")

                    output_image = gr.Image(
                        label="Output",
                        type="pil",
                        height=430,
                        elem_id="output-box",
                    )

                # ── RIGHT: Controls ──
                with gr.Column(scale=9, min_width=400, elem_classes=["cyber-panel", "tight-col"]):
                    gr.Markdown("### ◈ Controls")

                    with gr.Group():
                        gr.Markdown("**Canvas**")
                        with gr.Row():
                            width_input = gr.Number(value=width, label="Width", precision=0)
                            height_input = gr.Number(value=height, label="Height", precision=0)

                    with gr.Group():
                        gr.Markdown("**Style**")
                        with gr.Row():
                            background_input = gr.Dropdown(
                                choices=BACKGROUND_CHOICES,
                                value=background,
                                label="Background",
                            )
                            cmap_input = gr.Dropdown(
                                choices=CMAP_CHOICES,
                                value=cmap,
                                label="Colormap",
                            )

                    with gr.Group():
                        gr.Markdown("**Render**")
                        with gr.Row():
                            max_iterations_input = gr.Dropdown(
                                choices=ITERATION_CHOICES,
                                value=int(max_iterations),
                                label="Max Iterations",
                            )
                            density_input = gr.Slider(
                                minimum=0,
                                maximum=50,
                                step=1,
                                value=density,
                                label="Density",
                            )
                        reverse_image_input = gr.Checkbox(
                            value=reverse_image,
                            label="Reverse Image",
                        )

                    with gr.Group():
                        gr.Markdown("**Padding**")
                        with gr.Row():
                            left_padding_input = gr.Slider(
                                minimum=-1, maximum=1, step=0.01,
                                value=left_padding, label="Left",
                            )
                            right_padding_input = gr.Slider(
                                minimum=-1, maximum=1, step=0.01,
                                value=right_padding, label="Right",
                            )
                        with gr.Row():
                            top_padding_input = gr.Slider(
                                minimum=-1, maximum=1, step=0.01,
                                value=top_padding, label="Top",
                            )
                            bottom_padding_input = gr.Slider(
                                minimum=-1, maximum=1, step=0.01,
                                value=bottom_padding, label="Bottom",
                            )

        render_button.click(
            fn=render_image,
            inputs=[
                hash_text_box,
                cmap_input,
                max_iterations_input,
                width_input,
                height_input,
                background_input,
                density_input,
                left_padding_input,
                right_padding_input,
                top_padding_input,
                bottom_padding_input,
                reverse_image_input,
            ],
            outputs=output_image,
        )

    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
        share=False,
        quiet=False,
    )


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    launch_ui(
        hash_text=HASH_TEXT,
        cmap=CMAP,
        max_iterations=MAX_ITERATIONS,
        width=WIDTH,
        height=HEIGHT,
        background=BACKGROUND,
        density=DENSITY,
        left_padding=LEFT_PADDING,
        right_padding=RIGHT_PADDING,
        top_padding=TOP_PADDING,
        bottom_padding=BOTTOM_PADDING,
        reverse_image=REVERSE_IMAGE,
        css=GRADIO_CSS,
    )
