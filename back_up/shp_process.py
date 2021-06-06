import numpy as np
import ogr
import shapefile
import csv
import sys
import ospybook as pd
from ospybook.vectorplotter import VectorPlotter
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import geometry
import os
import pandas


def shp2csv(shp_file_path, csv_file_path, shp_file_encoding='utf-8', csv_file_encoding ='utf-8'):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shp_file_path, 0)
    if dataSource is None:  # 判断是否成功打开
        print('could not open')
        sys.exit(1)
    else:
        print('done!')

    layer = dataSource.GetLayer(0)

    shp_file = shapefile.Reader(shp_file_path, encoding=shp_file_encoding)

    file = open(csv_file_path, mode='w+', encoding=csv_file_encoding, newline='')
    csv_file = csv.writer(file)

    header_fields = []
    for fields in shp_file.fields:
        header_fields.append(fields[0])

    header_fields.append('Geometry')
    header_fields.append('Type')

    csv_file.writerow(header_fields)

    shp_len = len(shp_file)

    for i in range(shp_len):
        attr = []

        record = shp_file.record(i)

        attr.append("0")  # ('DeletionFlag', 'C', 1, 0)
        attr.append(str(record[0]))  # ['NAME', 'C', 100, 0]
        attr.append(str(record[1]))  # ['KIND', 'C', 30, 0]

        feat = layer.GetFeature(i)  # 提取数据层中的第一个要素

        type_and_geo = str(feat.GetGeometryRef()).split(' ', maxsplit=1)  # 提取该要素的轮廓坐标

        shp_type = type_and_geo[0]
        geo = type_and_geo[1]

        attr.append(geo)
        attr.append(shp_type)

        csv_file.writerow(attr)


def shp_show():
    # shp_file_path = r'C:\D-drive-37093\research\路径规划\China_Roads_All_WGS84_2016\县道_polyline.shp'
    # csv_file_path = r'县道_polyline_5_28.csv'
    # shp2csv(shp_file_path=shp_file_path, csv_file_path=csv_file_path, shp_file_encoding='GBK', csv_file_encoding='GBK')
    filename = r'C:\D-drive-37093\research\路径规划\China_Roads_All_WGS84_2016'
    driver = ogr.GetDriverByName('ESRI Shapefile')  # 这个函数是不区分大小写的

    shp_test = driver.Open(filename, 0)  # 0是只读，1是可写
    if shp_test is None:
        print('could not open')
        sys.exit(1)

    print(dir(shp_test))
    layer_count = shp_test.GetLayerCount()

    for i in range(layer_count):
        print('正在绘制', i)
        lyr = shp_test.GetLayerByIndex(i)

        vp = VectorPlotter(True)
        try:
            vp.plot(lyr, 'bo')
            vp.draw()
        except:
            print('excep.')


def multi_shp_show():
    file1 = r'C:\D-drive-37093\research\路径规划\China_Roads_All_WGS84_2016\县界_面.shp'
    file2 = r'C:\D-drive-37093\research\路径规划\China_Roads_All_WGS84_2016\国道_线.shp'

    shp1 = gpd.read_file(file1, encoding='GBK')
    shp2 = gpd.read_file(file2, encoding='GBK')
    fig, ax = plt.subplots(figsize=(12, 8))
    ax = shp1.geometry.plot(ax=ax)
    ax = shp2.geometry.plot(ax=ax)
    fig.savefig('图1.png', dpi=300)


def shp_to_img():
    dir = r'C:\D-drive-37093\research\路径规划\China_Roads_All_WGS84_2016'
    filenames = os.listdir(dir)
    for filename in filenames:
        if 'shp' in filename:
            filepath = os.path.join(dir, filename)
            shp = gpd.read_file(filepath, encoding='GBK')
            fig, ax = plt.subplots(figsize=(12, 8))
            ax = shp.geometry.plot(ax=ax)
            fig.savefig(filename + '_5_28.png', dpi=600)


def cut_shape():
    china = gpd.read_file(r'C:\D-drive-37093\research\路径规划\China_Roads_All_WGS84_2016\行人道路_线.shp')
    # ax = china.plot(alpha=0.05)
    # 103.86369,31.30775  103.87486,31.31707
    sichuan = china.cx[103.86369:103.87486, 31.30775:31.31707]

    ax = sichuan.plot(color='red')
    plt.show()


def print_all_line():
    dir = r'C:\D-drive-37093\research\路径规划\China_Roads_All_WGS84_2016'
    filenames = ['铁路_线.shp', '高速公路_线.shp', '县道_polyline.shp', '乡镇村道_polyline.shp', '行人道路_线.shp', '公园绿地_面.shp',
                 '国道_线.shp', '九级路_线.shp', '轮渡_polyline.shp', '其他路_polyline.shp', '省道_线.shp', '水系_面.shp',
                 '铁路_线.shp']

    colors = ['yellow', 'brown', 'blue', 'red', 'coral', 'orange', 'green', 'aquamarine', 'purple', 'pink', 'black',
              'grey']
    i = 0
    fig, ax = plt.subplots(dpi=500, figsize=(24, 8))
    # 104.2642,31.18343 104.49252,31.04799
    for filename in filenames:
        all_df = gpd.read_file(os.path.join(dir, filename))
        part_df = all_df.cx[104.2642:104.49252, 31.04799:31.18343]  # lng lat
        if len(part_df) > 0:
            ax = part_df.plot(ax=ax, color=colors[i])
            i += 1
    fig.savefig('图2.png')


if __name__ == '__main__':
    print_all_line()
