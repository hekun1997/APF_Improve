import sys
from back_up.APF import *
from MapProcess import *
from Position import sysIN


def runTheProject(start, end, dynamic_obs, enemys):
    len_lng, len_lat, df, list_obs, list_road = read_map_info()

    # 最后的输出需要根据这个转换
    X = len_lng  # x 轴多少个点，30米一个点
    Y = len_lat

    # map_list = make_map(X, Y)  # py 图像化

    # obs_XY = []
    # for i in range(0,100):
    #     x=random.randint(0,29)
    #     y=random.randint(0,29)
    #     a=(x, y)
    #     obs_XY.append(a)
    # print(obs_XY)

    # 原始障碍物
    obs_XY = index_to_XY(list_obs, Y)

    # 加入传入的障碍物
    obs_XY = dynamic_obs_to_obs_XY(dynamic_obs, obs_XY, df, Y)

    # 加入传入的敌军信息
    enemy_XY = enemys_to_enemy_XY(enemys, df, Y)
    # enemy_XY = [(7, 7)]  # 测试数据


    # todo 2021-5-20 如何将道路添加到地图中
    road_XY = index_to_XY(list_road, Y)

    # 画出最初的地图
    # draw(obs_XY, map_list, start, end)

    visited_list = apf(X, Y, start, end, obs_XY, enemy_XY, df)
    # return visited_list
    print(position_to_lnglat(visited_list, Y, df))

    # 画出路径规划结果
    # drawAll(obs_XY, enemy_XY, map_list, start, end, visited_list)


if __name__ == '__main__':
    # input_data = ['(103.9468089,31.24781989)', '(103.9909756,31.27948656)', '[(103.90542,31.32615322)]', '[(103.90542, 31.33254211)]']
    input_data = ['(103.92363,31.26324)', '(103.9959,31.28437)',
                  '[]', '[]']

    # 其他模块调用路径规划算法,需要下列代码
    # input_data = []
    # for i in range(1, len(sys.argv)):
    #     input_data.append((sys.argv[i]))

    start, end, dynamic_obs, enemys = sysIN(input_data)

    runTheProject(start, end, dynamic_obs, enemys)
