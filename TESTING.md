# ASUcend test handoff (October 24, 2026)

## Local results

**44 / 44 automated tests pass** (`python3 -m unittest discover -s tests -v`, about 6 seconds). No Cubbie account was used.

- `tests/test_asucend.py`: quest flow, one-time XP, proof rules, skips, adaptation, legacy state migration, corruption safety, event ranking, card escaping, XP bar accuracy across level boundaries (including above level 11).
- `tests/test_personalization.py`: opt-in defaults, voice vs. theme independence, weekly-card consent, custom palettes, reset keeps XP, sample mode is read-only.
- `tests/test_profiles.py`: child profiles need setup and live in separate files; parent confirmation is the only proof for kids; kid quests reject event links; college can't use parent proof or kid tracks; age group locks after the first task; nickname validation (no path tricks); `forget` deletes only that child; themes restricted per age group; every kid theme renders in both kid layouts; teens get the player layout with kid tracks; all player themes are 1080x1350; parent-typed text is escaped and never expanded; card assets aren't hidden by `.gitignore`; `--png` never breaks card delivery.

Every command in `SKILL.md` and `references/` was also run end to end against a scratch data folder (student flow, child flow, cards with PNG, reset, profile deletion).

## Official validator

Ran `skills/cubbie-skill-creator/scripts/validate_cubbie_skill.py` from https://github.com/imaginix-inc/cubbie-hackathon-kit: **OK, no warnings** (50 files, about 1.5 MB).

## PNG cards

`card.py --png` renders with `resvg-py==0.3.2` and the bundled fonts in `assets/fonts/`, with system fonts switched off, so output doesn't depend on what the sandbox has installed. Verified on macOS. Linux x86_64 and aarch64 wheels exist for that version, but **rendering inside Cubbie's sandbox is not yet verified.** Without `resvg-py`, the script tries cairosvg, rsvg-convert, Inkscape, ImageMagick or headless Chrome, and otherwise reports `png_error` so Cubbie sends a text summary.

## Required live Cubbie testing (not done yet)

1. Push to the public repo's `main` (SKILL.md at the root) and run the validator from a clean clone.
2. Text https://github.com/kjodhpur/asucend to Cubbie and approve the install.
3. `Start ASUcend. I'm shy, interested in AI, at Tempe, only free Friday afternoons, and want free events.` Expect a real, upcoming, sourced event after at most three questions, and no repeated questions.
4. Accept it; agree to, then separately decline, a calendar entry and reminder. Cubbie must not claim success after a failure.
5. After a real quest, send a short reflection. Expect one XP award and the First Spark medal; a repeat completion gives 0 XP.
6. New conversation: `How much XP and what badges do I have?` Progress must persist.
7. `Make my ASUcend player card.` Confirm Cubbie ran the venv setup, sent a **PNG** that shows inline in iMessage with all text visible, and didn't turn on weekly cards.
8. `Make next week easier`, a week with no events, and a run with Calendar disconnected.
9. Personalization: `Immersive fantasy voice, but keep cards off.` / `No roleplay for my assignment.` / `Cozy voice, sci-fi card.` / `Turn off XP and reminders but keep finding events.` / `Forget the game extras but keep my progress.`
10. Child profile: `Set up ASUcend for my daughter Maya, she's 7. She loves dinosaurs.` Expect a nickname-only profile in the 6-8 group, the dinos theme, home tasks only, no event searches, and XP only after the parent confirms. Then `Make Maya's card` (star chart, no XP numbers) and `Delete Maya's profile` (asks first, deletes only hers).

Real Calendar, Canvas, reminders, event browsing, iMessage attachments, the PNG renderer in Cubbie's sandbox and image-generation availability can only be confirmed on a live account.
