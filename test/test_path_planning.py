from Path_planning import *
import unittest


class path_planning_test(unittest.TestCase):

    def test_path_planning(self):
        input_data = ['(104.3327,31.0941)', '(104.41518,31.14377)']
        start_lnglat, end_lnglat = assemble_input_data(input_data)
        path = path_planning_with_plot(start_lnglat, end_lnglat, 0, 0)
        print(path)
        print(len(path))