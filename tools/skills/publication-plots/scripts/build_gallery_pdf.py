#!/usr/bin/env python3
"""Build a title-plus-images PDF gallery from a JSON specification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image
from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.pdfgen.canvas import Canvas


PAGE_SIZES = {
    "A3-landscape": landscape(A3),
    "A3-portrait": portrait(A3),
    "A4-landscape": landscape(A4),
    "A4-portrait": portrait(A4),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True, help="JSON gallery specification")
    parser.add_argument("--output", type=Path, required=True, help="Output PDF")
    parser.add_argument("--page-size", choices=PAGE_SIZES, default="A3-landscape")
    parser.add_argument("--columns", type=int, default=2)
    return parser.parse_args()


def place_image(canvas: Canvas, path: Path, x: float, y: float, width: float, height: float) -> None:
    with Image.open(path) as image:
        image_width, image_height = image.size
    scale = min(width / image_width, height / image_height)
    draw_width = image_width * scale
    draw_height = image_height * scale
    canvas.drawImage(
        str(path),
        x + (width - draw_width) / 2,
        y + (height - draw_height) / 2,
        width=draw_width,
        height=draw_height,
        preserveAspectRatio=True,
        mask="auto",
    )


def main() -> None:
    args = parse_args()
    if args.columns < 1:
        raise SystemExit("--columns must be positive")
    spec_path = args.spec.resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    sections = spec.get("sections")
    if not isinstance(sections, list) or not sections:
        raise SystemExit("spec.sections must be a non-empty list")

    page_width, page_height = PAGE_SIZES[args.page_size]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(args.output), pagesize=(page_width, page_height), pageCompression=1)
    canvas.setTitle(spec.get("document_title", "Figure gallery"))

    margin_x = 30.0
    bottom = 20.0
    title_y = page_height - 42.0
    top = page_height - 66.0
    gap = 12.0

    for section in sections:
        title = section.get("title")
        images = section.get("images")
        if not isinstance(title, str) or not title.strip():
            raise SystemExit("every section needs a non-empty title")
        if not isinstance(images, list) or not images:
            raise SystemExit(f"section {title!r} needs at least one image")
        image_paths = [(spec_path.parent / item).resolve() for item in images]
        missing = [str(path) for path in image_paths if not path.is_file()]
        if missing:
            raise SystemExit("missing images: " + ", ".join(missing))

        rows = (len(image_paths) + args.columns - 1) // args.columns
        cell_width = (page_width - 2 * margin_x - gap * (args.columns - 1)) / args.columns
        cell_height = (top - bottom - gap * (rows - 1)) / rows
        if cell_width <= 0 or cell_height <= 0:
            raise SystemExit("page grid has no usable area")

        canvas.setFillColorRGB(37 / 255, 49 / 255, 60 / 255)
        canvas.setFont("Helvetica-Bold", 28)
        canvas.drawString(margin_x + 4, title_y, title)
        for index, image_path in enumerate(image_paths):
            column = index % args.columns
            row = index // args.columns
            x = margin_x + column * (cell_width + gap)
            y = top - (row + 1) * cell_height - row * gap
            place_image(canvas, image_path, x, y, cell_width, cell_height)
        canvas.showPage()

    canvas.save()
    print(args.output.resolve())


if __name__ == "__main__":
    main()
