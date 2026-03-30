#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import yaml

try:
    from PIL import Image, ImageStat
except Exception as exc:  # pragma: no cover
    raise RuntimeError("Pillow is required to validate editorial covers") from exc


ROOT = Path(__file__).resolve().parents[2]
PRODUCT_ROOT = ROOT / "products" / "chummer"
CONFIG_PATH = PRODUCT_ROOT / "PUBLIC_GUIDE_EDITORIAL_COVERS.yaml"
CURATION_PATH = PRODUCT_ROOT / "PUBLIC_GUIDE_IMAGE_CURATION.yaml"
PUBLIC_EDITORIAL_TEXT_BANNED_PHRASES = (
    "engine truth",
    "future lanes",
    "truth filter",
    "trust seams",
    "provenance",
    "bounded product moves",
    "grounded seams",
    "each lane",
    "session shell",
    "bounded post-session coaching",
    "canon",
    "artifacts",
    "hosted participation",
    "hosting",
    "public assets",
    "renders",
    "briefs",
)


def _load_yaml(path: Path) -> dict[str, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a YAML object")
    return payload


def _luma_mean(image: Image.Image) -> float:
    red, green, blue = ImageStat.Stat(image.convert("RGB")).mean
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _luma_stddev(image: Image.Image) -> float:
    red, green, blue = ImageStat.Stat(image.convert("RGB")).stddev
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _bright_ratio(image: Image.Image, threshold: int) -> float:
    histogram = image.convert("L").histogram()
    total = float(sum(histogram) or 1.0)
    return sum(histogram[int(threshold) :]) / total


def _normalized_asset_key(value: object) -> str:
    return str(value or "").replace("\\", "/").strip()


def _normalized_repo_path(value: object) -> str:
    return _normalized_asset_key(value).lstrip("./")


def _cover_text_errors(target: str, spec: dict[str, object]) -> list[str]:
    text_fields: list[tuple[str, str]] = []
    for key in ("series_label", "title", "subtitle"):
        value = str(spec.get(key) or "").strip()
        if value:
            text_fields.append((key, value))
    chips = spec.get("chips") or []
    if isinstance(chips, list):
        for index, chip in enumerate(chips):
            value = str(chip or "").strip()
            if value:
                text_fields.append((f"chips[{index}]", value))

    errors: list[str] = []
    for field_name, value in text_fields:
        lowered = value.lower()
        for phrase in PUBLIC_EDITORIAL_TEXT_BANNED_PHRASES:
            if phrase in lowered:
                errors.append(f"{target}: {field_name} contains banned editorial phrase {phrase!r}")
    return errors


def _check_feature_cover(target: str, image: Image.Image) -> list[str]:
    width, height = image.size
    left = image.crop((0, 0, int(width * 0.29), height))
    right = image.crop((int(width * 0.31), 0, width, height))
    center = image.crop((int(width * 0.35), int(height * 0.18), int(width * 0.92), int(height * 0.86)))
    top_right = image.crop((int(width * 0.72), 0, width, int(height * 0.62)))

    left_mean = _luma_mean(left)
    left_std = _luma_stddev(left)
    right_mean = _luma_mean(right)
    right_std = _luma_stddev(right)
    center_std = _luma_stddev(center)
    hot_180 = _bright_ratio(top_right, 180)
    hot_160 = _bright_ratio(top_right, 160)

    errors: list[str] = []
    if left_mean > 48.0:
        errors.append(f"{target}: copy rail is too bright ({left_mean:.1f})")
    if left_std < 18.0:
        errors.append(f"{target}: copy rail is too flat ({left_std:.1f})")
    if right_mean < left_mean + 6.0:
        errors.append(f"{target}: panel does not separate enough from copy rail ({right_mean:.1f} vs {left_mean:.1f})")
    if right_std < 18.0:
        errors.append(f"{target}: panel detail is too flat ({right_std:.1f})")
    if center_std < 16.0:
        errors.append(f"{target}: center composition lacks visual texture ({center_std:.1f})")
    if hot_180 > 0.09:
        errors.append(f"{target}: hotspot spread is too aggressive ({hot_180:.4f} > 0.09)")
    if hot_160 > 0.20:
        errors.append(f"{target}: bright-region dominance is too aggressive ({hot_160:.4f} > 0.20)")
    return errors


def _check_mosaic_cover(target: str, image: Image.Image) -> list[str]:
    width, height = image.size
    left = image.crop((0, 0, int(width * 0.29), height))
    right = image.crop((int(width * 0.31), 0, width, height))
    center = image.crop((int(width * 0.35), int(height * 0.12), int(width * 0.95), int(height * 0.92)))

    left_mean = _luma_mean(left)
    left_std = _luma_stddev(left)
    right_std = _luma_stddev(right)
    center_std = _luma_stddev(center)

    errors: list[str] = []
    if left_mean > 42.0:
        errors.append(f"{target}: copy rail is too bright ({left_mean:.1f})")
    if left_std < 18.0:
        errors.append(f"{target}: copy rail is too flat ({left_std:.1f})")
    if right_std < 22.0:
        errors.append(f"{target}: mosaic panel detail is too flat ({right_std:.1f})")
    if center_std < 20.0:
        errors.append(f"{target}: mosaic composition reads too flat ({center_std:.1f})")
    return errors


def main() -> int:
    config = _load_yaml(CONFIG_PATH)
    curation = _load_yaml(CURATION_PATH)
    defaults = dict(config.get("defaults") or {}) if isinstance(config.get("defaults"), dict) else {}
    expected_size = (int(defaults.get("width") or 1600), int(defaults.get("height") or 900))
    output_root = ROOT / str(config.get("output_root") or "products/chummer/public-guide-curated-assets")
    configured_assets = dict(config.get("assets") or {}) if isinstance(config.get("assets"), dict) else {}
    curated_assets = dict(curation.get("assets") or {}) if isinstance(curation.get("assets"), dict) else {}

    errors: list[str] = []
    validated = 0
    for target, raw_spec in configured_assets.items():
        if not isinstance(raw_spec, dict):
            errors.append(f"{target}: config row must be a YAML object")
            continue
        spec = dict(raw_spec)
        target_key = _normalized_asset_key(target)
        output_path = output_root / target_key
        if not output_path.is_file():
            errors.append(f"{target_key}: missing generated editorial cover at {output_path}")
            continue
        curation_row = curated_assets.get(target_key)
        if not isinstance(curation_row, dict):
            errors.append(f"{target_key}: missing image-curation row")
        else:
            review_status = str(curation_row.get("review_status") or "").strip().lower()
            embed_policy = str(curation_row.get("embed_policy") or "").strip().lower()
            source_override = _normalized_repo_path(curation_row.get("source_override"))
            expected_source_override = _normalized_repo_path((Path(str(config.get("output_root") or "products/chummer/public-guide-curated-assets")) / target_key).as_posix())
            if review_status != "editorial_cover":
                errors.append(f"{target_key}: curation review_status must be editorial_cover")
            if embed_policy != "manual":
                errors.append(f"{target_key}: curation embed_policy must be manual")
            if source_override != expected_source_override:
                errors.append(
                    f"{target_key}: curation source_override must lock to {expected_source_override}, got {source_override or '<empty>'}"
                )
            elif not (ROOT / source_override).is_file():
                errors.append(f"{target_key}: curation source_override is missing on disk at {ROOT / source_override}")
        image = Image.open(output_path).convert("RGB")
        if image.size != expected_size:
            errors.append(f"{target_key}: expected size {expected_size[0]}x{expected_size[1]}, got {image.size[0]}x{image.size[1]}")
        kind = str(spec.get("kind") or "feature_cover").strip().lower()
        errors.extend(_cover_text_errors(target_key, spec))
        if kind == "mosaic_cover":
            errors.extend(_check_mosaic_cover(target_key, image))
        else:
            errors.extend(_check_feature_cover(target_key, image))
        validated += 1

    for target, raw_row in curated_assets.items():
        if not isinstance(raw_row, dict):
            continue
        review_status = str(raw_row.get("review_status") or "").strip().lower()
        embed_policy = str(raw_row.get("embed_policy") or "").strip().lower()
        if review_status == "editorial_cover" and embed_policy == "manual" and target not in configured_assets:
            errors.append(f"{target}: editorial-cover curation row has no matching cover config entry")

    if errors:
        raise SystemExit("editorial_cover_validation_failed:\n- " + "\n- ".join(errors))
    print(f"validated_editorial_covers={validated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
