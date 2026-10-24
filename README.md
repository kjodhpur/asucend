# ASUcend (asucend)

Cubbie Skill for Arizona State University students. Comfort-scaled campus missions from real ASU events, with XP tracked in Cubbie — no extra app.

**Install in Cubbie only:** text this link (do not treat any website as the install):

https://github.com/kjodhpur/asucend

## Install

1. Open your Cubbie conversation.
2. Send: https://github.com/kjodhpur/asucend
3. Approve the install when Cubbie asks.
4. Start with: `Hey Cubbie, start ASUcend. I'm an ASU student and want my first campus quest.`

Cubbie reads `SKILL.md`, uses web search / optional calendar / reminders / memory, and runs `scripts/xp.py` only for quest and XP state.

## Example later messages

- Cubbie, show my ASUcend missions.
- I completed my networking mission.
- How much XP have I earned?
- Give me an easier challenge next week.
- Show my weekly progress.

## Team

- Kanha Jodhpurkar — TODO: add school email before hackathon submit

## Local checks

```bash
python3 scripts/xp.py --sample status
python3 <path-to-kit>/skills/cubbie-skill-creator/scripts/validate_cubbie_skill.py .
```

## Pre-submit E2E (real Cubbie)

Before submitting the hackathon entry, on a real Cubbie account:

1. Complete onboarding (interests, comfort, free times, campus).
2. Receive a real, correctly sourced campus event suggestion (source/link shown before you decide).
3. Accept or decline an optional reminder (Cubbie asks first).
4. Record one completed mission and receive XP.
5. Ask about XP later and confirm progress is still there.

## Hackathon

Cubbie Hackathon Track 1. Site: https://hackathon.cubbie.ai
