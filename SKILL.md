---
name: chip-emoji
aliases:
  - chip emoji
  - chip-emoji-pack
  - human20-emoji
  - h20-emoji
  - /chipemoji
  - /emoji_pack_h20
  - /h20_emoji_phrase
description: Generate and publish Telegram custom emoji packs in a branded pill style: multi-emoji logo strips, standalone marks, and uppercase phrase pills.
metadata:
  clawdbot:
    emoji: "🔤"
    command: "/chipemoji"
---

# chip-emoji

Generate Telegram **custom emoji packs** that install via `https://t.me/addemoji/...`.

The skill is optimized for branded pill-style emoji:

- words/phrases split into multiple 100×100 custom emoji tiles;
- white rounded pill backing for readability on dark and Telegram-blue backgrounds;
- optional brand mark on the left;
- Bot API publishing to `custom_emoji` sticker sets.

## Brand assets

By default this public version uses the Human 2.0 public brand assets:

- Brand page: `https://human20.app/brand`
- Lockup PNG: `https://human20.app/brand/logos/png/h20-lockup-dark-1440.png`
- Mark PNG: `https://human20.app/brand/logos/png/h20-mark-512.png`
- Preferred font: Geologica, if installed locally.

Never redraw a brand logo manually if the official asset exists.

## Core visual rule

A wordmark/phrase is not one emoji. It is assembled from adjacent tiles:

```text
[start] [middle] ... [end]
```

Use at least 2 tiles even for short pill elements, because the left/right rounded caps need safe space.

## CLI

Main script:

```bash
python3 bin/chip_emoji.py --help
```

Generate a logo pill locally:

```bash
python3 bin/chip_emoji.py logo \
  --slug h20-logo-medium \
  --pad-x 34
```

Generate an uppercase phrase locally:

```bash
python3 bin/chip_emoji.py phrase \
  --text "новая версия openclaw" \
  --slug openclaw-version \
  --weight 900
```

Create a new Telegram custom emoji pack:

```bash
python3 bin/chip_emoji.py publish-new \
  --owner-id "<TELEGRAM_USER_ID>" \
  --title "@human20 — научись внедрять ИИ" \
  --name-prefix human20_ai \
  --include-logo \
  --include-mark \
  --phrase "новая версия openclaw" \
  --phrase "Новости ИИ" \
  --weight 900
```

Add a phrase to an existing pack:

```bash
python3 bin/chip_emoji.py add-phrase \
  --owner-id "<TELEGRAM_USER_ID>" \
  --set-name "<existing_set_name_by_botusername>" \
  --text "Среда внедрения ИИ" \
  --weight 900
```

## Updating an existing pack

Prefer updating an existing pack with `addStickerToSet` / `replaceStickerInSet` instead of creating a new pack every time.

Recommended workflow for new elements:

1. Generate local 100×100 `.webp` tile(s).
2. Add them with `addStickerToSet`.
3. Verify via `getStickerSet` count and capture new `custom_emoji_id` values.
4. Send a message containing the newly added custom emoji entities grouped by row, so the user can see/use them even if the public addemoji page lags.

Recommended workflow for changes:

1. Locate target `custom_emoji_id` / `file_id` via `getStickerSet`.
2. Render replacement tile(s).
3. Use `replaceStickerInSet` for the specific old sticker(s).
4. Verify with `getStickerSet`.
5. Send the updated row with `custom_emoji_id` entities.

## Telegram propagation caveat

`addStickerToSet` / `replaceStickerInSet` may return `ok: true` and `getStickerSet` may show an increased count, but Telegram clients and the public `addemoji` page can lag for up to about an hour.

Do not treat client lag as failure if Bot API verification succeeds, but communicate the propagation delay clearly.

## Environment

Publishing requires a bot token with Telegram Bot API access:

- `TELEGRAM_BOT_TOKEN`, or
- `SERVER_BOT_TOKEN`

Do not write tokens into files or commits.

## Output

Local generation writes to:

```text
out/chip-emoji/<slug>/
```

Each output includes:

- `preview.png` — visual check on dark and Telegram-blue backgrounds;
- `strip.png` — assembled phrase/logo strip;
- `tiles/*.png` and `tiles/*.webp` — Telegram-ready 100×100 tiles;
- `manifest.json` — source URLs, order, roles, and settings.

Publishing prints:

```text
https://t.me/addemoji/<set_name>
```

## Proven settings

Good medium logo settings:

- white pill backing;
- lockup content height: `68px`;
- horizontal padding: `34px`;
- vertical padding: `9px`;
- output width rounded up to whole 100px tiles;
- standalone mark can be included as separate emoji.

For phrases:

- uppercase text;
- Geologica font, bold weight `900` by default;
- white pill backing;
- optional mark on the left;
- dark text `#2C2C2C`.
