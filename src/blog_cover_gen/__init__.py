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
        "schema": "blog-cover-gen.json-payload.v1",
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


def _write_image_and_json_payload(output_path: Path, rgb_image: np.ndarray, json_payload: dict) -> None:
    """Write PNG output, JSON sidecar, and embedded JSON payload."""
    imageio.imwrite(str(output_path), rgb_image, format="png")

    json_payload_text = json.dumps(json_payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

    sidecar_path = output_path.with_suffix(".json")
    sidecar_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    _embed_png_text_chunk(output_path, "blog_cover_gen", json_payload_text)


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
                if key == "blog_cover_gen":
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

    raise ValueError(f"No embedded blog_cover_gen JSON payload found in {image_path}")


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

    if background_color.strip():
        rgb_image[zero_mask] = _parse_hex_color(background_color)

    final_image = (255 - rgb_image).astype(np.uint8) if flip else rgb_image
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
    )
