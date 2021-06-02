from osgeo import gdal
from gdalconst import *
import sys

def read_elevation_info(image_path):
    """
    desc
    :param image_path: the image path ready to read.
    :return:
    """
    data = []
    dataset = gdal.Open(image_path, GA_ReadOnly)
    if dataset is None:
        print("Unable to open image file.")
        return data
    else:
        print("Open image file success.")

        geoTransform = dataset.GetGeoTransform()
        print(geoTransform)
        im_proj = dataset.GetProjection()  # 获取投影信息
        print(im_proj)
        bands_num = dataset.RasterCount
        print("Image height:" + dataset.RasterYSize.__str__() + " Image width:" + dataset.RasterXSize.__str__())
        print(bands_num.__str__() + " bands in total.")
        for i in range(bands_num):
            # 获取影像的第i+1个波段
            band_i = dataset.GetRasterBand(i + 1)
            # 读取第i+1个波段数据
            band_data = band_i.ReadAsArray(0, 0, band_i.XSize, band_i.YSize)
            print('band data. ', band_data)
            data.append(band_data)
            print("band " + (i + 1).__str__() + " read success.")
        print('return data. ', data)
        # 返回的data就是高程信息，海拔
        return data


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
