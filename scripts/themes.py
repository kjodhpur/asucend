"""Original genre-inspired styles; no third-party game logos, characters or assets.
Each theme is a palette plus a hand-drawn scene in assets/cards/scenes/<theme>.svg.
"""
import re

SANS = "Oswald,'Avenir Next Condensed','Arial Narrow','Helvetica Neue',Arial,sans-serif"
ROUND = "Nunito,'Arial Rounded MT Bold','Chalkboard SE','Trebuchet MS',sans-serif"
THEMES = {
    # 13+ player-card themes
    'neon': {'label':'Neon Runner', 'background':'#0B0620', 'panel':'#140B33', 'edge':'#B26BFF', 'accent':'#38F9FF', 'accent2':'#FF3DCB', 'highlight':'#FFE66D', 'text':'#F4F1FF', 'muted':'#C9C2EE', 'font':SANS, 'eyebrow':'MISSION STATUS', 'tag':'POWER UP IRL', 'decor':'grid'},
    'fantasy': {'label':'Arcane Quest', 'background':'#120F22', 'panel':'#1E1830', 'edge':'#C9A15E', 'accent':'#F7D591', 'accent2':'#A889EE', 'highlight':'#FFB86B', 'text':'#FBF4E4', 'muted':'#D8C9A8', 'font':"Cinzel,Palatino,'Palatino Linotype',Georgia,serif", 'eyebrow':'ADVENTURER RECORD', 'tag':'THE JOURNEY CONTINUES', 'decor':'runes'},
    'retro': {'label':'Pixel Adventure', 'background':'#0E1A2B', 'panel':'#13243A', 'edge':'#65D9A4', 'accent':'#F4DF69', 'accent2':'#5CF7C8', 'highlight':'#FF6B6B', 'text':'#F2F6FF', 'muted':'#A9C3D9', 'font':"'Space Mono',Menlo,'Courier New',monospace", 'eyebrow':'STAGE CLEAR', 'tag':'PRESS START IRL', 'decor':'pixels'},
    'anime': {'label':'Anime Adventure', 'background':'#1D1433', 'panel':'#261A47', 'edge':'#F895D5', 'accent':'#FCB3E7', 'accent2':'#8AE8FF', 'highlight':'#FFE08A', 'text':'#FFF6FC', 'muted':'#E2CFEA', 'font':"Nunito,'Avenir Next','Trebuchet MS',sans-serif", 'eyebrow':'CHAPTER PROGRESS', 'tag':'A NEW CHAPTER BEGINS', 'decor':'stars'},
    'cozy': {'label':'Cozy Wanderer', 'background':'#14261F', 'panel':'#1D3329', 'edge':'#E5BC89', 'accent':'#F4DAAD', 'accent2':'#A1DFC6', 'highlight':'#FFB38A', 'text':'#FFF8EC', 'muted':'#D9CDB4', 'font':"Alegreya,Georgia,'Baskerville',serif", 'eyebrow':'MY LITTLE JOURNEY', 'tag':'GROW AT YOUR PACE', 'decor':'dots'},
    'scifi': {'label':'Starfleet Pathfinder', 'background':'#04121F', 'panel':'#0A2236', 'edge':'#47CFDC', 'accent':'#73F9EA', 'accent2':'#E1A9FF', 'highlight':'#FFC861', 'text':'#EAFBFF', 'muted':'#A7CCD8', 'font':"Oswald,Futura,'Avenir Next Condensed','Arial Narrow',sans-serif", 'eyebrow':'CAPTAIN LOG', 'tag':'NEXT MISSION READY', 'decor':'orbits'},
    # Kid themes (6-12), chosen by the child, never assigned by gender
    'dinos': {'label':'Dino Valley', 'background':'#173B2C', 'panel':'#FFFFFF', 'edge':'#2E8B57', 'accent':'#3FBF6F', 'accent2':'#FF9F43', 'highlight':'#FFD23F', 'text':'#1E3328', 'muted':'#4E6B5C', 'font':ROUND, 'eyebrow':'DINO QUEST', 'tag':'ROAR-SOME WORK', 'decor':'hills'},
    'space': {'label':'Rocket Crew', 'background':'#141A4A', 'panel':'#FFFFFF', 'edge':'#5B6CFF', 'accent':'#5B6CFF', 'accent2':'#FF6FB5', 'highlight':'#FFD23F', 'text':'#1C2050', 'muted':'#575C8F', 'font':ROUND, 'eyebrow':'SPACE QUEST', 'tag':'TO THE STARS', 'decor':'planets'},
    'unicorn': {'label':'Rainbow Meadow', 'background':'#5B3E96', 'panel':'#FFFFFF', 'edge':'#B884FF', 'accent':'#B05CFF', 'accent2':'#FF7EB6', 'highlight':'#FFC93C', 'text':'#3A2366', 'muted':'#6F5A94', 'font':ROUND, 'eyebrow':'MAGIC QUEST', 'tag':'SPARKLE ON', 'decor':'rainbow'},
    'robots': {'label':'Robot Lab', 'background':'#12303F', 'panel':'#FFFFFF', 'edge':'#1FB5C9', 'accent':'#1FB5C9', 'accent2':'#FF7A45', 'highlight':'#FFD23F', 'text':'#12303F', 'muted':'#4D6A78', 'font':ROUND, 'eyebrow':'ROBOT QUEST', 'tag':'BEEP BOOP, GREAT JOB', 'decor':'gears'},
}
PLAYER_THEMES = ('neon', 'fantasy', 'retro', 'anime', 'cozy', 'scifi')
KID_THEMES = ('dinos', 'space', 'unicorn', 'robots')
# Which card layout and themes each age segment gets (see xp.SEGMENTS).
SEGMENT_CARDS = {
    'college': {'layout':'player', 'themes':PLAYER_THEMES+('custom',), 'default':'neon'},
    'teen': {'layout':'player', 'themes':PLAYER_THEMES+('custom',), 'default':'neon'},
    'junior': {'layout':'junior', 'themes':KID_THEMES, 'default':'space'},
    'little': {'layout':'little', 'themes':KID_THEMES, 'default':'dinos'},
}
FEATURES = ('progression','storylines','calendar_matching','reminders','weekly_checkins','weekly_cards','visual_medals','photo_evidence')
MODES = ('off','light','immersive')
COLOR = re.compile(r'^#[0-9a-fA-F]{6}$')

def default_options(segment='college'):
    return {'voice_mode':'off', 'world':'', 'voice_archetype':'', 'card_theme':SEGMENT_CARDS[segment]['default'],
            'custom_colors':{}, 'features':{f:False for f in FEATURES}}

def options_for(state):
    segment=state.get('segment','college')
    old = state.get('preferences',{})
    result=default_options(segment)
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
    if result['card_theme'] not in SEGMENT_CARDS[segment]['themes']:
        result['card_theme']=SEGMENT_CARDS[segment]['default']
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
        custom=options.get('custom_colors',{})
        for k,v in custom.items():
            if k in ('background','accent','accent2') and isinstance(v,str) and COLOR.fullmatch(v):
                result[k]=v.upper()
    return result
