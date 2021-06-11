from osgeo import gdal
import sys


def read_all_latlng(file_path):
    """
    运行很慢，容易爆内存
    :param file_path:
    :return:
    """
    filePath = '../Data/ASTGTM2_N26E100/ASTGTM2_N26E100_dem.tif'
    dataset = gdal.Open(filePath)

    adfGeoTransform = dataset.GetGeoTransform()

    # 左上角地理坐标 经度 纬度
    print(adfGeoTransform[0])
    print(adfGeoTransform[3])

    nXSize = dataset.RasterXSize  # 列数
    nYSize = dataset.RasterYSize  # 行数

    arrSlope = []  # 用于存储每个像素的（X，Y）坐标
    for i in range(nYSize):
        row = []
        for j in range(nXSize):
            px = adfGeoTransform[0] + i * adfGeoTransform[1] + j * adfGeoTransform[2]
            py = adfGeoTransform[3] + i * adfGeoTransform[4] + j * adfGeoTransform[5]
            col = [px, py]
            row.append(col)
        arrSlope.append(row)

    print(len(arrSlope))
    print(arrSlope)


if __name__ == '__main__':
    file_path = '../Data/ASTGTM2_N26E100/ASTGTM2_N26E100_dem.tif'
    elevation_info = read_elevation_info(file_path)
    print('-------')
    read_all_latlng(file_path)
