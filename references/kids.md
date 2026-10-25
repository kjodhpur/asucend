# Child profiles (ages 6-17), parent-run

Use this file only when the student asks to set up ASUcend for a child: their own child, or a younger sibling or a child they tutor **with the parent's or guardian's permission**. The adult texts Cubbie; the child never does. Cubbie texts only its own student, so every reminder, question and celebration goes to the adult.

## What changes for a child

- **Quests are home tasks, never events.** Homework, reading, practice (music, sport, a skill), creativity and helping (chores, kindness). No event searches, links, start times, locations or meetups with strangers. The script rejects event fields on a child profile.
- **The adult confirms completion.** XP is awarded only with `--proof parent`, after the adult says the task is done. Never ask for photos of the child.
- **Nickname only.** Store a first name or nickname. Never a surname, school, birthday, photo or address. Ask for the age group, not the exact age.
- **Learning, not shortcuts.** Cubbie may help the adult explain a concept or plan homework time, but never writes answers to graded work for the child.
- **No pressure.** No streak guilt and no comparing siblings. Each child's profile is private and separate.
- **Digital rewards only.** Stars, levels, badges and cards. If the family adds real treats, that's their choice; ASUcend never promises them.

## Set up a profile

Ask one question at a time:

1. "What should I call them? A first name or nickname is perfect." Use lowercase letters, digits and dashes for the profile name (`maya`, `leo-2`).
2. "Which age group? 6-8, 9-12 or 13-17?" Map to `little`, `junior` or `teen`.
3. Let **the child** pick a card theme. 6-12: dinos, space, unicorn or robots. 13-17: neon, fantasy, retro, anime, cozy or scifi. Never pick a theme based on whether the child is a boy or a girl.

```bash
python3 scripts/xp.py --profile maya --today 2026-10-24 setup --segment little
python3 scripts/preferences.py --profile maya theme --name dinos
python3 scripts/preferences.py --profile maya feature --name progression --enabled 1
```

The age group can change only before the first task; after that, create a new profile. `python3 scripts/xp.py profiles` lists every profile with its age group and level.

## Add, accept and complete tasks

Suggested sizes. 6-8: mostly micro (10) or easy (25). 9-12: easy to standard (50). 13-17: up to brave (75); boss (100) is for a big project such as a science fair or an essay.

```bash
python3 scripts/xp.py --profile maya --today 2026-10-24 offer --title "Spelling words" --track homework --difficulty easy
python3 scripts/xp.py --profile maya --today 2026-10-24 accept --quest-id ID
python3 scripts/xp.py --profile maya --today 2026-10-24 complete --quest-id ID --verified --proof parent
```

Accept when the child agrees to take the task on. Complete only after the adult confirms it's done; "she says she did it" is a cue to ask the adult to check. A skip is never a failure: `skip --quest-id ID`.

## Talk to each age group's level (in messages to the adult)

- **6-8:** stars and simple words. "Maya earned a star! 3 more stars to her next level." No XP numbers.
- **9-12:** levels and badges. "Level 5, Skill Builder! New badge: Bookworm."
- **13-17:** XP and the skill tree, like a student, without the cute tone.

Badges for children: First Star, Homework Hero (5 homework), Bookworm (3 reading), Practice Power, Idea Maker, Super Helper (3 each), Big Challenge (a boss task), All-Rounder (every track), Quest Legend (20 tasks).

## Cards and check-ins

```bash
python3 scripts/card.py --profile maya --once --today 2026-10-24 --out /path/to/private/maya.svg --png
```

The adult chooses whether to show the card to the child. A weekly check-in ("Want me to send Maya's card every Sunday at 6 pm?") is created only after a yes, and goes to the adult.

## Delete a child's data

When the adult asks to delete a child's profile, confirm once, then:

```bash
python3 scripts/xp.py --profile maya forget --confirm
```

This permanently deletes that child's progress file. It never touches the student's own progress or other children's.
