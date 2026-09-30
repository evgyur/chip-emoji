# Any image as an inline custom-emoji mosaic

Use for any supplied/authorized image, including the approved Human20 mascot. Not a photo attachment. Preserve source pixels/identity, no redraw, no forced stretching/cropping. Tool: scripts/mosaic.py, Python stdlib + ImageMagick convert, no PIL or network writes.

## Accepted geometry

9 columns × 11 rows. Content canvas 900x880. Source proportionally fit to 840x840, centered with transparent margins. Crop row-major into 100x80 content tiles, then PAD each to 100x100 (10 transparent pixels top/bottom). Do NOT resize 100x80 to 100x100: it cancels compensation. Telegram line advance can be less than emoji height; full-height content overlaps and clips head/hands. Do not force source to 900x1125 then extent900x1100: clipping and distortion. This preset was visually accepted on Chip's mobile client, not a universal guarantee for every client/font size. Check actual preview.

Prepare: `python3 <skill-dir>/scripts/mosaic.py prepare <source.png> <fresh-output-dir>` (optional --columns, --rows, --content-height, --margin). Outputs source.png, tiles/*.webp, manifest.json. Default square fit is conservative for landscape/portrait; reduce columns/adjust rows explicitly if useful, never clip. Inspect local reconstruction before publication.

## Reuse accepted mascot

assets/human20-mosaic.json stores accepted pack and 99 ordered IDs; reuse without creating another pack. Approved original: img/assets/human20/mascot-explaining-approved.png. Never rely solely on old scratch scripts/state (temporary).

## Publish new image

A new set is an external side effect: scope authority for source and owner bot, live getMe and managed-runtime verification required. Use the timeout-aware publishing procedure below. Use secure token scope, never print or persist secrets. Preupload, add sequentially, save resume state and reconcile timeouts with getStickerSet before retry. Read back exact count/dimensions/order and put live custom_emoji_id values into manifest (upload file_id is NOT emoji ID). Replacement can change IDs: rebuild message entities from live pack. Never blame cache without evidence.

## Compose

`python3 <skill-dir>/scripts/mosaic.py compose <manifest.json> <payload.json> --before-file <plain-text.txt> --entities-file <before-entities.json> --after-file <optional-plain-tail.txt>`

Payload contains text and explicit Bot API entities; offsets in UTF-16, astral glyphs count two. Existing entities describe BEFORE only; AFTER is plain (merge rich tail entities with shifted UTF-16 offsets yourself). For middle placement preserve all suffix bold/link/code entities explicitly. No parse_mode with explicit entities. Telethon requires MessageEntityCustomEmoji(document_id=int(id)): convert using live transport schema. U+200B starts mosaic, no spaces between cells, exactly one newline per row; avoids enlarged emoji-only rendering. Never replace with Unicode-only grid.

No automatic sends: /tg owns copy gates, ChipCR sender, preview chat, exact fetch-back, native attestation and public-publish authorization. Text/caption limits differ; never truncate silently. Read final exact message: all row-major IDs, entity count plus original footer emojis, correct sender, bold/links/copy retained. API success is not visual success; mobile QA checks seams, compression and complete head/hands.

Tests: «сделай эту картинку из эмодзи» -> prepare/authorized publish/mobile QA; «/tg вставь маскота мозаикой» -> accepted IDs + explicit entities; «прикрепи фото» -> normal photo, not mosaic; «превью» -> no public publication.
