# Any image as an inline custom-emoji mosaic

Use for any supplied/authorized image, including the approved Human20 mascot. Not a photo attachment. Preserve source pixels/identity, no redraw, no forced stretching/cropping. Tool: scripts/mosaic.py, Python stdlib + ImageMagick convert, no PIL or network writes.

## Accepted geometry

9 columns × 11 rows. Content canvas 900x880. Source proportionally fit to 840x840, centered with transparent margins. Crop row-major into 100x80 content tiles, then PAD each to 100x100 (10 transparent pixels top/bottom). Do NOT resize 100x80 to 100x100: it cancels compensation. Telegram line advance can be less than emoji height; full-height content overlaps and clips head/hands. Do not force source to 900x1125 then extent900x1100: clipping and distortion. This preset was visually accepted on Chip's mobile client, not a universal guarantee for every client/font size. Check actual preview.

Prepare: `python3 <skill-dir>/scripts/mosaic.py prepare <source.png> <fresh-output-dir>` (optional --columns, --rows, --content-height, --margin). Outputs source.png, tiles/*.webp, manifest.json. Default square fit is conservative for landscape/portrait; reduce columns/adjust rows explicitly if useful, never clip. Inspect local reconstruction before publication.

## Reliable slow assembly with a permanent final image

Prefer **static custom emoji plus staged edits of one message** when a picture must assemble gradually and stay complete. Independent video emoji are not a shared animation timeline: transparent starting frames and short full-image intervals can leave a client with only part of a mosaic visible. A valid video pack, matching IDs or a successful API response does not prove synchronized playback. Do not diagnose cache or a client defect without evidence.

1. Prepare the proportional padded tiles above. Publish the content tiles as `static`; add one separate static blank/background tile with the same 100x100 geometry and row padding. Keep its ID outside the row-major content ID list. Do not use an animated transparent tile as the blank.
2. Keep one message and one exact reply parent. For an explicitly authorized direct reply, verify the publishing bot with `getMe` and use its own identity when eligible to send custom emoji. A preview-only request does not authorize sending. Preserve an existing reply/message instead of publishing duplicate mosaics.
3. Generate deterministic payloads offline:

   ```bash
   python3 scripts/mosaic.py reveal-frames manifest.json frames.json \
     --blank-id <published-static-blank-id> --steps 6
   ```

   Optional `--seed`, `--before-file`, `--after-file` and `--entities-file` preserve repeatable reveal order and the existing compose contracts. The manifest holds only content `emoji_ids` in display order. The helper changes which cells are visible, never their positions, row/newline geometry, UTF-16 offsets or final order. It performs no network calls.
4. Apply `frames[].payload` in order with `editMessageText`, explicit entities and no `parse_mode`. Keep every grid cell occupied by either its static content ID or the static blank ID. Space edits roughly 1–1.5 seconds apart; honor Telegram `retry_after` rather than assuming a frame rate. This is a one-time reveal on delivery, not a looping pack animation; later readers see the complete static result.
5. Treat the full final payload as the invariant, not the animation completing. Record progress, and in a `finally`/recovery path apply the final frame if an intermediate edit fails. On an ambiguous outcome, read back the same message before retrying. Resume to the complete final frame; do not rewind an already visible image or send a new message automatically. The executor, not the offline helper, owns this error/recovery behavior.
6. Read the exact message back. Require all final row-major content IDs, **zero blank IDs**, correct sender/reply parent and preserved footer links. Read the exact pack back and require static, non-video, non-animated 100x100 content. Download all live tiles, remove only the intentional row padding and reconstruct the image; inspect the full source/wording/order rather than three isolated samples. Telegram may re-encode WebP, so decoded visual comparison is stronger than upload `file_unique_id` equality.
7. Separate server/asset proof from client appearance. The final static workflow has owner-confirmed mobile acceptance; it is the preferred route for this effect, not proof for every later client/font setting. If the owner still sees missing pieces or seams, inspect their exact screenshot/message. Do not claim mobile QA from a local reconstruction alone. Preserve a known old pack unless its removal is explicitly requested; if the fix uses a new static pack, update both message entities and its addemoji footer and report the new link.

Checks: six frames must reveal monotonically and deterministically; the final payload must equal ordinary full `compose`; invalid blank IDs, geometry and step counts must fail; rich prefixes/astral characters must retain correct offsets. Test existing `prepare` and `compose` behavior too. Store only portable recipes and compact nonsecret receipts in a public skill, never raw chat envelopes, credentials or real recipients' identifiers.

## Reuse accepted mascot

assets/human20-mosaic.json stores accepted pack and 99 ordered IDs; reuse without creating another pack. Approved original: img/assets/human20/mascot-explaining-approved.png. Never rely solely on old scratch scripts/state (temporary).

## Publish new image

A new set is an external side effect: scope authority for source and owner bot, live getMe and managed-runtime verification required. Use the timeout-aware publishing procedure below. Use secure token scope, never print or persist secrets. Preupload, add sequentially, save resume state and reconcile timeouts with getStickerSet before retry. Read back exact count/dimensions/order and put live custom_emoji_id values into manifest (upload file_id is NOT emoji ID). Replacement can change IDs: rebuild message entities from live pack. Never blame cache without evidence.

## Compose

`python3 <skill-dir>/scripts/mosaic.py compose <manifest.json> <payload.json> --before-file <plain-text.txt> --entities-file <before-entities.json> --after-file <optional-plain-tail.txt>`

Payload contains text and explicit Bot API entities; offsets in UTF-16, astral glyphs count two. Existing entities describe BEFORE only; AFTER is plain (merge rich tail entities with shifted UTF-16 offsets yourself). For middle placement preserve all suffix bold/link/code entities explicitly. No parse_mode with explicit entities. Telethon requires MessageEntityCustomEmoji(document_id=int(id)): convert using live transport schema. U+200B starts mosaic, no spaces between cells, exactly one newline per row; avoids enlarged emoji-only rendering. Never replace with Unicode-only grid.

A preview-only request does not authorize a send. For an explicitly requested direct reply use the verified bot's own identity and exact recovered reply parent when eligible. For `/tg` work preserve its selected sender, preview destination and publication gates. Text/caption limits differ; never truncate silently. Read final exact message: all row-major IDs, entity count plus original footer emojis, correct sender, bold/links/copy retained. API success is not visual success; mobile QA checks seams, compression and complete head/hands.

Tests: «сделай эту картинку из эмодзи» -> prepare/authorized publish/mobile QA; «/tg вставь маскота мозаикой» -> accepted IDs + explicit entities; «прикрепи фото» -> normal photo, not mosaic; «превью» -> no public publication.
