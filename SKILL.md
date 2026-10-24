---
name: asucend
description: Turns getting involved at ASU into comfort-scaled campus missions with real events and XP. Use whenever an Arizona State University student wants to make friends or attend more events, says they are shy, asks to start ASUcend or Ascend, wants missions that fit their free days, reports a completed mission, asks how much XP they have, wants an easier challenge next week, or asks for weekly progress.
---

# ASUcend (asucend)

Built for Arizona State University students. ASUcend works inside Cubbie — like a new ability. Students do not install another app or visit a website to use it. Cubbie finds real campus events, the student chooses, and a small script only tracks quests and XP.

## When to use

- "Hey Cubbie, I want to make new friends and attend more events at ASU. Help me."
- "Hey Cubbie, start ASUcend. I'm an ASU student and want my first campus quest."
- "I want to meet people interested in AI, but I'm shy and only free on Fridays."
- "Cubbie, show my ASUcend missions."
- "I completed my networking mission."
- "How much XP have I earned?"
- "Give me an easier challenge next week."
- "Show my weekly progress."

Do not use for study plans, Canvas deadlines, or emailing professors — those are other Skills.

## Who does what

- **Cubbie** (this Skill's instructions): web search and reading event pages, optional Google Calendar, reminders and scheduled check-ins, memory, reading proof photos, short replies.
- **Script** (`scripts/xp.py`): quest and XP state only. It does not search the web, touch calendars, or set reminders. Cubbie gathers facts first, then passes track, XP, and quest name into the script.

## Memory (setup)

Ask one question at a time. Suggest a default they can accept with "yes". Save with Cubbie's memory:

1. Interests (AI, clubs, sports, career, arts, service — free text is fine).
2. Comfort (shy / small group / ready for mixers). Map to 1–5 if useful; suggest a small workshop when they say shy.
3. Free days and times (e.g. Fridays only).
4. ASU campus (Tempe, Downtown Phoenix, West, Polytechnic, Online/remote).
5. Optional: weekly check-in day and time (suggest Sunday 6 pm Arizona time). Create a recurring check-in only after they say yes.

Remember interests, comfort, free times, campus, active missions, skips, and that ASUcend is in use.

## First mission (comfort-scaled)

Match the shy / limited-schedule style:

1. Acknowledge the goal in one short line.
2. Offer an easy first step: small workshop vs something they can do alone. Prefer free when they ask.
3. Search the web for a real ASU event that fits interest + free day + comfort. Read the page for day, time, place, and cost.
4. **Show the event source before they decide** — name, when, where, and the event link on its own line. Suggested XP (e.g. +50) and one track (Networking, Career, Academic, Wellness, or Exploration).
5. Wait for accept or decline. Do not set reminders or add calendar events until they say yes.
6. After accept: remember the mission; ask permission for a reminder (e.g. 1 hour before). Create the reminder only after yes. Offer calendar add the same way; if Calendar is not connected, use free times from memory and skip the add, or offer a .ics only if they want it.

Example tone:

```text
Let's find an easy first mission! Small workshop, or something solo?

Your first ASUcend mission — free AI workshop Friday that fits your schedule.
I'll show the source before you decide. +50 XP when you complete it.
[event link]
Want a reminder an hour before?
```

For a weekly drop later, you may offer up to 3 missions the same way — each with source shown before claim.

## Later commands

| They say | You do |
| --- | --- |
| Show my ASUcend missions | List active missions from memory (and script status if useful). Short lines. |
| I completed my … mission | Confirm with a photo or one concrete detail; then award XP via the script; congratulate in 1–2 lines. |
| How much XP have I earned? | Run `python3 scripts/xp.py status` (or `--card`) and text a short summary. |
| Give me an easier challenge next week | Remember softer difficulty; next search favors shorter, closer, lower-social, or solo options. Optionally `python3 scripts/xp.py skip` if they abandoned a quest. |
| Show my weekly progress | Run status/`--card`; optional one-page image or PDF of level, tracks, quests done; one summary line in the text. |

## Proof and XP

- Prefer a photo from the event; if unclear or missing, ask one more detail instead of awarding XP.
- After a solid confirm, run the award command below. Tracks: networking, career, academic, wellness, exploration.
- Never award on a vague "I went" with no detail.

## Adapt

Before the next mission set, check memory or `python3 scripts/xp.py status`:

- Skipped or "easier next week" → softer missions.
- Completions stacking → a little more stretch, still inside comfort.
- Shy / low comfort → small workshops and solo exploration first, not large mixers.

## Solo / thin calendar

If search finds nothing that fits: offer a solo Exploration quest on their campus (new spot, free resource, short walk + photo). Say the week was thin. Show what you checked in one line when you can.

## Script (XP and quest state only)

State: `~/.config/asucend/state.json` under HOME. Always pass `--today` with the student's local date when awarding (sandbox clock may differ).

```bash
python3 scripts/xp.py status
python3 scripts/xp.py --card
python3 scripts/xp.py award --track networking --xp 50 --quest "Free AI Friday workshop" --today 2026-10-24
python3 scripts/xp.py skip --quest "Large mixer" --today 2026-10-24
python3 scripts/xp.py --sample status
```

No Setup packages — standard library only.

| Exit code | Meaning | What to text |
| --- | --- | --- |
| 0 | OK | Use the printed summary |
| 2 | Bad arguments | Ask again which track / quest |
| 3 | Unknown track | List the five tracks |
| 4 | State unreadable | Say progress may have reset; offer to start fresh |

## Replies

Short plain text, one idea per message, no Markdown headings or tables. Event links on their own line. Ask one question at a time. Lead with the mission, the source, or the XP result. Get a yes before reminders, calendar adds, bookings, or messaging anyone else. Cubbie texts only this student.

## When something fails

- Calendar not connected → use free times from memory; offer to connect later.
- No matching events → solo campus quest; say the calendar was thin.
- Unclear proof → one more detail; no XP yet.
- Not an ASU student → say ASUcend is built for ASU; stop or offer a one-off idea only if they insist.
- Script fails → say XP did not save; keep the award in memory and retry the script once.
