#!/usr/bin/env python3
"""Check raster figure dimensions and detect likely blank exports."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageStat


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument("--min-width", type=int, default=1200)
    parser.add_argument("--min-height", type=int, default=800)
    parser.add_argument("--min-stddev", type=float, default=3.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    failures: list[str] = []
    for path in args.images:
        if not path.is_file():
            failures.append(f"missing: {path}")
            continue
        try:
            with Image.open(path) as image:
                width, height = image.size
                sample = image.convert("RGB")
                sample.thumbnail((256, 256))
                stddev = sum(ImageStat.Stat(sample).stddev) / 3
        except Exception as error:
            failures.append(f"unreadable: {path}: {error}")
            continue
        print(f"{path}: {width}x{height}, mean-channel-stddev={stddev:.2f}")
        if width < args.min_width or height < args.min_height:
            failures.append(f"undersized: {path}: {width}x{height}")
        if stddev < args.min_stddev:
            failures.append(f"likely blank: {path}: stddev={stddev:.2f}")
    if failures:
        raise SystemExit("\n".join(failures))


if __name__ == "__main__":
    main()
