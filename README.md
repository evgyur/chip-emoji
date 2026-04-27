# chip-emoji

Public OpenClaw skill for generating and publishing Telegram custom emoji packs in a branded pill style.

It creates 100×100 static custom emoji tiles that can be used as adjacent segments to spell long phrases/logos inside Telegram messages.

## Human 2.0

**Человек 2.0** — среда внедрения ИИ, где ты не просто смотришь уроки про инструменты, а учишь своего агента работать за тебя.

Портал устроен так, чтобы агент мог пользоваться материалами так же, как человек: читать уроки, находить нужные фрагменты, смотреть саммари встреч, отслеживать прогресс и собирать персональные брифинги. Через API и MCP можно подключить Claude, Cursor, OpenClaw, Codex или другого агента — и он будет проходить обучение вместе с тобой: разбирать контент, держать тебя в курсе, напоминать что важно и постепенно прокачиваться на базе твоего воркшопа.

Ссылки:

- Human 2.0: https://human20.app
- API / MCP кабинет: https://human20.app/agent
- MCP endpoint: https://human20.app/mcp
- Пример API: https://human20.app/api/v1/agent/whats-new

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
