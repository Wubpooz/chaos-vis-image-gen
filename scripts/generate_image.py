#!/usr/bin/env python3
import argparse
from pathlib import Path

from blog_cover_gen import render_cover_from_hash


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a single chaos-style blog cover image from an encrypted hash.")
    parser.add_argument("--hash-file", required=True, help="Path to a text file containing one encrypted hash string.")
    parser.add_argument("--password", default="cha0tic", help="Password used to decrypt the hash.")
    parser.add_argument("--output", default="output/cover.png", help="Output PNG path.")
    parser.add_argument("--cmap", default="inferno", help="Matplotlib colormap.")
    parser.add_argument("--density", type=int, default=15, help="Log-density enhancement rounds.")
    parser.add_argument("--iterations", type=int, default=100_000_000, help="Simulation iterations.")
    parser.add_argument("--width", type=int, default=690, help="Output grid width.")
    parser.add_argument("--height", type=int, default=476, help="Output grid height.")
    parser.add_argument("--left-padding", type=float, default=0.35, help="Left padding ratio.")
    parser.add_argument("--right-padding", type=float, default=0.35, help="Right padding ratio.")
    parser.add_argument("--top-padding", type=float, default=0.05, help="Top padding ratio.")
    parser.add_argument("--bottom-padding", type=float, default=0.05, help="Bottom padding ratio.")
    parser.add_argument("--background-color", default="", help="Hex color for zero-density pixels (e.g. #000000).")
    parser.add_argument("--flip", action="store_true", help="Invert final image colors.")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress output.")
    args = parser.parse_args()

    hash_text = Path(args.hash_file).read_text(encoding="utf-8").strip()
    output = render_cover_from_hash(
        hash_text,
        args.output,
        password=args.password,
        max_iterations=args.iterations,
        width=args.width,
        height=args.height,
        left_padding=args.left_padding,
        right_padding=args.right_padding,
        top_padding=args.top_padding,
        bottom_padding=args.bottom_padding,
        density=args.density,
        cmap=args.cmap,
        show_progress=not args.no_progress,
        background_color=args.background_color,
        flip=args.flip,
    )
    print(f"Saved image: {output}")


if __name__ == "__main__":
    main()
