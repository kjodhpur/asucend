# Reward cards

Cards are drawn by `scripts/card.py` from hand-designed templates. They are free and identical every time; no image-generation credits are used. Every card is a 1080x1350 portrait.

## Layout for each age group

| Profile | Layout | Shows | Themes |
| --- | --- | --- | --- |
| Student `me`, Teen 13-17 | Player card | Level crest, title, XP bar (this level), quests this week, lifetime quests, momentum, skill-tree chart, medal vault | neon, fantasy, retro, anime, cozy, scifi, custom |
| Junior 9-12 | Quest card | Level badge, title ribbon, XP bar, this week's finished tasks, skill bars, badge stickers | dinos, space, unicorn, robots |
| Little 6-8 | Star chart | Level badge, title ribbon, stars this week, road to the next level (no numbers), sticker book | dinos, space, unicorn, robots |

Templates live in `assets/cards/layouts/`, theme scenes in `assets/cards/scenes/`, colours and fonts in `scripts/themes.py`. All art is original.

## Making a card

```bash
# Student, one-off request (doesn't turn on weekly cards):
python3 scripts/card.py --once --today 2026-10-24 --out /path/to/private/card.svg --png
# A child's card:
python3 scripts/card.py --profile maya --once --today 2026-10-24 --out /path/to/private/maya.svg --png
# Weekly card, only after the student opted into weekly_cards and a weekly check-in:
python3 scripts/card.py --today 2026-10-24 --out /path/to/private/weekly.svg --png
# Try another look once without saving it:
python3 scripts/card.py --once --today 2026-10-24 --theme retro --out /path/to/private/retro.svg
# Fictional demo data, never personal:
python3 scripts/card.py --sample --today 2026-10-24 --out /tmp/asucend-demo.svg
python3 scripts/card.py --sample --profile junior-demo --today 2026-10-24 --theme robots --out /tmp/junior-demo.svg
```

Pass the student-local date. Without `--once`, the script refuses unless weekly cards are on.

## Sending it

- `--png` writes a PNG beside the SVG. Use the venv Python from the Setup section of SKILL.md so `resvg-py` is available; it renders with the bundled fonts in `assets/fonts/`, so the card looks the same everywhere.
- The script prints `png_path`. Send that image. If it prints `png_error`, send the SVG if the chat can show it; otherwise send a short text summary (level, XP to the next level, new medals) and say the image couldn't be made. Never promise an image that wasn't created.
- With a reply, say what's new in one or two lines: "Level 4 unlocked! New medal: First Contact."
- Ask before sending a card to anyone else or posting it.

## Illustrated medals (optional)

Only with `visual_medals` on, at a level-up or a rare medal, ask: "Want an illustrated medal? It may use extra generation credits." Use image generation only if Cubbie actually has it and the student says yes; otherwise send the template card. Never promise image generation.
