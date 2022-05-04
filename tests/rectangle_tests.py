import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

import unittest

from pyrstar import rectangle as rct


class TestRectangleMethods(unittest.TestCase):
    def test_init(self):
        p1 = [0,1,1]
        p2 = [0,5,6]
        p3 = [1,2,2]
        p4 = [0,0]

        fullrect = rct.Rectangle(p1,p3)

        self.assertEqual([0,1,1],fullrect.minima)
        self.assertEqual([1,2,2],fullrect.maxima)

        pointrect = rct.Rectangle(p3,p3)
        self.assertTrue(pointrect.is_point)
        self.assertFalse(fullrect.is_point)


    def test_init_exceptions(self):
        p1 = [0,1,1]
        p2 = [0,5,6]
        p4 = [0,0]

        with self.assertRaises(ValueError):
            rct.Rectangle(p1,p4)

        with self.assertRaises(ValueError):
            rct.Rectangle(p1,p2)


    def test_equality_comparison(self):
        R1 = rct.Rectangle([1,1,1],[2,2,2])
        R2 = rct.Rectangle([1,1,1],[2,2,2])

        self.assertEqual(R1,R2)

        R3 = rct.Rectangle([1,1],[2,2])

        self.assertNotEqual(R1,R3)

        R4 = rct.Rectangle([1,1,1],[3,3,3])

        self.assertNotEqual(R1,R4)


    def test_volume(self):
        R1 = rct.Rectangle([-1,-1,-1],[0,0,0])
        self.assertEqual(1,R1.volume())


    def test_intersection(self):
        RA = rct.Rectangle([0,0,0],[2,2,2])
        RB = rct.Rectangle([0,0,0],[1,1,1])
        RC = rct.Rectangle([-1,-1,-1],[1,1,1])
        self.assertEqual(RB, RA.intersect(RC))


    def test_intersection_volume(self):
        RA = rct.Rectangle([0,0,0],[2,2,2])
        RC = rct.Rectangle([-1,-1,-1],[1,1,1])
        self.assertEqual(1, RA.intersection_volume(RC))


    def test_degenerate_intersection_is_empty(self):
        R1 = rct.Rectangle([0,0],[1,1])
        R2 = rct.Rectangle([1,0],[2,1])
        self.assertEqual(0, R1.intersection_volume(R2))


    def test_is_element(self):
        R1 = rct.Rectangle([0,0],[1,1])
        self.assertTrue(R1.is_element([0.5,0.5]))


    def test_is_proper_superset(self):
        R1 = rct.Rectangle([-1,-1],[1,1])
        R2 = rct.Rectangle([0,0],[1,1])
        self.assertTrue(R1.is_proper_superset(R2))


    def test_union(self):
        R1 = rct.Rectangle([-1,-1],[0,0])
        R2 = rct.Rectangle([0,0],[1,1])
        R3 = rct.Rectangle([-1,-1],[1,1])
        self.assertEqual(R3, R1.union(R2))


    def test_union_with_point(self):
        R1 = rct.Rectangle([-1,-1],[0,0])
        P = [1,1]
        R3 = rct.Rectangle([-1,-1],[1,1])
        self.assertEqual(R3, R1.union_with_point(P))


    def test_center(self):
        R1 = rct.Rectangle([-2,0],[2,2])
        P = [0,1]
        RP = rct.Rectangle(P,P)
        self.assertEqual(P,R1.center())
        self.assertEqual(P,RP.center())


    def test_center_distance_squared(self):
        pass




class TestRectangleFunctions(unittest.TestCase):
    def test_are_bounds_rectangular(self):
        # bounds do not have the same dimension
        L1 = [0,1,1]
        U1 = [0,3]
        self.assertFalse(rct.are_bounds_rectangular(L1,U1))

        # every coordinate of upper bound is not strictly greater than
        # corresponding coordinate of lower bound
        L2 = [1,1,1]
        U2 = [-1,-1,-1]
        self.assertFalse(rct.are_bounds_rectangular(L2,U2))

        # rectangular bounds
        self.assertTrue(rct.are_bounds_rectangular(U2,L2))


    def test_point_to_center_distance_squared(self):
        P = [1,1,1]
        R = rct.Rectangle([2,2,2],[4,4,4])
        self.assertEqual(12, rct.point_to_center_distance_squared(P,R))


    def test_bounding_box(self):
        pass


    def test_bounding_box_points(self):
        pass


    def test_EmptyRectangle(self):
        ER = rct.EmptyRectangle(5)
        self.assertEqual(0, ER.volume())
        self.assertTrue(ER.is_point)


    def test_rectangle_perimeter(self):
        R1 = rct.Rectangle([0,0,0],[1,1,1])
        self.assertEqual(12, rct.rectangle_perimeter(R1))
        self.assertEqual(0, rct.EmptyRectangle(1))




if __name__ == "__main__":
    unittest.main()
