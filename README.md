# chaos-vis-image-gen

## Quick start

Use this [Colab Notebook](https://colab.research.google.com/drive/1Bah3UDoY9OWzAAnxnhXVEl0KoHE8RDGZ?usp=sharing) to get started!

## API usage

### Render from encrypted hash

```python
from chaos_vis_image_gen import render_cover_from_hash

output = render_cover_from_hash(
    hash_text=open("example.hash.txt").read().strip(),
    output_path="output/cover.png",
    password="cha0tic",
    width=690,
    height=476,
    left_padding=0.35,
    right_padding=0.35,
    top_padding=0.05,
    bottom_padding=0.05,
    density=15,
    cmap="inferno",
    background_color="",  # e.g. "#000000" for zero-density pixels
    flip=False,
)
print(output)
```

### Extract JSON payload from image

```python
from chaos_vis_image_gen import extract_json_payload_from_image

json_payload = extract_json_payload_from_image("output/cover.png")
print(json_payload)
```

### Render from JSON payload

```python
from chaos_vis_image_gen import render_cover_from_json_payload, extract_json_payload_from_image

json_payload = extract_json_payload_from_image("output/cover.png")
new_output = render_cover_from_json_payload(json_payload, output_path="output/cover_rebuilt.png")
print(new_output)
```

## Local Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Generate image from hash:

```bash
python scripts/generate_image.py \
  --hash-file example.hash.txt \
  --password cha0tic \
  --output output/cover.png \
  --cmap inferno \
  --density 15 \
  --iterations 100000000 \
  --width 690 \
  --height 476 \
  --left-padding 0.35 \
  --right-padding 0.35 \
  --top-padding 0.05 \
  --bottom-padding 0.05 \
  --background-color ""

# add --flip to invert final colors
# add --no-progress if you don't want tqdm output
```

## JSON payload behavior

For each rendered image `foo.png`, the generator writes:
- sidecar `foo.json`
- embedded PNG `tEXt` JSON payload under key `chaos_vis_image_gen`

`json_payload.hash` is always present:
- If rendering from hash (`render_cover_from_hash`), it stores that source hash.
- If rendering without a source hash, it auto-generates:
  - `generated:<sha256-of-canonical-args-json>`

`json_payload.render_config` includes:
- `max_iterations`
- `width`, `height`
- `left_padding`, `right_padding`, `top_padding`, `bottom_padding`
- `density`, `cmap`
- `background_color`
- `flip`
