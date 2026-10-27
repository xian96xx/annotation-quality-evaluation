import unittest
from public_study import parse_boxes,compare,iou
class PublicStudyTests(unittest.TestCase):
 def test_compare_same_target_is_perfect(self):
  a=[(1.,2.,6.,7.)]*5
  self.assertEqual([r['iou'] for r in compare(a)],[1,1,1,1])
 def test_iou_and_invalid_file(self):
  self.assertEqual(iou((0,0,2,2),(0,0,1,1)),0.25)
  with self.assertRaises(ValueError):parse_boxes(b'1,2,0,4\n')
if __name__=='__main__':unittest.main()
