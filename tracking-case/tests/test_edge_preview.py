import unittest
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from edge_preview import propose
class EdgePreviewTests(unittest.TestCase):
 def setUp(self):self.box=[100,100,200,200]
 def test_only_requested_edge_changes(self):
  p=propose(self.box,[95,105,190,190],'left_expand',1000,1000)
  self.assertEqual(p['box'],[95,100,200,200]);self.assertEqual(p['status'],'pending_human_review');self.assertEqual(self.box,[100,100,200,200])
 def test_top_shrink(self):
  self.assertEqual(propose(self.box,[99,108,199,199],'top_shrink',1000,1000)['box'],[100,108,200,200])
 def test_anchors_large_move_and_wrong_direction_rejected(self):
  with self.assertRaises(ValueError):propose(self.box,[95,100,200,200],'left_expand',1000,1000,is_anchor=True)
  with self.assertRaises(ValueError):propose(self.box,[50,100,200,200],'left_expand',1000,1000)
  with self.assertRaises(ValueError):propose(self.box,[100,95,200,200],'top_shrink',1000,1000)
 def test_anchor_status_must_be_boolean(self):
  with self.assertRaises(ValueError):propose(self.box,[95,100,200,200],'left_expand',1000,1000,is_anchor='false')
 def test_invalid_or_outside_is_rejected(self):
  with self.assertRaises(ValueError):propose(self.box,[-1,100,200,200],'left_expand',1000,1000)
  with self.assertRaises(ValueError):propose(self.box,[95,100,200,float('nan')],'left_expand',1000,1000)
 def test_limit_override_bounded(self):
  self.assertEqual(propose(self.box,[100,118,200,200],'top_shrink',1000,1000,max_fraction=.2)['delta_px'],18)
  with self.assertRaises(ValueError):propose(self.box,[100,118,200,200],'top_shrink',1000,1000,max_fraction=.21)
 def test_cli_never_overwrites_input_or_existing_output(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d); inp=p/'input.json';out=p/'output.json'
   data={'width':1000,'height':1000,'items':[{'frame':1,'original':self.box,'source':[95,100,200,200],'edge':'left_expand','is_anchor':False}]}
   inp.write_text(json.dumps(data),encoding='utf8');out.write_text('keep',encoding='utf8')
   script=Path(__file__).resolve().parents[1]/'edge_preview.py'
   before=inp.read_bytes()
   for target in (inp,out):
    run=subprocess.run([sys.executable,str(script),'--input',str(inp),'--out',str(target)],capture_output=True)
    self.assertNotEqual(run.returncode,0)
   self.assertEqual(inp.read_bytes(),before);self.assertEqual(out.read_text(encoding='utf8'),'keep')
if __name__=='__main__':unittest.main()
