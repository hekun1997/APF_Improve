import math
import gdal


def get_dem_info(path):
    dataset = gdal.Open(path)
    return dataset


def get_elevation(lnglat):
    path = concat_lnglat_path(lnglat[0], lnglat[1])
    dataset = get_dem_info(path)
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
    # dataset = get_dem_info(path)
    dem_gcs = dataset
    elevation_info_array = dem_gcs.ReadAsArray().astype(float)

    gtf = dataset.GetGeoTransform()
    print(gtf)

    x_geo = lnglat[0]  # longitude
    y_geo = lnglat[1]  # latitude

    x = int(round((x_geo - gtf[0]) / gtf[1]))
    y = int(round((y_geo - gtf[3]) / gtf[5]))

    return elevation_info_array[y, x]


# unused.
def adjustment_lnglat(lng, lat, dataset):
    XSize = dataset.RasterXSize  # 网格的X轴像素数量
    YSize = dataset.RasterYSize  # 网格的Y轴像素数量

    geoTransform = dataset.GetGeoTransform()

    lng_start = geoTransform[0]
    lat_start = geoTransform[3]

    lng_pixel = geoTransform[1]
    lat_pixel = geoTransform[5]

    lng_end = lng_start + XSize * lng_pixel
    lat_end = lat_start + YSize * lat_pixel

    if lng < min(lng_start, lng_end):
        lng += 1
    elif lng > max(lng_start, lng_end):
        lng -= 1

    if lat < min(lat_start, lat_end):
        lat += 1
    elif lat > max(lat_start, lat_end):
        lat -= 1

    return (lng, lat)


def concat_lnglat_path(lng, lat, base_path='C:\\D-drive-37093\\PycharmWorkSpace\\apf_enemy\\Data', dir_prefix = 'ASTGTM2_'):
    lng = math.ceil(lng)
    lat = math.floor(lat)
    lnglat = ''
    if lat > 0:
        lnglat += 'N' + str(lat)
    else:
        lnglat += 'S' + str(lat)

    if lng > 0:
        lnglat += 'E' + str(lng)
    else:
        lnglat += 'W' + str(lng)

    path = base_path + '\\' + dir_prefix + lnglat + '\\' + dir_prefix + lnglat + '_dem.tif'

    return path


def get_colors():
    colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple',
              'brown', 'orange', 'pink', 'grey', 'brown', 'purple', 'pink', 'magenta', 'deepskyblue',
              'y', 'crimson', 'r', 'c']
    return colors


if __name__ == '__main__':
    # h = get_elevation((102.99986111111112, 32.00013888888889), path)
    lnglat = (102.99986111111102, 32.00013888888889)

    elevation = get_elevation(lnglat)


    print(elevation)
