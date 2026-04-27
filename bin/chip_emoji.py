#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Iterable

import requests
from PIL import Image, ImageDraw, ImageFont

TILE = 100
SCALE = 4
OUT_ROOT = Path.cwd() / "out" / "chip-emoji"
LOCKUP_URL = "https://human20.app/brand/logos/png/h20-lockup-dark-1440.png"
MARK_URL = "https://human20.app/brand/logos/png/h20-mark-512.png"
GEOLOGICA = Path("/home/chip/human20-app/frontend-v2/public/brand/fonts/Geologica[CRSV,SHRP,slnt,wght].ttf")
BRAND_TEXT = "#2C2C2C"
TG_BLUE = "#3390EC"
DARK_BG = "#0F172A"
CANVAS = "#F3F4F6"


def slugify(s: str) -> str:
    s = s.lower().replace("ё", "е")
    s = re.sub(r"[^a-zа-я0-9]+", "-", s, flags=re.I).strip("-")
    return s or "chip-emoji"


def safe_set_name(prefix: str, bot_username: str) -> str:
    prefix = re.sub(r"[^a-z0-9_]", "_", prefix.lower()).strip("_") or "chip_emoji"
    suffix = f"_by_{bot_username.lower()}"
    stem = f"{prefix}_{int(time.time())}"
    return (stem[: 64 - len(suffix)] + suffix)[:64]


def fetch(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    dest.write_bytes(r.content)
    return dest


def load_font(size: int, weight: int = 900):
    if GEOLOGICA.exists():
        f = ImageFont.truetype(str(GEOLOGICA), size)
        try:
            # Geologica variable axes: Weight, Cursive, Sharpness, Slant.
            f.set_variation_by_axes([weight, 0, 0, 0])
        except Exception:
            pass
        return f
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int, max_h: int, start: int, min_size: int, weight: int = 900):
    for size in range(start, min_size - 1, -2):
        f = load_font(size, weight=weight)
        b = draw.textbbox((0, 0), text, font=f)
        if b[2] - b[0] <= max_w and b[3] - b[1] <= max_h:
            return f
    return load_font(min_size, weight=weight)


def clean_out(slug: str, clean: bool) -> Path:
    out = OUT_ROOT / slug
    if clean and out.exists():
        shutil.rmtree(out)
    (out / "tiles").mkdir(parents=True, exist_ok=True)
    return out


def rounded_white_pill(canvas_w: int, visible_w: int, pill_h: int) -> tuple[Image.Image, int, int]:
    canvas = Image.new("RGBA", (canvas_w, TILE), (0, 0, 0, 0))
    pill_x = (canvas_w - visible_w) // 2
    pill_y = (TILE - pill_h) // 2
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((pill_x + 2, pill_y + 2, pill_x + visible_w - 1, pill_y + pill_h + 2), radius=pill_h // 2, fill=(0, 0, 0, 34))
    canvas = Image.alpha_composite(canvas, shadow)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((pill_x, pill_y, pill_x + visible_w - 1, pill_y + pill_h), radius=pill_h // 2, fill=(255, 255, 255, 255), outline=(229, 231, 235, 255), width=1)
    return canvas, pill_x, pill_y


def save_tiles(strip: Image.Image, out: Path, stem: str) -> list[dict]:
    entries = []
    tiles = strip.width // TILE
    for i in range(tiles):
        role = "start" if i == 0 else "end" if i == tiles - 1 else "middle"
        crop = strip.crop((i * TILE, 0, (i + 1) * TILE, TILE))
        png = out / "tiles" / f"{stem}_{i+1:02d}_{role}.png"
        webp = out / "tiles" / f"{stem}_{i+1:02d}_{role}.webp"
        crop.save(png)
        crop.save(webp, "WEBP", lossless=True, quality=100, method=6)
        entries.append({"index": i + 1, "role": role, "png": str(png.relative_to(out)), "webp": str(webp.relative_to(out))})
    return entries


def make_preview(strip: Image.Image, out: Path, title: str):
    w = max(strip.width + 40, 560)
    prev = Image.new("RGB", (w, 300), DARK_BG)
    d = ImageDraw.Draw(prev)
    d.text((20, 15), f"{title} — dark background", fill="white")
    prev.paste(strip, (20, 45), strip)
    d.text((20, 135), f"{title} — Telegram blue bubble", fill="white")
    d.rounded_rectangle((20, 165, strip.width + 20, 265), radius=45, fill=TG_BLUE)
    prev.paste(strip, (20, 165), strip)
    prev.save(out / "preview.png")


def render_logo(slug: str, pad_x: int = 34, content_h: int = 68, pad_y: int = 9, clean: bool = False) -> Path:
    out = clean_out(slug, clean)
    src = fetch(LOCKUP_URL, out / "source-h20-lockup-dark-1440.png")
    logo = Image.open(src).convert("RGBA")
    logo = logo.crop(logo.getbbox())
    logo_w = math.ceil(logo.width * (content_h / logo.height))
    logo = logo.resize((logo_w, content_h), Image.Resampling.LANCZOS)
    visible_w = logo_w + pad_x * 2
    canvas_w = math.ceil(visible_w / TILE) * TILE
    pill_h = content_h + pad_y * 2
    strip, pill_x, _ = rounded_white_pill(canvas_w, visible_w, pill_h)
    strip.alpha_composite(logo, (pill_x + pad_x, (TILE - content_h) // 2))
    strip.save(out / "strip.png")
    entries = save_tiles(strip, out, "h20_logo")
    make_preview(strip, out, "Human 2.0 logo pill")
    manifest = {"kind": "logo", "source_url": LOCKUP_URL, "pad_x": pad_x, "content_h": content_h, "pad_y": pad_y, "tile_size": TILE, "tiles": entries}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def render_mark(slug: str, clean: bool = False) -> Path:
    out = clean_out(slug, clean)
    src = fetch(MARK_URL, out / "source-h20-mark-512.png")
    mark = Image.open(src).convert("RGBA")
    mark = mark.crop(mark.getbbox())
    mark_w = 86
    mark_h = round(mark.height * (mark_w / mark.width))
    mark = mark.resize((mark_w, mark_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    canvas.alpha_composite(mark, ((TILE - mark_w) // 2, (TILE - mark_h) // 2))
    png = out / "tiles" / "h20_mark_standalone.png"
    webp = out / "tiles" / "h20_mark_standalone.webp"
    canvas.save(png)
    canvas.save(webp, "WEBP", lossless=True, quality=100, method=6)
    canvas.save(out / "preview.png")
    (out / "manifest.json").write_text(json.dumps({"kind": "mark", "source_url": MARK_URL, "tile_size": TILE, "tiles": [{"index": 1, "role": "standalone", "png": str(png.relative_to(out)), "webp": str(webp.relative_to(out))}]}, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def render_phrase(text: str, slug: str | None = None, include_mark: bool = True, min_tiles: int = 2, pad_x: int = 22, clean: bool = False, weight: int = 900) -> Path:
    phrase = " ".join(text.strip().split()).upper()
    slug = slug or slugify(phrase)
    out = clean_out(slug, clean)
    tmp = Image.new("RGBA", (4000, TILE * SCALE), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    mark_w = mark_h = 0
    gap = 0
    mark = None
    if include_mark:
        src = fetch(MARK_URL, out / "source-h20-mark-512.png")
        mark = Image.open(src).convert("RGBA").crop(Image.open(src).convert("RGBA").getbbox())
        mark_h = 54 * SCALE
        mark_w = round(mark.width * (mark_h / mark.height))
        mark = mark.resize((mark_w, mark_h), Image.Resampling.LANCZOS)
        gap = 14 * SCALE
    max_h = 42 * SCALE
    font = fit_font(d, phrase, 2400 * SCALE, max_h, 24 * SCALE, 14 * SCALE, weight=weight)
    b = d.textbbox((0, 0), phrase, font=font)
    tw, th = b[2] - b[0], b[3] - b[1]
    pad_l = pad_x * SCALE
    pad_r = max(28, pad_x) * SCALE
    pill_h = 72 * SCALE
    raw_w = pad_l + mark_w + gap + tw + pad_r
    canvas_w = max(min_tiles * TILE * SCALE, math.ceil(raw_w / (TILE * SCALE)) * TILE * SCALE)
    visible_w = raw_w
    canvas = Image.new("RGBA", (canvas_w, TILE * SCALE), (0, 0, 0, 0))
    pill_x = (canvas_w - visible_w) // 2
    pill_y = (TILE * SCALE - pill_h) // 2
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((pill_x + 2*SCALE, pill_y + 2*SCALE, pill_x + visible_w - 1, pill_y + pill_h + 2*SCALE), radius=pill_h // 2, fill=(0, 0, 0, 34))
    canvas = Image.alpha_composite(canvas, shadow)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((pill_x, pill_y, pill_x + visible_w - 1, pill_y + pill_h), radius=pill_h // 2, fill=(255, 255, 255, 255), outline=(229, 231, 235, 255), width=SCALE)
    x = pill_x + pad_l
    if mark is not None:
        canvas.alpha_composite(mark, (x, (TILE * SCALE - mark_h) // 2))
        x += mark_w + gap
    ty = (TILE * SCALE - th) // 2 - b[1] - SCALE
    d.text((x, ty), phrase, font=font, fill=BRAND_TEXT)
    strip = canvas.resize((canvas_w // SCALE, TILE), Image.Resampling.LANCZOS)
    strip.save(out / "strip.png")
    entries = save_tiles(strip, out, slugify(phrase))
    make_preview(strip, out, phrase)
    manifest = {"kind": "phrase", "text": phrase, "source_url": MARK_URL if include_mark else None, "include_mark": include_mark, "tile_size": TILE, "tiles": entries}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def webp_paths(out: Path) -> list[Path]:
    return sorted((out / "tiles").glob("*.webp"))


def telegram_base():
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("SERVER_BOT_TOKEN")
    if not token:
        raise SystemExit("Need TELEGRAM_BOT_TOKEN or SERVER_BOT_TOKEN in environment")
    return f"https://api.telegram.org/bot{token}"


def bot_username(base: str) -> str:
    r = requests.get(base + "/getMe", timeout=20)
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise SystemExit(data)
    return data["result"]["username"]


def add_file_to_set(base: str, owner_id: str, set_name: str, path: Path, emoji: str = "💬"):
    sticker = {"sticker": "attach://stickerfile", "format": "static", "emoji_list": [emoji]}
    with path.open("rb") as f:
        r = requests.post(base + "/addStickerToSet", data={"user_id": owner_id, "name": set_name, "sticker": json.dumps(sticker, ensure_ascii=False)}, files={"stickerfile": (path.name, f, "image/webp")}, timeout=60)
    if not (r.ok and r.json().get("ok")):
        raise SystemExit(f"addStickerToSet failed for {path}: {r.text}")


def create_set(base: str, owner_id: str, title: str, name: str, paths: list[Path]) -> str:
    files = {}
    stickers = []
    emoji_list = ["💬", "✨", "🔵", "🤍", "🧠", "🚀", "✅", "🐾"]
    try:
        for i, p in enumerate(paths):
            key = f"sticker{i}"
            files[key] = (p.name, p.open("rb"), "image/webp")
            stickers.append({"sticker": f"attach://{key}", "format": "static", "emoji_list": [emoji_list[i % len(emoji_list)]]})
        r = requests.post(base + "/createNewStickerSet", data={"user_id": owner_id, "name": name, "title": title, "stickers": json.dumps(stickers, ensure_ascii=False), "sticker_type": "custom_emoji"}, files=files, timeout=90)
    finally:
        for v in files.values():
            try:
                v[1].close()
            except Exception:
                pass
    if not (r.ok and r.json().get("ok")):
        raise SystemExit(f"createNewStickerSet failed: {r.text}")
    return f"https://t.me/addemoji/{name}"


def cmd_logo(args):
    out = render_logo(args.slug, args.pad_x, args.content_h, args.pad_y, args.clean)
    print(json.dumps({"out": str(out), "preview": str(out / "preview.png"), "tiles": len(webp_paths(out))}, ensure_ascii=False, indent=2))


def cmd_mark(args):
    out = render_mark(args.slug, args.clean)
    print(json.dumps({"out": str(out), "preview": str(out / "preview.png")}, ensure_ascii=False, indent=2))


def cmd_phrase(args):
    out = render_phrase(args.text, args.slug, not args.no_mark, args.min_tiles, args.pad_x, args.clean, args.weight)
    print(json.dumps({"out": str(out), "preview": str(out / "preview.png"), "tiles": len(webp_paths(out))}, ensure_ascii=False, indent=2))


def cmd_publish_new(args):
    base = telegram_base()
    name = args.set_name or safe_set_name(args.name_prefix, bot_username(base))
    paths: list[Path] = []
    work_slug = name.replace("_by_", "-")
    if args.include_logo:
        paths.extend(webp_paths(render_logo(work_slug + "-logo", args.pad_x, args.content_h, args.pad_y, True)))
    for phrase in args.phrase or []:
        paths.extend(webp_paths(render_phrase(phrase, slug=work_slug + "-" + slugify(phrase), include_mark=True, clean=True, weight=args.weight)))
    if args.include_mark:
        paths.extend(webp_paths(render_mark(work_slug + "-mark", True)))
    if not paths:
        raise SystemExit("Nothing to publish: pass --include-logo, --include-mark, or --phrase")
    link = create_set(base, args.owner_id, args.title, name, paths)
    print(json.dumps({"set_name": name, "link": link, "stickers": len(paths)}, ensure_ascii=False, indent=2))


def cmd_add_phrase(args):
    out = render_phrase(args.text, args.slug or slugify(args.text), not args.no_mark, args.min_tiles, args.pad_x, args.clean, args.weight)
    base = telegram_base()
    for p in webp_paths(out):
        add_file_to_set(base, args.owner_id, args.set_name, p, "💬")
    print(json.dumps({"set_name": args.set_name, "link": f"https://t.me/addemoji/{args.set_name}", "added": len(webp_paths(out)), "preview": str(out / "preview.png")}, ensure_ascii=False, indent=2))


def build_parser():
    p = argparse.ArgumentParser(description="Generate and publish Chip/Human 2.0 Telegram custom emoji packs")
    sub = p.add_subparsers(required=True)
    logo = sub.add_parser("logo")
    logo.add_argument("--slug", default="h20-logo-pill")
    logo.add_argument("--pad-x", type=int, default=34)
    logo.add_argument("--content-h", type=int, default=68)
    logo.add_argument("--pad-y", type=int, default=9)
    logo.add_argument("--clean", action="store_true")
    logo.set_defaults(func=cmd_logo)

    mark = sub.add_parser("mark")
    mark.add_argument("--slug", default="h20-mark")
    mark.add_argument("--clean", action="store_true")
    mark.set_defaults(func=cmd_mark)

    phrase = sub.add_parser("phrase")
    phrase.add_argument("--text", required=True)
    phrase.add_argument("--slug")
    phrase.add_argument("--no-mark", action="store_true")
    phrase.add_argument("--min-tiles", type=int, default=2)
    phrase.add_argument("--pad-x", type=int, default=22)
    phrase.add_argument("--weight", type=int, default=900, help="Geologica variable font weight; default 900 for bold phrase pills")
    phrase.add_argument("--clean", action="store_true")
    phrase.set_defaults(func=cmd_phrase)

    pub = sub.add_parser("publish-new")
    pub.add_argument("--owner-id", required=True)
    pub.add_argument("--title", default="Chip emoji pack")
    pub.add_argument("--name-prefix", default="chip_emoji")
    pub.add_argument("--set-name")
    pub.add_argument("--include-logo", action="store_true")
    pub.add_argument("--include-mark", action="store_true")
    pub.add_argument("--phrase", action="append")
    pub.add_argument("--pad-x", type=int, default=34)
    pub.add_argument("--content-h", type=int, default=68)
    pub.add_argument("--pad-y", type=int, default=9)
    pub.add_argument("--weight", type=int, default=900, help="Geologica variable font weight for phrases")
    pub.set_defaults(func=cmd_publish_new)

    add = sub.add_parser("add-phrase")
    add.add_argument("--owner-id", required=True)
    add.add_argument("--set-name", required=True)
    add.add_argument("--text", required=True)
    add.add_argument("--slug")
    add.add_argument("--no-mark", action="store_true")
    add.add_argument("--min-tiles", type=int, default=2)
    add.add_argument("--pad-x", type=int, default=22)
    add.add_argument("--weight", type=int, default=900, help="Geologica variable font weight; default 900 for bold phrase pills")
    add.add_argument("--clean", action="store_true")
    add.set_defaults(func=cmd_add_phrase)
    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
