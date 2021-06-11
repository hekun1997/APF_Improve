from osgeo import gdal
import numpy as np


class Dataset:
    def __init__(self, in_file):
        self.in_file = in_file  # Tiff或者ENVI文件

        dataset = gdal.Open(self.in_file)
        self.dataset = dataset
        self.XSize = dataset.RasterXSize  # 网格的X轴像素数量
        self.YSize = dataset.RasterYSize  # 网格的Y轴像素数量

        """
        note: 横纬竖经。东经正数，西经为负数。北纬为正数，南纬为负数。
              lat, Decrease from north to South.
              lng, Increase from west to East.

        geoTransform[0]：左上角像素经度  lng
        geoTransform[1]：影像宽度方向上的分辨率(经度范围/像素个数),向右移动一步
        geoTransform[2]：旋转, 0表示上面为北方
        geoTransform[3]：左上角像素纬度  lat
        geoTransform[4]：旋转, 0表示上面为北方
        geoTransform[5]：影像宽度方向上的分辨率(纬度范围/像素个数)
        """
        self.GeoTransform = dataset.GetGeoTransform()  # 投影转换信息
        self.ProjectionInfo = dataset.GetProjection()  # 投影信息

    def get_data(self, band):
        """
        读取第几个通道的数据
        :param band:
        :return:
        """
        dataset = gdal.Open(self.in_file)
        band = dataset.GetRasterBand(band)
        data = band.ReadAsArray()
        return data

    def get_lon_lat(self):
        """
        :return: all the Longitude, Latitude.
        """
        gtf = self.GeoTransform
        x_range = range(0, self.XSize)
        y_range = range(0, self.YSize)
        x, y = np.meshgrid(x_range, y_range)
        lon = gtf[0] + x * gtf[1] + y * gtf[2]
        lat = gtf[3] + x * gtf[4] + y * gtf[5]
        return lon, lat

    def get_all_elevation(self):
        """
        return all the elevation info array of given tif file.
        :return: elevation_info_array
        """
        dem_gcs = self.dataset
        elevation_info_array = dem_gcs.ReadAsArray().astype(np.float)
        return elevation_info_array

    # todo test.
    def get_elevation(self, site_latlng):
        """
        Note:
            Xgeo = gt[0] + Xpixel * gt[1] + Yline * gt[2]
            Ygeo = gt[3] + Xpixel * gt[4] + Yline * gt[5]

            Xpixel - Pixel/column of DEM
            Yline - Line/row of DEM

            Xgeo - Longitude
            Ygeo - Latitude

            [0] = Longitude of left-top pixel
            [3] = Latitude of left-top pixel

            [1] = + Pixel width
            [5] = - Pixel height

            [2] = 0 for north up DEM
            [4] = 0 for north up DEM

        :param site_latlng: {'lat' : Latitude, 'lng' : Longitude }
        :return:
        """
        dem_gcs = self.dataset
        elevation_info_array = dem_gcs.ReadAsArray().astype(float)

        gtf = self.GeoTransform

        y_geo = site_latlng['lat']  # latitude
        x_geo = site_latlng['lng']  # longitude

        x = int(round((x_geo - gtf[0]) / gtf[1]))
        y = int(round((y_geo - gtf[3]) / gtf[5]))

        return elevation_info_array[y, x]


if __name__ == '__main__':
    file_path = r'/Data/ASTGTM2_N31E103/ASTGTM2_N31E103_num.tif'
    tif = Dataset(file_path)

    print(tif.GeoTransform)

    site_latlng = {'lat': 31.33365322, 'lng': 103.90542}
    elevation = tif.get_elevation(site_latlng)
    print(elevation)
