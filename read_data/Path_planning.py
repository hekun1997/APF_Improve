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
    """
    :return:
    """
    filenames = ['县道_polyline.shp', '乡镇村道_polyline.shp', '行人道路_线.shp', '高速公路_线.shp', '国道_线.shp',
                 '其他路_polyline.shp', '九级路_线.shp', '省道_线.shp', '铁路_线.shp', '九级路_线.shp']
    colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple',
              'brown', 'orange', 'pink', 'grey', 'brown', 'purple', 'pink', 'magenta', 'deepskyblue',
              'y', 'crimson', 'sage', 'c']


    lat_start = min(start_lnglat[1], end_lnglat[1]) - 0.1
    lat_end = max(start_lnglat[1], end_lnglat[1]) + 0.1
    lng_start = min(start_lnglat[0], end_lnglat[0]) - 0.1
    lng_end = max(start_lnglat[0], end_lnglat[0]) + 0.1

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

    plt.plot(x, y, 'o')
    plt.show()

    # if start point, end point not in path, add that to path.
    judgement_path(path, start_lnglat, end_lnglat)
    return path


def assemble_input_data(input_data):

    temp_start_lnglat = input_data[0].replace("(", "").replace(")", "").strip().split(',')
    temp_end_lnglat = input_data[1].replace("(", "").replace(")", "").strip().split(',')

    start_lng = round(float(temp_start_lnglat[0].strip()), 5)
    start_lat = round(float(temp_start_lnglat[1].strip()), 5)

    end_lng = round(float(temp_end_lnglat[0].strip()), 5)
    end_lat = round(float(temp_end_lnglat[1].strip()), 5)

    start_lnglat = (start_lng, start_lat)
    end_lnglat = (end_lng, end_lat)

    # lat_start = min(start_lnglat[1], end_lnglat[1]) - 0.1
    # lat_end = max(start_lnglat[1], end_lnglat[1]) + 0.1
    # lng_start = min(start_lnglat[0], end_lnglat[0]) - 0.1
    # lng_end = max(start_lnglat[0], end_lnglat[0]) + 0.1

    lat_start = min(start_lnglat[1], end_lnglat[1]) - 0.1
    lat_end = max(start_lnglat[1], end_lnglat[1]) + 0.1
    lng_start = min(start_lnglat[0], end_lnglat[0]) - 0.1
    lng_end = max(start_lnglat[0], end_lnglat[0]) + 0.1

    return lat_start, lat_end, lng_start, lng_end


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
    path = nx.shortest_path(graph, start_node, end_node, weight='distance')
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


if __name__ == '__main__':

        # note: run this project.
        start_lnglat = (104.11172, 31.05421)
        # end_lnglat = (103.96817, 31.26513)
        end_lnglat = (104.132, 31.06591)
        path = path_planning_with_plot(start_lnglat, end_lnglat, 0, 0)
        print(path)
        print(len(path))

    # input_data = list()
    # for i in range(1, len(sys.argv)):
    #     input_data.append(sys.argv[i])
    #
    # print(input_data)
    # input_data = ['(124.456789123, 3.123131231224)', '(123.234234234, 455.1231231)']
    # print(assemble_input_data(input_data))
