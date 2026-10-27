import unittest
from demo import demo_sequence,inspect
class TestDemo(unittest.TestCase):
 def test_injected_events(self):
  actual={(i,k) for i,k,_ in inspect(demo_sequence())}
  self.assertEqual(actual,{(2,'out_of_bounds'),(5,'large_jump'),(6,'large_jump'),(8,'invalid_geometry')})
 def test_clean_sequence(self):
  self.assertEqual(inspect([[10+i,10,20+i,20] for i in range(10)]),[])
 def test_invalid_breaks_comparison(self):
  self.assertEqual([k for _,k,_ in inspect([[10,10,20,20],[0,0,0,3],[500,10,510,20]])],['invalid_geometry'])
 def test_boundary_inclusive(self):
  self.assertEqual(inspect([[0,0,640,360]]),[])
if __name__=='__main__':unittest.main()
