import pandas as pd
# import numpy as np
from math import radians, cos, sin, asin, sqrt
# from geopy.distance import geodesic

# longtitude经度
# latitude纬度

#传入地图左上和右下，两个点的值
def process_city(left_up,right_down):
    df = pd.read_csv("../Data/csv/县道_polyline.csv", encoding='gbk')
    Geometry = df['Geometry']
    # 把series转成dataframe
    df_Geometry = pd.DataFrame({'Geometry': Geometry.values})
    # print(len(df_Geometry))
    location = []
    for i in range(0,len(df_Geometry)):
        print("县道进度",i)
        data = df_Geometry.iloc[i, 0].replace('LINESTRING (', '').replace(')', '')
        a = data.split(',')
        b = []
        for i in range(len(a)):
            if i == 0:
                b.append((a[i].split(' ')[0], a[i].split(' ')[1]))
            else:
                # 除了第0个，其余split之后都多了一个空格，所有有变化
                b.append((a[i].split(' ')[1], a[i].split(' ')[2]))

        # location为标准格式：[(116.74496484, 116.74496484), (116.74469916, 116.74469916)]
        #加入到location之前，判断b中的值是否在四个点的范围内：
        for item in b:
            lon = float(item[0])
            lat = float(item[1])
            #判断经纬度是否在地图内,若在则加入到location中
            if (lon >= left_up[0]) & (lon <= right_down[0]) & (lat >= right_down[1]) & (lat <= left_up[1]):
                location.append((lon, lat))
    #县道中所有的都在location中
    res = pd.DataFrame({'location':location})
    res.to_csv('划定地图范围内的县道.csv',index=False)


#传入地图左上和右下，两个点的值
def process_village(left_up,right_down):
    df = pd.read_csv("../Data/csv/乡镇村道_polyline.csv", encoding='gbk')
    Geometry = df['Geometry']
    # 把series转成dataframe
    df_Geometry = pd.DataFrame({'Geometry': Geometry.values})
    # print(len(df_Geometry))
    location = []
    for i in range(0,len(df_Geometry)):
        print("乡镇村道进度",i)
        data = df_Geometry.iloc[i, 0].replace('LINESTRING (', '').replace(')', '')
        a = data.split(',')
        b = []
        for i in range(len(a)):
            if i == 0:
                b.append((a[i].split(' ')[0], a[i].split(' ')[1]))
            else:
                # 除了第0个，其余split之后都多了一个空格，所有有变化
                b.append((a[i].split(' ')[1], a[i].split(' ')[2]))

        # location为标准格式：[(116.74496484, 116.74496484), (116.74469916, 116.74469916)]
        #加入到location之前，判断b中的值是否在四个点的范围内：
        for item in b:
            lon = float(item[0])
            lat = float(item[1])
            #判断经纬度是否在地图内,若在则加入到location中
            if (lon >= left_up[0]) & (lon <= right_down[0]) & (lat >= right_down[1]) & (lat <= left_up[1]):
                location.append((lon, lat))
    #县道中所有的都在location中
    res = pd.DataFrame({'location':location})
    res.to_csv('划定地图范围内的乡镇村道.csv',index=False)

#传入地图左上和右下，两个点的值
def process_water(left_up,right_down):
    df = pd.read_csv("../Data/csv/水系_面.csv", encoding='gbk')
    Geometry = df['Geometry']
    # 把series转成dataframe
    df_Geometry = pd.DataFrame({'Geometry': Geometry.values})
    # print(len(df_Geometry))
    location = []
    for i in range(0,len(df_Geometry)):
        print("水系_面进度",i)
        data = df_Geometry.iloc[i, 0].replace('POLYGON ((', '').replace('))', '')
        a = data.split(',')
        b = []
        for i in range(len(a)):
            if i == 0:
                b.append((a[i].split(' ')[0], a[i].split(' ')[1]))
            else:
                # 除了第0个，其余split之后都多了一个空格，所有有变化
                b.append((a[i].split(' ')[1], a[i].split(' ')[2]))

        # location为标准格式：[(116.74496484, 116.74496484), (116.74469916, 116.74469916)]
        #加入到location之前，判断b中的值是否在四个点的范围内：
        for item in b:
            lon = float(item[0])
            lat = float(item[1])
            #判断经纬度是否在地图内,若在则加入到location中
            if (lon >= left_up[0]) & (lon <= right_down[0]) & (lat >= right_down[1]) & (lat <= left_up[1]):
                location.append((lon, lat))
    #县道中所有的都在location中
    res = pd.DataFrame({'location':location})
    res.to_csv('划定地图范围内的水系_面.csv',index=False)


def geodistance(lng1,lat1,lng2,lat2):
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)]) # 经纬度转换成弧度
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    distance=2*asin(sqrt(a))*6371*1000 # 地球平均半径，6371km
    return distance

#处理三个csv中的数据
def process_the_csv(left_up,right_down):
    process_city(left_up, right_down)
    process_village(left_up, right_down)
    process_water(left_up, right_down)

if __name__ == "__main__":
    # 5km*5km地图四个点的经纬度
    left_up = (103.9054200000, 31.336431)
    left_down = (103.905420, 31.246142)
    right_up = (104.009629, 31.336431)
    right_down = (104.0095866667, 31.24615322)

    process_the_csv(left_up,right_down)

    # print(geodistance(left_down[0],left_down[1],right_down[0],right_down[1]))