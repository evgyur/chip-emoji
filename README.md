# chip-emoji

Public OpenClaw skill for generating and publishing Telegram custom emoji packs in a branded pill style.

It creates 100×100 static custom emoji tiles that can be used as adjacent segments to spell long phrases/logos inside Telegram messages.

## Install/use

```bash
pip install -r requirements.txt
python3 bin/chip_emoji.py --help
```

## Example

```bash
python3 bin/chip_emoji.py phrase \
  --text "Новости ИИ" \
  --slug ai-news \
  --weight 900 \
  --clean
```

Publishing requires `TELEGRAM_BOT_TOKEN` or `SERVER_BOT_TOKEN`.

See [`SKILL.md`](SKILL.md) for the OpenClaw skill instructions.
