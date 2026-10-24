---
name: asucend
description: Turns getting involved at ASU into a weekly leveling game with real-event missions and XP. Use whenever an Arizona State University student says they still haven't joined anything, wants campus events that fit their free time, asks for involvement quests, club ideas, ways to meet people at ASU, or a Sunday stats card of their Ascend progress.
---

# Ascend (asucend)

Built for Arizona State University students. Halfway through the semester and they still haven't joined anything — Ascend turns getting involved into a real-world leveling game. Cubbie drops weekly missions from real ASU events; the student levels up by showing up and sending proof.

## When to use

- "I still haven't joined anything at ASU."
- "Find me something to do on campus this week."
- "Give me involvement quests / Ascend missions."
- "Show my Ascend level / Sunday stats."

Do not use for study plans, Canvas deadlines, or emailing professors — those are other Skills.

## Memory (setup, once)

Ask one question at a time. Suggest a default they can accept with "yes". Save answers with Cubbie's memory so later weeks skip setup:

1. Interests (clubs, sports, career, arts, service, gaming — free text is fine).
2. Comfort level 1–5 (1 = quiet / solo-friendly, 5 = very outgoing). Suggest 3 if unsure.
3. Usual free times (e.g. Tue/Thu after 4, weekends).
4. ASU campus (Tempe, Downtown Phoenix, West, Polytechnic, Online/remote).
5. Preferred weekly quest-drop day and time (suggest Sunday 6 pm Arizona time).

Remember: interests, comfort, free times, campus, quest-drop schedule, XP totals, current week missions, and which quests were skipped or completed.

## Main flow

### 1. Weekly quest drop (scheduled check-in)

After setup, offer a recurring check-in at the day and time they picked. Create it only after they say yes. Word the check-in so it still makes sense next week: run Ascend, search this week's ASU events, drop 3 missions.

When the check-in fires (or when they ask for missions now):

1. Search the web for real ASU events this week that match their interests, campus, and free times. Good starting points: ASU event calendars, Sun Devil Fitness, career services, club/org pages, and college newsletters. Read promising pages for day, time, and place.
2. If Google Calendar is connected, use free blocks that overlap their usual free times. If Calendar is not connected, use the free times from memory — say so in one short line.
3. Build exactly 3 missions. Prefer real events. Scale difficulty to comfort level and last week's results (see Adapt).
4. Text as short plain lines, one mission per message or one short block:

```text
This week's Ascend missions:
1) [Event name] — [day] [time], [place] · +[XP] [Track]
2) ...
3) ...
Reply 1, 2, or 3 to claim. Or "solo" for a campus exploration quest.
```

Each mission needs: event name, day, time, place, XP reward, and one XP track (Networking, Career, Academic, Wellness, or Exploration).

### 2. Claim, nudge, calendar

- When they claim a mission, remember it and set a reminder for 1 hour before the event (text). Create the reminder only after they confirm the time looks right.
- At the nudge: offer to add the event to Google Calendar. Add it only after they say yes. If Calendar is not connected, offer a .ics file instead, or skip.
- Never book tickets, RSVP, or message other people without an explicit yes. Cubbie texts only this student.

### 3. Proof and XP

- After the event window, ask for a photo from the event (badge, room, crowd, flyer — anything that shows they were there).
- Read the photo. If it reasonably matches the event/place/time, award XP with the script below and congratulate in one or two lines (new track total + level if it changed).
- If the photo is unclear or missing, ask for one more detail (where / what room / who spoke) instead of awarding XP. Do not award on a vague "I went."

### 4. Adapt every week

Before picking next week's 3 missions, check memory (or run `python3 scripts/xp.py status`):

- After skipped quests: easier — shorter events, closer to campus, lower social load, solo-friendly options.
- After completed quests: a little harder — slightly bigger events, new orgs, light networking stretch.
- Always stay within comfort level (1–2 stay mostly solo/small; 4–5 can include mixers and large club meetings).

### 5. Sunday stats card

On their preferred weekly drop (or when they ask "Ascend stats"):

1. Run `python3 scripts/xp.py status` (or `--card`) for level, XP by track, and quests done.
2. Make a simple shareable image or one-page PDF (level, five track bars or totals, quests completed this week / all time).
3. Text the image/PDF with one short summary line. This card is meant to be shareable for votes and views — keep it clean and campus-proud, not spammy. Optionally point them at the public Ascend site for a polished share link:
   https://asucend.vercel.app
   (That site is a landing page, not how to install this Skill. Install is always the GitHub repo link.)

## Solo / fallback missions

When web search finds no good matches for their free times:

- Offer 1–3 solo Exploration quests around their campus: a spot they haven't been, a free campus resource (library floor, tutoring center, career closet, rec center tour), or a short walk with a photo proof at a landmark.
- Say plainly that the calendar was thin this week.

## Optional script (XP math)

State lives under HOME at `~/.config/asucend/state.json` so it survives Skill updates. Cubbie fetches event context itself; pass awards into the script. Always pass the student's local date with `--today` when awarding (sandbox clock may differ).

From this Skill's folder:

```bash
# Show level, tracks, recent quests
python3 scripts/xp.py status

# Compact lines for a Sunday card
python3 scripts/xp.py --card

# Award XP after a confirmed photo (tracks: networking|career|academic|wellness|exploration)
python3 scripts/xp.py award --track networking --xp 40 --quest "Devils Advocate mixer" --today 2026-10-24

# Record a skip (softens next week's difficulty)
python3 scripts/xp.py skip --quest "Career fair booth crawl" --today 2026-10-24

# Sample mode (bundled data; does not touch real state)
python3 scripts/xp.py --sample status
```

No Setup packages required — standard library only.

| Exit code | Meaning | What to text |
| --- | --- | --- |
| 0 | OK | Use the printed summary |
| 2 | Bad arguments | Ask again which track / quest |
| 3 | Unknown track | List the five tracks |
| 4 | State unreadable | Say progress reset locally; offer to start fresh |

## Replies

Keep each reply to a few short lines, plain text, no Markdown headings or tables. One idea per message. Put event links on their own line. Lead with the mission or the XP result. Ask one question at a time. Long lists or the Sunday board go in an image or PDF, not a wall of text.

## When something fails

- Calendar not connected → use free times from setup; offer to connect Calendar later.
- No matching events → solo campus exploration quests; say the week was thin.
- Unclear or missing photo → ask one more detail; do not award XP yet.
- Student outside ASU → say Ascend is built for ASU campuses; offer a one-off exploration list only if they insist.
- Script fails → tell them XP could not be saved this time; remember the award in memory and retry the script once later.
