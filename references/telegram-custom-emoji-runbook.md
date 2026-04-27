# Telegram custom emoji runbook

## Important

- Use `sticker_type=custom_emoji` when creating the set.
- Each tile must be 100×100.
- Static custom emoji are uploaded as `.webp` with `format=static`.
- Long labels should be split into adjacent segments.
- Prefer updating the existing set with `addStickerToSet` / `replaceStickerInSet`.
- Telegram clients/public addemoji pages can lag after updates even when Bot API returns `ok`.

## Safe publishing rules

- Tokens come from environment only.
- Do not commit `.env`, sessions, Bot API tokens, or Telegram user session strings.
- User IDs and set names should be command-line arguments, not hardcoded secrets.
