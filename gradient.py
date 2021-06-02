from MapProcess import *
import math
import pandas as pd
# todo 测试有多少个地方需要添加障碍物


def getNext(index,X, Y):
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
    num = x*Y + Y-y-1 # 因为从零开始,所以减1
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
