# ASUcend: a Cubbie Skill for ASU students

ASUcend turns ASU campus life into a gentle, real-world RPG inside Cubbie's messages. Real, verified ASU events become quests. Students opt in to XP, medals, a game-style voice and themed weekly player cards. Student parents, older siblings and tutors can also run separate, parent-confirmed homework quests for a child (ages 6-17), with reward cards designed for each age group.

**Install in Cubbie:** text https://github.com/kjodhpur/asucend to Cubbie, approve the install, then send:

> Start ASUcend. I'm an ASU student interested in AI, shy, and only free Friday afternoons. Find my first free quest.

No app, server, database, wallet or paid rewards. Cubbie handles browsing, Calendar, reminders, memory and messaging; small standard-library Python scripts keep the game state and draw the cards.

## What's inside

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Core instructions Cubbie follows: hard rules, the student quest loop, replies and fallbacks |
| `references/kids.md` | Parent-run child profiles: setup, tasks, parent confirmation, privacy, deletion |
| `references/personalization.md` | Opt-in features, game voice, storylines, choosing a theme from a favorite game |
| `references/cards.md` | Reward card layouts per age group, themes, PNG delivery and fallbacks |
| `scripts/xp.py` | Quest ledger: profiles, age segments, XP, levels, medals, adaptive difficulty |
| `scripts/plan.py` | Ranks Cubbie-verified event candidates against free time, cost and comfort |
| `scripts/card.py` | Renders portrait reward cards (SVG, plus PNG with `--png`) |
| `scripts/preferences.py`, `scripts/themes.py` | Opt-in features, voice, card themes |
| `assets/cards/` | Hand-drawn original card layouts and theme scenes |
| `assets/fonts/` | Open Font License fonts so PNG cards look the same in any sandbox |
| `assets/sample_*` | **Fictional demo data only** |
| `tests/` | Unit and command-line integration tests |

## Age groups and cards

| Profile | Quests | Card |
| --- | --- | --- |
| ASU student (default) | Verified ASU events, solo campus quests | Player card: neon, fantasy, retro, anime, cozy, scifi or custom colours |
| Teen 13-17 (parent-run) | Homework, study, projects, helping | Player card, same themes |
| Junior 9-12 (parent-run) | Homework, reading, practice, chores | Quest card: dinos, space, unicorn, robots |
| Little 6-8 (parent-run) | Homework, reading, chores | Star chart: dinos, space, unicorn, robots |

Child profiles never search events or store links, locations or photos; only a nickname is kept, and XP needs the parent's confirmation.

## Run it locally

```bash
python3 -m unittest discover -s tests -v
python3 scripts/plan.py --sample
python3 scripts/xp.py --sample --today 2026-10-24 --json status
python3 scripts/card.py --sample --today 2026-10-24 --theme fantasy --out /tmp/asucend-fantasy.svg
python3 scripts/card.py --sample --profile little-demo --today 2026-10-24 --theme dinos --out /tmp/asucend-little.svg
```

For PNG cards (what iMessage shows inline), install the renderer once and add `--png`:

```bash
python3 -m venv ~/.local/share/venvs/asucend
~/.local/share/venvs/asucend/bin/pip install resvg-py==0.3.2
~/.local/share/venvs/asucend/bin/python scripts/card.py --sample --today 2026-10-24 --out /tmp/asucend.svg --png
```

## Before submitting

```bash
python3 ../cubbie-hackathon-kit/skills/cubbie-skill-creator/scripts/validate_cubbie_skill.py .
```

Then push to `main` of the public repo and run the live checks in `TESTING.md` on a real Cubbie account. Local tests don't replace that. Review the public entry preview as a team before submitting.

Everything beyond event discovery is opt-in and reversible; `python3 scripts/preferences.py reset-presentation` turns all extras off without losing XP. Game themes are original genre art: no commercial game characters, logos or screens are included.
