import math
# import gdal
from matplotlib import pyplot as plt
from osgeo import gdal

import gradient


def get_dem_info(path):
    dataset = gdal.Open(path)
    return dataset


# 获取地图障碍物，需要多次调用文件，每一格都需要打开一次，这里一个经纬度只需要打开一次。

def get_dataset_from_cache(ele_dict, concat_lnglat, path):
    if concat_lnglat in ele_dict:
        return ele_dict[concat_lnglat]

    dataset = get_dem_info(path)
    gtf, elevation_info_array = dataset.GetGeoTransform(), dataset.ReadAsArray().astype(float)
    ele_dict[concat_lnglat] = [gtf, elevation_info_array]

    return [gtf, elevation_info_array]


def get_elevation(ele_dict, lnglat):
    concat_lnglat, path = concat_lnglat_path(lnglat[0], lnglat[1])
    # todo 6.23 优化读取逻辑
    # dataset = get_dem_info(path)
    gtf, elevation_info_array = get_dataset_from_cache(ele_dict, concat_lnglat, path)
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
    # dem_gcs = dataset
    # elevation_info_array = dem_gcs.ReadAsArray().astype(float)

    # gtf = dataset.GetGeoTransform()
    # print(gtf)

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


def concat_lnglat_path(lng, lat, base_path=r'D:\PycharmWorkSpace\apf_enemy\Data', dir_prefix = 'ASTGTM2_'):
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

    return lnglat, path


def get_colors():
    colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple',
              'brown', 'orange', 'pink', 'grey', 'brown', 'purple', 'pink', 'magenta', 'deepskyblue',
              'y', 'crimson', 'r', 'c']
    return colors


def lnglat_to_xy(lnglat, lnglat_range, x_size, y_size):
    miny = lnglat_range['miny']  # min_lat
    maxy = lnglat_range['maxy']
    minx = lnglat_range['minx']  # min_lng
    maxx = lnglat_range['maxx']

    x = round(((lnglat[0] - minx) / (maxx - minx)) * x_size)  # 取整， 四舍五入，方便后面计算
    y = round(((lnglat[1] - miny) / (maxy - miny)) * y_size)

    return (x, y)


def list_lnglat_to_xy(list_lnglat, lnglat_range, x_size, y_size):
    miny = lnglat_range['miny']  # min_lat
    maxy = lnglat_range['maxy']
    minx = lnglat_range['minx']  # min_lng
    maxx = lnglat_range['maxx']

    list_xy = list()

    for lnglat in list_lnglat:
        x = round(((lnglat[0] - minx) / (maxx - minx)) * x_size)  # 取整， 四舍五入，方便后面计算
        y = round(((lnglat[1] - miny) / (maxy - miny)) * y_size)
        list_xy.append((x, y))

    return list_xy


def xy_to_lnglat(xy, lnglat_range, x_size, y_size):
    miny = lnglat_range['miny']  # min_lat
    maxy = lnglat_range['maxy']
    minx = lnglat_range['minx']  # min_lng
    maxx = lnglat_range['maxx']

    lng = (xy[0] / x_size) * (maxx - minx) + minx
    lat = (xy[1] / y_size) * (maxy - miny) + miny

    return (lng, lat)


def list_xy_to_lnglat(list_xy, lnglat_range, x_size, y_size):
    miny = lnglat_range['miny']  # min_lat
    maxy = lnglat_range['maxy']
    minx = lnglat_range['minx']  # min_lng
    maxx = lnglat_range['maxx']

    list_lnglat = list()

    for xy in list_xy:
        lng = (xy[0] / x_size) * (maxx - minx) + minx
        lat = (xy[1] / y_size) * (maxy - miny) + miny
        list_lnglat.append((lng, lat))

    return list_lnglat


def get_gradient(start_lnglat, end_lnglat):
    gradients = gradient.create_gradient(start_lnglat, end_lnglat)
    return gradients


def check_obs_and_enemy(dynamic_obs, enemies, lnglat_range):
    min_lat = lnglat_range['miny']  # min_lat
    max_lat = lnglat_range['maxy']
    min_lng = lnglat_range['minx']  # min_lng
    max_lng = lnglat_range['maxx']

    ret_obs = list()
    ret_enemies = list()

    for obs in dynamic_obs:  # lnglat
        if min_lng < obs[0] < max_lng and min_lat < obs[1] < max_lat:
            ret_obs.append(obs)

    for enemy in enemies:
        if min_lng < enemy[0] < max_lng and min_lat < enemy[1] < max_lat:
            ret_enemies.append(enemy)

    return ret_obs, ret_enemies


def draw_lnglat_path(lnglat_path, start, end, dynamic_obs, lnglat_range, x_size, y_size):
    x = [start[0], end[0]]
    y = [start[1], end[1]]
    plt.plot(x, y, '.', c='red')

    x = list()
    y = list()
    for lnglat in lnglat_path:
        x.append(lnglat[0])
        y.append(lnglat[1])
    plt.plot(x, y, '.', c='green')

    x = list()
    y = list()
    for ob in dynamic_obs:
        xy = xy_to_lnglat(ob, lnglat_range, x_size, y_size)
        x.append(xy[0])
        y.append(xy[1])
    plt.plot(x, y, '.', c='black')

    plt.show()
    print(lnglat_path)


def draw_xy_path(xy_path, start, end, obs):
    x = [start[0], end[0]]
    y = [start[1], end[1]]
    plt.plot(x, y, '.', c='red')

    x = list()
    y = list()
    for lnglat in xy_path:
        x.append(lnglat[0])
        y.append(lnglat[1])
    plt.plot(x, y, '.', c='green')

    x = list()
    y = list()
    for ob in obs:
        x.append(ob[0])
        y.append(ob[1])
    plt.plot(x, y, '.', c='black')

    plt.show()


def assemble_input_data(input_data):
    start = eval(input_data[0])
    end = eval(input_data[1])

    dynamic_obs = []
    for item in eval(input_data[2]):
        dynamic_obs.append(item)

    enemies = []
    for item in eval(input_data[3]):
        enemies.append(item)

    return start, end, dynamic_obs, enemies


if __name__ == '__main__':
    input_data = ['(103.91496,31.25339)', '(103.95037,31.28386)',
                  '[]', '[]']

    # 其他模块调用路径规划算法,需要下列代码
    # input_data = []
    # for i in range(1, len(sys.argv)):
    #     input_data.append((sys.argv[i]))

    # start, end, dynamic_obs, enemys = sysIN(input_data)
    # obstacle = get_gradient(start, end)
    #
    # x_size, y_size, lnglat_range = create_map_params(start, end)
    #
    # print(list_xy_to_lnglat(obstacle, lnglat_range, x_size, y_size))
