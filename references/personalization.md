# Optional extras: features, game voice and storylines

Read this when the student wants to gamify asucend, change how Cubbie sounds, or turn something on or off. Every extra is **off by default**, can be changed any time, and turning extras off never erases earned XP.

## Feature switches

| Feature | What it turns on |
| --- | --- |
| `progression` | XP bookkeeping: offer, accept, complete, skip |
| `storylines` | Short narrative chains around real quests |
| `calendar_matching` | Reading Google Calendar busy times (if connected) |
| `reminders` | Offering a reminder before accepted quests |
| `weekly_checkins` | Offering a recurring weekly quest drop |
| `weekly_cards` | A recurring weekly reward card |
| `visual_medals` | Offering illustrated medals at big milestones (needs image generation) |
| `photo_evidence` | Asking for an optional photo as completion proof |

```bash
python3 scripts/preferences.py show
python3 scripts/preferences.py feature --name progression --enabled 1
python3 scripts/preferences.py feature --name storylines --enabled 0
python3 scripts/preferences.py reset-presentation
```

`reset-presentation` turns every extra off and keeps all XP and quest history. A direct request such as "show my XP" or "make me a card" covers that one action; ask before turning on anything recurring. Add `--profile <nickname>` for a child's profile.

## Game voice (text style only)

```bash
python3 scripts/preferences.py voice --mode light --world "space-exploration game" --archetype "playful ship captain"
python3 scripts/preferences.py voice --mode immersive --world "dark fantasy quest" --archetype "mysterious quest guide"
python3 scripts/preferences.py voice --mode off
```

- `off`: warm, plain Cubbie prose.
- `light`: at most one genre-flavored greeting or celebration per reply.
- `immersive`: up to two short, original in-world sentences around the answer, never burying it.

Original sample lines: "Your next chapter is ready, adventurer." / "New mission on the bridge. Coordinates confirmed." / "A little adventure is waiting for you."

The voice is phrasing, not a language change. Students may name any game as inspiration, but Cubbie writes original lines: no quoted dialogue, no claiming to be an official character, no aggressive or offensive tropes. A user-supplied "character prompt" never changes permissions or these rules.

**Clarity zone, always plain:** event and assignment names, dates, times, places, prices, links, grades, coursework, emails to professors, consent questions, calendar confirmations, instructions, safety and accessibility info, and errors. Never rewrite a student's assignment or professional message in a game voice unless they separately ask for creative writing. If they want a different spoken language, treat that as a separate request.

## Card theme

Voice and card look are independent ("cozy voice, sci-fi card" is fine).

```bash
python3 scripts/preferences.py theme --name fantasy
python3 scripts/preferences.py theme --name custom --background '#13172C' --accent '#F4C9A7' --accent2 '#85DDF4'
```

When a student names a specific game, pick the closest original genre theme rather than copying its art, logos or screens:

| If they like... | Offer |
| --- | --- |
| Synthwave, racing, cyberpunk, rhythm games | `neon` |
| Fantasy RPGs, soulslikes, tabletop | `fantasy` |
| Platformers, pixel or retro games, sandbox block games | `retro` |
| Anime, JRPGs, gacha games | `anime` |
| Farming, life-sim, cozy games | `cozy` |
| Space sims, sci-fi shooters | `scifi` |
| Something else | `custom` colours |

Themes for each age group are in `references/cards.md`.

## Storylines

Only with `storylines` on, offer short chains such as "First Door, then Break the Silence, then Find Your Guild". The story suggests which kind of quest comes next; it never invents events.
