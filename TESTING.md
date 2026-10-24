# ASUcend test handoff — October 24, 2026

## Offline results

**19 / 19 local automated tests passed**, run in two batches to stay within the session tool runtime. No actual Cubbie account was used in these tests.

Covered:
- Accept → verified completion → fixed XP → level up → badges → reopen saved progress
- Duplicate and concurrent completion attempts award XP only once
- Unverified proof, unscheduled/unaccepted quest, invalid source and fake difficulty cannot earn points
- Solo quests, no-penalty skips, comfort updates and easier-next-week adaptation
- Old v1 state retains prior XP and completed quest history when updated
- Malformed state causes an error, not a reset
- Sample mode cannot mutate personal state
- Calendar busy-block collision + travel buffer, free-time window, free-event cost constraint
- Missing calendar information is disclosed, not claimed to mean availability
- Malicious/unsourced candidates rejected
- SVG card renders and HTML/XML special characters are escaped

Run local tests:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/plan.py --sample
python3 scripts/xp.py --sample --today 2026-10-24 --json status
python3 scripts/card.py --sample --today 2026-10-24 --out /tmp/asucend-demo.svg
```

If the complete suite exceeds a shell's short timeout, run:

```bash
python3 -m unittest discover -s tests -v -k Cards -k test_badge_unlocks -k test_concurrent_completion -k test_deterministic_quest -k test_double_completion -k test_easy_mode -k test_end_to_end -k test_invalid_source -k test_legacy_state -k test_proof_required
python3 -m unittest discover -s tests -v -k test_read_only_sample -k test_skipping_no_penalty -k test_solo_and_comfort -k test_state_corruption -k test_unverified_not_counted -k Planning
```

## Format

Local Agent Skills format checks passed: valid `SKILL.md` frontmatter, `asucend` identifier, description under 1,024 chars, fewer than 500 lines, referenced files present. **The organizer kit's exact validator was not run in this environment**, because the kit could not be downloaded from the runtime. Run it from an installed separate checkout:

```bash
python3 ../cubbie-hackathon-kit/skills/cubbie-skill-creator/scripts/validate_cubbie_skill.py .
```

## Required REAL Cubbie testing (not yet completed)

1. Push the ZIP contents to the public GitHub repo root. `SKILL.md` must be at the root.
2. Text https://github.com/kjodhpur/asucend to Cubbie and approve installation.
3. Text: `Start ASUcend. I'm shy, interested in AI, at Tempe, only free Friday afternoons, and want free events.` Verify onboarding doesn't repeat already known preferences.
4. Request a verified event with date, time, location, cost and original HTTPS source. Confirm it is actually upcoming. Do not use `example.org` demo links.
5. Accept it, then consent to or decline calendar addition and reminder. Check it doesn't claim success after a failure.
6. After a real quest, send a short reflection or appropriate photo. Verify one XP award and medal; repeat completion and ensure zero additional XP.
7. Start a new conversation. Ask: `How much XP and what badges do I have?` Verify persistence.
8. Request `Make my weekly ASUcend player card.` Test attachment/display on the recipient device.
9. Ask for `easier next week`, try a no-events week, then test no Calendar connection.
10. Run the hackathon kit's exact validator and its live `status` command before submission. Ask for human approval of the public submission preview.

**Important:** real Calendar, Canvas, scheduled reminders, event browsing, iMessage attachment delivery, and image-generation availability require Cubbie account tests and are not established by local tests.

## Update: game-inspired dialogue and optional themes (October 24, 2026)

Personalization is now implemented in `scripts/preferences.py` and `scripts/themes.py`:
- Independent **text character-voice** mode: off/light/immersive; user-chosen fictional game atmosphere and voice archetype, with all factual task content plain and unchanged.
- Visual reward-card appearance independent from the conversational voice: neon, fantasy, retro, anime, cozy, scifi, or a safe custom dark palette.
- Feature-by-feature opt-in (progression, storylines, calendar matching, reminders, weekly check-ins, weekly cards, image-art offers, photo-evidence prompts). Default off.
- `reset-presentation` disables extras without erasing completed quests or XP.
- Weekly card script refuses an unsolicited render unless weekly cards are opted in; `--once` covers a direct one-off user request.
- The script never creates replicas of copyrighted game UIs or character artwork. Actual game-like voice is directed by Cubbie's Skill instructions and **must be verified in a real Cubbie conversation**; no local test can validate an LLM's tone reliably.

**Latest local outcome: 28 of 28 tests passed**: 19 existing regression tests plus 9 personalization tests, run in bounded batches. SVGs for all six themes parsed, produced distinct output, and rendered as PNG previews. Format sanity checks passed (YAML frontmatter, correct `asucend` name, description <1024 chars, Skill <500 lines, resource files exist). Official organizer validator could not run because the git host was unavailable from this runtime.

Re-run:

```bash
python3 -m unittest discover -s tests -p 'test_asucend.py' -v
python3 -m unittest discover -s tests -p 'test_personalization.py' -v
python3 scripts/preferences.py --sample show
python3 scripts/card.py --sample --today 2026-10-24 --theme fantasy --out /tmp/asucend-fantasy.svg
```

**Cubbie live QA additions:**
- `Set my voice to immersive fantasy, but leave the weekly cards off.` Confirm only story introductions/celebrations have a fantasy personality. All event metadata remains exact.
- `No roleplay for my assignment or calendar instructions.` Confirm immediate factual clarity.
- `Use a cozy voice but cyberpunk visuals.` Confirm independent preferences.
- `Turn off reminders, cards and XP, but keep helping me find events.` Confirm no scheduling or XP awards.
- `Make one sci-fi card this time only.` Confirm a one-time card does not enable weekly messages.
- `Forget the game extras but keep my earned progress.` Confirm reset does not destroy XP.
