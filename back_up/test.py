import math
import sys

import gdal
import ogr
import matplotlib.pyplot as plt
from shapely import geometry
import geopandas as gpd
import pandas as pd
import numpy as np
from Path_planning import assemble_graph_data, create_graph, get_shortest_path


def read_shp():
    driver = ogr.GetDriverByName('ESRI Shapefile')  # 载入驱动
    filename = r'C:\D-drive-37093\research\路径规划\China_Roads_All_WGS84_2016\县道_polyline.shp'  # 不止需要.shp文件，还需要附带的其它信息文件
    dataSource = driver.Open(filename, 0)  # 第二个参数为0是只读，为1是可写
    if dataSource is None:  # 判断是否成功打开
        print('could not open')
        sys.exit(1)
    else:
        print('done!')

    layer = dataSource.GetLayer(0)  # 读取第一个图层

    '''读出上下左右边界，坐标系为地理坐标系'''
    extent = layer.GetExtent()
    print('extent:', extent)
    print('ul:', extent[0], extent[1])  # 左右边界
    print('lr:', extent[2], extent[3])  # 下上边界

    n = layer.GetFeatureCount()  # 该图层中有多少个要素
    print('feature count:', n)

    for i in range(n):
        feat = layer.GetFeature(i)  # 提取数据层中的第一个要素

        geom = feat.GetGeometryRef()  # 提取该要素的轮廓坐标
        # LINESTRING (116.74496484 29.52956304,116.74469916 29.53050903,116.74446192 29.53263303,116.74447488 29.532942,116.74454184 29.53319103,116.744715 29.53357299,116.74496088 29.53394802)
        print(geom)


def read_csv():
    labels = ['DeletionFlag', 'NAME', 'KIND', 'Geometry']
    df = pd.read_csv('../Data/csv/县道_polyline_5_28.csv', names=labels)
    df.head()


def simple_plt():
    x = np.arange(1, 11)
    y = 2 * x + 5
    plt.axis([1, 11, 1, 30])
    plt.title("Matplotlib demo")
    plt.xlabel("x axis caption")
    plt.ylabel("y axis caption")
    plt.xticks(rotation=-15)
    plt.plot(x, y)
    plt.show()


def simple_plt_with_data():
    data = '(116.74496484 29.52956304,116.74469916 29.53050903,116.74446192 29.53263303,116.74447488 29.532942,116.74454184 29.53319103,116.744715 29.53357299,116.74496088 29.53394802)'
    data = data.replace('(', '').replace(')', '')
    all_lat_lng = data.split(',')

    lat = []  # x
    lng = []  # y

    for lat_lng_str in all_lat_lng:
        lat_lng = lat_lng_str.split(' ')
        lat.append(lat_lng[1])
        lng.append(lat_lng[0])

    plt.title("lat lng demo")
    plt.xlabel("lat")
    plt.ylabel("lng")

    plt.xticks(rotation=-15)

    plt.scatter(lat, lng, alpha=0.6)
    plt.show()


def get_remove_node(enemies):
    nodes = list()
    for enemy in enemies:
        geo_str = str(enemy['geometry']).split(' ', 1).replace('(', '').replcae(')', '').strip()

        x = str(round(float(geo_str[0]), 1))
        y = str(round(geo_str[1], 1))
        node_val = '(' + x + ',' + y + ')'

        nodes.append(node_val)

    nodes = list(set(nodes))
    return nodes


def remove_nodes(graph, nodes):
    for node in nodes:
        graph.remove_node(node)

    return graph


def back_up():
    # start_geo = gpd.GeoDataFrame([['start', 1, geometry.Point(0, 1)]],
    #                              columns=['Name', 'ID', 'geometry'])
    colors = ['yellow', 'grey', 'brown', 'orange', 'pink', 'green', 'grey', 'purple', 'pink', 'grey']

    point = gpd.GeoDataFrame([geometry.Point(0, 3), geometry.Point(3, 0)],
                             index=['a', 'b'], columns=['geometry'])

    line = gpd.GeoDataFrame([geometry.LineString([(0, 0), (0, 3), (3, 3), (3, 0)]),
                             geometry.LineString([(0, 1), (3, 1)]),
                             geometry.LineString([(0, 2), (3, 2)]),
                             geometry.LineString([(1, 0), (1, 3)]),
                             geometry.LineString([(2, 0), (2, 3)])],
                            index=['a', 'b', 'c', 'd', 'e'], columns=['geometry'])

    enemy = gpd.GeoDataFrame([geometry.Point(3, 3), geometry.Point(0.5, 3)],
                             index=['a', 'b'], columns=['geometry'])

    graph_data = pd.DataFrame(columns=['id', 'from', 'to', 'distance'])
    graph_data = assemble_graph_data(line, graph_data)
    graph_data['distance'] = 1

    graph = create_graph(graph_data)

    overlay_result = gpd.overlay(enemy, line, how='intersection')
    overlay_result2 = gpd.overlay(line, enemy, how='intersection')
    nodes = get_remove_node(overlay_result)
    graph = remove_nodes(nodes)
    print(overlay_result)

    # import networkx as nx
    # nx.draw(graph)
    # plt.show()

    ax = point.plot(color='blue')
    ax = line.plot(ax=ax, color='pink')
    ax = enemy.plot(ax=ax, color='red')
    ax = overlay_result.plot(ax=ax, color='black')

    graph.remove_node(2)

    path = get_shortest_path(graph, '(0.0,3.0)', '(3.0,0.0)')
    plt.show()


def line_and_string():
    point = gpd.GeoDataFrame([geometry.Point(0, 3), geometry.Point(3, 0)],
                             index=['a', 'b'], columns=['geometry'])
    enemy = gpd.GeoDataFrame([geometry.Point(3, 3), geometry.Point(0.5, 3)],
                             index=['a', 'b'], columns=['geometry'])
    line = gpd.GeoDataFrame([geometry.LineString([(0, 0), (0, 3), (3, 3), (3, 0)]),
                             geometry.LineString([(0, 1), (3, 1)]),
                             geometry.LineString([(0, 2), (3, 2)]),
                             geometry.LineString([(1, 0), (1, 3)]),
                             geometry.LineString([(2, 0), (2, 3)])],
                            index=['a', 'b', 'c', 'd', 'e'], columns=['geometry'])

    line.intersects(enemy)  # 看哪条线与点相交

    ax = point.plot(color='blue')
    ax = line.plot(ax=ax, color='pink')
    ax = enemy.plot(ax=ax, color='red')


def assemble_filepath(filenames, base_path, dir_prefix = 'ASTGTM2_'):
    paths = list()
    for filename in filenames:
        path = base_path + '\\' + dir_prefix + filename + '\\' + dir_prefix + filename + '_dem.tif'
        paths.append(path)
    return paths


def get_range_ele():
    start_lnglat = (103.84093, 31.33363)
    end_lnglat = (104.84818, 31.33454)

    max_lng = math.ceil(max(start_lnglat[0], end_lnglat[0]))
    min_lng = math.floor(min(start_lnglat[0], end_lnglat[0]))
    max_lat = math.ceil(max(start_lnglat[1], end_lnglat[1]))
    min_lat = math.floor(min(start_lnglat[1], end_lnglat[1]))

    filenames = list()

    for lng in range(min_lng, max_lng):
        for lat in range(min_lat, max_lat):
            print((lng, lat))
            lnglat = ''

            if lat > 0:
                lnglat += 'N' + str(lat)
            else:
                lnglat += 'S' + str(lat)

            if lng > 0:
                lnglat += 'E' + str(lng)
            else:
                lnglat += 'W' + str(lng)

            filenames.append(lnglat)
    print(filenames)

    base_path = r'C:\D-drive-37093\PycharmWorkSpace\apf_enemy\Data'
    dir_prefix = 'ASTGTM2_'

    paths = assemble_filepath(filenames, base_path)
    print(paths)

    for path in paths:
        geo = gdal.Open(path)
        print(geo.GetGeoTransform())


def concat_lnglat(lng, lat):
    lnglat = ''
    if lat > 0:
        lnglat += 'N' + str(lat)
    else:
        lnglat += 'S' + str(lat)

    if lng > 0:
        lnglat += 'E' + str(lng)
    else:
        lnglat += 'W' + str(lng)

    return lnglat


if __name__ == '__main__':
    input_lnglat = (103.84093, 31.33363)

    lng = math.ceil(input_lnglat[0])
    lat = math.floor(input_lnglat[1])

    lnglat = concat_lnglat(lng, lat)

    base_path = r'C:\D-drive-37093\PycharmWorkSpace\apf_enemy\Data'
    dir_prefix = 'ASTGTM2_'

    path = base_path + '\\' + dir_prefix + lnglat + '\\' + dir_prefix + lnglat + '_dem.tif'
    print(path)

    geo = gdal.Open(path)
    print(geo.GetGeoTransform())
