from MapProcess import *
import math
import pandas as pd
import numpy as np
# todo 测试有多少个地方需要添加障碍物


def getNext(index, X, Y):
    possible_moves_list = []
    x = math.floor(index / Y)
    y = Y - index % Y - 1
    if x == 0:
        if y == 0:
            possible_moves_list.append((x + 1, y))
            possible_moves_list.append((x, y + 1))
        elif y == (Y - 1):
            possible_moves_list.append((x + 1, y))
            possible_moves_list.append((x, y - 1))
        else:
            possible_moves_list.append((x + 1, y))
            possible_moves_list.append((x, y + 1))
            possible_moves_list.append((x, y - 1))
    elif x == (X - 1):
        if y == 0:
            possible_moves_list.append((x - 1, y))
            possible_moves_list.append((x, y + 1))
        elif y == (Y - 1):
            possible_moves_list.append((x - 1, y))
            possible_moves_list.append((x, y - 1))
        else:
            possible_moves_list.append((x, y + 1))
            possible_moves_list.append((x, y - 1))
            possible_moves_list.append((x - 1, y))
    elif (x != 0) & (x != (X - 1)):
        if y == 0:
            possible_moves_list.append((x, y + 1))
            possible_moves_list.append((x - 1, y))
            possible_moves_list.append((x + 1, y))
        elif y == (Y - 1):
            possible_moves_list.append((x, y - 1))
            possible_moves_list.append((x - 1, y))
            possible_moves_list.append((x + 1, y))
        else:
            possible_moves_list.append((x, y - 1))
            possible_moves_list.append((x, y + 1))
            possible_moves_list.append((x + 1, y))
            possible_moves_list.append((x - 1, y))
    return possible_moves_list


def XY_to_index(XY, Y):
    x = XY[0]
    y = XY[1]
    num = x*Y + Y-y-1  # 因为从零开始,所以减1
    return num


def index_to_XY(index, Y):
    x = math.floor(index / Y)
    y = Y - index % Y - 1
    return (x,y)


# 计算两点间的坡度差(0代表不能通过，1代表可以通过，通过为坡度小于30度)
def calculate_gradient(curr_h, next_h):
    # 目前设定两点间距离为30.9米
    # 用tan来近似代替坡度
    if(curr_h-next_h)<0:
        # 上坡
        tan_p = (next_h-curr_h)/30.9
        # 30度的值等于 math.tan(math.pi/6)
        if tan_p > math.tan(math.pi/6):
            return 0
        else:
            return 1
    elif(curr_h-next_h)==0:
        return 1
    else:
        # 下坡
        tan_p = 30.9/(curr_h-next_h)
        if tan_p > math.tan(math.pi/3):
            return 1
        else:
            return 0


# 判断是否存在坡度过陡的路线
def dropout_gradient(curr_index, possible_moves_list, Y, df, locaitons):
    curr_h = df['height'][curr_index]
    for item in possible_moves_list:
        next_index = XY_to_index(item, Y)
        next_h = df['height'][next_index]
        if(calculate_gradient(curr_h,next_h)==0):
            # todo 记住该点的坐标
            curr_XY = index_to_XY(curr_index,Y)
            location = ((item[0]+curr_XY[0])/2*6,(item[1]+curr_XY[1])/2*6)  # *6使得两点之间的距离扩大
            if location in locaitons:
                continue
            else:
                locaitons.append(location)
    return locaitons


len_lng, len_lat, df, list_obs, list_road = read_map_info()
X = len_lng
Y = len_lat

# locaitons为最后的需要加点的坐标
locaitons = []
for index in range(0, len(df)-1):
    possible_moves_list = getNext(index, X, Y)
    locaitons = dropout_gradient(index, possible_moves_list, Y, df, locaitons)

df = pd.DataFrame(locaitons)

df.columns = ['x', 'y']
# x按照升序排列，y按照降序排列
df.sort_values(["x", "y"], ascending=[True, False], inplace=True)

df.to_csv(r'C:\D-drive-37093\PycharmWorkSpace\apf_enemy\gradient.csv', index=False)

# 数据量太大，如果全放在obstacles中，需要运行很久


def get_surround_points(x, y, x_size, y_size):
    surround_points = list()
    if x == 0 and y == 0:  # 原点时
        surround_points.append((x + 1, y))  # 右边的点
        surround_points.append((x, y + 1))  # 上面的点

    elif x == x_size and y == 0:  # 最右角
        surround_points.append((x - 1, y))  # 左边的点
        surround_points.append((x, y + 1))  # 上面的点

    elif x == x_size and y == y_size:  # 最右上角
        surround_points.append((x, y - 1))  # 下面的点
        surround_points.append((x - 1, y))  # 左边的点

    elif x == 0 and y == y_size:  # 最左上角
        surround_points.append((x + 1, y))  # 右边的点
        surround_points.append((x, y - 1))  # 下面的点

    elif x != 0 and y == 0:  # x轴时
        surround_points.append((x - 1, y))  # 左边的点
        surround_points.append((x, y + 1))  # 上面的点
        surround_points.append((x + 1, y))  # 右边的点

    elif x == x_size and y != 0:  # 右边
        surround_points.append((x, y - 1))  # 下面的点
        surround_points.append((x - 1, y))  # 左边的点
        surround_points.append((x, y + 1))  # 上面的点

    elif x != 0 and y == y_size:  # 顶边
        surround_points.append((x, y - 1))  # 下面的点
        surround_points.append((x - 1, y))  # 左边的点
        surround_points.append((x + 1, y))  # 右边的点

    elif x == 0 and y != 0:  # 左边
        surround_points.append((x, y + 1))  # 上面的点
        surround_points.append((x + 1, y))  # 右边的点
        surround_points.append((x, y - 1))  # 下面的点

    elif x != 0 and y != 0:  # 不在边上
        surround_points.append((x - 1, y))  # 左边的点
        surround_points.append((x, y + 1))  # 上面的点
        surround_points.append((x + 1, y))  # 右边的点
        surround_points.append((x, y - 1))  # 下面的点

    return surround_points


def create_gradient(start_lnglat, end_lnglat):
    x_size, y_size, lnglat_range = create_map_params(start_lnglat, end_lnglat)

    gradients = list()  # 不能通过的点

    # todo 写的太烂了 需要优化
    # for x in range(0, x_size + 1):
    #     for y in range(0, y_size + 1):
    #         surr_points = get_surround_points(x, y, x_size, y_size)
    #         curr_lnglat = Utils.xy_to_lnglat((x, y), lnglat_range, x_size, y_size)
    #         curr_h = Utils.get_elevation(curr_lnglat)
    #         for point in surr_points:
    #             next_lnglat = Utils.xy_to_lnglat(point, lnglat_range, x_size, y_size)
    #             next_h = Utils.get_elevation(next_lnglat)
    #             if calculate_gradient(curr_h, next_h) == 0:
    #                 old_gradients.append(point

    array = np.zeros((x_size + 1, y_size + 1), dtype=float)

    for x in range(0, x_size + 1):  # 避免index out bounds 错误
        for y in range(0, y_size + 1):
            curr_lnglat = Utils.xy_to_lnglat((x, y), lnglat_range, x_size, y_size)
            curr_h = Utils.get_elevation(curr_lnglat)
            array[x, y] = curr_h

    for x in range(0, x_size + 1):
        for y in range(0, y_size + 1):
            surr_points = get_surround_points(x, y, x_size, y_size)
            curr_h = array[x, y]
            for point in surr_points:
                next_h = array[point[0], point[1]]
                if calculate_gradient(curr_h, next_h) == 0:
                    gradients.append(point)

    return gradients


if __name__ == '__main__':
    start_lnglat = (103.98345, 31.26724)
    end_lnglat = (103.99971, 31.27608)
    create_gradient(start_lnglat, end_lnglat)
