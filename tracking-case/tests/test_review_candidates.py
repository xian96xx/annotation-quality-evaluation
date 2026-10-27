import unittest
from review_candidates import candidates

class CandidateTests(unittest.TestCase):
 def test_hypothesis_and_anchor_exclusion(self):
  anchors={0:[100,100,200,200],2:[100,100,200,200]}
  frames=[{'index':0,'bbox':anchors[0]},{'index':1,'bbox':[100,100,200,180]},{'index':2,'bbox':anchors[2]}]
  out=candidates(frames,anchors,1000,1000)
  self.assertEqual([x['status'] for x in out],['skipped','review','skipped'])
  self.assertIn('occlusion_unknown',out[1]['reason'])
 def test_explicit_occlusion_and_edge_are_skipped(self):
  anchors={0:[100,100,200,200],3:[100,100,200,200]}
  frames=[{'index':1,'bbox':[100,100,200,180],'occluded':True},{'index':2,'bbox':[0,100,90,180]}]
  self.assertEqual([r['reason'] for r in candidates(frames,anchors,1000,1000)],['known_occlusion','near_edge'])
 def test_missing_and_bad_indexes(self):
  a={0:[100,100,200,200],3:[100,100,200,200]}
  self.assertEqual(candidates([{'index':1,'bbox':None}],a,1000,1000)[0]['reason'],'missing_or_invalid_box')
  with self.assertRaises(ValueError):candidates([{'index':1,'bbox':None},{'index':1,'bbox':None}],a,1000,1000)
 def test_benign_perspective_change_can_trigger_candidate(self):
  # True target contracts as its pose or distance changes; this is not proof of a label error.
  anchors={0:[100,100,200,200],2:[100,100,200,200]}
  out=candidates([{'index':1,'bbox':[110,110,190,190],'occluded':False}],anchors,1000,1000)
  self.assertEqual(out[0]['status'],'review')
if __name__=='__main__':unittest.main()
