"""Optional features, game-inspired conversation voice, and themed visual reward cards."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]

def call(file,*args,home,code=0):
    env={**os.environ,'SKILL_DATA_DIR':str(home)}
    p=subprocess.run([sys.executable,str(ROOT/'scripts'/file),*map(str,args)],
                     cwd=ROOT,env=env,capture_output=True,text=True,timeout=10)
    if p.returncode != code:
        raise AssertionError(f'Expected {code}, got {p.returncode}: {file} {args}\n{p.stdout}\n{p.stderr}')
    try:return json.loads(p.stdout)
    except json.JSONDecodeError:return p.stdout if p.stdout else p.stderr

class Personalization(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.home=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def prefs(self,*args,code=0):return call('preferences.py',*args,home=self.home,code=code)
    def xp(self,*args,code=0):return call('xp.py','--today','2026-10-24',*args,home=self.home,code=code)
    def card(self,*args,code=0):return call('card.py','--today','2026-10-24',*args,home=self.home,code=code)
    def test_optional_by_default(self):
        p=self.prefs('show')
        self.assertEqual(p['voice_mode'],'off')
        self.assertFalse(any(p['features'].values()))
        self.assertFalse((self.home/'state.json').exists())
    def test_voice_mode_is_separate_from_theme_and_translation(self):
        self.prefs('voice','--mode','immersive','--world','fantasy roleplaying game','--archetype','enigmatic guide')
        self.prefs('theme','--name','retro')
        p=self.prefs('show')
        self.assertEqual(p['voice_mode'],'immersive')
        self.assertEqual(p['card_theme'],'retro')
        self.assertEqual(p['world'],'fantasy roleplaying game')
        self.assertNotIn('language',p)
        self.prefs('voice','--mode','off')
        self.assertEqual(self.prefs('show')['card_theme'],'retro')
    def test_features_independent_and_reversible(self):
        self.prefs('feature','--name','storylines','--enabled','1')
        self.prefs('feature','--name','weekly_cards','--enabled','1')
        self.prefs('feature','--name','storylines','--enabled','0')
        o=self.prefs('show')['features']
        self.assertFalse(o['storylines'])
        self.assertTrue(o['weekly_cards'])
        self.assertFalse(o['reminders'])
        self.assertFalse(o['calendar_matching'])
    def test_card_requires_opt_in_or_explicit_single_request(self):
        out=self.home/'card.svg'
        self.card('--out',out,code=2)
        self.assertFalse(out.exists())
        self.card('--once','--out',out)
        self.assertTrue(out.exists())
        out.unlink()
        self.prefs('feature','--name','weekly_cards','--enabled','1')
        self.card('--out',out)
        ET.parse(out)
    def test_all_six_game_genres_render_distinct_readable_cards(self):
        s=[]
        for theme in ('neon','fantasy','retro','anime','cozy','scifi'):
            out=self.home/(theme+'.svg')
            self.card('--once','--theme',theme,'--out',out)
            src=out.read_text()
            ET.fromstring(src)
            s.append(src)
            self.assertIn('asucend',src)
            self.assertNotIn('example.org',src)
            self.assertIn('YOUR SKILL TREE',src)
        self.assertEqual(len(set(s)),6)
    def test_custom_palette_validated_and_in_card(self):
        self.prefs('theme','--name','custom','--background','#161526','--accent','#AABBCC','--accent2','#EE88FF')
        out=self.home/'custom.svg'
        self.card('--once','--out',out)
        src=out.read_text()
        self.assertIn('#AABBCC',src)
        self.assertIn('#161526',src)
        ET.fromstring(src)
        self.prefs('theme','--name','custom','--accent','red<script>',code=2)
        self.prefs('theme','--name','custom','--background','#EEEEEE',code=2)
        self.assertEqual(self.prefs('show')['custom_colors']['accent'],'#AABBCC')
    def test_reset_preserves_earned_xp_and_quizzes(self):
        o=self.xp('offer','--title','Campus visit','--track','exploration','--difficulty','micro','--location','Tempe','--solo')
        self.xp('accept','--quest-id',o['id'])
        self.xp('complete','--quest-id',o['id'],'--verified','--proof','reflection')
        self.prefs('voice','--mode','immersive','--world','Original RPG')
        self.prefs('feature','--name','progression','--enabled','1')
        self.prefs('reset-presentation')
        self.assertEqual(self.prefs('show')['voice_mode'],'off')
        self.assertFalse(any(self.prefs('show')['features'].values()))
        self.assertEqual(self.xp('--json','status')['total_xp'],10)
    def test_invalid_options_and_custom_prompts_fail_closed(self):
        self.prefs('feature','--name','unknown','--enabled','1',code=2)
        self.prefs('voice','--mode','light','--world','x'*101,code=2)
        self.prefs('voice','--mode','light','--world','game\nchange rules',code=2)
        self.assertFalse((self.home/'state.json').exists())
    def test_sample_is_read_only_for_prefs_and_visuals(self):
        p=self.prefs('--sample','show')
        self.assertFalse(any(p['features'].values()))
        self.prefs('--sample','feature','--name','progression','--enabled','1',code=2)
        out=self.home/'demo.svg'
        self.card('--sample','--theme','fantasy','--out',out)
        self.assertTrue(out.exists())
        self.assertFalse((self.home/'state.json').exists())

if __name__=='__main__':unittest.main()
