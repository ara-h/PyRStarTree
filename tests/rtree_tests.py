import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

import unittest

from pyrstar import rectangle as rct
from pyrstar import rtree as rtr

class TestRStarTreeMethods(unittest.TestCase):
    def test_init(self):
        pass


    def test_init_exceptions(self):
        pass


    def test_equality_comparison(self):
        pass


    def test_does_point_to_leaves(self):
        pass


    def test_update_bounding_rectangle(self):
        pass


    def test_add_point_data(self):
        pass


    def test_delete_point_data(self):
        pass


    def test_add_child(self):
        pass


    def test_delete_child(self):
        pass


class TestRStarTreeFunctions(unittest.TestCase):
    def test_overlap_enlargement_required(self):
        pass


    def test_volume_enlargement_required(self):
        pass


    def test_path_to_subtree(self):
        pass


    def test_choose_subtree(self):
        pass


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
