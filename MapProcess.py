import math

import numpy as np
from math import radians, cos, sin, asin, sqrt
import pandas as pd
import os
import geopandas as gpd


# lng经度，lat纬度
from matplotlib import pyplot as plt
from shapely.geometry import Point

import Utils


def geodistance(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)])  # 经纬度转换成弧度
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    distance = 2 * asin(sqrt(a)) * 6371 * 1000  # 地球平均半径，6371km
    return distance


# 根据地图信息来获取APF用到的地图信息
def read_map_info():
    # df = pd.read_csv("F:\\UESTC\\apf_enemy\\map.csv", encoding='gbk')  # 数据为从左上，往下走，在往右走
    df = pd.read_csv(r'C:\D-drive-37093\PycharmWorkSpace\apf_enemy\map.csv', encoding='gbk')
    lng = len(df['lng'].unique())
    lat = len(df['lat'].unique())
    list_obs = list(df.loc[df['type'] == 1].index)
    list_road = list(df.loc[df['type'] == -1].index)
    return lng, lat, df, list_obs, list_road


def read_map_info_from_dem(start_lnglat, end_lnglat):
    filenames = get_shp_filenames()

    colors = Utils.get_colors()

    min_lng, max_lng, min_lat, max_lat = adjustment_range(start_lnglat, end_lnglat)

    all_geo_df = pd.DataFrame()

    start_geo = gpd.GeoDataFrame([['start', 1, Point(start_lnglat[0], start_lnglat[1])]],
                                 columns=['Name', 'ID', 'geometry'])
    end_geo = gpd.GeoDataFrame([['end', 2, Point(end_lnglat[0], end_lnglat[1])]],
                               columns=['Name', 'ID', 'geometry'])
    ax = start_geo.plot(color='red')
    ax = end_geo.plot(ax=ax, color='black')

    for i in range(len(filenames)):
        geo_df = gpd.read_file(filenames[i], encoding='GBK', bbox=(min_lng, min_lat, max_lng, max_lat))
        if len(geo_df) > 0:
            ax = geo_df.plot(ax=ax, color=colors[i])

            all_geo_df = all_geo_df.append(geo_df, ignore_index=True)

    plt.show()


def get_filename_from_input_data(start_lnglat, end_lnglat):
    max_lng = math.ceil(max(start_lnglat[0], end_lnglat[0]))
    min_lng = math.floor(min(start_lnglat[0], end_lnglat[0]))
    max_lat = math.ceil(max(start_lnglat[1], end_lnglat[1]))
    min_lat = math.floor(min(start_lnglat[1], end_lnglat[1]))

    filename = list()

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

            filename.append(lnglat)
    print(filename)
    return filename


def get_shp_filenames(base_path=r'C:\D-drive-37093\research\路径规划\China_Roads_All_WGS84_2016'):
    # file_paths = list()

    # for root, dirs, files in os.walk(base_path):
    #     for file in files:
    #         if file.endswith('.shp'):
    #             file_paths.append(os.path.join(root, file))
    # file_paths = ['九级路_线.shp', '乡镇村道_polyline.shp', '公园绿地_面.shp', '其他路_polyline.shp', '县中心_点.shp',
    #               '县界_面.shp', '县道_polyline.shp', '国界_面.shp', '国道_线.shp', '市中心_点.shp', '市届_面.shp',
    #               '水系_面.shp', '省会_点.shp', '省界_面.shp', '省道_线.shp', '行人道路_线.shp', '轮渡_polyline.shp',
    #               '铁路_线.shp', '高速公路_线.shp']
    file_paths = ['九级路_线.shp', '乡镇村道_polyline.shp', '其他路_polyline.shp',
                  '县道_polyline.shp', '国道_线.shp',
                  '水系_面.shp',  '省道_线.shp', '行人道路_线.shp']
    file_paths = [os.path.join(base_path, file_path) for file_path in file_paths]

    return file_paths


def adjustment_range(start_lnglat, end_lnglat):

    min_lng = min(start_lnglat[0], end_lnglat[0])
    max_lng = max(start_lnglat[0], end_lnglat[0])
    min_lat = min(start_lnglat[1], end_lnglat[1])
    max_lat = max(start_lnglat[1], end_lnglat[1])

    range_value = max(max_lat - min_lat, max_lng - max_lng) / 10
    print(range_value)

    min_lng -= range_value
    max_lng += range_value
    min_lat -= range_value
    max_lat += range_value

    return min_lng, max_lng, min_lat, max_lat


# 将position (x,y)如(0,1)转为经纬度表的序号  X=len_lng,Y=len_lat
def position_to_LngLatNum(position, Y):
    x = position[0]
    y = position[1]
    num = x * Y + Y - y - 1  # 因为从零开始,所以减1
    return num


def change_file():
    # df_village = pd.read_csv("划定地图范围内的乡镇村道.csv", encoding='gbk')
    # df_city = pd.read_csv("划定地图范围内的县道.csv", encoding='gbk')
    df_water = pd.read_csv("划定地图范围内的水系_面.csv", encoding='gbk')
    df_water['lat'] = 0
    lng = []
    lat = []
    for index2, row2 in df_water.iterrows():
        x, y = row2['location'].split(',')
        lng.append(float(x.replace('(', '')))
        lat.append(float(y.replace(')', '')))

    dic = {'lng': lng,
           'lat': lat}
    res = pd.DataFrame(dic)
    res.to_csv('划定地图范围内的水系_面.csv', index=False)
    return 0


# format map to csv.
def back_up():
    # 添加路网数据 路为-1，水为1
    df = pd.read_excel("data1.xlsx", encoding='gbk')
    df_village = pd.read_csv("划定地图范围内的乡镇村道.csv", encoding='gbk')
    df_city = pd.read_csv("划定地图范围内的县道.csv", encoding='gbk')
    # df_water = pd.read_csv("划定地图范围内的水系_面.csv", encoding='gbk')
    lng = []
    lat = []
    df['type'] = 0
    for index2, row2 in df_village.iterrows():
        print(index2)
        for index1, row1 in df.iterrows():
            if (abs(row2["lng"] - row1["lng"]) < 0.000139) & (abs(row2["lat"] - row1["lat"]) < 0.000139):
                df.loc[index1:index1, ('type')] = -1  # 将该列的type进行修改
                break

    for index2, row2 in df_city.iterrows():
        print(index2)
        for index1, row1 in df.iterrows():
            if (abs(row2["lng"] - row1["lng"]) < 0.000139) & (abs(row2["lat"] - row1["lat"]) < 0.000139):
                df.loc[index1:index1, ('type')] = -1  # 将该列的type进行修改
                break

    df.to_csv(r'C:\D-drive-37093\PycharmWorkSpace\apf_enemy\map.csv', index=False)


if __name__ == '__main__':
    start_lnglat = (104.09256,31.0331)
    end_lnglat = (104.13488,31.06554)
    read_map_info_from_dem(start_lnglat, end_lnglat)

