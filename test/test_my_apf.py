import unittest

from matplotlib import pyplot as plt

import Utils
import Artificial_Potential_Field_Method as apf


class apf_test(unittest.TestCase):

    def test_apf(self):
        input_data = ['(103.98345, 31.26724)', '(103.99971, 31.27608)',
                      '[(103.90542,31.32615322),(103.9548644, 31.29281989)]', '[(103.90542, 31.33254211)]']
        start, end, dynamic_obs, enemys = apf.sysIN(input_data)

        lnglat_path, obs_xy, lnglat_range, x_size, y_size = apf.runTheProject(start, end, dynamic_obs, enemys)

        x = []
        y = []
        for lnglat in lnglat_path:
            x.append(lnglat[0])
            y.append(lnglat[1])
        plt.plot(x, y, '.', c='green')

        x = [103.98345, 103.99971]
        y = [31.26724, 31.27608]
        plt.plot(x, y, '.', c='red')

        x = list()
        y = list()
        for ob in obs_xy:
            xy = Utils.xy_to_lnglat(ob, lnglat_range, x_size, y_size)
            x.append(xy[0])
            y.append(xy[1])
        plt.plot(x, y, '.', c='black')

        plt.show()

        # print('----')
        # print(obs_xy)
        # print(Utils.list_lnglat_to_xy(lnglat_path, lnglat_range, x_size, y_size))

    def test_local_minimum(self):
        start, end = (0, 0), (40, 40)
        obs = [(0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10),
               (11, 10), (12, 10), (13, 10), (14, 10), (15, 10),
               (25, 1), (25, 2), (25, 3), (25, 4), (25, 5), (25, 6), (25, 7), (25, 8), (25, 9), (25, 10), (25, 11),
               (25, 12), (25, 13), (25, 14), (25, 15), (25, 16), (25, 17), (25, 18), (25, 19), (25, 20), (25, 21), (25, 22),
               (25, 23), (25, 24), (25, 25),
               (24, 25), (23, 25), (22, 25), (21, 25), (20, 25), (19, 25), (18, 25), (17, 25), (16, 25), (15, 25), (14, 25), (13, 25), (12, 25), (11, 25), (10, 25),
               (39, 40), (40, 41), (40, 39)]


        path = apf.apf(0, 0, start, end, obs, [], None)

        # show plot.
        x = [0, 40]
        y = [0, 40]
        plt.plot(x, y, '.', c='red')

        x = list()
        y = list()
        for xy in obs:
            x.append(xy[0])
            y.append(xy[1])
        plt.plot(x, y, '.', c='black')

        x = list()
        y = list()
        for xy in path:
            x.append(xy[0])
            y.append(xy[1])
        plt.plot(x, y, '.', c='green')

        plt.show()