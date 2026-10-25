#!/usr/bin/env python3
"""Opt-in, template-generated SVG achievement card, never AI image generation.

Each age segment has one portrait layout (assets/cards/layouts/<layout>.svg) and each
theme supplies a palette (themes.py) plus an original scene (assets/cards/scenes/<theme>.svg).
This script only fills in the student's numbers; all text is escaped. No commercial game assets.
"""
from __future__ import annotations
import argparse
import html
import json
import math
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from xp import load_state, snapshot, iso_day, profile_name, GameError, THRESHOLDS, DEFAULT_PROFILE
from themes import THEMES, SEGMENT_CARDS, options_for, palette_for

CARDS = Path(__file__).resolve().parent.parent / 'assets' / 'cards'
FONTS = CARDS.parent / 'fonts'
TRACK_COLORS = {'networking':'#FD71B6','career':'#FBCB6D','academic':'#A991FF',
                'wellness':'#57DFB3','exploration':'#61CFF7',
                'homework':'#5B6CFF','reading':'#FF8A3D','practice':'#2FB463',
                'creativity':'#F2559F','helping':'#E8A700'}
RADAR_LABELS = {'networking':'NETWORK','career':'CAREER','academic':'ACADEMIC','wellness':'WELLNESS',
                'exploration':'EXPLORE','homework':'HOMEWORK','reading':'READING','practice':'PRACTICE',
                'creativity':'CREATIVE','helping':'HELPING'}
RARITY_COLORS = {'common':'#9FD8FF','rare':'#4DA3FF','epic':'#C77DFF','legendary':'#FFC94D'}
STICKER_COLORS = {'common':'#3FBF6F','rare':'#4D7CFF','epic':'#B05CFF','legendary':'#FFB020'}
STAR = 'M0 -16 L4.7 -6.5 L15.2 -4.9 L7.6 2.5 L9.4 12.9 L0 8 L-9.4 12.9 L-7.6 2.5 L-15.2 -4.9 L-4.7 -6.5Z'
MEDAL_GLYPHS = {
    'first-spark':'M0 -16 L4 -4 L16 0 L4 4 L0 16 L-4 4 L-16 0 L-4 -4Z',
    'first-contact':'M-15 0 a9 9 0 1 0 18 0 a9 9 0 1 0 -18 0 M-3 0 a9 9 0 1 0 18 0 a9 9 0 1 0 -18 0',
    'campus-cartographer':'M0 -16 L6 0 L0 16 L-6 0Z M-16 0 H16',
    'courage-rising':'M0 16 C-12 10 -10 -2 0 -16 C10 -2 12 10 0 16Z',
    'opportunity-hunter':'M-14 0 a14 14 0 1 0 28 0 a14 14 0 1 0 -28 0 M-5 0 a5 5 0 1 0 10 0 a5 5 0 1 0 -10 0',
    'five-quests':'M-12 0 L-3 10 L13 -10',
    'balanced-hero':'M0 -15 L14 -5 L9 12 L-9 12 L-14 -5Z',
    'boss-slayer':'M-13 -13 L13 13 M13 -13 L-13 13 M-15 6 L-6 15 M15 6 L6 15',
    'campus-legend':'M-14 10 L-14 -8 L-6 2 L0 -12 L6 2 L14 -8 L14 10Z',
    'first-star':STAR,
    'homework-hero':'M-11 11 L-13 13 L-11 5 L7 -13 L13 -7 L-5 11Z M3 -9 L9 -3',
    'bookworm':'M0 -8 C-6 -13 -12 -13 -15 -11 V11 C-12 9 -6 9 0 13 C6 9 12 9 15 11 V-11 C12 -13 6 -13 0 -8Z M0 -8 V13',
    'practice-power':'M3 -16 L-9 2 H0 L-3 16 L9 -2 H0Z',
    'idea-maker':'M-6 8 C-6 2 -12 -1 -12 -6 A12 12 0 0 1 12 -6 C12 -1 6 2 6 8Z M-5 13 H5',
    'super-helper':'M0 13 C-17 1 -14 -12 -6 -12 C-2 -12 0 -9 0 -7 C0 -9 2 -12 6 -12 C14 -12 17 1 0 13Z',
    'big-challenge':'M-16 12 L-5 -8 L1 2 L6 -4 L16 12Z',
    'all-rounder':'M0 -15 L14 -5 L9 12 L-9 12 L-14 -5Z',
    'quest-legend':'M-14 10 L-14 -8 L-6 2 L0 -12 L6 2 L14 -8 L14 10Z',
}
HEX = 'M0 -34 L30 -17 L30 17 L0 34 L-30 17 L-30 -17Z'

def esc(v):
    return html.escape(str(v),quote=True)

def level_start(level):
    """XP at which a level begins; past the table each level spans 400 XP (see xp.level_for)."""
    if level<=len(THRESHOLDS):
        return THRESHOLDS[level-1]
    return THRESHOLDS[-1]+(level-len(THRESHOLDS))*400

def radar(tracks, r=78):
    """Pentagon skill chart centred on 0,0; styled by the layout's CSS classes."""
    keys=list(tracks); top=max(1,max(tracks.values()))
    def pt(i,radius):
        a=math.radians(-90+72*i)
        return round(radius*math.cos(a),1),round(radius*math.sin(a),1)
    rings=''.join('<path class="radar-ring" d="M'+' L'.join(f'{x} {y}' for x,y in (pt(i,r*f) for i in range(5)))+'Z"/>'
                  for f in (1/3,2/3,1))
    axes=''.join(f'<line class="radar-axis" x1="0" y1="0" x2="{x}" y2="{y}"/>' for x,y in (pt(i,r) for i in range(5)))
    pts=[pt(i,r*max(0.08,tracks[k]/top)) for i,k in enumerate(keys)]
    shape='<path class="radar-shape" d="M'+' L'.join(f'{x} {y}' for x,y in pts)+'Z"/>'
    dots=''.join(f'<circle class="radar-dot" cx="{x}" cy="{y}" r="5"/>' for x,y in pts)
    labels=[]
    for i,k in enumerate(keys):
        x,y=pt(i,r+20)
        anchor='middle' if abs(x)<20 else ('start' if x>0 else 'end')
        labels.append(f'<text class="radar-label" x="{x}" y="{y+(16 if y>0 else 0)}" text-anchor="{anchor}">{RADAR_LABELS.get(k,esc(k.upper()))}</text>')
    return rings+axes+shape+dots+''.join(labels)

def track_list(tracks, width=420, row=36, bar_x=190, bar_w=160, bar_h=10):
    top=max(1,max(tracks.values())); rows=[]
    for i,(key,xp) in enumerate(tracks.items()):
        y=i*row; color=TRACK_COLORS.get(key,'#9FD8FF')
        rows.append(f'<circle cx="7" cy="{y-8}" r="7" fill="{color}"/>'
                    f'<text class="track-name" x="24" y="{y}">{esc(key.title())}</text>'
                    f'<rect class="bar-bg" x="{bar_x}" y="{y-4-bar_h}" width="{bar_w}" height="{bar_h}" rx="{bar_h/2}"/>'
                    f'<rect x="{bar_x}" y="{y-4-bar_h}" width="{round(bar_w*xp/top)}" height="{bar_h}" rx="{bar_h/2}" fill="{color}"/>'
                    f'<text class="track-xp" x="{width}" y="{y}" text-anchor="end" fill="{color}">{xp}</text>')
    return ''.join(rows)

def wrap(name, limit=12):
    lines=['']
    for word in name.split():
        if lines[-1] and len(lines[-1])+1+len(word)>limit:
            lines.append(word)
        else:
            lines[-1]=(lines[-1]+' '+word).strip()
    return lines[:2]

def medals(badges, slots=4, gap=150, cols=None, row_gap=150, sticker=False):
    """Earned medals first (newest last), then locked '?' slots. Hexes for 13+, round stickers for kids."""
    cols=cols or slots
    shown=badges[-slots:]; out=[]
    for i in range(slots):
        x=(i%cols)*gap; y=(i//cols)*row_gap
        if i>=len(shown):
            shape=f'<circle class="medal-locked" r="34"/>' if sticker else f'<path class="medal-locked" d="{HEX}"/>'
            out.append(f'<g transform="translate({x} {y})">{shape}'
                       f'<text class="medal-locked-text" y="12" text-anchor="middle">?</text></g>')
            continue
        b=shown[i]
        glyph=MEDAL_GLYPHS.get(b.get('id'),STAR)
        if sticker:
            color=STICKER_COLORS.get(b.get('rarity'),STICKER_COLORS['common'])
            frame=(f'<circle r="38" fill="{color}" stroke="#FFFFFF" stroke-width="6"/>'
                   f'<path class="medal-glyph" d="{glyph}" stroke="#FFFFFF" transform="scale(1.25)"/>')
            name_fill='class="medal-name"'
        else:
            color=RARITY_COLORS.get(b.get('rarity'),RARITY_COLORS['common'])
            frame=(f'<path class="medal-frame" d="{HEX}" stroke="{color}" filter="url(#glow)"/>'
                   f'<path class="medal-glyph" d="{glyph}" stroke="{color}"/>')
            name_fill=f'class="medal-name" fill="{color}"'
        names=''.join(f'<text {name_fill} y="{(56 if sticker else 60)+j*18}" text-anchor="middle">{esc(line)}</text>'
                      for j,line in enumerate(wrap(str(b.get('name','Medal')))))
        out.append(f'<g transform="translate({x} {y})">{frame}{names}</g>')
    return ''.join(out)

def quest_list(done, rows=3, width=820):
    if not done:
        return '<text class="quest" x="0" y="0">No quests finished yet this week. You can do it!</text>'
    out=[]
    for i,q in enumerate(done[-rows:]):
        y=i*46; title=str(q.get('title','Quest'))
        title=title if len(title)<=34 else title[:33]+'…'
        out.append(f'<circle class="check" cx="14" cy="{y-9}" r="16"/>'
                   f'<path d="M6 {y-9} L12 {y-2} L22 {y-16}" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
                   f'<text class="quest" x="46" y="{y}">{esc(title)}</text>'
                   f'<text class="quest-xp" x="{width}" y="{y}" text-anchor="end">+{esc(q.get("xp",0))} XP</text>')
    if len(done)>rows:
        out.append(f'<text class="muted" x="{width}" y="-50" text-anchor="end">+ {len(done)-rows} more this week</text>')
    return ''.join(out)

def star_chart(count, slots=10, cols=5, gap=180, row_gap=118):
    out=[]
    for i in range(slots):
        x=(i%cols)*gap; y=(i//cols)*row_gap
        cls='star-on' if i<count else 'star-off'
        out.append(f'<path class="{cls}" d="{STAR}" transform="translate({x} {y}) scale(3.2)"/>')
    return ''.join(out)

def progress_path(pct, dots=10, gap=78):
    filled=round(pct*dots/100)
    out=[f'<path d="M0 0 H{(dots-1)*gap}" class="path-line"/>']
    for i in range(dots):
        out.append(f'<circle class="{"dot-on" if i<filled else "dot-off"}" cx="{i*gap}" cy="0" r="22"/>')
    return ''.join(out)

def scene_for(theme):
    path=CARDS/'scenes'/f'{theme}.svg'
    if not path.is_file():
        raise GameError(f'Card scene for {theme} is missing.')
    return path.read_text(encoding='utf-8')

def fill(template, values):
    def sub(m):
        if m.group(1) not in values:
            raise ValueError(f'Card template uses unknown placeholder {m.group(1)}')
        return str(values[m.group(1)])
    # Single pass, so braces inside student-supplied text are never expanded.
    return re.sub(r'\{\{(\w+)\}\}',sub,template)

def create_svg(data, options=None, theme_override=None, today=None, player=None):
    options=options or {}
    segment=data.get('segment','college')
    cards=SEGMENT_CARDS[segment]
    chosen=theme_override or options.get('card_theme') or cards['default']
    if chosen not in cards['themes']:
        raise GameError(f"Theme {chosen} isn't available for this age group. Choose: {', '.join(cards['themes'])}.")
    c=palette_for(options,chosen)
    level=data['level']; total=data['total_xp']; target=data['next_level_at']
    previous=level_start(level)
    week=len(data['completed_this_week']); momentum=data['momentum_weeks']
    pct=min(100,max(0,round(100*(total-previous)/max(1,target-previous))))
    day=date.fromisoformat(today) if today else None
    who=(player or '').upper()
    text={'label':c['label'],'eyebrow':f"{who} · {c['eyebrow']}" if who else c['eyebrow'],'tag':c['tag'],
          'title_upper':data['title'].upper(),'level':level,'next_level':level+1,'total_xp':total,
          'level_xp':total-previous,'level_span':target-previous,'xp_to_next':data.get('xp_to_next',target-total),
          'xp_pct':pct,'week_label':f'WEEK OF {day:%b} {day.day}'.upper() if day else '',
          'week_count':week,'week_label_short':'QUEST THIS WEEK' if week==1 else 'QUESTS THIS WEEK',
          'stars_label':'1 STAR!' if week==1 else f'{week} STARS!',
          'lifetime':data['completed_count'],'momentum':momentum,
          'momentum_label':'WEEK OF MOMENTUM' if momentum==1 else 'WEEKS OF MOMENTUM'}
    for key in ('background','panel','edge','accent','accent2','highlight','text','muted'):
        text['c_'+key]=c[key]
    values={k:esc(v) for k,v in text.items()}
    values['font']=c['font']   # trusted constant from themes.py; quotes must stay literal CSS
    tracks=data['tracks']
    values['scene']=fill(scene_for(chosen),{k:v for k,v in values.items() if k.startswith('c_')})
    if cards['layout']=='player':
        values.update(radar=radar(tracks),track_list=track_list(tracks),medals=medals(data['badges']))
    elif cards['layout']=='junior':
        values.update(track_list=track_list(tracks,width=380,row=44,bar_x=196,bar_w=130,bar_h=14),
                      medals=medals(data['badges'],slots=4,gap=200,cols=2,row_gap=108,sticker=True),
                      quest_list=quest_list(data['completed_this_week']))
    else:
        values.update(star_chart=star_chart(week),progress_path=progress_path(pct),
                      medals=medals(data['badges'],slots=4,gap=170,sticker=True))
    layout=(CARDS/'layouts'/f"{cards['layout']}.svg").read_text(encoding='utf-8')
    return fill(layout,values)

def to_png(svg_path, png_path, width=1080, height=1350):
    """Best-effort PNG for messaging apps that don't show SVG. Prefers resvg-py with the bundled
    fonts (identical output in any sandbox), then any other renderer that happens to exist."""
    attempts=[]
    try:
        import resvg_py  # type: ignore
        png=resvg_py.svg_to_bytes(svg_path=str(svg_path),skip_system_fonts=True,font_dirs=[str(FONTS)])
        png_path.write_bytes(bytes(png))
        return 'resvg-py'
    except ImportError:
        attempts.append('resvg-py')
    except Exception as e:
        attempts.append(f'resvg-py ({e.__class__.__name__})')
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(url=str(svg_path),write_to=str(png_path),output_width=width,output_height=height)
        return 'cairosvg'
    except ImportError:
        attempts.append('cairosvg')
    except Exception as e:  # renderer present but failed
        attempts.append(f'cairosvg ({e.__class__.__name__})')
    commands=[('rsvg-convert',['rsvg-convert','-w',str(width),'-h',str(height),'-o',str(png_path),str(svg_path)]),
              ('inkscape',['inkscape',str(svg_path),'--export-type=png',f'--export-filename={png_path}',f'--export-width={width}']),
              ('magick',['magick','-background','none',str(svg_path),'-resize',f'{width}x{height}',str(png_path)])]
    for chrome in ('chromium','chromium-browser','google-chrome','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'):
        commands.append((chrome,[chrome,'--headless=new','--disable-gpu','--hide-scrollbars',
                                 f'--window-size={width},{height}',f'--screenshot={png_path}',svg_path.resolve().as_uri()]))
    for name,cmd in commands:
        if not (shutil.which(cmd[0]) or Path(cmd[0]).is_file()):
            attempts.append(name); continue
        try:
            subprocess.run(cmd,check=True,capture_output=True,timeout=60)
            if png_path.is_file() and png_path.stat().st_size>0:
                return Path(name).name
        except (OSError,subprocess.SubprocessError):
            attempts.append(name)
    raise GameError('No PNG renderer available (tried '+', '.join(attempts)+'). Send the SVG or a text summary instead.')

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--sample',action='store_true',help='Demo card uses fictional data')
    p.add_argument('--profile',help="Whose card: 'me' (default) or a child's nickname")
    p.add_argument('--today',required=True,help='Student-local YYYY-MM-DD')
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--theme',choices=(*THEMES,'custom'),help='One-time visual override; does not save preference')
    p.add_argument('--once',action='store_true',help='Explicit one-off user request, even when weekly cards disabled')
    p.add_argument('--png',action='store_true',help='Also write a PNG next to the SVG, if a renderer is available')
    args=p.parse_args(argv)
    try:
        if args.out.suffix.lower()!='.svg':raise GameError('Output must be .svg')
        name=profile_name(args.profile)
        state=load_state(args.sample,name)
        opts=options_for(state)
        if not args.sample and not args.once and not opts['features']['weekly_cards']:
            raise GameError('Weekly visual cards are off. Ask the student to opt in first, or use --once after a direct request.')
        data=snapshot(state,iso_day(args.today))
        args.out.parent.mkdir(parents=True,exist_ok=True)
        player=None if name==DEFAULT_PROFILE else name
        args.out.write_text(create_svg(data,opts,args.theme,args.today,player),encoding='utf-8')
        result={'card_path':str(args.out),'visual_theme':args.theme or opts['card_theme'],
                'segment':data['segment'],'format':'SVG','no_image_generation_used':True,
                'message':'Private card created. Do not automatically share; ask before sending to anyone else.'}
        if args.png:
            png=args.out.with_suffix('.png')
            try:
                result.update(png_path=str(png),png_renderer=to_png(args.out,png))
            except GameError as e:
                result.update(png_path=None,png_error=str(e))
        print(json.dumps(result))
        return 0
    except (OSError,GameError,ValueError) as e:
        print(str(e),file=sys.stderr)
        return 2

if __name__=='__main__':sys.exit(main())
