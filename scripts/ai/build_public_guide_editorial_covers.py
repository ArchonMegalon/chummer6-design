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


def _focus_tuple(raw_value: object, default: tuple[float, float] = (0.5, 0.5)) -> tuple[float, float]:
    if isinstance(raw_value, (list, tuple)) and len(raw_value) >= 2:
        return (
            max(0.0, min(1.0, float(raw_value[0]))),
            max(0.0, min(1.0, float(raw_value[1]))),
        )
    return default


def _zoom_value(raw_value: object, default: float = 1.0) -> float:
    try:
        zoom = float(raw_value)
    except (TypeError, ValueError):
        return default
    return max(1.0, zoom)


def _float_value(raw_value: object, default: float) -> float:
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return default


def _int_value(raw_value: object, default: int) -> int:
    try:
        return int(float(raw_value))
    except (TypeError, ValueError):
        return default


def _fit_cover(
    image: Image.Image,
    size: tuple[int, int],
    focus: tuple[float, float],
    *,
    zoom: float = 1.0,
) -> Image.Image:
    centering = (max(0.0, min(1.0, focus[0])), max(0.0, min(1.0, focus[1])))
    if zoom <= 1.001:
        return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=centering)
    crop_width = max(1, int(round(size[0] / zoom)))
    crop_height = max(1, int(round(size[1] / zoom)))
    cropped = ImageOps.fit(image, (crop_width, crop_height), method=Image.Resampling.LANCZOS, centering=centering)
    return cropped.resize(size, Image.Resampling.LANCZOS)


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


def _apply_blur_regions(image: Image.Image, regions: object, *, radius: float) -> Image.Image:
    if not isinstance(regions, list) or not regions:
        return image
    width, height = image.size
    base = image.convert("RGBA")
    for raw_region in regions:
        if not isinstance(raw_region, (list, tuple)) or len(raw_region) < 4:
            continue
        left = int(float(raw_region[0]) * width)
        top = int(float(raw_region[1]) * height)
        right = int(float(raw_region[2]) * width)
        bottom = int(float(raw_region[3]) * height)
        left = max(0, min(width - 1, left))
        top = max(0, min(height - 1, top))
        right = max(left + 1, min(width, right))
        bottom = max(top + 1, min(height, bottom))
        crop = base.crop((left, top, right, bottom))
        blurred = crop.filter(ImageFilter.GaussianBlur(radius=radius))
        base.paste(blurred, (left, top, right, bottom))
    return base.convert(image.mode)


def _apply_darken_regions(image: Image.Image, regions: object, *, factor: float) -> Image.Image:
    if not isinstance(regions, list) or not regions:
        return image
    width, height = image.size
    base = image.convert("RGBA")
    clamped_factor = max(0.15, min(1.0, float(factor)))
    for raw_region in regions:
        if not isinstance(raw_region, (list, tuple)) or len(raw_region) < 4:
            continue
        left = int(float(raw_region[0]) * width)
        top = int(float(raw_region[1]) * height)
        right = int(float(raw_region[2]) * width)
        bottom = int(float(raw_region[3]) * height)
        left = max(0, min(width - 1, left))
        top = max(0, min(height - 1, top))
        right = max(left + 1, min(width, right))
        bottom = max(top + 1, min(height, bottom))
        crop = base.crop((left, top, right, bottom)).convert("RGB")
        darkened = _darken(crop, clamped_factor).convert("RGBA")
        base.paste(darkened, (left, top, right, bottom))
    return base.convert(image.mode)


def _vertical_gradient(size: tuple[int, int], top: tuple[int, int, int, int], bottom: tuple[int, int, int, int]) -> Image.Image:
    mask = Image.linear_gradient("L").resize(size)
    return Image.composite(Image.new("RGBA", size, bottom), Image.new("RGBA", size, top), mask)


def _fit_text_block(
    draw: ImageDraw.ImageDraw,
    *,
    text: str,
    font_path: str,
    max_size: int,
    min_size: int,
    max_width: int,
    max_lines: int,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    cleaned = str(text or "").strip()
    if not cleaned:
        font = _font(font_path, min_size)
        return font, [], min_size
    for size in range(max_size, min_size - 1, -4):
        font = _font(font_path, size)
        lines = _wrap_text(draw, cleaned, font, max_width)
        line_widths = [draw.textbbox((0, 0), line, font=font)[2] for line in lines] if lines else [0]
        if len(lines) <= max_lines and max(line_widths) <= max_width:
            return font, lines, size
    font = _font(font_path, min_size)
    return font, _wrap_text(draw, cleaned, font, max_width), min_size


def _series_style(spec: dict[str, object]) -> str:
    target = str(spec.get("_target") or "")
    if target.startswith("assets/hero/"):
        return "hero"
    if target.startswith("assets/horizons/"):
        return "horizon"
    if target.startswith("assets/parts/"):
        return "part"
    if target.startswith("assets/pages/"):
        return "index"
    return "feature"


def _apply_editorial_finish(image: Image.Image, *, sigma: float = 10.0, opacity: int = 18) -> Image.Image:
    base = image.convert("RGBA")
    noise = Image.effect_noise(base.size, sigma).convert("L")
    noise = ImageOps.autocontrast(noise)
    noise_layer = Image.merge("RGBA", (noise, noise, noise, Image.new("L", base.size, opacity)))
    vignette = Image.new("L", base.size, 0)
    vignette_draw = ImageDraw.Draw(vignette)
    width, height = base.size
    vignette_draw.ellipse((-int(width * 0.14), -int(height * 0.22), int(width * 1.14), int(height * 1.20)), fill=190)
    vignette = ImageOps.invert(vignette).filter(ImageFilter.GaussianBlur(radius=84))
    vignette_layer = Image.new("RGBA", base.size, (3, 6, 10, 0))
    vignette_layer.putalpha(vignette)
    return Image.alpha_composite(Image.alpha_composite(base, vignette_layer), noise_layer)


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


def _draw_bracket_box(
    draw: ImageDraw.ImageDraw,
    *,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int, int],
    width: int = 3,
    arm: int = 26,
) -> None:
    left, top, right, bottom = box
    arm_x = min(arm, max(10, (right - left) // 3))
    arm_y = min(arm, max(10, (bottom - top) // 3))
    draw.line((left, top, left + arm_x, top), fill=color, width=width)
    draw.line((left, top, left, top + arm_y), fill=color, width=width)
    draw.line((right - arm_x, top, right, top), fill=color, width=width)
    draw.line((right, top, right, top + arm_y), fill=color, width=width)
    draw.line((left, bottom - arm_y, left, bottom), fill=color, width=width)
    draw.line((left, bottom, left + arm_x, bottom), fill=color, width=width)
    draw.line((right - arm_x, bottom, right, bottom), fill=color, width=width)
    draw.line((right, bottom - arm_y, right, bottom), fill=color, width=width)


def _draw_scene_overlay(
    draw: ImageDraw.ImageDraw,
    *,
    motif: str,
    rect: tuple[int, int, int, int],
    accent: tuple[int, int, int, int],
    secondary: tuple[int, int, int, int],
) -> None:
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top

    def pt(px: float, py: float) -> tuple[int, int]:
        return (left + int(width * px), top + int(height * py))

    accent_soft = (accent[0], accent[1], accent[2], min(128, max(48, accent[3])))
    accent_faint = (accent[0], accent[1], accent[2], max(28, accent[3] // 2))
    secondary_soft = (secondary[0], secondary[1], secondary[2], min(118, max(44, secondary[3])))
    secondary_faint = (secondary[0], secondary[1], secondary[2], max(24, secondary[3] // 2))

    _draw_bracket_box(
        draw,
        box=(pt(0.14, 0.12)[0], pt(0.14, 0.12)[1], pt(0.43, 0.34)[0], pt(0.43, 0.34)[1]),
        color=accent_soft,
        width=3,
        arm=max(22, width // 28),
    )
    _draw_bracket_box(
        draw,
        box=(pt(0.56, 0.18)[0], pt(0.56, 0.18)[1], pt(0.86, 0.40)[0], pt(0.86, 0.40)[1]),
        color=secondary_soft,
        width=2,
        arm=max(18, width // 32),
    )
    _draw_bracket_box(
        draw,
        box=(pt(0.24, 0.58)[0], pt(0.24, 0.58)[1], pt(0.50, 0.80)[0], pt(0.50, 0.80)[1]),
        color=accent_soft,
        width=2,
        arm=max(18, width // 32),
    )

    draw.arc((pt(0.06, 0.04)[0], pt(0.04, 0.04)[1], pt(0.72, 0.72)[0], pt(0.72, 0.72)[1]), start=208, end=318, fill=secondary_faint, width=2)
    draw.arc((pt(0.42, 0.26)[0], pt(0.10, 0.08)[1], pt(1.02, 0.86)[0], pt(0.92, 0.94)[1]), start=196, end=294, fill=accent_faint, width=2)
    draw.line((pt(0.10, 0.48), pt(0.28, 0.48), pt(0.36, 0.42), pt(0.50, 0.42), pt(0.62, 0.34), pt(0.78, 0.34)), fill=secondary_faint, width=2)
    draw.line((pt(0.60, 0.74), pt(0.82, 0.74)), fill=accent_faint, width=2)

    for px, py, radius, fill in (
        (0.18, 0.48, 8, accent_soft),
        (0.62, 0.34, 7, secondary_soft),
        (0.73, 0.74, 6, accent_soft),
    ):
        x, y = pt(px, py)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)

    if motif in {"network_nodes", "route_grid"}:
        nodes = [pt(0.54, 0.16), pt(0.72, 0.26), pt(0.82, 0.48), pt(0.66, 0.64), pt(0.48, 0.74)]
        for start, end in zip(nodes, nodes[1:]):
            draw.line((*start, *end), fill=accent_soft, width=2)
        for x, y in nodes:
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), outline=secondary_soft, width=2)
    elif motif in {"ledger_grid", "clinic_ticks", "pulse_bands"}:
        baseline = top + int(height * 0.84)
        for idx in range(6):
            x = left + int(width * (0.18 + idx * 0.10))
            draw.line((x, baseline - int(height * 0.14), x, baseline + int(height * 0.02)), fill=accent_faint, width=2)
        draw.line((left + int(width * 0.14), baseline, right - int(width * 0.08), baseline), fill=secondary_faint, width=2)
    elif motif in {"dossier_grid", "shelf_brackets", "print_columns"}:
        for idx in range(3):
            box_left = left + int(width * 0.58)
            box_top = top + int(height * (0.50 + idx * 0.11))
            box_right = right - int(width * 0.08)
            box_bottom = box_top + int(height * 0.07)
            draw.rounded_rectangle((box_left, box_top, box_right, box_bottom), radius=12, outline=secondary_faint, width=2)
    elif motif == "swatch_grid":
        for row in range(2):
            for col in range(3):
                x1 = left + int(width * (0.58 + col * 0.10))
                y1 = top + int(height * (0.52 + row * 0.12))
                x2 = x1 + int(width * 0.07)
                y2 = y1 + int(height * 0.05)
                color = accent_faint if (row + col) % 2 == 0 else secondary_faint
                draw.rounded_rectangle((x1, y1, x2, y2), radius=10, outline=color, width=2)


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
    title_font_path = str(defaults.get("title_font"))
    label_font_path = str(defaults.get("label_font"))
    body_font_path = str(defaults.get("body_font"))
    label_font = _font(label_font_path, 27)
    chip_font = _font(label_font_path, 22)
    style = _series_style(spec)

    source_value = str(spec.get("source") or "").strip()
    if source_value and not source_value.startswith("raw:"):
        source_value = f"raw:{source_value}"
    background_source_value = str(spec.get("background_source") or source_value).strip()
    panel_source_value = str(spec.get("panel_source") or source_value).strip()
    background_source_path = _resolve_source(repo_root, source_root, background_source_value, output_root)
    panel_source_path = _resolve_source(repo_root, source_root, panel_source_value, output_root)
    focus = _focus_tuple(spec.get("focus"), (0.5, 0.5))
    background_focus = _focus_tuple(spec.get("background_focus"), focus)
    panel_focus = _focus_tuple(spec.get("panel_focus"), focus)
    background_zoom = _zoom_value(spec.get("background_zoom"), 1.0)
    panel_zoom = _zoom_value(spec.get("panel_zoom"), 1.0)
    accent = _hex_rgba(str(spec.get("accent") or "#4fd1ff"), 255)
    secondary = _hex_rgba(str(spec.get("accent_secondary") or "#ff7a45"), 255)
    copy_width = _int_value(spec.get("copy_width"), {"hero": 598, "horizon": 506, "part": 510}.get(style, 548))
    rail_width = copy_width + 70
    pad = 72
    background_brightness = max(0.40, min(1.20, _float_value(spec.get("background_brightness"), 0.64)))
    background_saturation = max(0.60, min(1.40, _float_value(spec.get("background_saturation"), 0.94)))
    background_contrast = max(0.80, min(1.40, _float_value(spec.get("background_contrast"), 1.08)))
    background_blur_sigma = max(0.0, min(40.0, _float_value(spec.get("background_blur_sigma"), 16.0)))
    panel_brightness = max(0.80, min(1.30, _float_value(spec.get("panel_brightness"), 1.0)))
    panel_saturation = max(0.80, min(1.40, _float_value(spec.get("panel_saturation"), 1.10)))
    panel_contrast = max(0.80, min(1.40, _float_value(spec.get("panel_contrast"), 1.06)))
    panel_sharpness = max(0.80, min(1.40, _float_value(spec.get("panel_sharpness"), 1.18)))
    editorial_finish_sigma = max(0.0, min(20.0, _float_value(spec.get("editorial_finish_sigma"), 10.0)))
    editorial_finish_opacity = max(0, min(64, _int_value(spec.get("editorial_finish_opacity"), 18)))

    background_source_image = Image.open(background_source_path).convert("RGB")
    panel_source_image = Image.open(panel_source_path).convert("RGB")
    background = _fit_cover(background_source_image, (width, height), background_focus, zoom=background_zoom)
    background = _contrast(_saturate(_darken(background, background_brightness), background_saturation), background_contrast)
    background = background.filter(ImageFilter.GaussianBlur(radius=background_blur_sigma))
    background = _apply_blur_regions(background, spec.get("background_blur_regions"), radius=float(spec.get("background_blur_radius") or 28))
    background = _apply_darken_regions(background, spec.get("background_darken_regions"), factor=float(spec.get("background_darken_factor") or 0.62))
    canvas = _blend_overlay(background, _hex_rgba("#07111a", 255), int(spec.get("background_overlay_alpha") or 118))

    panel_width = width - copy_width + 110
    panel_image = _fit_cover(panel_source_image, (panel_width, height), panel_focus, zoom=panel_zoom)
    panel_image = _apply_blur_regions(panel_image, spec.get("panel_blur_regions"), radius=float(spec.get("panel_blur_radius") or 28))
    panel_image = _apply_darken_regions(panel_image, spec.get("panel_darken_regions"), factor=float(spec.get("panel_darken_factor") or 0.62))
    panel_image = ImageEnhance.Brightness(panel_image).enhance(panel_brightness)
    panel_image = _sharpness(_contrast(_saturate(panel_image, panel_saturation), panel_contrast), panel_sharpness)
    panel_overlay_alpha = _int_value(spec.get("panel_overlay_alpha"), 18 if style == "hero" else 22)
    panel_image = _blend_overlay(panel_image, accent, panel_overlay_alpha)
    panel_mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(panel_mask)
    mask_draw.polygon(
        [
            (copy_width - 22, 0),
            (width, 0),
            (width, height),
            (copy_width - 118, height),
        ],
        fill=255,
    )
    panel_mask = panel_mask.filter(ImageFilter.GaussianBlur(radius=14))
    panel_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    panel_layer.paste(panel_image.convert("RGBA"), (copy_width - 12, 0))
    canvas = Image.composite(panel_layer, canvas, panel_mask)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rail = _vertical_gradient((rail_width, height), (8, 12, 18, 224), (8, 12, 18, 204))
    overlay.alpha_composite(rail, (0, 0))
    draw.polygon(
        [
            (copy_width - 72, 0),
            (copy_width + 82, 0),
            (copy_width - 4, height),
            (copy_width - 146, height),
        ],
        fill=(8, 12, 18, 150),
    )
    draw.rounded_rectangle((pad - 6, 76, copy_width - 70, 184), radius=28, fill=(14, 19, 28, 118), outline=(255, 255, 255, 28), width=1)
    info_bottom = height - 100
    draw.rounded_rectangle((pad - 8, 204, copy_width - 46, info_bottom), radius=34, fill=(10, 15, 22, 72), outline=(255, 255, 255, 18), width=1)
    _draw_panel_motif(
        draw,
        motif=str(spec.get("motif") or ""),
        rect=(pad + 8, 88, copy_width - 92, 182),
        accent=(accent[0], accent[1], accent[2], 150),
        secondary=(secondary[0], secondary[1], secondary[2], 122),
    )
    _draw_scene_overlay(
        draw,
        motif=str(spec.get("motif") or ""),
        rect=(copy_width + 54, 36, width - 40, height - 66),
        accent=(accent[0], accent[1], accent[2], 92 if style == "hero" else 108),
        secondary=(secondary[0], secondary[1], secondary[2], 78 if style == "hero" else 92),
    )
    seam_points = [(copy_width + 22, 0), (copy_width + 38, 0), (copy_width - 46, height), (copy_width - 62, height)]
    draw.polygon(seam_points, fill=(accent[0], accent[1], accent[2], 170))
    draw.line((copy_width + 46, 34, copy_width - 12, height - 34), fill=(secondary[0], secondary[1], secondary[2], 140), width=3)
    draw.line((pad, height - 78, copy_width - 92, height - 78), fill=(255, 255, 255, 34), width=1)

    series_label = str(spec.get("series_label") or "").strip()
    if series_label:
        _tracked_text(draw, (pad, 48), series_label, label_font, (238, 240, 243, 230), 3)
    title = str(spec.get("title") or "").strip()
    title_y = 238 if style == "hero" else 224
    title_max_width = copy_width - (pad * 2) - 8
    if title:
        title_font, title_lines, title_size = _fit_text_block(
            draw,
            text=title,
            font_path=title_font_path,
            max_size=122 if style == "hero" else 104,
            min_size=72 if style == "hero" else 62,
            max_width=title_max_width,
            max_lines=2,
        )
        title_step = int(title_size * 0.84)
        draw.line((pad, title_y - 22, pad + 72, title_y - 22), fill=(secondary[0], secondary[1], secondary[2], 200), width=3)
        for idx, line in enumerate(title_lines):
            draw.text((pad, title_y + idx * title_step), line, font=title_font, fill=(246, 247, 250, 245))
        subtitle_start_y = title_y + len(title_lines) * title_step + 18
    else:
        subtitle_start_y = title_y

    subtitle = str(spec.get("subtitle") or "").strip()
    if subtitle:
        body_font, subtitle_lines, body_size = _fit_text_block(
            draw,
            text=subtitle,
            font_path=body_font_path,
            max_size=34 if style == "hero" else 31,
            min_size=24,
            max_width=title_max_width,
            max_lines=4,
        )
        body_step = int(body_size * 1.22)
        for idx, line in enumerate(subtitle_lines[:4]):
            draw.text((pad + 2, subtitle_start_y + idx * body_step), line, font=body_font, fill=(218, 223, 228, 228))
    else:
        subtitle_lines = []
        body_step = 0

    chips_y = max(subtitle_start_y + min(len(subtitle_lines), 4) * body_step + 30, height - 96)

    chips = [str(item).strip() for item in (spec.get("chips") or []) if str(item).strip()]
    chip_x = pad
    for chip in chips[:3]:
        chip_width = _draw_chip(draw, text=chip, x=chip_x, y=chips_y, font=chip_font, accent=(accent[0], accent[1], accent[2], 225))
        chip_x += chip_width + 14

    _draw_footer(draw, width=width, height=height, font=chip_font, accent=(secondary[0], secondary[1], secondary[2], 220))
    combined = _apply_editorial_finish(
        Image.alpha_composite(canvas, overlay),
        sigma=editorial_finish_sigma,
        opacity=editorial_finish_opacity,
    ).convert("RGB")
    target_path = output_root / str(spec.get("_target") or "")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    combined.save(target_path, format="PNG", compress_level=6)
    return target_path


def _draw_mosaic_cover(spec: dict[str, object], *, repo_root: Path, source_root: Path, output_root: Path, defaults: dict[str, object]) -> Path:
    width = int(defaults.get("width") or 1600)
    height = int(defaults.get("height") or 900)
    title_font_path = str(defaults.get("title_font"))
    label_font_path = str(defaults.get("label_font"))
    body_font_path = str(defaults.get("body_font"))
    label_font = _font(label_font_path, 27)
    chip_font = _font(label_font_path, 22)
    accent = _hex_rgba(str(spec.get("accent") or "#4fd1ff"), 255)
    secondary = _hex_rgba(str(spec.get("accent_secondary") or "#ff7a45"), 255)
    copy_width = 548
    pad = 72

    canvas = Image.new("RGBA", (width, height), (8, 12, 18, 255))
    bg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg)
    bg_draw.rectangle((0, 0, width, height), fill=(8, 12, 18, 255))
    bg_draw.rectangle((0, 0, copy_width + 54, height), fill=(12, 18, 28, 255))
    bg_draw.polygon([(copy_width - 28, 0), (copy_width + 98, 0), (copy_width + 18, height), (copy_width - 110, height)], fill=(12, 18, 28, 192))

    raw_tile_sources = spec.get("tile_sources") or []
    tile_specs: list[dict[str, object]] = []
    if isinstance(raw_tile_sources, list):
        for raw_entry in raw_tile_sources:
            if isinstance(raw_entry, dict):
                source_value = str(raw_entry.get("source") or "").strip()
                if source_value:
                    tile_specs.append(
                        {
                            "source": source_value,
                            "focus": _focus_tuple(raw_entry.get("focus"), (0.5, 0.5)),
                            "zoom": _zoom_value(raw_entry.get("zoom"), 1.0),
                        }
                    )
            elif str(raw_entry).strip():
                tile_specs.append({"source": str(raw_entry).strip(), "focus": (0.5, 0.5), "zoom": 1.0})

    layout = str(spec.get("layout") or "grid").strip().lower()
    gutter = 18
    grid_left = copy_width + 44
    grid_top = 84
    grid_width = width - grid_left - 58
    grid_height = height - 146

    if layout == "editorial_cluster" and tile_specs:
        cluster_specs = tile_specs[:6]
        lead_width = int(grid_width * 0.58)
        side_width = grid_width - lead_width - gutter
        top_height = int(grid_height * 0.52)
        small_height = int((top_height - gutter) / 2)
        bottom_height = grid_height - top_height - gutter
        bottom_width = int((grid_width - gutter * 2) / 3)
        placements = [
            (grid_left, grid_top, lead_width, top_height),
            (grid_left + lead_width + gutter, grid_top, side_width, small_height),
            (grid_left + lead_width + gutter, grid_top + small_height + gutter, side_width, small_height),
            (grid_left, grid_top + top_height + gutter, bottom_width, bottom_height),
            (grid_left + bottom_width + gutter, grid_top + top_height + gutter, bottom_width, bottom_height),
            (grid_left + (bottom_width + gutter) * 2, grid_top + top_height + gutter, bottom_width, bottom_height),
        ]
        frame = ImageDraw.Draw(canvas)
        for idx, (tile_spec, (x, y, tile_width, tile_height)) in enumerate(zip(cluster_specs, placements)):
            source_path = _resolve_source(repo_root, source_root, str(tile_spec.get("source") or ""), output_root)
            tile = Image.open(source_path).convert("RGB")
            tile = _fit_cover(tile, (tile_width, tile_height), tile_spec.get("focus") or (0.5, 0.5), zoom=float(tile_spec.get("zoom") or 1.0))
            tile = _contrast(_saturate(_darken(tile, 0.80 if idx == 0 else 0.76), 1.05), 1.06)
            tile = _blend_overlay(tile, accent if idx % 2 == 0 else secondary, 18 if idx == 0 else 20)
            shadow_offset = 14 if idx == 0 else 10
            radius = 28 if idx == 0 else 22
            frame.rounded_rectangle((x + shadow_offset, y + shadow_offset, x + tile_width + shadow_offset, y + tile_height + shadow_offset), radius=radius, fill=(0, 0, 0, 118))
            canvas.alpha_composite(tile, (x, y))
            frame.rounded_rectangle((x, y, x + tile_width, y + tile_height), radius=radius, outline=accent if idx % 2 == 0 else secondary, width=3)
    else:
        columns = 4 if len(tile_specs) > 6 else 3
        rows = max(1, math.ceil(len(tile_specs) / columns))
        tile_width = int((grid_width - gutter * (columns - 1)) / columns)
        tile_height = int((grid_height - gutter * (rows - 1)) / rows)

        for idx, tile_spec in enumerate(tile_specs):
            source_path = _resolve_source(repo_root, source_root, str(tile_spec.get("source") or ""), output_root)
            tile = Image.open(source_path).convert("RGB")
            tile = _fit_cover(tile, (tile_width, tile_height), tile_spec.get("focus") or (0.5, 0.5), zoom=float(tile_spec.get("zoom") or 1.0))
            tile = _contrast(_saturate(_darken(tile, 0.78), 1.05), 1.06)
            tile = _blend_overlay(tile, accent if idx % 2 == 0 else secondary, 18)
            col = idx % columns
            row = idx // columns
            row_start = row * columns
            row_count = min(columns, max(0, len(tile_specs) - row_start))
            row_span = row_count * tile_width + max(0, row_count - 1) * gutter
            row_offset = max(0, (grid_width - row_span) // 2)
            x = grid_left + row_offset + col * (tile_width + gutter)
            y = grid_top + row * (tile_height + gutter)
            frame = ImageDraw.Draw(canvas)
            frame.rounded_rectangle((x + 10, y + 12, x + tile_width + 10, y + tile_height + 12), radius=24, fill=(0, 0, 0, 110))
            canvas.alpha_composite(tile, (x, y))
            frame.rounded_rectangle((x, y, x + tile_width, y + tile_height), radius=22, outline=accent if idx % 2 == 0 else secondary, width=3)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rail = _vertical_gradient((copy_width + 44, height), (8, 12, 18, 220), (8, 12, 18, 196))
    overlay.alpha_composite(rail, (0, 0))
    draw.polygon([(copy_width + 2, 0), (copy_width + 18, 0), (copy_width - 44, height), (copy_width - 60, height)], fill=(accent[0], accent[1], accent[2], 165))
    draw.line((copy_width + 24, 34, copy_width - 18, height - 34), fill=(secondary[0], secondary[1], secondary[2], 144), width=3)
    draw.rounded_rectangle((pad - 6, 76, copy_width - 74, 184), radius=28, fill=(14, 19, 28, 118), outline=(255, 255, 255, 28), width=1)
    draw.rounded_rectangle((pad - 8, 210, copy_width - 52, height - 104), radius=34, fill=(10, 15, 22, 72), outline=(255, 255, 255, 18), width=1)
    _draw_panel_motif(
        draw,
        motif="network_nodes",
        rect=(pad + 8, 86, copy_width - 94, 182),
        accent=(accent[0], accent[1], accent[2], 160),
        secondary=(secondary[0], secondary[1], secondary[2], 120),
    )

    series_label = str(spec.get("series_label") or "").strip()
    if series_label:
        _tracked_text(draw, (pad, 48), series_label, label_font, (238, 240, 243, 230), 3)

    title = str(spec.get("title") or "").strip()
    title_font, title_lines, title_size = _fit_text_block(
        draw,
        text=title,
        font_path=title_font_path,
        max_size=116,
        min_size=72,
        max_width=copy_width - (pad * 2) - 8,
        max_lines=2,
    )
    title_y = 242
    title_step = int(title_size * 0.84)
    draw.line((pad, title_y - 22, pad + 72, title_y - 22), fill=(secondary[0], secondary[1], secondary[2], 200), width=3)
    for idx, line in enumerate(title_lines):
        draw.text((pad, title_y + idx * title_step), line, font=title_font, fill=(246, 247, 250, 245))

    subtitle = str(spec.get("subtitle") or "").strip()
    body_font, subtitle_lines, body_size = _fit_text_block(
        draw,
        text=subtitle,
        font_path=body_font_path,
        max_size=32,
        min_size=24,
        max_width=copy_width - (pad * 2) - 8,
        max_lines=4,
    )
    subtitle_y = title_y + len(title_lines) * title_step + 20
    body_step = int(body_size * 1.22)
    for idx, line in enumerate(subtitle_lines[:4]):
        draw.text((pad + 2, subtitle_y + idx * body_step), line, font=body_font, fill=(218, 223, 228, 226))

    chips = [str(item).strip() for item in (spec.get("chips") or []) if str(item).strip()]
    chip_x = pad
    chips_y = max(subtitle_y + min(len(subtitle_lines), 4) * body_step + 32, height - 96)
    for chip in chips[:3]:
        chip_width = _draw_chip(draw, text=chip, x=chip_x, y=chips_y, font=chip_font, accent=(accent[0], accent[1], accent[2], 225))
        chip_x += chip_width + 14

    _draw_footer(draw, width=width, height=height, font=chip_font, accent=(secondary[0], secondary[1], secondary[2], 220))
    combined = _apply_editorial_finish(Image.alpha_composite(canvas, overlay)).convert("RGB")
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
