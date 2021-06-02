import numpy as np
from math import radians, cos, sin, asin, sqrt
import pandas as pd
import os


# lng经度，lat纬度
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
if __name__ == '__main__':
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
