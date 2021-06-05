import math

import networkx as nx
import geopandas as gpd
import pandas as pd
from geopy.distance import geodesic
import os
import matplotlib.pyplot as plt
from shapely.geometry import Point
from scipy.spatial import cKDTree
import numpy as np
import sys

import Utils


def path_planning(start_lnglat, end_lnglat, encoding='GBK', dir=r'C:\D-drive-37093\research\路径规划\China_Roads_All_WGS84_2016'):
    """
    :return:
    """
    filenames = ['县道_polyline.shp', '乡镇村道_polyline.shp', '行人道路_线.shp', '高速公路_线.shp', '国道_线.shp',
                 '其他路_polyline.shp', '九级路_线.shp', '省道_线.shp', '铁路_线.shp', '九级路_线.shp']
    # colors = ['yellow', 'grey', 'brown', 'orange', 'pink', 'green', 'grey', 'purple', 'pink', 'grey']

    lat_start, lat_end, lng_start, lng_end = assemble_input_data(start_lnglat, end_lnglat)
    start_node, end_node = None, None
    all_part_df = pd.DataFrame()

    # start_geo = gpd.GeoDataFrame([['start', 1, Point(start_lnglat[0], start_lnglat[1])]],
    #                              columns=['Name', 'ID', 'geometry'])
    # end_geo = gpd.GeoDataFrame([['end', 2, Point(end_lnglat[0], end_lnglat[1])]],
    #                            columns=['Name', 'ID', 'geometry'])
    # ax = start_geo.plot(color='red')
    # ax = end_geo.plot(ax=ax, color='black')

    for i in range(len(filenames)):
        geo_df = gpd.read_file(os.path.join(dir, filenames[i]), encoding='GBK',
                               bbox=(lng_start, lat_start, lng_end, lat_end))
        if len(geo_df) > 0:
            # ax = geo_df.plot(ax=ax, color=colors[i])

            all_part_df = all_part_df.append(geo_df, ignore_index=True)

            temp_start_node, temp_end_node = get_nearest_point(geo_df, start_lnglat, end_lnglat)
            start_node, end_node = judgement_distance(start_node, end_node, temp_start_node, temp_end_node)

    graph_data = pd.DataFrame(columns=['id', 'from', 'to', 'distance'])
    graph_data = assemble_graph_data(all_part_df, graph_data)
    graph = create_graph(graph_data)

    path = get_shortest_path(graph, start_node['lnglat'], end_node['lnglat'])
    # print(path)
    # print(len(path))
    x = list()
    y = list()

    for i in range(len(path)):
        temp_xy = path[i].replace('(', '').replace(')', '').strip().split(',')
        x.append(float(temp_xy[0]))
        y.append(float(temp_xy[1]))

    # plt.plot(x, y, 'o')
    # plt.show()

    # if start point, end point not in path, add that to path.
    judgement_path(path, start_lnglat, end_lnglat)
    return path


def path_planning_with_plot(start_lnglat, end_lnglat, obstacles, enemies, dir=r'C:\D-drive-37093\research\路径规划\China_Roads_All_WGS84_2016'):

    filenames = ['县道_polyline.shp', '乡镇村道_polyline.shp', '行人道路_线.shp', '高速公路_线.shp', '国道_线.shp',
                 '其他路_polyline.shp', '九级路_线.shp', '省道_线.shp', '铁路_线.shp', '九级路_线.shp']
    colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple',
              'brown', 'orange', 'pink', 'grey', 'brown', 'purple', 'pink', 'magenta', 'deepskyblue',
              'y', 'crimson', 'sage', 'c']

    lat_start, lat_end, lng_start, lng_end = get_lnglat_range(start_lnglat, end_lnglat)

    start_node, end_node = None, None
    all_part_df = pd.DataFrame()

    start_geo = gpd.GeoDataFrame([['start', 1, Point(start_lnglat[0], start_lnglat[1])]],
                                 columns=['Name', 'ID', 'geometry'])
    end_geo = gpd.GeoDataFrame([['end', 2, Point(end_lnglat[0], end_lnglat[1])]],
                               columns=['Name', 'ID', 'geometry'])
    ax = start_geo.plot(color='red')
    ax = end_geo.plot(ax=ax, color='black')

    for i in range(len(filenames)):
        geo_df = gpd.read_file(os.path.join(dir, filenames[i]), encoding='GBK',
                               bbox=(lng_start, lat_start, lng_end, lat_end))
        if len(geo_df) > 0:
            ax = geo_df.plot(ax=ax, color=colors[i])

            all_part_df = all_part_df.append(geo_df, ignore_index=True)

            temp_start_node, temp_end_node = get_nearest_point(geo_df, start_lnglat, end_lnglat)
            start_node, end_node = judgement_distance(start_node, end_node, temp_start_node, temp_end_node)

    graph_data = pd.DataFrame(columns=['id', 'from', 'to', 'distance'])
    graph_data = assemble_graph_data(all_part_df, graph_data)
    graph = create_graph(graph_data)

    path = get_shortest_path(graph, start_node['lnglat'], end_node['lnglat'])
    # print(path)
    # print(len(path))
    x = list()
    y = list()

    for i in range(len(path)):
        temp_xy = path[i].replace('(', '').replace(')', '').strip().split(',')
        x.append(float(temp_xy[0]))
        y.append(float(temp_xy[1]))

    plt.plot(x, y, '.')
    plt.show()

    # if start point, end point not in path, add that to path.
    judgement_path(path, start_lnglat, end_lnglat)
    return path


def assemble_input_data(input_data):

    temp_start_lnglat = input_data[0].replace("(", "").replace(")", "").strip().split(',')
    temp_end_lnglat = input_data[1].replace("(", "").replace(")", "").strip().split(',')

    start_lng = round(float(temp_start_lnglat[0].strip()), 5)  # 起始点的lng值
    start_lat = round(float(temp_start_lnglat[1].strip()), 5)

    end_lng = round(float(temp_end_lnglat[0].strip()), 5)
    end_lat = round(float(temp_end_lnglat[1].strip()), 5)

    start_lnglat = (start_lng, start_lat)
    end_lnglat = (end_lng, end_lat)

    return start_lnglat, end_lnglat


def assemble_graph_data(shp, graph_data):
    shp_data = pd.DataFrame(shp)

    for i in range(len(shp_data)):  # 每次提取两点，从前一点到后一点
        geometry = str(shp_data.iloc[i]['geometry'])

        # 'LINESTRING (104.41113678 31.14637938, 104.41143666 31.148338545)'
        geometry_split = geometry.split('(')
        # geo_type = geometry_split[0]

        all_geometry_data = geometry_split[1].replace(')', '').split(',')  # lng lat

        length = len(all_geometry_data)
        for j in range(length):
            if j == length - 1:
                break
            geometry_data = all_geometry_data[j].strip().split(' ')
            next_geometry_data = all_geometry_data[j + 1].strip().split(' ')

            lng = geometry_data[0]
            lat = geometry_data[1]

            next_lng = next_geometry_data[0]
            next_lat = next_geometry_data[1]

            distance = geodesic((lat, lng), (next_lat, next_lng)).m
            index = len(graph_data)

            # 小数点后7位就是1cm
            data = {
                'id': index,
                'from': '(' + str(round(float(lng), 5)) + ',' + str(round(float(lat), 5)) + ')',
                'to': '(' + str(round(float(next_lng), 5)) + ',' + str(round(float(next_lat), 5)) + ')',
                'distance': float(distance)
            }

            graph_data = graph_data.append(data, ignore_index=True)

    return graph_data


def get_lnglat_range(start_lnglat, end_lnglat):
    min_lat = min(start_lnglat[1], end_lnglat[1])
    max_lat = max(start_lnglat[1], end_lnglat[1])
    min_lng = min(start_lnglat[0], end_lnglat[0])
    max_lng = max(start_lnglat[0], end_lnglat[0])

    range_val = max(max_lng - min_lng, max_lat - min_lat) / 2

    min_lat -= range_val
    max_lat += range_val
    min_lng -= range_val
    max_lng += range_val

    return min_lat, max_lat, min_lng, max_lng

def get_nearest_point(geo_dataframe, start_lnglat, end_lnglat):
    start_gpd = gpd.GeoDataFrame([['start', 0, Point(start_lnglat[0], start_lnglat[1])]]
                                 , columns=['Name', 'ID', 'geometry'])
    end_gpd = gpd.GeoDataFrame([['end', 1, Point(end_lnglat[0], end_lnglat[1])]],
                                 columns=['Name', 'ID', 'geometry'])

    start_node = ckd_nearest(start_gpd, geo_dataframe)
    end_node = ckd_nearest(end_gpd, geo_dataframe)

    return start_node, end_node


def create_graph(graph_data):
    graph = nx.from_pandas_edgelist(graph_data, 'from', 'to',
                                    edge_attr=['id', 'distance'])  # nx.DiGraph , create_using=nx.DiGraph 加参数是有向图

    return graph


def get_shortest_path(graph, start_node, end_node):
    path = nx.shortest_path(graph, start_node, end_node, weight='distance', method='bellman-ford')
    return path


def ckd_nearest(gdfA, gdfB):
    A = np.concatenate(
        [np.array(geom.coords) for geom in gdfA.geometry.to_list()])
    B = [np.array(geom.coords) for geom in gdfB.geometry.to_list()]
    # , gdfB_cols=['Place', 'geometry']
    # B_ix = tuple(itertools.chain.from_iterable(
    #     [itertools.repeat(i, x) for i, x in enumerate(list(map(len, B)))]))

    B = np.concatenate(B)
    ckd_tree = cKDTree(B)
    dist, idx = ckd_tree.query(A, k=1)

    # idx = itemgetter(*idx)(B_ix) 返回的是地理线的坐标，但不能确定是哪个点
    # gdf = pd.concat(
    #     [gdfA, gdfB.loc[idx, gdfB_cols].reset_index(drop=True),
    #      pd.Series(dist, name='dist')], axis=1)
    # nearest_node = pd.DataFrame(gdfB).iloc[idx]
    lnglat = (B[idx][0, 0], B[idx][0, 1])

    nearest_node = {
        'lnglat': '(' + str(round(float(lnglat[0]), 5)) + ',' + str(round(float(lnglat[1]), 5)) + ')',
        'dist': dist
    }

    return nearest_node


def judgement_distance(start_node, end_node, temp_start_node, temp_end_node):

    if start_node is None:
        start_node = temp_start_node
    elif start_node['dist'] > temp_start_node['dist']:
        start_node = temp_start_node

    if end_node is None:
        end_node = temp_end_node
    elif end_node['dist'] > temp_end_node['dist']:
        end_node = temp_end_node

    return start_node, end_node


def judgement_path(path, start_lnglat, end_lnglat):
    """

    :param path:
    :param start_lnglat:
    :param end_lnglat:
    :return:
    """
    # path planning failed.
    if len(path) == 0:
        return path

    if path[0] != str(start_lnglat):
        path.insert(0, str(start_lnglat))

    if path[len(path) - 1] != str(end_lnglat):
        path.insert(len(path), str(end_lnglat))


def last_test():
    # nearest_()
    dir = r'C:\D-drive-37093\research\路径规划\China_Roads_All_WGS84_2016'
    # 11.1m 201m 485m 20.4m 443m
    # 104.40986742 31.1397723 lng lat
    # 103.95937,31.24799  103.96817,31.26513
    # x -> lng, y -> lat '九级路_线.shp'
    filenames = ['县道_polyline.shp', '乡镇村道_polyline.shp', '行人道路_线.shp', '高速公路_线.shp', '国道_线.shp',
                 '其他路_polyline.shp', '九级路_线.shp', '省道_线.shp', '铁路_线.shp', '九级路_线.shp']

    colors = ['yellow', 'grey', 'brown', 'orange', 'pink', 'green', 'grey', 'purple', 'pink', 'grey']

    start_lnglat = (103.95937, 31.24799)
    # end_lnglat = (103.96817, 31.26513)
    end_lnglat = (104.05, 31.15)

    all_part_df = pd.DataFrame()

    start_geo = gpd.GeoDataFrame([['start', 1, Point(start_lnglat[0], start_lnglat[1])]],
                                 columns=['Name', 'ID', 'geometry'])
    end_geo = gpd.GeoDataFrame([['end', 2, Point(end_lnglat[0], end_lnglat[1])]],
                               columns=['Name', 'ID', 'geometry'])
    ax = start_geo.plot(color='red')
    ax = end_geo.plot(ax=ax, color='black')

    lat_start, lat_end, lng_start, lng_end = assemble_input_data(start_lnglat, end_lnglat)

    start_node, end_node = None, None

    for i in range(len(filenames)):
        all_df = gpd.read_file(os.path.join(dir, filenames[i]), encoding='GBK',
                               bbox=(lng_start, lat_start, lng_end, lat_end))
        # part_df = all_df.cx[lng_start:lng_end, lat_start:lat_end]  # lng lat

        if len(all_df) > 0:
            print('i is :', i)
            print('has elements num is: ', len(all_df))
            all_part_df = all_part_df.append(all_df, ignore_index=True)
            ax = all_df.plot(ax=ax, color=colors[i])

            temp_start_node, temp_end_node = get_nearest_point(all_df, start_lnglat, end_lnglat)
            start_node, end_node = judgement_distance(start_node, end_node, temp_start_node, temp_end_node)

    print('all_part_df is :', len(all_part_df))
    graph_data = pd.DataFrame(columns=['id', 'from', 'to', 'distance'])
    graph_data = assemble_graph_data(all_part_df, graph_data)
    graph = create_graph(graph_data)

    path = get_shortest_path(graph, start_node['lnglat'], end_node['lnglat'])

    print(path)

    x = list()
    y = list()

    for i in range(len(path)):
        temp_xy = path[i].replace('(', '').replace(')', '').strip().split(',')
        x.append(float(temp_xy[0]))
        y.append(float(temp_xy[1]))

    plt.plot(x, y, 'o')
    plt.show()

distance_between_points = 30

def create_map_params(start_lnglat, end_lnglat):
    miny = min(start_lnglat[1], end_lnglat[1])  # min_lat
    maxy = max(start_lnglat[1], end_lnglat[1])
    minx = min(start_lnglat[0], end_lnglat[0])  # min_lng
    maxx = max(start_lnglat[0], end_lnglat[0])

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

    return x_size, y_size, lnglat_range


if __name__ == '__main__':
    start = (103.98345, 31.26724)
    end = (103.99971, 31.27608)
    x_size, y_size, lnglat_range = create_map_params(start, end)

    paths = [(103.98345, 31.26724), (103.98376882352942, 31.26724), (103.98376882352942, 31.26751625), (103.98408764705883, 31.26751625), (103.98408764705883, 31.267792500000002), (103.98440647058824, 31.267792500000002), (103.98472529411765, 31.267792500000002), (103.98504411764706, 31.267792500000002), (103.98504411764706, 31.26806875), (103.98504411764706, 31.268345), (103.98536294117648, 31.268345), (103.98568176470589, 31.268345), (103.98568176470589, 31.268621250000002), (103.9860005882353, 31.268621250000002)]
    obs = [(10, 27), (11, 25), (10, 27), (11, 26), (9, 27), (10, 26), (11, 25), (12, 24), (10, 25), (11, 26), (11, 24), (10, 26), (11, 25), (12, 24), (11, 24), (12, 23), (18, 18), (18, 19), (18, 20), (18, 21), (18, 26), (18, 27), (18, 28), (17, 18), (17, 19), (17, 20), (17, 21), (18, 26), (17, 26), (18, 25), (17, 27), (17, 28), (22, 25), (23, 15), (23, 20), (21, 25), (22, 26), (23, 26), (22, 25), (24, 14), (22, 15), (22, 20), (22, 26), (25, 10), (23, 14), (25, 21), (25, 22), (24, 10), (24, 21), (24, 22), (29, 25), (29, 24), (31, 9), (31, 10), (31, 11), (31, 12), (31, 13), (31, 14), (31, 15), (31, 16), (31, 17), (31, 18), (30, 25), (30, 24), (32, 8), (30, 9), (30, 10), (30, 11), (30, 12), (30, 13), (30, 14), (30, 15), (30, 16), (30, 17), (30, 18), (31, 8), (35, 3), (35, 5), (34, 3), (34, 5), (38, 28), (38, 29), (37, 28), (37, 29), (39, 30), (39, 29), (45, 14), (45, 15), (44, 14), (44, 15)]

    x = []
    y = []
    for lnglat in paths:
        x.append(lnglat[0])
        y.append(lnglat[1])

    plt.plot(x, y, '.', c='red')

    x = [103.98345, 103.99971]
    y = [31.26724, 31.27608]

    plt.plot(x, y, '.', c='black')

    x = list()
    y = list()

    for ob in obs:
        xy = Utils.xy_to_lnglat(ob, lnglat_range, x_size, y_size)
        x.append(xy[0])
        y.append(xy[1])

    plt.plot(x, y, '.', c='green')

    plt.show()
    # # note: run this project.
    # # ['(104.11172, 31.05421)', '(104.132, 31.06591)']
    # input_data = ['(103.98345,31.26724)', '(103.99971,31.27608)']
    # start_lnglat, end_lnglat = assemble_input_data(input_data)
    # path = path_planning_with_plot(start_lnglat, end_lnglat, 0, 0)
    # print(path)
    # print(len(path))

    # input_data = list()
    # for i in range(1, len(sys.argv)):
    #     input_data.append(sys.argv[i])
    #
    # print(input_data)
    # input_data = ['(124.456789123, 3.123131231224)', '(123.234234234, 455.1231231)']
    # print(assemble_input_data(input_data))
