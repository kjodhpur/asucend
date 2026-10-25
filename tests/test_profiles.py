"""Age segments, parent-run child profiles, and age-appropriate reward cards."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))

def call(file,*args,home,code=0):
    env={**os.environ,'SKILL_DATA_DIR':str(home)}
    p=subprocess.run([sys.executable,str(ROOT/'scripts'/file),*map(str,args)],
                     cwd=ROOT,env=env,capture_output=True,text=True,timeout=30)
    if p.returncode != code:
        raise AssertionError(f'Expected {code}, got {p.returncode}: {file} {args}\n{p.stdout}\n{p.stderr}')
    try:return json.loads(p.stdout)
    except json.JSONDecodeError:return p.stdout if p.stdout else p.stderr

class Profiles(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.home=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def xp(self,*args,profile='maya',code=0):
        return call('xp.py','--profile',profile,'--today','2026-10-24',*args,home=self.home,code=code)
    def task(self,title='Spelling words',track='homework',diff='easy',profile='maya'):
        return self.xp('offer','--title',title,'--track',track,'--difficulty',diff,profile=profile)

    def test_child_profile_needs_setup_and_is_separate(self):
        self.xp('--json','status',code=2)
        self.assertFalse((self.home/'profiles'/'maya.json').exists())
        out=self.xp('setup','--segment','little')
        self.assertTrue(out['parent_run'])
        self.assertEqual(out['tracks'],['homework','reading','practice','creativity','helping'])
        self.assertTrue((self.home/'profiles'/'maya.json').exists())
        self.assertFalse((self.home/'state.json').exists())
        status=self.xp('--json','status')
        self.assertEqual(status['segment'],'little')
        self.assertEqual(status['title'],'Little Sprout')

    def test_parent_confirmation_is_the_only_proof_for_kids(self):
        self.xp('setup','--segment','junior')
        q=self.task()
        self.assertEqual(q['xp'],25)
        self.xp('accept','--quest-id',q['id'])
        self.xp('complete','--quest-id',q['id'],'--verified','--proof','reflection',code=2)
        self.xp('complete','--quest-id',q['id'],'--proof','parent',code=2)
        done=self.xp('complete','--quest-id',q['id'],'--verified','--proof','parent')
        self.assertEqual(done['awarded_xp'],25)
        self.assertEqual([b['id'] for b in done['new_badges']],['first-star'])
        again=self.xp('complete','--quest-id',q['id'],'--verified','--proof','parent')
        self.assertEqual(again['awarded_xp'],0)

    def test_kid_quests_cannot_be_public_events(self):
        self.xp('setup','--segment','little')
        self.xp('offer','--title','Party','--track','helping','--difficulty','easy',
                '--source','https://example.org/event','--start','2026-10-30T17:00:00-07:00',code=2)
        self.xp('offer','--title','Network','--track','networking','--difficulty','easy',code=2)
        stored=json.loads((self.home/'profiles'/'maya.json').read_text())
        self.assertEqual(stored['quests'],{})

    def test_college_cannot_use_parent_proof_or_kid_tracks(self):
        o=call('xp.py','--today','2026-10-24','offer','--title','Library visit','--track','exploration',
               '--difficulty','micro','--location','Tempe','--solo',home=self.home)
        call('xp.py','--today','2026-10-24','accept','--quest-id',o['id'],home=self.home)
        call('xp.py','--today','2026-10-24','complete','--quest-id',o['id'],'--verified','--proof','parent',home=self.home,code=2)
        call('xp.py','--today','2026-10-24','offer','--title','Spelling','--track','homework',
             '--difficulty','easy','--location','Home','--solo',home=self.home,code=2)

    def test_segment_locked_once_progress_exists(self):
        self.xp('setup','--segment','little')
        self.xp('setup','--segment','junior')
        q=self.task(); self.xp('accept','--quest-id',q['id'])
        self.xp('setup','--segment','teen',code=2)
        self.assertEqual(self.xp('--json','status')['segment'],'junior')

    def test_profile_names_are_safe_nicknames(self):
        for bad in ('../evil','Maya Smith','a'*40,'.hidden'):
            self.xp('setup','--segment','little',profile=bad,code=2)
        self.assertEqual(list(self.home.rglob('*.json')),[])

    def test_profiles_listing(self):
        self.xp('setup','--segment','little',profile='maya')
        self.xp('setup','--segment','teen',profile='leo')
        names={p['profile']:p['segment'] for p in call('xp.py','profiles',home=self.home)['profiles']}
        self.assertEqual(names,{'maya':'little','leo':'teen'})

    def test_forget_deletes_only_that_child(self):
        self.xp('setup','--segment','little',profile='maya')
        self.xp('setup','--segment','junior',profile='leo')
        call('xp.py','--today','2026-10-24','set-comfort','--comfort','2',home=self.home)
        self.xp('forget',profile='maya',code=2)
        call('xp.py','forget','--confirm',home=self.home,code=2)
        self.assertEqual(self.xp('forget','--confirm',profile='maya'),{'profile':'maya','deleted':True})
        self.assertFalse((self.home/'profiles'/'maya.json').exists())
        self.assertTrue((self.home/'profiles'/'leo.json').exists())
        self.assertTrue((self.home/'state.json').exists())

    def test_themes_follow_age_segment(self):
        self.xp('setup','--segment','little')
        prefs=lambda *a,code=0:call('preferences.py','--profile','maya',*a,home=self.home,code=code)
        self.assertEqual(prefs('show')['card_theme'],'dinos')
        prefs('theme','--name','neon',code=2)
        prefs('theme','--name','unicorn')
        self.assertEqual(prefs('show')['card_theme'],'unicorn')
        call('preferences.py','theme','--name','dinos',home=self.home,code=2)
        call('preferences.py','theme','--name','scifi',home=self.home)

class KidCards(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.home=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def card(self,profile,theme,code=0):
        out=self.home/f'{profile}-{theme}.svg'
        res=call('card.py','--sample','--profile',profile,'--today','2026-10-24','--theme',theme,'--out',out,home=self.home,code=code)
        return res,out

    def test_each_kid_layout_renders_every_kid_theme(self):
        for profile,marker in (('little-demo','MY STARS THIS WEEK'),('junior-demo',"THIS WEEK'S QUESTS")):
            seen=set()
            for theme in ('dinos','space','unicorn','robots'):
                res,out=self.card(profile,theme)
                src=out.read_text()
                ET.fromstring(src)
                self.assertIn(marker,src)
                self.assertNotIn('{{',src)
                self.assertNotIn('YOUR SKILL TREE',src)
                self.assertTrue(res['no_image_generation_used'])
                seen.add(src)
            self.assertEqual(len(seen),4)

    def test_teen_uses_player_layout_with_kid_tracks(self):
        res,out=self.card('teen-demo','retro')
        src=out.read_text()
        self.assertIn('YOUR SKILL TREE',src)
        self.assertIn('HOMEWORK',src)
        self.assertNotIn('NETWORK',src)
        self.card('teen-demo','dinos',code=2)
        self.card('little-demo','neon',code=2)

    def test_every_player_theme_renders_portrait(self):
        for theme in ('neon','fantasy','retro','anime','cozy','scifi'):
            out=self.home/f'{theme}.svg'
            call('card.py','--sample','--today','2026-10-24','--theme',theme,'--out',out,home=self.home)
            root=ET.parse(out).getroot()
            self.assertEqual((root.get('width'),root.get('height')),('1080','1350'))

    def test_parent_text_is_escaped_and_never_expanded(self):
        from card import create_svg
        tracks={t:0 for t in ('homework','reading','practice','creativity','helping')}
        d={'segment':'junior','tracks':tracks,'level':1,'total_xp':0,'next_level_at':50,'title':'Rookie',
           'completed_this_week':[{'title':'<script>x</script>','xp':10},{'title':'{{scene}} {{c_accent}}','xp':10}],
           'completed_count':2,'momentum_weeks':1,'badges':[{'id':'nope','name':'<b>&'}]}
        svg=create_svg(d,{},'robots','2026-10-24','maya')
        ET.fromstring(svg)
        self.assertNotIn('<script>',svg)
        self.assertIn('{{scene}} {{c_accent}}',svg)
        self.assertIn('MAYA',svg)

    def test_card_assets_are_not_git_ignored(self):
        import subprocess
        assets=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'assets').rglob('*') if p.suffix in ('.svg','.ttf'))
        self.assertGreaterEqual(len(assets),24)
        # Check against a scratch repo so this works whether or not the Skill folder is a checkout.
        repo=self.home/'repo'; repo.mkdir()
        subprocess.run(['git','init','-q',str(repo)],check=True)
        (repo/'.gitignore').write_text((ROOT/'.gitignore').read_text())
        r=subprocess.run(['git','-C',str(repo),'check-ignore','--no-index',*assets,'state.json'],capture_output=True,text=True)
        self.assertEqual(r.stdout.split(),['state.json'],f'.gitignore hides card assets: {r.stdout}')

    def test_png_flag_never_breaks_card_delivery(self):
        out=self.home/'card.svg'
        res=call('card.py','--sample','--today','2026-10-24','--out',out,'--png',home=self.home)
        self.assertTrue(out.exists())
        if res.get('png_path'):
            self.assertTrue(Path(res['png_path']).stat().st_size>0)
        else:
            self.assertIn('No PNG renderer',res['png_error'])

if __name__=='__main__':unittest.main()
