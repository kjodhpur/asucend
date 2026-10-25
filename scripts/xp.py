#!/usr/bin/env python3
"""asucend deterministic quest ledger and digital rewards. Python 3 stdlib only.

Cubbie discovers/verifies events and confirms quest proof. This script never calls
Cubbie, fetches websites, reads calendar, verifies a photo, or sends messages.
"""
from __future__ import annotations
import argparse
import hashlib
import fcntl
from contextlib import contextmanager
import json
import os
import re
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

TRACKS = ('networking', 'career', 'academic', 'wellness', 'exploration')
KID_TRACKS = ('homework', 'reading', 'practice', 'creativity', 'helping')
DIFFICULTY = {'micro': 10, 'easy': 25, 'standard': 50, 'brave': 75, 'boss': 100}
THRESHOLDS = [0, 50, 120, 220, 350, 520, 720, 960, 1240, 1560, 1920]
TITLES = ('The Initiate', 'The Explorer', 'The Pathfinder', 'The Wayfinder', 'The Vanguard',
          'The Trailblazer', 'The Guardian', 'The Luminary', 'The Champion', 'The Ascendant', 'Campus Legend')
# Age segments. Under-18 profiles are parent-run home/homework quests: no events, links or photos.
SEGMENTS = {
    'college': {'label': 'ASU student (18+)', 'tracks': TRACKS, 'parent_run': False, 'titles': TITLES},
    'teen': {'label': 'Teen Trailblazers (13-17)', 'tracks': KID_TRACKS, 'parent_run': True,
             'titles': ('Starter', 'Grinder', 'Focus Finder', 'Skill Builder', 'Momentum Maker', 'Deep Worker',
                        'Strategist', 'Achiever', 'Elite', 'Mastermind', 'Legend')},
    'junior': {'label': 'Junior Questers (9-12)', 'tracks': KID_TRACKS, 'parent_run': True,
               'titles': ('Rookie', 'Apprentice', 'Adventurer', 'Quest Seeker', 'Skill Builder', 'Brain Knight',
                          'Study Ranger', 'Quest Captain', 'Master Mind', 'Grand Champion', 'Legend')},
    'little': {'label': 'Little Explorers (6-8)', 'tracks': KID_TRACKS, 'parent_run': True,
               'titles': ('Little Sprout', 'Busy Bee', 'Bright Spark', 'Shining Star', 'Super Star', 'Rocket Learner',
                          'Brave Explorer', 'Big Thinker', 'Homework Hero', 'Mega Champion', 'Legend')},
}
DEFAULT_PROFILE = 'me'
PROFILE_NAME = re.compile(r'^[a-z0-9][a-z0-9-]{0,31}$')
ASSETS = Path(__file__).resolve().parent.parent / 'assets'
SAMPLE = ASSETS / 'sample_state.json'

class GameError(Exception):
    def __init__(self, message, code=2):
        super().__init__(message)
        self.code = code


def data_dir():
    return Path(os.environ.get('SKILL_DATA_DIR', str(Path.home() / '.config' / 'asucend')))


def profile_name(raw):
    name = (raw or DEFAULT_PROFILE).strip().lower()
    if not PROFILE_NAME.fullmatch(name):
        raise GameError('Profile names are a first name or nickname: letters, digits, dashes (max 32).')
    return name


def state_path(sample=False, profile=None):
    """'me' keeps the original state.json; each child gets profiles/<name>.json."""
    name = profile_name(profile)
    if sample:
        return SAMPLE if name == DEFAULT_PROFILE else ASSETS / 'sample_profiles' / f'{name}.json'
    return data_dir() / 'state.json' if name == DEFAULT_PROFILE else data_dir() / 'profiles' / f'{name}.json'


def tracks_for(state):
    return SEGMENTS[state.get('segment', 'college')]['tracks']


def empty_state(segment='college'):
    return {'schema_version': 3, 'segment': segment, 'tracks': {t: 0 for t in SEGMENTS[segment]['tracks']},
            'quests': {}, 'quests_done': [], 'quests_skipped': [], 'comfort': 3,
            'preferences': {'easier_next_week': False}, 'badges': [], 'updated': None}


def load_state(sample=False, profile=None, allow_new=False):
    p = state_path(sample, profile)
    if not p.exists():
        if sample:
            raise GameError('Sample state is missing', 4)
        if profile_name(profile) != DEFAULT_PROFILE and not allow_new:
            raise GameError(f"No profile '{profile_name(profile)}' yet. Run setup --segment first.", 2)
        return empty_state()
    try:
        raw = json.loads(p.read_text(encoding='utf-8'))
    except (ValueError, OSError):
        raise GameError('Progress file cannot be read. No changes made.', 4)
    if not isinstance(raw, dict) or not isinstance(raw.get('tracks', {}), dict):
        raise GameError('Invalid progress file. No changes made.', 4)
    segment = raw.get('segment', 'college')
    if segment not in SEGMENTS:
        raise GameError('Invalid age segment in progress file. No changes made.', 4)
    state = empty_state(segment)
    for track in SEGMENTS[segment]['tracks']:
        v = raw.get('tracks', {}).get(track, 0)
        if type(v) is not int or v < 0:
            raise GameError(f'Invalid stored XP for {track}. No changes made.', 4)
        state['tracks'][track] = v
    for key in ('quests_done', 'quests_skipped', 'badges'):
        v = raw.get(key, [])
        if not isinstance(v, list):
            raise GameError(f'Invalid stored {key}. No changes made.', 4)
        state[key] = v
    q = raw.get('quests', {})
    if not isinstance(q, dict):
        raise GameError('Invalid quest ledger. No changes made.', 4)
    state['quests'] = q
    comfort = raw.get('comfort', 3)
    if type(comfort) is not int or not 1 <= comfort <= 5:
        raise GameError('Invalid comfort value. No changes made.', 4)
    state['comfort'] = comfort
    if isinstance(raw.get('preferences'), dict):
        state['preferences'].update(raw['preferences'])
    state['updated'] = raw.get('updated')
    return state


def save_state(state, sample=False, profile=None):
    if sample:
        raise GameError('Sample mode is read-only; run a real command without --sample.', 2)
    target = state_path(False, profile)
    target.parent.mkdir(parents=True, exist_ok=True)
    state['updated'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    fd, path = tempfile.mkstemp(prefix='.asucend-', suffix='.json', dir=target.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(path, target)
        try:
            os.chmod(target, 0o600)
        except OSError:
            pass
    finally:
        if os.path.exists(path):
            os.unlink(path)


def level_for(xp):
    lvl = 1
    for idx, threshold in enumerate(THRESHOLDS):
        if xp < threshold:
            break
        lvl = idx + 1
    if xp >= THRESHOLDS[-1]:
        lvl += (xp - THRESHOLDS[-1]) // 400
    return lvl


def next_threshold(xp):
    lvl = level_for(xp)
    return THRESHOLDS[lvl] if lvl < len(THRESHOLDS) else THRESHOLDS[-1] + (lvl-len(THRESHOLDS)+1)*400


def title_for(level, segment='college'):
    titles = SEGMENTS[segment]['titles']
    return titles[min(level-1, len(titles)-1)]


def iso_day(raw):
    try:
        return date.fromisoformat(raw).isoformat()
    except (ValueError, TypeError):
        raise GameError('Supply student-local --today YYYY-MM-DD', 2)


def parse_datetime(raw):
    try:
        dt = datetime.fromisoformat(raw)
        if dt.utcoffset() is None:
            raise ValueError('missing timezone')
        return dt
    except (ValueError, TypeError):
        raise GameError('Use ISO date/time with timezone, e.g. 2026-10-30T17:00:00-07:00', 2)


def valid_source(raw):
    try:
        u = urlsplit(raw)
        return u.scheme == 'https' and bool(u.netloc) and not u.username and not u.password
    except ValueError:
        return False


def quest_id(title, start, source):
    return hashlib.sha256(f'{title.casefold().strip()}|{start}|{source}'.encode()).hexdigest()[:12]


def badges_for(state):
    done = state['quests_done']
    tracks = [q.get('track') for q in done]
    levels = []
    def add(condition, badge, label, rarity):
        if condition:
            levels.append({'id': badge, 'name': label, 'rarity': rarity})
    if SEGMENTS[state.get('segment', 'college')]['parent_run']:
        add(len(done) >= 1, 'first-star', 'First Star', 'common')
        add(tracks.count('homework') >= 5, 'homework-hero', 'Homework Hero', 'rare')
        add(tracks.count('reading') >= 3, 'bookworm', 'Bookworm', 'rare')
        add(tracks.count('practice') >= 3, 'practice-power', 'Practice Power', 'rare')
        add(tracks.count('creativity') >= 3, 'idea-maker', 'Idea Maker', 'rare')
        add(tracks.count('helping') >= 3, 'super-helper', 'Super Helper', 'rare')
        add(any(q.get('difficulty') == 'boss' for q in done), 'big-challenge', 'Big Challenge', 'epic')
        add(all(t in tracks for t in KID_TRACKS), 'all-rounder', 'All-Rounder', 'legendary')
        add(len(done) >= 20, 'quest-legend', 'Quest Legend', 'legendary')
        return levels
    add(len(done) >= 1, 'first-spark', 'First Spark', 'common')
    add('networking' in tracks, 'first-contact', 'First Contact', 'common')
    add(tracks.count('exploration') >= 3, 'campus-cartographer', 'Campus Cartographer', 'rare')
    add(sum(q.get('difficulty') == 'brave' for q in done) >= 1, 'courage-rising', 'Courage Rising', 'epic')
    add(tracks.count('career') >= 3, 'opportunity-hunter', 'Opportunity Hunter', 'rare')
    add(len(done) >= 5, 'five-quests', 'Quest Keeper', 'rare')
    add(all(t in tracks for t in TRACKS), 'balanced-hero', 'Balanced Hero', 'legendary')
    add(any(q.get('difficulty') == 'boss' for q in done), 'boss-slayer', 'Boss Slayer', 'epic')
    add(len(done) >= 10, 'campus-legend', 'Campus Legend', 'legendary')
    return levels


def update_badges(state, today):
    known = {b.get('id') for b in state['badges'] if isinstance(b, dict)}
    new = []
    for b in badges_for(state):
        if b['id'] not in known:
            item = dict(b, earned_on=today)
            state['badges'].append(item)
            new.append(item)
    return new


def momentum(state, today):
    # A paused week doesn't remove XP or destroy prior achievements.
    weeks = set()
    for q in state['quests_done']:
        try:
            d = date.fromisoformat(q['date'])
            weeks.add(d.toordinal() - d.weekday())
        except (KeyError, TypeError, ValueError):
            continue
    current = date.fromisoformat(today)
    monday = current.toordinal() - current.weekday()
    if monday not in weeks:
        monday -= 7
    n = 0
    while monday in weeks:
        n += 1
        monday -= 7
    return n


def difficulty_hint(state):
    # Last four decisions, not lifetime counts, determines adaptation.
    events = []
    for q in state['quests_done']:
        events.append((q.get('date', ''), 'done'))
    for q in state['quests_skipped']:
        events.append((q.get('date', ''), 'skip'))
    events.sort(key=lambda pair: pair[0])
    last = [x[1] for x in events[-4:]]
    if state['preferences'].get('easier_next_week') or last.count('skip') >= 2:
        return 'gentler (micro/easy or solo)'
    if len(last) >= 3 and last.count('done') >= 3 and state['comfort'] >= 3:
        return 'stretch slightly, with consent'
    return 'steady; respect comfort level'


def snapshot(state, today):
    xp = sum(state['tracks'].values())
    completed_week = []
    current_yearweek = date.fromisoformat(today).isocalendar()[:2]
    for q in state['quests_done']:
        try:
            if date.fromisoformat(q['date']).isocalendar()[:2] == current_yearweek:
                completed_week.append({'title': q.get('title', q.get('quest', '?')), 'xp': q.get('xp', 0)})
        except (KeyError, ValueError, TypeError):
            continue
    segment = state.get('segment', 'college')
    return {'segment': segment, 'level': level_for(xp), 'title': title_for(level_for(xp), segment), 'total_xp': xp,
            'next_level_at': next_threshold(xp), 'xp_to_next': next_threshold(xp)-xp,
            'tracks': state['tracks'], 'active': [q for q in state['quests'].values() if q.get('status') == 'accepted'],
            'completed_count': len(state['quests_done']), 'completed_this_week': completed_week,
            'momentum_weeks': momentum(state, today), 'difficulty_hint': difficulty_hint(state),
            'comfort': state['comfort'], 'badges': state['badges']}


def resolve_quest(state, ident):
    if ident in state['quests']:
        return state['quests'][ident]
    matches = [q for q in state['quests'].values() if q.get('title', '').casefold() == ident.casefold()]
    if len(matches) != 1:
        raise GameError('Quest not found or title ambiguous. Use the quest ID.')
    return matches[0]



@contextmanager
def write_lock():
    """Serialize concurrent Cubbie turns that update a student's private ledger."""
    directory = data_dir()
    directory.mkdir(parents=True, exist_ok=True)
    lock_path = directory / '.ledger.lock'
    with open(lock_path, 'a+', encoding='utf-8') as handle:
        try:
            os.chmod(lock_path, 0o600)
        except OSError:
            pass
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

def list_profiles():
    found = [DEFAULT_PROFILE] if state_path(False).exists() else []
    folder = data_dir() / 'profiles'
    if folder.is_dir():
        found += sorted(p.stem for p in folder.glob('*.json') if PROFILE_NAME.fullmatch(p.stem))
    out = []
    for name in found:
        st = load_state(False, name)
        xp = sum(st['tracks'].values())
        out.append({'profile': name, 'segment': st['segment'], 'level': level_for(xp), 'total_xp': xp})
    return {'profiles': out}


def forget_profile(args):
    """Delete one child's progress file at the parent's request. Never the student's own ledger."""
    name = profile_name(args.profile)
    if name == DEFAULT_PROFILE:
        raise GameError("forget only deletes a child's profile, not the student's own progress.")
    if args.sample or not args.confirm:
        raise GameError('Confirm with the parent first, then pass --confirm.')
    path = state_path(False, name)
    if not path.exists():
        raise GameError(f"No profile '{name}'.")
    path.unlink()
    return {'profile': name, 'deleted': True}


def run(args):
    if args.command == 'profiles':
        return list_profiles()
    if args.command == 'forget':
        return forget_profile(args)
    state = load_state(args.sample, args.profile, allow_new=args.command == 'setup')
    today = iso_day(args.today) if args.today else None
    cmd = args.command or 'status'
    parent_run = SEGMENTS[state['segment']]['parent_run']
    if cmd in ('status', 'badges', 'recommend', 'card-data'):
        if not today:
            raise GameError('Pass --today in the student\'s local timezone for accurate weekly stats.')
        snap = snapshot(state, today)
        if cmd == 'status':
            if args.json:
                return snap
            return (f"asucend: L{snap['level']} {snap['title']} · {snap['total_xp']} XP "
                    f"({snap['xp_to_next']} to next) · {snap['completed_count']} quests done; "
                    f"{len(snap['badges'])} medals; momentum {snap['momentum_weeks']} weeks. "
                    f"Active: {len(snap['active'])}. Next: {snap['difficulty_hint']}")
        if cmd == 'badges':
            return {'badges': snap['badges']}
        if cmd == 'recommend':
            return {'recommended_difficulty': snap['difficulty_hint'], 'comfort': state['comfort']}
        return snap
    if args.sample:
        raise GameError('Sample mode is read-only. Use real state for changes.')
    if not today:
        raise GameError('Pass --today YYYY-MM-DD before commands that modify progress.')
    if cmd == 'setup':
        if args.segment != state['segment']:
            if state['quests'] or state['quests_done'] or sum(state['tracks'].values()):
                raise GameError('This profile already has quests; create a new profile for a different age group.')
            prefs = state['preferences']
            state = empty_state(args.segment)
            state['preferences'].update(prefs)
        result = {'profile': profile_name(args.profile), 'segment': args.segment,
                  'label': SEGMENTS[args.segment]['label'], 'parent_run': SEGMENTS[args.segment]['parent_run'],
                  'tracks': list(SEGMENTS[args.segment]['tracks'])}
    elif cmd == 'set-comfort':
        if args.comfort is None or not 1 <= args.comfort <= 5:
            raise GameError('Comfort must be between 1 and 5.')
        state['comfort'] = args.comfort
        result = {'comfort': args.comfort}
    elif cmd == 'easier':
        state['preferences']['easier_next_week'] = bool(args.on)
        result = {'easier_next_week': bool(args.on)}
    elif cmd == 'offer':
        if args.track not in tracks_for(state) or args.difficulty not in DIFFICULTY:
            raise GameError(f"Invalid track or difficulty. Tracks: {', '.join(tracks_for(state))}.")
        title = (args.title or '').strip()
        if not title or len(title) > 160:
            raise GameError('Title must be 1–160 characters.')
        if parent_run:
            # Child quests are tasks set by a parent, never public events or links.
            if args.source or args.start:
                raise GameError('Kid quests are home/homework tasks: no event links or start times.')
            args.location = (args.location or '').strip() or 'Home'
            args.solo = True
        if not (args.location or '').strip():
            raise GameError('Location required.')
        if args.solo:
            if args.source:
                raise GameError('Solo quest must not pretend to be a sourced event.')
            start = args.start or today
        else:
            if not valid_source(args.source or ''):
                raise GameError('Real event quests need an HTTPS source URL; verify it first.')
            if not args.start:
                raise GameError('Real events require start date/time.')
            parse_datetime(args.start)
            start = args.start
        ident = quest_id(title, start, args.source or 'solo')
        if ident in state['quests']:
            return {'id': ident, 'status': state['quests'][ident]['status'], 'already_exists': True}
        state['quests'][ident] = {'id': ident, 'title': title, 'track': args.track,
             'difficulty': args.difficulty, 'xp': DIFFICULTY[args.difficulty],
             'source_url': args.source or None, 'starts_at': start,
             'location': args.location.strip(), 'solo': args.solo, 'status': 'offered',
             'created_on': today}
        result = {'id': ident, 'status': 'offered', 'xp': DIFFICULTY[args.difficulty]}
    elif cmd in ('accept', 'skip', 'complete'):
        q = resolve_quest(state, args.quest_id)
        if cmd == 'accept':
            if q['status'] not in ('offered', 'accepted'):
                raise GameError('Only an offered quest can be accepted.')
            q['status'] = 'accepted'
            result = {'id': q['id'], 'status': 'accepted', 'xp_on_completion': q['xp']}
        elif cmd == 'skip':
            if q['status'] in ('completed', 'skipped'):
                raise GameError('This quest was already closed.')
            q['status'] = 'skipped'
            state['quests_skipped'].append({'id': q['id'], 'quest': q['title'], 'date': today})
            result = {'id': q['id'], 'status': 'skipped', 'lost_xp': 0}
        else:
            if q['status'] == 'completed':
                return {'id': q['id'], 'already_completed': True, 'awarded_xp': 0,
                        'total_xp': sum(state['tracks'].values())}
            if q['status'] != 'accepted':
                raise GameError('Accept this quest before completion.')
            if parent_run and (not args.verified or args.proof != 'parent'):
                raise GameError('No XP: a parent must confirm this task is done, then pass --verified --proof parent.')
            if not parent_run and (not args.verified or args.proof not in ('photo', 'reflection', 'checkin')):
                raise GameError('No XP: Cubbie must validate proof, then pass --verified --proof photo|reflection|checkin.')
            before = level_for(sum(state['tracks'].values()))
            q['status'] = 'completed'
            q['completed_on'] = today
            # Store proof type, never store images, identifiers, or reflection text.
            q['proof_type'] = args.proof
            state['tracks'][q['track']] += q['xp']
            state['quests_done'].append({'id': q['id'], 'title': q['title'], 'quest': q['title'],
              'track': q['track'], 'xp': q['xp'], 'date': today, 'difficulty': q['difficulty']})
            medals = update_badges(state, today)
            after = level_for(sum(state['tracks'].values()))
            result = {'id': q['id'], 'awarded_xp': q['xp'], 'total_xp': sum(state['tracks'].values()),
              'level': after, 'leveled_up': after > before, 'new_badges': medals,
              'offer_optional_visual': after > before or bool(medals)}
    else:
        raise GameError('Unknown command.')
    save_state(state, profile=args.profile)
    return result


def build_parser():
    p = argparse.ArgumentParser(description='asucend private quest/XP ledger. Never fetches events or contacts Cubbie.')
    p.add_argument('--sample', action='store_true', help='Read bundled sample, never modify it')
    p.add_argument('--today', help='Student-local date YYYY-MM-DD (recommended for all commands)')
    p.add_argument('--json', action='store_true', help='JSON output')
    p.add_argument('--profile', help="Whose ledger: 'me' (default) or a child's nickname")
    s = p.add_subparsers(dest='command')
    s.add_parser('profiles')
    u = s.add_parser('setup'); u.add_argument('--segment', choices=tuple(SEGMENTS), required=True)
    s.add_parser('forget').add_argument('--confirm', action='store_true')
    s.add_parser('status')
    s.add_parser('badges')
    s.add_parser('recommend')
    s.add_parser('card-data')
    c = s.add_parser('set-comfort'); c.add_argument('--comfort', type=int, required=True)
    e = s.add_parser('easier'); e.add_argument('--on', type=int, choices=(0,1), required=True)
    o = s.add_parser('offer')
    for name in ('title', 'track', 'difficulty'):
        o.add_argument('--'+name, required=True)
    o.add_argument('--location')
    o.add_argument('--start');o.add_argument('--source');o.add_argument('--solo', action='store_true')
    for action in ('accept','skip','complete'):
        a=s.add_parser(action); a.add_argument('--quest-id', required=True)
        if action == 'complete':
            a.add_argument('--verified', action='store_true')
            a.add_argument('--proof', choices=('photo','reflection','checkin','parent'))
    return p


def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    try:
        is_mutation = (args.command in ('setup','forget','offer','accept','skip','complete','set-comfort','easier'))
        if is_mutation and not args.sample:
            with write_lock():
                result = run(args)
        else:
            result = run(args)
    except GameError as e:
        print(str(e), file=sys.stderr)
        return e.code
    print(json.dumps(result, indent=2, ensure_ascii=False) if isinstance(result,(dict,list)) else result)
    return 0

if __name__ == '__main__':
    sys.exit(main())
