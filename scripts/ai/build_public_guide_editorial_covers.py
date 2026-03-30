#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

import yaml
from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = ROOT / "products" / "chummer"
CONFIG_PATH = PRODUCT_ROOT / "PUBLIC_GUIDE_EDITORIAL_COVERS.yaml"


def _load_yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a YAML object")
    return payload


def _hex_rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    red, green, blue = ImageColor.getrgb(str(value))
    return (red, green, blue, max(0, min(255, int(alpha))))


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def _asset_roots(repo_root: Path, source_root: Path) -> list[Path]:
    roots = [source_root]
    for candidate in (
        repo_root / "products" / "chummer" / "public-guide-curated-assets",
        repo_root.parent / "Chummer6",
        repo_root.parent / "chummer6",
    ):
        if candidate not in roots:
            roots.append(candidate)
    return roots


def _resolve_source(repo_root: Path, source_root: Path, raw_value: str, output_root: Path) -> Path:
    cleaned = str(raw_value or "").strip()
    if not cleaned:
        raise FileNotFoundError("empty source path")
    prefer_generated = True
    if cleaned.startswith("raw:"):
        prefer_generated = False
        cleaned = cleaned[4:].strip()
    path = Path(cleaned)
    candidates: list[Path] = []
    if cleaned.startswith("assets/"):
        rel = Path(cleaned).relative_to("assets")
        if prefer_generated:
            candidates.append(output_root / cleaned)
        candidates.extend(
            [
                source_root / rel,
                repo_root.parent / "Chummer6" / cleaned,
                repo_root / cleaned,
            ]
        )
    elif path.is_absolute():
        candidates.append(path)
    else:
        candidates.extend([repo_root / cleaned, repo_root.parent / cleaned])
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"unable to resolve source {cleaned}; checked: {searched}")


def _fit_cover(image: Image.Image, size: tuple[int, int], focus: tuple[float, float]) -> Image.Image:
    centering = (max(0.0, min(1.0, focus[0])), max(0.0, min(1.0, focus[1])))
    return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=centering)


def _darken(image: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Brightness(image).enhance(factor)


def _saturate(image: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Color(image).enhance(factor)


def _contrast(image: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Contrast(image).enhance(factor)


def _sharpness(image: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Sharpness(image).enhance(factor)


def _blend_overlay(base: Image.Image, color: tuple[int, int, int, int], alpha: int) -> Image.Image:
    overlay = Image.new("RGBA", base.size, (color[0], color[1], color[2], alpha))
    return Image.alpha_composite(base.convert("RGBA"), overlay)


def _tracked_text(draw: ImageDraw.ImageDraw, position: tuple[int, int], text: str, font: ImageFont.FreeTypeFont, fill: tuple[int, int, int, int], tracking: int) -> None:
    x, y = position
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        bbox = draw.textbbox((x, y), char, font=font)
        x = bbox[2] + tracking


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = [word for word in text.split() if word]
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        width = draw.textbbox((0, 0), trial, font=font)[2]
        if width <= max_width:
            current = trial
            continue
        lines.append(current)
        current = word
    lines.append(current)
    return lines


def _draw_chip(draw: ImageDraw.ImageDraw, *, text: str, x: int, y: int, font: ImageFont.FreeTypeFont, accent: tuple[int, int, int, int]) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    pad_x = 18
    pad_y = 10
    width = bbox[2] - bbox[0] + pad_x * 2
    height = bbox[3] - bbox[1] + pad_y * 2
    draw.rounded_rectangle((x, y, x + width, y + height), radius=14, fill=(14, 19, 28, 200), outline=accent, width=2)
    draw.text((x + pad_x, y + pad_y - 1), text, font=font, fill=(245, 247, 250, 235))
    return width


def _draw_panel_motif(draw: ImageDraw.ImageDraw, *, motif: str, rect: tuple[int, int, int, int], accent: tuple[int, int, int, int], secondary: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    if motif == "hazard_arcs":
        draw.arc((left + 24, top + 20, left + 360, top + 356), start=210, end=340, fill=accent, width=4)
        draw.arc((left + 90, top + 90, left + 410, top + 410), start=210, end=330, fill=secondary, width=2)
        draw.line((left + 110, top + 210, left + 420, top + 210), fill=secondary, width=2)
    elif motif == "network_nodes":
        nodes = [(left + 80, top + 80), (left + 230, top + 150), (left + 160, top + 290), (left + 350, top + 250)]
        for start, end in zip(nodes, nodes[1:]):
            draw.line((*start, *end), fill=accent, width=3)
        for node in nodes:
            draw.ellipse((node[0] - 10, node[1] - 10, node[0] + 10, node[1] + 10), fill=secondary, outline=accent, width=2)
    elif motif == "forge_lattice":
        for offset in range(0, 220, 44):
            draw.line((left + 40 + offset, top + 30, left + 160 + offset, top + 210), fill=accent, width=3)
            draw.line((left + 160 + offset, top + 30, left + 40 + offset, top + 210), fill=secondary, width=2)
    elif motif == "dossier_grid":
        for row in range(4):
            draw.rounded_rectangle((left + 30, top + 28 + row * 62, left + 220, top + 70 + row * 62), radius=10, outline=accent, width=2)
        draw.line((left + 260, top + 34, left + 420, top + 220), fill=secondary, width=2)
        draw.line((left + 420, top + 34, left + 260, top + 220), fill=secondary, width=2)
    elif motif == "route_grid":
        for offset in range(0, 220, 44):
            draw.line((left + 30 + offset, top + 30, left + 150 + offset, top + 240), fill=secondary, width=2)
        for node_x, node_y in ((left + 80, top + 80), (left + 190, top + 190), (left + 320, top + 100), (left + 400, top + 230)):
            draw.ellipse((node_x - 8, node_y - 8, node_x + 8, node_y + 8), fill=accent)
    elif motif == "print_columns":
        for idx in range(4):
            x = left + 24 + idx * 74
            draw.rounded_rectangle((x, top + 26, x + 48, top + 248), radius=14, outline=accent if idx % 2 == 0 else secondary, width=2)
    elif motif == "pulse_bands":
        baseline = top + height // 2
        points = [
            (left + 20, baseline),
            (left + 110, baseline),
            (left + 140, baseline - 48),
            (left + 172, baseline + 64),
            (left + 215, baseline - 94),
            (left + 252, baseline + 40),
            (left + 330, baseline),
            (left + 420, baseline),
        ]
        draw.line(points, fill=accent, width=4, joint="curve")
        draw.line((left + 20, baseline + 34, left + 420, baseline + 34), fill=secondary, width=2)
    elif motif == "ledger_grid":
        for row in range(5):
            draw.line((left + 24, top + 34 + row * 36, left + 420, top + 34 + row * 36), fill=secondary, width=1)
        for col in range(5):
            draw.line((left + 24 + col * 88, top + 24, left + 24 + col * 88, top + 180), fill=accent, width=1)
    elif motif == "signal_bars":
        for idx, height_scale in enumerate((0.28, 0.46, 0.66, 0.88)):
            bar_height = int(210 * height_scale)
            x = left + 40 + idx * 70
            draw.rounded_rectangle((x, top + 250 - bar_height, x + 42, top + 250), radius=14, fill=accent if idx >= 2 else secondary)
    elif motif == "swatch_grid":
        for row in range(3):
            for col in range(4):
                x = left + 26 + col * 84
                y = top + 30 + row * 74
                fill = accent if (row + col) % 2 == 0 else secondary
                draw.rounded_rectangle((x, y, x + 58, y + 42), radius=10, fill=(fill[0], fill[1], fill[2], 80), outline=fill, width=2)
    elif motif == "shelf_brackets":
        for idx in range(4):
            y = top + 40 + idx * 56
            draw.line((left + 34, y, left + 420, y), fill=secondary, width=2)
            draw.rectangle((left + 70 + idx * 70, y - 12, left + 116 + idx * 70, y + 12), outline=accent, width=3)
    elif motif == "clinic_ticks":
        draw.line((left + 32, top + 74, left + 414, top + 74), fill=secondary, width=2)
        for idx in range(6):
            x = left + 48 + idx * 64
            draw.line((x, top + 42, x, top + 202), fill=accent, width=2)
            draw.rounded_rectangle((x - 14, top + 118 - idx * 6, x + 14, top + 144 - idx * 6), radius=8, outline=secondary, width=2)
        draw.arc((left + 46, top + 54, left + 346, top + 300), start=196, end=334, fill=accent, width=4)
        draw.line((left + 72, top + 232, left + 240, top + 232), fill=accent, width=3)


def _draw_footer(draw: ImageDraw.ImageDraw, *, width: int, height: int, font: ImageFont.FreeTypeFont, accent: tuple[int, int, int, int]) -> None:
    label = "PUBLIC GUIDE"
    text_bbox = draw.textbbox((0, 0), label, font=font)
    x = width - (text_bbox[2] - text_bbox[0]) - 86
    y = height - 58
    draw.line((x - 80, y + 12, x - 16, y + 12), fill=accent, width=3)
    draw.text((x, y), label, font=font, fill=(232, 236, 241, 220))


def _draw_feature_cover(spec: dict[str, object], *, repo_root: Path, source_root: Path, output_root: Path, defaults: dict[str, object]) -> Path:
    width = int(defaults.get("width") or 1600)
    height = int(defaults.get("height") or 900)
    title_font = _font(str(defaults.get("title_font")), 112 if len(str(spec.get("title") or "")) <= 10 else 96)
    label_font = _font(str(defaults.get("label_font")), 30)
    body_font = _font(str(defaults.get("body_font")), 34)
    chip_font = _font(str(defaults.get("label_font")), 24)
    index_font = _font(str(defaults.get("title_font")), 168)

    source_value = str(spec.get("source") or "").strip()
    if source_value and not source_value.startswith("raw:"):
        source_value = f"raw:{source_value}"
    source_path = _resolve_source(repo_root, source_root, source_value, output_root)
    focus_values = spec.get("focus") or [0.5, 0.5]
    focus = (
        float(focus_values[0]) if isinstance(focus_values, (list, tuple)) and len(focus_values) >= 1 else 0.5,
        float(focus_values[1]) if isinstance(focus_values, (list, tuple)) and len(focus_values) >= 2 else 0.5,
    )
    accent = _hex_rgba(str(spec.get("accent") or "#4fd1ff"), 255)
    secondary = _hex_rgba(str(spec.get("accent_secondary") or "#ff7a45"), 255)

    source_image = Image.open(source_path).convert("RGB")
    background = _fit_cover(source_image, (width, height), focus)
    background = _contrast(_saturate(_darken(background, 0.62), 0.9), 1.08)
    background = background.filter(ImageFilter.GaussianBlur(radius=18))
    canvas = _blend_overlay(background, _hex_rgba("#07111a", 255), 118)

    panel_width = int(width * 0.66)
    panel_image = _fit_cover(source_image, (panel_width, height), focus)
    panel_image = _sharpness(_contrast(_saturate(panel_image, 1.14), 1.08), 1.25)
    panel_image = _blend_overlay(panel_image, accent, 26)
    panel_mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(panel_mask)
    mask_draw.polygon(
        [
            (width - panel_width + 54, 0),
            (width, 0),
            (width, height),
            (width - panel_width - 26, height),
        ],
        fill=255,
    )
    panel_mask = panel_mask.filter(ImageFilter.GaussianBlur(radius=8))
    panel_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    panel_layer.paste(panel_image.convert("RGBA"), (width - panel_width, 0))
    canvas = Image.composite(panel_layer, canvas, panel_mask)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, 690, height), fill=(7, 12, 18, 210))
    draw.polygon(
        [
            (488, 0),
            (630, 0),
            (560, height),
            (430, height),
        ],
        fill=(7, 12, 18, 160),
    )
    draw.rectangle((74, 76, 516, 290), fill=(14, 19, 28, 120))
    _draw_panel_motif(
        draw,
        motif=str(spec.get("motif") or ""),
        rect=(88, 92, 484, 306),
        accent=(accent[0], accent[1], accent[2], 165),
        secondary=(secondary[0], secondary[1], secondary[2], 128),
    )
    seam_points = [(588, 0), (602, 0), (530, height), (516, height)]
    draw.polygon(seam_points, fill=(accent[0], accent[1], accent[2], 170))
    draw.line((604, 32, 566, height - 32), fill=(secondary[0], secondary[1], secondary[2], 150), width=3)

    series_label = str(spec.get("series_label") or "").strip()
    if series_label:
        _tracked_text(draw, (88, 70), series_label, label_font, (238, 240, 243, 230), 3)
    index_label = str(spec.get("index") or "").strip()
    if index_label:
        draw.text((84, 262), index_label, font=index_font, fill=(accent[0], accent[1], accent[2], 62))

    title = str(spec.get("title") or "").strip()
    title_y = 262
    if title:
        title_font = _font(str(defaults.get("title_font")), 108 if len(title) <= 10 else 92)
        title_lines = _wrap_text(draw, title, title_font, 420)
        for idx, line in enumerate(title_lines):
            draw.text((88, title_y + idx * 94), line, font=title_font, fill=(246, 247, 250, 245))
        subtitle_start_y = title_y + len(title_lines) * 94 + 20
    else:
        subtitle_start_y = title_y

    subtitle = str(spec.get("subtitle") or "").strip()
    if subtitle:
        subtitle_lines = _wrap_text(draw, subtitle, body_font, 430)
        for idx, line in enumerate(subtitle_lines[:4]):
            draw.text((92, subtitle_start_y + idx * 44), line, font=body_font, fill=(218, 223, 228, 226))
        chips_y = subtitle_start_y + min(len(subtitle_lines), 4) * 44 + 34
    else:
        chips_y = subtitle_start_y + 24

    chips = [str(item).strip() for item in (spec.get("chips") or []) if str(item).strip()]
    chip_x = 88
    for chip in chips[:3]:
        chip_width = _draw_chip(draw, text=chip, x=chip_x, y=chips_y, font=chip_font, accent=(accent[0], accent[1], accent[2], 225))
        chip_x += chip_width + 14

    _draw_footer(draw, width=width, height=height, font=chip_font, accent=(secondary[0], secondary[1], secondary[2], 220))
    combined = Image.alpha_composite(canvas, overlay).convert("RGB")
    target_path = output_root / str(spec.get("_target") or "")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    combined.save(target_path, format="PNG", compress_level=6)
    return target_path


def _draw_mosaic_cover(spec: dict[str, object], *, repo_root: Path, source_root: Path, output_root: Path, defaults: dict[str, object]) -> Path:
    width = int(defaults.get("width") or 1600)
    height = int(defaults.get("height") or 900)
    label_font = _font(str(defaults.get("label_font")), 30)
    title_font = _font(str(defaults.get("title_font")), 102)
    body_font = _font(str(defaults.get("body_font")), 32)
    chip_font = _font(str(defaults.get("label_font")), 24)
    accent = _hex_rgba(str(spec.get("accent") or "#4fd1ff"), 255)
    secondary = _hex_rgba(str(spec.get("accent_secondary") or "#ff7a45"), 255)

    canvas = Image.new("RGBA", (width, height), (8, 12, 18, 255))
    bg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg)
    bg_draw.rectangle((0, 0, width, height), fill=(8, 12, 18, 255))
    bg_draw.rectangle((0, 0, 690, height), fill=(12, 18, 28, 255))
    bg_draw.polygon([(500, 0), (656, 0), (590, height), (442, height)], fill=(12, 18, 28, 200))

    tile_sources = [str(item).strip() for item in (spec.get("tile_sources") or []) if str(item).strip()]
    columns = 4 if len(tile_sources) > 6 else 3
    rows = max(1, math.ceil(len(tile_sources) / columns))
    gutter = 18
    grid_left = 612
    grid_top = 86
    grid_width = width - grid_left - 70
    grid_height = height - 160
    tile_width = int((grid_width - gutter * (columns - 1)) / columns)
    tile_height = int((grid_height - gutter * (rows - 1)) / rows)

    for idx, raw_source in enumerate(tile_sources):
        source_path = _resolve_source(repo_root, source_root, raw_source, output_root)
        tile = Image.open(source_path).convert("RGB")
        tile = _fit_cover(tile, (tile_width, tile_height), (0.5, 0.5))
        tile = _contrast(_saturate(_darken(tile, 0.78), 1.05), 1.06)
        tile = _blend_overlay(tile, accent if idx % 2 == 0 else secondary, 18)
        col = idx % columns
        row = idx // columns
        row_start = row * columns
        row_count = min(columns, max(0, len(tile_sources) - row_start))
        row_span = row_count * tile_width + max(0, row_count - 1) * gutter
        row_offset = max(0, (grid_width - row_span) // 2)
        x = grid_left + row_offset + col * (tile_width + gutter)
        y = grid_top + row * (tile_height + gutter)
        canvas.alpha_composite(tile, (x, y))
        frame = ImageDraw.Draw(canvas)
        frame.rounded_rectangle((x, y, x + tile_width, y + tile_height), radius=22, outline=accent if idx % 2 == 0 else secondary, width=3)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, 580, height), fill=(8, 12, 18, 185))
    draw.polygon([(574, 0), (596, 0), (524, height), (502, height)], fill=(accent[0], accent[1], accent[2], 165))
    draw.line((598, 34, 566, height - 34), fill=(secondary[0], secondary[1], secondary[2], 144), width=3)
    _draw_panel_motif(
        draw,
        motif="network_nodes",
        rect=(88, 88, 468, 292),
        accent=(accent[0], accent[1], accent[2], 160),
        secondary=(secondary[0], secondary[1], secondary[2], 120),
    )

    series_label = str(spec.get("series_label") or "").strip()
    if series_label:
        _tracked_text(draw, (88, 70), series_label, label_font, (238, 240, 243, 230), 3)

    title = str(spec.get("title") or "").strip()
    title_lines = _wrap_text(draw, title, title_font, 430)
    title_y = 302
    for idx, line in enumerate(title_lines):
        draw.text((88, title_y + idx * 92), line, font=title_font, fill=(246, 247, 250, 245))

    subtitle = str(spec.get("subtitle") or "").strip()
    subtitle_y = title_y + len(title_lines) * 92 + 18
    subtitle_lines = _wrap_text(draw, subtitle, body_font, 430)
    for idx, line in enumerate(subtitle_lines[:4]):
        draw.text((92, subtitle_y + idx * 42), line, font=body_font, fill=(218, 223, 228, 226))

    chips = [str(item).strip() for item in (spec.get("chips") or []) if str(item).strip()]
    chip_x = 88
    chips_y = subtitle_y + min(len(subtitle_lines), 4) * 42 + 34
    for chip in chips[:3]:
        chip_width = _draw_chip(draw, text=chip, x=chip_x, y=chips_y, font=chip_font, accent=(accent[0], accent[1], accent[2], 225))
        chip_x += chip_width + 14

    _draw_footer(draw, width=width, height=height, font=chip_font, accent=(secondary[0], secondary[1], secondary[2], 220))
    combined = Image.alpha_composite(canvas, overlay).convert("RGB")
    target_path = output_root / str(spec.get("_target") or "")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    combined.save(target_path, format="PNG", compress_level=6)
    return target_path


def build_editorial_covers(repo_root: Path, source_root: Path) -> Path:
    config = _load_yaml(CONFIG_PATH)
    output_root = repo_root / str(config.get("output_root") or "products/chummer/public-guide-curated-assets")
    defaults = config.get("defaults") or {}
    if not isinstance(defaults, dict):
        defaults = {}
    output_root.mkdir(parents=True, exist_ok=True)
    assets = config.get("assets") or {}
    if not isinstance(assets, dict):
        return output_root

    feature_specs: list[dict[str, object]] = []
    mosaic_specs: list[dict[str, object]] = []
    for target, raw_spec in assets.items():
        if not isinstance(raw_spec, dict):
            continue
        spec = dict(raw_spec)
        spec["_target"] = str(target)
        kind = str(spec.get("kind") or "feature_cover").strip().lower()
        if kind == "mosaic_cover":
            mosaic_specs.append(spec)
        else:
            feature_specs.append(spec)

    for spec in feature_specs:
        _draw_feature_cover(spec, repo_root=repo_root, source_root=source_root, output_root=output_root, defaults=defaults)
    for spec in mosaic_specs:
        _draw_mosaic_cover(spec, repo_root=repo_root, source_root=source_root, output_root=output_root, defaults=defaults)
    return output_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic editorial covers for the public guide.")
    parser.add_argument("--repo-root", default=str(ROOT), help="Repository root.")
    parser.add_argument("--asset-root", default=str(ROOT.parent / "Chummer6" / "assets"), help="Asset source root.")
    args = parser.parse_args()
    build_editorial_covers(repo_root=Path(args.repo_root).resolve(), source_root=Path(args.asset_root).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
