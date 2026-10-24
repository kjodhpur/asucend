"""Original genre-inspired styles; no third-party game logos, characters or assets."""
import re

THEMES = {
    'neon': {'label':'Neon Runner', 'background':'#0F112A', 'panel':'#241B46', 'edge':'#9A69FF', 'accent':'#70E7FF', 'accent2':'#BB75FF', 'eyebrow':'MISSION STATUS', 'tag':'POWER UP IRL', 'decor':'grid'},
    'fantasy': {'label':'Arcane Quest', 'background':'#151326', 'panel':'#31243F', 'edge':'#D0A869', 'accent':'#F7D591', 'accent2':'#A889EE', 'eyebrow':'ADVENTURER RECORD', 'tag':'THE JOURNEY CONTINUES', 'decor':'runes'},
    'retro': {'label':'Pixel Adventure', 'background':'#101A24', 'panel':'#203544', 'edge':'#65D9A4', 'accent':'#F4DF69', 'accent2':'#5CF7C8', 'eyebrow':'STAGE CLEAR', 'tag':'PRESS START IRL', 'decor':'pixels'},
    'anime': {'label':'Anime Adventure', 'background':'#1D1433', 'panel':'#30265C', 'edge':'#F895D5', 'accent':'#FCB3E7', 'accent2':'#8AE8FF', 'eyebrow':'CHAPTER PROGRESS', 'tag':'A NEW CHAPTER BEGINS', 'decor':'stars'},
    'cozy': {'label':'Cozy Wanderer', 'background':'#172C2A', 'panel':'#28423C', 'edge':'#E5BC89', 'accent':'#F4DAAD', 'accent2':'#A1DFC6', 'eyebrow':'MY LITTLE JOURNEY', 'tag':'GROW AT YOUR PACE', 'decor':'dots'},
    'scifi': {'label':'Starfleet Pathfinder', 'background':'#0A2033', 'panel':'#153653', 'edge':'#47CFDC', 'accent':'#73F9EA', 'accent2':'#E1A9FF', 'eyebrow':'CAPTAIN LOG', 'tag':'NEXT MISSION READY', 'decor':'orbits'},
}
FEATURES = ('progression','storylines','calendar_matching','reminders','weekly_checkins','weekly_cards','visual_medals','photo_evidence')
MODES = ('off','light','immersive')
COLOR = re.compile(r'^#[0-9a-fA-F]{6}$')

def default_options():
    return {'voice_mode':'off', 'world':'', 'voice_archetype':'', 'card_theme':'neon',
            'custom_colors':{}, 'features':{f:False for f in FEATURES}}

def options_for(state):
    old = state.get('preferences',{})
    result=default_options()
    if not isinstance(old,dict):
        return result
    for field in ('voice_mode','world','voice_archetype','card_theme'):
        if isinstance(old.get(field),str):
            result[field]=old[field]
    if isinstance(old.get('custom_colors'),dict):
        result['custom_colors']={k:v for k,v in old['custom_colors'].items() if k in ('background','accent','accent2') and isinstance(v,str) and COLOR.fullmatch(v)}
    if isinstance(old.get('features'),dict):
        for key in FEATURES:
            if type(old['features'].get(key)) is bool:
                result['features'][key]=old['features'][key]
    if result['voice_mode'] not in MODES:result['voice_mode']='off'
    if result['card_theme'] not in (*THEMES,'custom'):result['card_theme']='neon'
    return result

def palette_for(options,override=None):
    theme=override or options.get('card_theme','neon')
    if theme not in (*THEMES,'custom'):
        raise ValueError('Unknown visual theme')
    result=dict(THEMES.get(theme,THEMES['neon']))
    if theme=='custom':
        result['label']='Custom World'
        result['eyebrow']='PLAYER RECORD'
        result['tag']='LEVEL UP IRL'
        result['decor']='stars'
        custom=options.get('custom_colors',{})
        for k,v in custom.items():
            if k in ('background','accent','accent2') and isinstance(v,str) and COLOR.fullmatch(v):
                result[k]=v.upper()
    return result
