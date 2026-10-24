"""ASUcend regression and integration checks. No external accounts/network required."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
PY=sys.executable

def invoke(file, *args, home=None, expected=0):
    env=os.environ.copy()
    if home:
        env['SKILL_DATA_DIR']=str(home)
    proc=subprocess.run([PY,str(ROOT/'scripts'/file),*map(str,args)],text=True,
                        capture_output=True,env=env, cwd=ROOT)
    if proc.returncode!=expected:
        raise AssertionError(f'Command failed ({proc.returncode} != {expected}): {proc.args}\nOUT: {proc.stdout}\nERR: {proc.stderr}')
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.stdout

class GameFlow(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.home=Path(self.tmp.name)
        self.date='2026-10-24'
    def tearDown(self):self.tmp.cleanup()
    def x(self, *parts, expected=0):
        return invoke('xp.py','--today',self.date,*parts,home=self.home,expected=expected)
    def offer(self,track='networking',diff='easy',title='AI workshop',start='2026-10-30T13:30:00-07:00'):
        return self.x('offer','--title',title,'--track',track,'--difficulty',diff,
          '--location','Tempe','--start',start,'--source','https://asu.edu/verified-event-demo')
    def test_end_to_end_persists_and_levels_up(self):
        a=self.offer(diff='standard'); ident=a['id']
        self.assertEqual(a['xp'],50)
        self.x('accept','--quest-id',ident)
        before=self.x('--json','status')
        self.assertEqual(before['total_xp'],0)
        result=self.x('complete','--quest-id',ident,'--verified','--proof','reflection')
        self.assertEqual(result['awarded_xp'],50)
        self.assertEqual(result['level'],2)
        self.assertTrue(result['leveled_up'])
        self.assertEqual([x['id'] for x in result['new_badges']], ['first-spark','first-contact'])
        persisted=self.x('--json','status')
        self.assertEqual(persisted['completed_count'],1)
        self.assertEqual(persisted['tracks']['networking'],50)
        self.assertEqual(persisted['momentum_weeks'],1)
    def test_double_completion_does_not_duplicate_xp(self):
        ident=self.offer()['id'];self.x('accept','--quest-id',ident)
        self.x('complete','--quest-id',ident,'--verified','--proof','photo')
        again=self.x('complete','--quest-id',ident,'--verified','--proof','photo')
        self.assertEqual(again['awarded_xp'],0)
        self.assertEqual(self.x('--json','status')['total_xp'],25)
    def test_proof_required_and_accept_required(self):
        ident=self.offer()['id']
        invoke('xp.py','--today',self.date,'complete','--quest-id',ident,
               '--verified','--proof','photo',home=self.home,expected=2)
        self.x('accept','--quest-id',ident)
        invoke('xp.py','--today',self.date,'complete','--quest-id',ident,home=self.home,expected=2)
        self.assertEqual(self.x('--json','status')['total_xp'],0)
    def test_unverified_not_counted(self):
        ident=self.offer()['id'];self.x('accept','--quest-id',ident)
        invoke('xp.py','--today',self.date,'complete','--quest-id',ident,'--proof','photo',home=self.home,expected=2)
        self.assertEqual(self.x('--json','status')['total_xp'],0)
    def test_skipping_no_penalty_and_cannot_complete(self):
        ident=self.offer()['id'];self.x('accept','--quest-id',ident)
        out=self.x('skip','--quest-id',ident)
        self.assertEqual(out['lost_xp'],0)
        invoke('xp.py','--today',self.date,'complete','--quest-id',ident,'--verified','--proof','reflection',
                 home=self.home,expected=2)
    def test_deterministic_quest_id_and_separate_dates(self):
        first=self.offer();dup=self.offer(); later=self.offer(start='2026-11-06T13:30:00-07:00')
        self.assertEqual(first['id'],dup['id']);self.assertTrue(dup['already_exists'])
        self.assertNotEqual(first['id'],later['id'])
    def test_solo_and_comfort(self):
        o=self.x('offer','--title','Visit a campus library','--track','exploration','--difficulty','micro',
                 '--location','Tempe','--solo'); self.assertEqual(o['xp'],10)
        self.x('set-comfort','--comfort','1')
        self.assertEqual(self.x('--json','status')['comfort'],1)
        self.x('accept','--quest-id',o['id'])
        self.x('complete','--quest-id',o['id'],'--verified','--proof','reflection')
        self.assertEqual(self.x('--json','status')['total_xp'],10)
    def test_invalid_source_and_xp_cannot_be_forged(self):
        invoke('xp.py','--today',self.date,'offer','--title','Fake','--track','career',
             '--difficulty','boss','--location','Tempe','--start','2026-10-29T12:00:00-07:00',
             '--source','http://fake.org',home=self.home,expected=2)
        invoke('xp.py','--today',self.date,'offer','--title','Fake','--track','career',
             '--difficulty','superboss','--location','Tempe','--start','2026-10-29T12:00:00-07:00',
             '--source','https://fake.org',home=self.home,expected=2)
        self.assertEqual(self.x('--json','status')['total_xp'],0)
    def test_state_corruption_does_not_reset(self):
        p=self.home/'state.json'; p.write_text('{broken')
        invoke('xp.py','--today',self.date,'status',home=self.home,expected=4)
        self.assertEqual(p.read_text(),'{broken')
    def test_legacy_state_migrates_without_discarding_xp(self):
        legacy={'tracks':{'networking':80,'career':40,'academic':25,'wellness':15,'exploration':55},
                'quests_done':[{'quest':'Original quest','track':'networking','xp':50,'date':'2026-10-20'}],
                'quests_skipped':[],'comfort':2,'updated':None}
        (self.home/'state.json').write_text(json.dumps(legacy))
        self.assertEqual(self.x('--json','status')['total_xp'],215)
        self.offer()
        state=json.loads((self.home/'state.json').read_text())
        self.assertEqual(state['tracks']['networking'],80)
        self.assertEqual(state['quests_done'][0]['quest'],'Original quest')
        self.assertEqual(state['schema_version'],2)
    def test_easy_mode_and_adaptation(self):
        self.x('easier','--on','1')
        self.assertIn('gentler',self.x('recommend')['recommended_difficulty'])
        self.x('easier','--on','0')
        self.assertIn('steady',self.x('recommend')['recommended_difficulty'])
    def test_badge_unlocks_are_unique_and_boss_rewards_fixed(self):
        ids=[]
        for n,(track,diff) in enumerate((('networking','brave'),('career','boss'),
                                         ('academic','easy'),('wellness','easy'),('exploration','easy'))):
            ident=self.offer(track=track,diff=diff,title=f'Unique quest {n}')['id']
            self.x('accept','--quest-id',ident)
            self.x('complete','--quest-id',ident,'--verified','--proof','reflection')
            ids.append(ident)
        snap=self.x('--json','status')
        self.assertEqual(snap['total_xp'],75+100+25+25+25)
        badge_ids=[b['id'] for b in snap['badges']]
        self.assertIn('balanced-hero',badge_ids)
        self.assertIn('boss-slayer',badge_ids)
        self.assertIn('courage-rising',badge_ids)
        self.assertEqual(len(badge_ids),len(set(badge_ids)))
    def test_concurrent_completion_is_idempotent(self):
        ident=self.offer(diff='standard')['id'];self.x('accept','--quest-id',ident)
        cmd=[PY,str(ROOT/'scripts/xp.py'),'--today',self.date,'complete','--quest-id',ident,
             '--verified','--proof','reflection']
        env=os.environ.copy();env['SKILL_DATA_DIR']=str(self.home)
        p1=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
        p2=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
        out1,err1=p1.communicate(timeout=10)
        out2,err2=p2.communicate(timeout=10)
        self.assertEqual((p1.returncode,p2.returncode),(0,0),err1+err2)
        outcomes=[json.loads(out1),json.loads(out2)]
        self.assertEqual(sorted(v['awarded_xp'] for v in outcomes),[0,50])
        self.assertEqual(self.x('--json','status')['total_xp'],50)
    def test_read_only_sample_does_not_write_real_state(self):
        r=invoke('xp.py','--sample','--today',self.date,'--json','status',home=self.home)
        self.assertEqual(r['total_xp'],215)
        invoke('xp.py','--sample','--today',self.date,'set-comfort','--comfort','5',home=self.home,expected=2)
        self.assertFalse((self.home/'state.json').exists())

class Planning(unittest.TestCase):
    def test_calendar_conflicts_free_windows_and_budget(self):
        o=invoke('plan.py','--sample')
        self.assertEqual(len(o['suggestions']),1)
        self.assertIn('Small AI workshop',o['suggestions'][0]['name'])
        reasons={r['reason'] for r in o['rejected']}
        self.assertIn('calendar conflict including travel buffer',reasons)
        self.assertIn('price unknown or exceeds budget',reasons)
    def test_calendar_unknown_does_not_claim_confirmed(self):
        src=json.loads((ROOT/'assets/sample_candidates.json').read_text())
        src['busy']=[];src['free']=[]
        with tempfile.TemporaryDirectory() as tmp:
            inp=Path(tmp)/'input.json';inp.write_text(json.dumps(src))
            o=invoke('plan.py','--input',inp)
        self.assertEqual(o['suggestions'][0]['availability_basis'], 'unknown')
    def test_missing_source_rejected(self):
        src=json.loads((ROOT/'assets/sample_candidates.json').read_text())
        src['events'][0]['source_url']='file:///private'
        with tempfile.TemporaryDirectory() as tmp:
            inp=Path(tmp)/'input.json';inp.write_text(json.dumps(src))
            o=invoke('plan.py','--input',inp)
        self.assertNotIn('Small AI workshop',str(o['suggestions']))

class Cards(unittest.TestCase):
    def test_svg_is_valid_and_source_free(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'weekly.svg'
            result=invoke('card.py','--sample','--today','2026-10-24','--out',out)
            self.assertTrue(result['no_image_generation_used'])
            ET.parse(out)
            data=out.read_text()
            self.assertIn('ASUCEND',data)
            self.assertIn('MISSION STATUS',data)
            self.assertNotIn('example.org',data)
    def test_svg_escapes_badge_names(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        from card import create_svg
        d={'tracks':{t:0 for t in ('networking','career','academic','wellness','exploration')},
           'level':1,'total_xp':0,'next_level_at':50,'title':'<script>oops</script>',
           'completed_this_week':[],'completed_count':0,'momentum_weeks':0,
           'badges':[{'name':'<unsafe>&'}]}
        svg=create_svg(d)
        ET.fromstring(svg)
        self.assertIn('&lt;unsafe&gt;&amp;',svg)
        self.assertNotIn('<script>',svg)

if __name__=='__main__':unittest.main()
