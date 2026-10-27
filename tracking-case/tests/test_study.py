import unittest
from study import study,truth,interpolate,edge_error
class Tests(unittest.TestCase):
 def test_anchors_exact(self):
  for n in (0,5,10): self.assertEqual(interpolate(n,(0,5,10)),truth(n))
 def test_add_middle_anchor_improves_synthetic_mean(self):
  r=study()
  a=sum(x['max_edge_error_px'] for x in r if x['strategy']=='two_anchors')
  b=sum(x['max_edge_error_px'] for x in r if x['strategy']=='three_anchors')
  self.assertLess(b,a)
 def test_error_symmetric_and_zero(self):
  self.assertEqual(edge_error((1,4),(1,4)),0)
  self.assertEqual(edge_error((1,4),(2,7)),edge_error((2,7),(1,4)))
if __name__=='__main__':unittest.main()
