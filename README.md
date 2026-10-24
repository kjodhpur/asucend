# ASUcend — a Cubbie Skill for ASU students

An adventurous but gentle real-life RPG inside Cubbie's messaging assistant. ASUcend uses actual ASU events as quests, opt-in calendar planning, comfort-aware difficulty, private XP/medals and optional digital player cards.

**Install in Cubbie:** send https://github.com/kjodhpur/asucend in a Cubbie conversation, confirm the install, then message:

> Start ASUcend. I'm an ASU student interested in AI, shy, and only free Friday afternoons. Find my first free quest.

No separate app, Vercel site, server, remote database, wallet or paid reward integration is required. Cubbie provides browsing, Calendar/Canvas if connected, reminders, memory and message delivery. Python only computes deterministic game state and generates an SVG card.

## Contents

- `SKILL.md` — primary Cubbie instructions, event sourcing, consent, game flow and sample commands
- `scripts/xp.py` — persistent quest ledger, XP, levels, medal unlocks, adaptive hints
- `scripts/plan.py` — offline ranking of Cubbie-supplied, sourced event candidates against calendar windows
- `scripts/card.py` — no-generation-credit weekly RPG card (SVG)
- `assets/sample_candidates.json` — **fictional demo input only**
- `assets/sample_state.json` — **fictional demo progress only**
- `tests/test_asucend.py` — local unit and CLI integration tests

## Offline smoke tests

```bash
python3 -m unittest discover -s tests -v
python3 scripts/plan.py --sample
python3 scripts/xp.py --sample --today 2026-10-24 --json status
python3 scripts/card.py --sample --today 2026-10-24 --out /tmp/asucend-demo.svg
```

## Install and validation checks

Run the official validator from a separate checkout of the Cubbie hackathon kit:

```bash
python3 ../cubbie-hackathon-kit/skills/cubbie-skill-creator/scripts/validate_cubbie_skill.py .
```

Push these files to `main` of the **public** repo. In a real Cubbie account, text the repo link, approve install, verify a sourced ASU event, accept the offered quest, opt into or decline a reminder, provide a brief completion reflection, earn XP, then ask for status in a new conversation. Local tests do **not** replace this test.

ASUcend awards **digital-only** game rewards. Optional generative art is feature-gated: Cubbie must actually support an image-generation ability and the student must request it. Default weekly cards use the local SVG script.

Do not treat example.org demo events as verified ASU listings. Do not submit to the hackathon until the team has reviewed the public entry preview and approved submission.

## Optional personalization (no new app)

A student's favorite **game-world voice** changes only the character-like encouragement in Cubbie's replies. It does **not** translate their actual language, alter assignment text, obscure date/time/links, or impersonate licensed game characters. Keep substantive instructions neutral and accurate.

Voice and visual appearance are **separate** preferences. Any game/fictional atmosphere can inspire an original conversation archetype; cards support six original genre packs (neon, fantasy, retro, anime, cozy, scifi) or a custom hex-color palette. No commercial game artwork is packaged.

Every extra is separately opt-in: XP, storylines, calendar matching, reminders, recurring check-ins, weekly cards, optional image-generation offers, and photo-proof prompts. User can return to plain mode without losing earned XP.

```bash
python3 scripts/preferences.py show
python3 scripts/preferences.py voice --mode light --world 'retro platforming game' --archetype 'cheerful adventure guide'
python3 scripts/preferences.py theme --name retro
python3 scripts/preferences.py feature --name weekly_cards --enabled 1
python3 scripts/card.py --sample --today 2026-10-24 --theme retro --out /tmp/asucend-retro.svg
```

Use `python3 scripts/preferences.py reset-presentation` to turn all extras off while **preserving XP and quest data**. Do not add Cubbie check-ins, calendar events, or messages without the student's consent.
