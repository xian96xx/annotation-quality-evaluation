import unittest
from public_geometry import geometry
class TestPublicGeometry(unittest.TestCase):
 def test_geometry(self):
  self.assertEqual(geometry([[10,10,20,20]]),[])
  self.assertEqual(geometry([[-1,10,20,20]]),[(0,'out_of_bounds')])
  self.assertEqual(geometry([[1,1,0,2]]),[(0,'invalid_geometry')])
if __name__=='__main__':unittest.main()
