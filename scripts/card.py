#!/usr/bin/env python3
"""Opt-in, template-generated SVG achievement card, never AI image generation.
Six original genre styles + student-owned custom colors. No commercial game assets.
"""
from __future__ import annotations
import argparse
import html
import json
import sys
from pathlib import Path
from xp import load_state, snapshot, iso_day, GameError, THRESHOLDS
from themes import THEMES, options_for, palette_for

TRACK_COLORS = {'networking':'#FD71B6','career':'#FBCB6D','academic':'#A991FF',
                'wellness':'#57DFB3','exploration':'#61CFF7'}

def esc(v):
    return html.escape(str(v),quote=True)

def art(theme, c):
    """Original SVG geometry that conveys genre without borrowed logos/artwork."""
    a=c['accent']; b=c['accent2']
    if theme=='retro':
        return ''.join(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{a if n%2 else b}" opacity="0.17"/>'
                       for n,(x,y,s) in enumerate([(1230,77,32),(1300,120,16),(1345,180,38),(45,600,38),(85,680,18),(1370,580,27),(1150,30,16)]))
    if theme=='scifi':
        return f'<ellipse cx="1250" cy="130" rx="205" ry="67" transform="rotate(-32 1250 130)" fill="none" stroke="{a}" stroke-width="3" opacity="0.25"/><circle cx="1250" cy="130" r="77" fill="none" stroke="{b}" opacity="0.23"/><path d="M50 660 L390 660 M1080 85 L1400 85" stroke="{a}" stroke-width="3" opacity="0.25"/>'
    if theme=='fantasy':
        return f'<path d="M1198 80 L1260 33 L1322 80 L1260 127Z" fill="none" stroke="{a}" stroke-width="4" opacity="0.25"/><path d="M1200 80 H1320 M1260 33 V127" stroke="{a}" opacity="0.2"/><circle cx="1260" cy="80" r="105" fill="none" stroke="{b}" opacity="0.20" stroke-dasharray="8,16"/>'
    if theme=='anime':
        return f'<path d="M1150 0 L1440 0 L1440 450Z" fill="{a}" opacity="0.06"/><path d="M1180 50 L1220 95 L1260 50 L1220 5Z" fill="{b}" opacity="0.19"/><path d="M1350 215 L1370 260 L1390 215 L1370 170Z" fill="{a}" opacity="0.20"/>'
    if theme=='cozy':
        return ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{a if i%2 else b}" opacity="0.10"/>' for i,(x,y,r) in enumerate([(1240,100,110),(140,700,85),(1310,610,32),(1400,280,55)]))
    return f'<path d="M1050 20 V750 M1160 20 V750 M1270 20 V750 M1380 20 V750 M20 160 H1420 M20 300 H1420 M20 440 H1420 M20 580 H1420" stroke="{a}" stroke-width="1" opacity="0.07"/>'

def create_svg(data, options=None, theme_override=None):
    options=options or {}
    chosen=theme_override or options.get('card_theme','neon')
    c=palette_for(options,theme_override)
    family = 'Courier New,monospace' if chosen == 'retro' else ('Georgia,serif' if chosen in ('fantasy','cozy') else 'Arial,sans-serif')
    corner = 0 if chosen == 'retro' else 8
    tracks=data['tracks']; max_xp=max(1,max(tracks.values()))
    bars=[]
    for i,(key,color) in enumerate(TRACK_COLORS.items()):
        y=342+i*46
        w=round(300*tracks[key]/max_xp)
        bars.append(f'<text x="752" y="{y}" class="small">{esc(key.title())}</text>'
         f'<rect x="951" y="{y-17}" width="300" height="15" rx="5" fill="{c["panel"]}" stroke="{c["edge"]}" stroke-opacity="0.2"/>'
         f'<rect x="951" y="{y-17}" width="{w}" height="15" rx="5" fill="{color}"/>'
         f'<text x="1355" y="{y-3}" text-anchor="end" class="tiny">{tracks[key]} XP</text>')
    level=data['level']; total=data['total_xp']; target=data['next_level_at']
    recent=data['completed_this_week']
    completion=f"{len(recent)} {'quest' if len(recent)==1 else 'quests'} this week"
    badges=data['badges'][-3:]
    badge_names=', '.join(b.get('name','Medal') for b in badges) if badges else 'Your first medal awaits'
    previous=THRESHOLDS[min(level-1,len(THRESHOLDS)-1)]
    progress=min(100,max(0,round(100*(total-previous)/max(1,target-previous))))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="810" viewBox="0 0 1440 810" role="img" aria-label="ASUcend themed player progress card">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{c['background']}"/><stop offset="1" stop-color="{c['panel']}"/></linearGradient>
<linearGradient id="energy" x1="0" x2="1"><stop stop-color="{c['accent']}"/><stop offset="1" stop-color="{c['accent2']}"/></linearGradient>
<style>
.big{{fill:#FFFFFF;font:bold 88px {family}}}.title{{fill:#FFFFFF;font:bold 54px {family}}}.small{{fill:#F6F2FF;font:24px {family}}}.tiny{{fill:#D1D1DF;font:20px {family}}}.eyebrow{{fill:{c['accent']};font:bold 17px {family};letter-spacing:3px}}
</style></defs>
<rect width="1440" height="810" rx="36" fill="url(#bg)"/>
{art(chosen,c)}
<rect x="36" y="36" width="1368" height="738" rx="29" fill="none" stroke="{c['edge']}" stroke-opacity="0.78" stroke-width="3"/>
<rect x="92" y="78" width="10" height="40" rx="5" fill="{c['accent']}"/>
<text x="121" y="110" class="eyebrow">{esc(c['eyebrow'])} / ASUCEND</text>
<text x="92" y="205" class="title">{esc(data['title'])}</text>
<text x="93" y="282" class="big">LVL {level}</text>
<text x="95" y="344" class="small">{total} / {target} XP</text>
<rect x="95" y="380" width="535" height="23" rx="{corner}" fill="{c['panel']}" stroke="{c['edge']}" stroke-opacity="0.35"/>
<rect x="95" y="380" width="{round(535*progress/100)}" height="23" rx="{corner}" fill="url(#energy)"/>
<text x="95" y="451" class="small">{esc(completion)}</text>
<text x="95" y="498" class="small">{data['completed_count']} lifetime quests</text>
<text x="95" y="544" class="small">{data['momentum_weeks']} {'week' if data['momentum_weeks']==1 else 'weeks'} of momentum</text>
<text x="752" y="270" class="eyebrow">YOUR SKILL TREE</text>
{''.join(bars)}
<rect x="91" y="616" width="1258" height="112" rx="21" fill="{c['panel']}" stroke="{c['edge']}" stroke-opacity="0.55" stroke-width="2"/>
<text x="121" y="660" class="eyebrow">UNLOCKED MEDALS</text>
<text x="121" y="703" class="small">{esc(badge_names[:90])}</text>
<text x="1350" y="113" text-anchor="end" class="eyebrow">{esc(c['tag'])}</text>
</svg>'''

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--sample',action='store_true',help='Demo card uses fictional data')
    p.add_argument('--today',required=True,help='Student-local YYYY-MM-DD')
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--theme',choices=(*THEMES,'custom'),help='One-time visual override; does not save preference')
    p.add_argument('--once',action='store_true',help='Explicit one-off user request, even when weekly cards disabled')
    args=p.parse_args(argv)
    try:
        if args.out.suffix.lower()!='.svg':raise GameError('Output must be .svg')
        state=load_state(args.sample)
        opts=options_for(state)
        if not args.sample and not args.once and not opts['features']['weekly_cards']:
            raise GameError('Weekly visual cards are off. Ask the student to opt in first, or use --once after a direct request.')
        data=snapshot(state,iso_day(args.today))
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(create_svg(data,opts,args.theme),encoding='utf-8')
        print(json.dumps({'card_path':str(args.out),'visual_theme':args.theme or opts['card_theme'],
                          'format':'SVG','no_image_generation_used':True,
                          'message':'Private card created. Do not automatically share; ask before sending to anyone else.'}))
        return 0
    except (OSError,GameError,ValueError) as e:
        print(str(e),file=sys.stderr)
        return 2

if __name__=='__main__':sys.exit(main())
