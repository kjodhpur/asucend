#!/usr/bin/env python3
"""Student-controlled optional game presentation preferences, stored in the private XP ledger.
No networking, no background behavior, no image generation, no messages sent.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from themes import THEMES, SEGMENT_CARDS, FEATURES, MODES, COLOR, options_for
from xp import GameError, load_state, save_state, write_lock


def clean_label(raw,field):
    val=(raw or '').strip()
    if len(val)>100 or any(ord(c)<32 for c in val):
        raise GameError(f'{field} must be at most 100 characters of plain text')
    return val

def is_dark(hexvalue):
    rgb=tuple(int(hexvalue[i:i+2],16) for i in (1,3,5))
    # Keep all auto-rendered text legible on custom backgrounds.
    lum=sum(w*c for w,c in zip((0.2126,0.7152,0.0722),rgb))
    return lum<100

def operation(args):
    state=load_state(args.sample,args.profile)
    opts=options_for(state)
    command=args.command or 'show'
    if command=='show':
        return opts
    if args.sample:
        raise GameError('Sample mode cannot change preferences')
    if command=='voice':
        if args.mode not in MODES:raise GameError('Use off, light or immersive')
        opts['voice_mode']=args.mode
        if args.world is not None:opts['world']=clean_label(args.world,'world')
        if args.archetype is not None:opts['voice_archetype']=clean_label(args.archetype,'archetype')
        result={'voice_mode':opts['voice_mode'],'world':opts['world'],'voice_archetype':opts['voice_archetype']}
    elif command=='theme':
        allowed=SEGMENT_CARDS[state.get('segment','college')]['themes']
        if args.name not in allowed:
            raise GameError('Choose one of: '+', '.join(allowed))
        opts['card_theme']=args.name
        if args.name=='custom':
            for field in ('background','accent','accent2'):
                value=getattr(args,field)
                if value is not None:
                    if not COLOR.fullmatch(value):
                        raise GameError(f'{field}: use a six-digit #RRGGBB hex color')
                    if field=='background' and not is_dark(value):
                        raise GameError('Choose a dark background for readable card text')
                    opts['custom_colors'][field]=value.upper()
        result={'card_theme':opts['card_theme'],'custom_colors':opts['custom_colors']}
    elif command=='feature':
        if args.name not in FEATURES:raise GameError('Unknown feature')
        opts['features'][args.name]=bool(args.enabled)
        result={'feature':args.name,'enabled':bool(args.enabled)}
    elif command=='reset-presentation':
        # Does not touch XP/quests; preserves older difficulty preference.
        from themes import default_options
        opts=default_options(state.get('segment','college'))
        result={'presentation_reset':True,'xp_preserved':True}
    else:
        raise GameError('Unknown command')
    # Preserve older script's adaptive-difficulty preference while updating display options.
    state.setdefault('preferences',{}).update(opts)
    save_state(state,profile=args.profile)
    return result


def parser():
    p=argparse.ArgumentParser(description='ASUcend optional settings')
    p.add_argument('--sample',action='store_true',help='Read demo state without mutations')
    p.add_argument('--profile',help="Whose settings: 'me' (default) or a child's nickname")
    sub=p.add_subparsers(dest='command')
    sub.add_parser('show')
    v=sub.add_parser('voice',help='Select how Cubbie narrates optional game flavor')
    v.add_argument('--mode',required=True,choices=MODES)
    v.add_argument('--world',help='Favorite game/genre inspiration; original persona, no quoted game dialogue')
    v.add_argument('--archetype',help='Voice archetype, e.g. warm quest guide, witty starship captain')
    t=sub.add_parser('theme',help='Visual appearance for opt-in SVG cards')
    t.add_argument('--name',required=True,choices=(*THEMES,'custom'))
    for field in ('background','accent','accent2'):
        t.add_argument('--'+field)
    f=sub.add_parser('feature',help='Enable/disable an individual optional feature')
    f.add_argument('--name',required=True,choices=FEATURES)
    f.add_argument('--enabled',required=True,type=int,choices=(0,1))
    sub.add_parser('reset-presentation')
    return p


def main(argv=None):
    args=parser().parse_args(argv)
    try:
        if args.command in ('voice','theme','feature','reset-presentation') and not args.sample:
            with write_lock(): result=operation(args)
        else:result=operation(args)
        print(json.dumps(result,indent=2,ensure_ascii=False))
        return 0
    except GameError as ex:
        print(str(ex),file=sys.stderr)
        return ex.code

if __name__=='__main__':sys.exit(main())
