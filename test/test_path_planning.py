from Path_planning import *
import unittest


class path_planning_test(unittest.TestCase):

    def test_path_planning(self):
        input_data = ['(104.10426,31.18817)', '(104.14597,31.23647)']
        start_lnglat, end_lnglat = assemble_input_data(input_data)
        path = path_planning_with_plot(start_lnglat, end_lnglat, 0, 0)
        print(path)
        print(len(path))

    def test_exception(self):
        try:
            print(1 / 1)
            print(2)
        except Exception as e:
            print(e)
        print(3)