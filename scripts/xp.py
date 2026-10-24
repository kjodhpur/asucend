#!/usr/bin/env python3
"""Ascend XP and level math for the asucend Cubbie Skill.

State is saved under HOME (~/.config/asucend/state.json) so it survives sandbox
restarts and Skill updates. --sample reads assets/sample_state.json and never
writes the student's real state.

Exit codes: 0 ok, 2 bad arguments, 3 unknown track, 4 state unreadable.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

TRACKS = ("networking", "career", "academic", "wellness", "exploration")
TRACK_LABEL = {
    "networking": "Networking",
    "career": "Career",
    "academic": "Academic",
    "wellness": "Wellness",
    "exploration": "Exploration",
}
# Cumulative XP thresholds for levels 1..N (level 1 starts at 0).
LEVEL_THRESHOLDS = [0, 50, 120, 220, 350, 520, 720, 960, 1240, 1560, 1920]
SAMPLE = Path(__file__).resolve().parent.parent / "assets" / "sample_state.json"
SKILL_NAME = "asucend"


def fail(message: str, code: int) -> None:
    print(message, file=sys.stderr)
    sys.exit(code)


def data_dir() -> Path:
    override = os.environ.get("SKILL_DATA_DIR")
    if override:
        return Path(override)
    return Path.home() / ".config" / SKILL_NAME


def state_path(*, sample: bool) -> Path:
    if sample:
        return SAMPLE
    return data_dir() / "state.json"


def empty_state() -> dict:
    return {
        "tracks": {t: 0 for t in TRACKS},
        "quests_done": [],
        "quests_skipped": [],
        "comfort": 3,
        "updated": None,
    }


def load_state(*, sample: bool) -> dict:
    path = state_path(sample=sample)
    if sample and not path.is_file():
        fail(f"Sample state missing at {path}", 4)
    if not path.is_file():
        return empty_state()
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        fail("Could not read Ascend progress file.", 4)
    if not isinstance(data, dict):
        fail("Ascend progress file is invalid.", 4)
    tracks = data.get("tracks") or {}
    normalized = empty_state()
    for t in TRACKS:
        try:
            normalized["tracks"][t] = max(0, int(tracks.get(t, 0)))
        except (TypeError, ValueError):
            normalized["tracks"][t] = 0
    for key in ("quests_done", "quests_skipped"):
        raw = data.get(key) or []
        if isinstance(raw, list):
            normalized[key] = [q for q in raw if isinstance(q, dict)]
    try:
        normalized["comfort"] = min(5, max(1, int(data.get("comfort", 3))))
    except (TypeError, ValueError):
        normalized["comfort"] = 3
    normalized["updated"] = data.get("updated")
    return normalized


def save_state(state: dict, *, sample: bool) -> None:
    if sample:
        return
    path = state_path(sample=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = dict(state)
    state["updated"] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    path.write_text(json.dumps(state, indent=2) + "\n")


def total_xp(state: dict) -> int:
    return sum(state["tracks"].values())


def level_for(xp: int) -> int:
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
        else:
            break
    # Beyond the table: +1 level every 400 XP past the last threshold.
    if xp >= LEVEL_THRESHOLDS[-1]:
        extra = (xp - LEVEL_THRESHOLDS[-1]) // 400
        level = len(LEVEL_THRESHOLDS) + extra
    return level


def xp_to_next(xp: int) -> int:
    level = level_for(xp)
    if level < len(LEVEL_THRESHOLDS):
        return max(0, LEVEL_THRESHOLDS[level] - xp)
    next_at = LEVEL_THRESHOLDS[-1] + ((level - len(LEVEL_THRESHOLDS) + 1) * 400)
    return max(0, next_at - xp)


def parse_today(raw: str | None) -> str:
    if not raw:
        return date.today().isoformat()
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError:
        fail("--today must be YYYY-MM-DD", 2)


def difficulty_hint(state: dict) -> str:
    done = len(state["quests_done"])
    skipped = len(state["quests_skipped"])
    recent_done = state["quests_done"][-3:]
    recent_skip = state["quests_skipped"][-3:]
    comfort = state["comfort"]
    if len(recent_skip) >= 2 and len(recent_done) == 0:
        tone = "easier"
    elif len(recent_done) >= 2 and len(recent_skip) == 0:
        tone = "a little harder"
    else:
        tone = "steady"
    return (
        f"adapt={tone}; comfort={comfort}/5; "
        f"done={done}; skipped={skipped}; "
        f"recent_done={len(recent_done)}; recent_skip={len(recent_skip)}"
    )


def format_status(state: dict, *, card: bool) -> str:
    xp = total_xp(state)
    level = level_for(xp)
    nxt = xp_to_next(xp)
    track_lines = [
        f"{TRACK_LABEL[t]}: {state['tracks'][t]}" for t in TRACKS
    ]
    done = len(state["quests_done"])
    week_done = [
        q.get("quest", "?")
        for q in state["quests_done"][-5:]
    ]
    if card:
        lines = [
            f"Ascend L{level} · {xp} XP · {nxt} to next",
            " · ".join(f"{TRACK_LABEL[t][:3]} {state['tracks'][t]}" for t in TRACKS),
            f"Quests done: {done}",
            difficulty_hint(state),
        ]
        return "\n".join(lines)
    lines = [
        f"Level {level} ({xp} XP, {nxt} to next)",
        "Tracks:",
        *[f"- {line}" for line in track_lines],
        f"Quests done: {done}",
    ]
    if week_done:
        lines.append("Recent: " + "; ".join(week_done))
    lines.append(difficulty_hint(state))
    return "\n".join(lines)


def cmd_status(args: argparse.Namespace) -> None:
    state = load_state(sample=args.sample)
    print(format_status(state, card=args.card))


def cmd_award(args: argparse.Namespace) -> None:
    track = (args.track or "").strip().lower()
    if track not in TRACKS:
        fail(
            "Unknown track. Use: networking, career, academic, wellness, exploration.",
            3,
        )
    if args.xp is None or args.xp < 1:
        fail("--xp must be a positive integer", 2)
    if not (args.quest or "").strip():
        fail("--quest is required", 2)
    state = load_state(sample=args.sample)
    before = level_for(total_xp(state))
    state["tracks"][track] += int(args.xp)
    entry = {
        "quest": args.quest.strip(),
        "track": track,
        "xp": int(args.xp),
        "date": parse_today(args.today),
    }
    state["quests_done"].append(entry)
    save_state(state, sample=args.sample)
    after = level_for(total_xp(state))
    leveled = f" Level up → {after}!" if after > before else ""
    print(
        f"+{args.xp} {TRACK_LABEL[track]} · total {total_xp(state)} XP · "
        f"L{after}.{leveled}"
    )
    print(format_status(state, card=True))


def cmd_skip(args: argparse.Namespace) -> None:
    if not (args.quest or "").strip():
        fail("--quest is required", 2)
    state = load_state(sample=args.sample)
    state["quests_skipped"].append(
        {"quest": args.quest.strip(), "date": parse_today(args.today)}
    )
    save_state(state, sample=args.sample)
    print(f"Skipped: {args.quest.strip()}")
    print(difficulty_hint(state))


def cmd_set_comfort(args: argparse.Namespace) -> None:
    if args.comfort is None or not (1 <= args.comfort <= 5):
        fail("--comfort must be 1–5", 2)
    state = load_state(sample=args.sample)
    state["comfort"] = int(args.comfort)
    save_state(state, sample=args.sample)
    print(f"Comfort set to {state['comfort']}/5")
    print(difficulty_hint(state))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ascend XP tracker for asucend")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use bundled sample state; never write real progress",
    )
    parser.add_argument(
        "--card",
        action="store_true",
        help="Compact status lines for a Sunday stats card",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show level and track XP")

    award = sub.add_parser("award", help="Award XP after confirmed proof")
    award.add_argument("--track", required=True)
    award.add_argument("--xp", type=int, required=True)
    award.add_argument("--quest", required=True)
    award.add_argument("--today", help="Student-local date YYYY-MM-DD")

    skip = sub.add_parser("skip", help="Record a skipped quest")
    skip.add_argument("--quest", required=True)
    skip.add_argument("--today", help="Student-local date YYYY-MM-DD")

    comfort = sub.add_parser("set-comfort", help="Store comfort level 1-5")
    comfort.add_argument("--comfort", type=int, required=True)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "status"
    if command == "status":
        cmd_status(args)
    elif command == "award":
        cmd_award(args)
    elif command == "skip":
        cmd_skip(args)
    elif command == "set-comfort":
        cmd_set_comfort(args)
    else:
        fail(f"Unknown command: {command}", 2)


if __name__ == "__main__":
    main()
