import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

import unittest

from pyrstar import rectangle as rct
from pyrstar import rtree as rtr

class TestRStarTreeMethods(unittest.TestCase):
    def setUp(self):
        self.pd1 = {1: [1,1], 2: [1.5,1.5]}
        self.pd2 = {3: [0,0.5], 4: [1.5,-0.5]}

    def test_init(self):
        rt1 = rtr.RStarTree(point_data=self.pd1)

        self.assertTrue(rt1.is_leaf)
        self.assertEqual([1,1],rt1.points[1])

        rt2 = rtr.RStarTree(point_data=self.pd2)

        rt3 = rtr.RStarTree(children=[rt1,rt2])

        self.assertFalse(rt3.is_leaf)

        bb = rct.Rectangle([0,-0.5],[1.5,1.5])
        self.assertEqual(bb, rt3.key)


    def test_init_exceptions(self):
        with self.assertRaises(ValueError):
            rtr.RStarTree()

        rt1 = rtr.RStarTree(point_data=self.pd1)

        with self.assertRaises(ValueError):
            rtr.RStarTree(children=[rt1],point_data=self.pd2)


    def test_equality_comparison(self):
        rt1 = rtr.RStarTree(point_data=self.pd1)
        rt2 = rtr.RStarTree(point_data=self.pd1)
        self.assertTrue(rt1 == rt2)


    def test_does_point_to_leaves(self):
        rt1 = rtr.RStarTree(point_data=self.pd1)
        rt2 = rtr.RStarTree(point_data=self.pd2)

        rt3 = rtr.RStarTree(children=[rt1,rt2])

        self.assertTrue(rt3.does_point_to_leaves())


    def test_update_bounding_rectangle(self):
        rt1 = rtr.RStarTree(point_data=self.pd1)

        rt1.points[5] = [2,2]
        rt1.update_bounding_rectangle()

        self.assertEqual(rt1.key.minima, [1,1])
        self.assertEqual(rt1.key.maxima, [2,2])


    def test_add_point_data(self):
        rt1 = rtr.RStarTree(point_data=self.pd1)
        rt1.add_point_data(5,[3,3])

        self.assertEqual([3,3],rt1.points[5])
        self.assertEqual(rt1.key.maxima,[3,3])


    def test_remove_point_data(self):
        rt1 = rtr.RStarTree(point_data=self.pd1)
        rt1.remove_point_data(2)

        self.assertFalse(2 in rt1.points)


    def test_add_child(self):
        rt1 = rtr.RStarTree(point_data=self.pd1)
        rt2 = rtr.RStarTree(point_data=self.pd2)
        rt3 = rtr.RStarTree(point_data={5:[2.5,0.5],6:[3,1]})

        rt4 = rtr.RStarTree(children=[rt1,rt2])
        rt4.add_child(rt3)

        self.assertTrue(rt3 in rt4.children)
        self.assertEqual(rt4.minima,[0,-0.5])
        self.assertEqual(rt4.maxima,[3,1.5])


    def test_remove_child(self):
        rt1 = rtr.RStarTree(point_data=self.pd1)
        rt2 = rtr.RStarTree(point_data=self.pd2)
        rt3 = rtr.RStarTree(point_data={5:[2.5,0.5],6:[3,1]})

        rt4 = rtr.RStarTree(children=[rt1,rt2,rt3])
        rt4.remove_child(rt3)

        self.assertFalse(rt3 in rt4.children)
        self.assertEqual(rt4.minima,[0,-0.5])
        self.assertEqual(rt4.maxima,[1.5,1.5])


class TestRStarTreeFunctions(unittest.TestCase):
    def setUp(self):
        self.pd1 = {1: [1,1], 2: [1.5,1.5]}
        self.pd2 = {3: [0,0.5], 4: [1.5,-0.5]}
        self.pd3 = {5: [2.5,0.5], 6: [3,1]}
        self.pd4 = {7: [1.5,0], 8: [0.5,1.25]}



    def test_overlap_enlargement_required(self):
        # If rt2 is expanded to accomodate rt4, the key rectangle should come
        # to overlap with the key rectangle of rt1. That overlap should be of
        # area 0.125.
        rt1 = rtr.RStarTree(point_data=self.pd1)
        rt2 = rtr.RStarTree(point_data=self.pd2)
        rt3 = rtr.RStarTree(point_data=self.pd3)
        rt4 = rtr.RStarTree(point_data=self.pd4)

        rtA = rtr.RStarTree(children=[rt1,rt2,rt3])

        self.assertEqual(rtr.overlap_enlargement_required(rtA,rt2,rt4.key), 0.125)


    def test_volume_enlargement_required(self):
        rt = rtr.RStarTree(point_data=self.pd3)
        entry = rct.Rectangle([0,0],[1.5,1])

        self.assertEqual(rtr.volume_enlargement_required(rt, entry), 0.5*1.5)

    def test_is_descendant():
        rt3 = rtr.RStarTree(point_data={1: [2.25,1.75], 2: [2.75,2.25]})
        rt2 = rtr.RStarTree(children=[rt3])
        rt2.key = rct.Rectangle([2,1.25],[4,2.75])
        rt1 = rtr.RStarTree(point_data={3: [1,1], 4: [3,3]})
        rtP = rtr.RStarTree(children=[rt1,rt2])

        self.assertTrue(rtr.is_descendant(rt3,rt3))
        self.assertTrue(rtr.is_descendant(rt2,rt3))
        self.assertFalse(rtr.is_descendant(rt1,rt3))

    def test_path_to_subtree(self):
        rt1 = rtr.RStarTree(point_data=self.pd1)
        rt2c = rtr.RStarTree(point_data={7: [0.5,0],8: [1,-0.25]})
        rt2 = rtr.RStarTree(children=[rt2c])
        rt2.key = rct.Rectangle([0,-0.5],[1.5,0.5])
        rt3 = rtr.RStarTree(point_data=self.pd3)
        rtA = rtr.RStarTree(children=[rt1,rt2,rt3])

        # base case: path from starting node to starting node
        self.assertEqual([rt1], rtr.path_to_subtree(rt1, rt1))

        # depth = 1: path from starting node to one of its children
        self.assertEqual([rtA,rt2], rtr.path_to_subtree(rtA, rt2))

        # depth >= 2: path from starting node to a non-immediate descendant
        self.assertEqual([rtA,rt2,rt2c], rtr.path_to_subtree(rtA,rt2c))


    def test_choose_subtree(self):
        # case 1: the criterion overlap_enlargement_required does not result in
        # any ties, and so rt1 is chosen
        points1 = {"a" : [0, 0], "b" : [1.75, 0.75]}
        rt1 = rtr.RStarTree(point_data=points1)

        points2 = {"c" : [0, 1], "d" : [0.5, 1.5]}
        rt2 = rtr.RStarTree(point_data=points2)

        points3 = {"e" : [1, 1], "f" : [1.5, 1.5]}
        rt3 = rtr.RStarTree(point_data=points3)

        rtA = rtr.RStarTree(children=[rt1,rt2,rt3])

        test_pt = [1.5, 0.5]
        test_entry = rct.Rectangle([test_pt, test_pt])

        # Expect rt1 as the chosen subtree and 1 as the level of insertion
        self.assertEqual((rt1, 1), rtr.choose_subtree(rtA, 0, test_entry))

        # case 2: criterion overlap_enlargment_required results in ties,
        # but ties are resolved by volume_enlargement_required, and so rt1 is
        # chosen

        points1 = {"a" : [1, 1], "b" : [1.5, 1.5]}
        rt1 = rtr.RStarTree(point_data=points1)

        points2 = {"c" : [2, 1], "d" : [2.5, 1.5]}
        rt2 = rtr.RStarTree(point_data=points2)

        points3 = {"e" : [2, -0.5], "f" : [2.5, 0]}
        rt3 = rtr.RStarTree(point_data=points3)

        rtA = rtr.RStarTree(children=[rt1,rt2,rt3])

        test_pt = [1.625, 0.5]
        test_entry = rct.Rectangle([test_pt, test_pt])

        # Expect rt1 as the chosen subtree and 1 as the level of insertion
        self.assertEqual((rt1, 1), rtr.choose_subtree(rtA, 0, test_entry))

        # case 3: first two criteria result in ties, but ties are resolved by
        # volume comparison, and so rt4 is chosen

        points1 = {"a" : [-1, -1], "b" : [-0.75, -0.75]}
        rt1 = rtr.RStarTree(point_data=points1)

        points2 = {"c" : [-1, -0.25], "d" : [-0.75, 0]}
        rt2 = rtr.RStarTree(point_data=points2)

        points3 = {"e" : [-0.25, -0.25], "f" : [0, 0]}
        rt3 = rtr.RStarTree(point_data=points3)

        points4 = {"g" : [-0.25,-0.825], "h" : [0, -0.75]}
        rt4 = rtr.RStarTree(point_data=points4)

        rtA = rtr.RStarTree(children=[rt1,rt2,rt3,rt4])

        test_pt = [-0.5,-0.5]
        test_entry = rct.Rectangle([test_pt, test_pt])

        # Expect rt4 as the chosen subtree and 1 as the level of insertion
        self.assertEqual((rt4, 1), rtr.choose_subtree(rtA, 0, test_entry))


    def test_choose_split_axis_leaf(self):
        pass


    def test_choose_split_index_leaf(self):
        pass


    def test_choose_split_axis(self):
        pass


    def test_choose_split_index(self):
        pass


class TestRTCursorMethods(unittest.TestCase):
    def test_oveflow_treatment_leaf(self):
        pass


    def test_overflow_treatment_node(self):
        pass


    def test_insert_point(self):
        pass


    def test_insert_node(self):
        pass


    def test_data_insertion(self):
        pass


class TestRStarTreeConditions(unittest.TestCase):
    def test_bounds(self):
        pass


    def test_entry_count_nodes(self):
        pass


    def test_entry_count_leaves(self):
        pass
