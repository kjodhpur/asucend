#!/usr/bin/env python3
"""Rank Cubbie-verified event candidates against supplied free/busy windows.
No network or calendar access: Cubbie reads them first and supplies local JSON.
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit

SAMPLE = Path(__file__).resolve().parent.parent / 'assets' / 'sample_candidates.json'


def dt(value):
    x = datetime.fromisoformat(value)
    if x.utcoffset() is None:
        raise ValueError('Timestamp must include timezone')
    return x


def intervals(raw):
    out = []
    for block in raw:
        start, end = dt(block['start']), dt(block['end'])
        if start >= end:
            raise ValueError('Invalid free/busy interval')
        out.append((start, end))
    return out


def overlaps(a, b, c, d):
    return a < d and c < b


def valid_https(value):
    try:
        p = urlsplit(value)
        return p.scheme == 'https' and bool(p.netloc) and not p.username and not p.password
    except (ValueError, TypeError):
        return False


def rank(data):
    """Return up to three sourced, non-conflicting events and rejection details.

    Calendar busy and free blocks are explicit. Missing BOTH -> no exact availability
    verification; user must approve scheduling, and we surface the uncertainty.
    """
    interests = {x.casefold() for x in data.get('interests', [])}
    campus = str(data.get('campus', '')).casefold()
    comfort = int(data.get('comfort', 3))
    if not 1 <= comfort <= 5:
        raise ValueError('Comfort must be 1-5')
    busy = intervals(data.get('busy', []))
    free = intervals(data.get('free', []))
    min_date = dt(data['now'])
    minutes = max(0,min(180,int(data.get('travel_buffer_minutes', 15))))
    buffer = timedelta(minutes=minutes)
    price_cap = data.get('max_price', None)
    if price_cap is not None and float(price_cap) < 0:
        raise ValueError('Price cap must not be negative')
    results, rejected = [], []
    for event in data.get('events', []):
        name = event.get('name','')
        try:
            start, end = dt(event['start']), dt(event['end'])
            price = event.get('price')
            reason = None
            if not name or not valid_https(event.get('source_url')) or not event.get('location'):
                reason = 'incomplete or unsourced event'
            elif end <= start or start <= min_date:
                reason = 'past or invalid event time'
            elif price_cap is not None and (price is None or float(price) > float(price_cap)):
                reason = 'price unknown or exceeds budget'
            elif any(overlaps(start-buffer,end+buffer,a,b) for a,b in busy):
                reason = 'calendar conflict including travel buffer'
            elif free and not any(a <= start-buffer and end+buffer <= b for a,b in free):
                reason = 'outside stated free time'
            if reason:
                rejected.append({'name':name,'reason':reason});continue
            score = 0
            tags = {str(x).casefold() for x in event.get('tags',[])}
            score += 25 * len(interests & tags)
            score += 15 if str(event.get('campus','')).casefold() == campus else -8
            social_intensity = int(event.get('social_intensity', 3))
            score += 20 - 10*abs(comfort-social_intensity)
            score += 10 if price == 0 else 0
            score += 3 if free else 0
            results.append({'name':name,'start':event['start'],'end':event['end'],
               'location':event['location'],'source_url':event['source_url'],
               'campus':event.get('campus',''),'price':price,
               'tags':sorted(tags),'score':score,
               'no_known_conflicts':True,
               'availability_basis':'free windows and/or calendar busy blocks provided' if (free or busy) else 'unknown',
               'note':'Confirm student is actually free' if not (free or busy) else 'Check with student before scheduling'})
        except (ValueError, TypeError, KeyError) as exc:
            rejected.append({'name':name,'reason':'invalid candidate fields'})
    results.sort(key=lambda x: (-x['score'],x['start'],x['name']))
    distinct, seen = [], set()
    for item in results:
        unique = (item['source_url'], item['start'])
        if unique not in seen:
            distinct.append(item)
            seen.add(unique)
    return {'suggestions':distinct[:3],'rejected':rejected,
            'notice':'Examples only; not live ASU events' if data.get('sample_only') else
              'Sources and event details must be checked by Cubbie before offering'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path)
    p.add_argument('--sample',action='store_true')
    args=p.parse_args()
    if not args.sample and not args.input:
        p.error('Provide --input <Cubbie-supplied JSON> or --sample')
    try:
        data=json.loads((SAMPLE if args.sample else args.input).read_text())
        print(json.dumps(rank(data),indent=2,ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as e:
        print('Cannot rank event candidates: '+str(e),file=sys.stderr)
        return 2

if __name__=='__main__':
    sys.exit(main())
