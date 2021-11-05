import math

from geopy.distance import geodesic

from ConstantProperties import distance_between_points
from Position import sysIN
from Utils import get_gradient, list_xy_to_lnglat

if __name__ == '__main__':
    import sys
    # input_data = ['(103.93049,31.24886)', '(104.00371,31.27373)',
    #               '[]', '[]']

    # 其他模块调用路径规划算法,需要下列代码
    input_data = []
    for i in range(1, len(sys.argv)):
        input_data.append((sys.argv[i]))

    start, end, dynamic_obs, enemys = sysIN(input_data)
    obstacle = get_gradient(start, end)

    miny = min(start[1], end[1])  # min_lat
    maxy = max(start[1], end[1])
    minx = min(start[0], end[0])  # min_lng
    maxx = max(start[0], end[0])

    lnglat_range = {
        'minx': minx,
        'maxx': maxx,
        'miny': miny,
        'maxy': maxy
    }

    y_dist = geodesic((miny, minx), (maxy, minx)).m
    x_dist = geodesic((miny, minx), (miny, maxx)).m

    # 30米一个点
    y_size = math.floor(y_dist / distance_between_points)
    x_size = math.floor(x_dist / distance_between_points)

    print(list_xy_to_lnglat(obstacle, lnglat_range, x_size, y_size))