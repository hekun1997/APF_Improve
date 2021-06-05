import os
import numpy as np

import Utils
from Agent_Obstacle_Goal import *
from MapProcess import position_to_LngLatNum
import pandas as pd


def PtoXY(P):
    xy = (P.x, P.y)
    return xy


def calculate_angle(cosValue, sinValue):
    global theta
    if sinValue >= 0:  # 角度在0-pi之间
        theta = math.acos(cosValue)
    elif sinValue < 0:  # 角度在pi-2pi
        # cosAlpha=-cosValue
        Alpha = math.acos(-cosValue)
        theta = Alpha + math.pi
    return theta


# 计算C点在AB直线的哪侧
def which_side(A_position,B_position,C_position):
    Vctor_AtoC=np.array([C_position.x-A_position.x,C_position.y-A_position.y])
    Vctor_BtoC=np.array([C_position.x-B_position.x,C_position.y-B_position.y])
    return np.cross(Vctor_AtoC,Vctor_BtoC)


# 计算C点到AB直线的距离
def calculate_Safe_dist(A_position,B_position,C_position):
    Vctor_AtoB = np.array([B_position.x - A_position.x, B_position.y - A_position.y])
    Vctor_AtoC = np.array([C_position.x - A_position.x, C_position.y - A_position.y])
    S=np.cross(Vctor_AtoB,Vctor_AtoC)
    A_B = math.sqrt((A_position.x - B_position.x) ** 2 + (A_position.y - B_position.y) ** 2)
    return abs(S/A_B)


# 找到和goal_position同一侧的障碍物
def find_oneside_obstacle(agent,goal,angle,obstacles):
    theta=angle+math.pi/2
    dists_goal = []
    vertical_spot = Goal(Position(agent.position.x + agent.move_radius * math.cos(theta),
                                  agent.position.y + agent.move_radius * math.sin(theta)))
    goal_flag = 0
    if which_side(agent.position, vertical_spot.position, goal.position) < 0:
        goal_flag = -1
    elif which_side(agent.position, vertical_spot.position, goal.position) > 0:
        goal_flag = 1
    for obstacle in obstacles:
        direction_flag = 0
        if which_side(agent.position, vertical_spot.position, obstacle.position) > 0:
            direction_flag = 1
        elif which_side(agent.position, vertical_spot.position, obstacle.position) < 0:
            direction_flag = -1
        # 障碍物和目标点同号则为同一侧
        if direction_flag == goal_flag:
            dists_goal.append(obstacle)
    return dists_goal


def calculate_dist_visitlist(a,b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


# 确认一下，这是靠近obs的角
def angle_of_ObstoGoal(obs,goal):
    cosValue = (goal.position.x - obs.position.x) / (obs.position.calculate_distance(goal.position))
    sinValue = (goal.position.y - obs.position.y) / (obs.position.calculate_distance(goal.position))
    theta=calculate_angle(cosValue,sinValue)
    return theta


def nearest_of_Obstacles(agent,obstacles):
    min_dist=Position.calculate_distance(agent.position,obstacles[0].position)
    min_obs=obstacles[0]
    for obstacle in obstacles:
        if Position.calculate_distance(agent.position,obstacle.position) <min_dist:
            min_dist = Position.calculate_distance(agent.position,obstacle.position)
            min_obs = obstacle
    return min_obs


# 计算是否陷入局部最小值
def out_to_trap(agent,goal,visited_list,obstacles):
    length = len(visited_list)
    flag = 0
    spot = Goal(Position(0, 0))
    if ((calculate_dist_visitlist(visited_list[length-1],visited_list[length-2])<0.3)|(calculate_dist_visitlist(visited_list[length-1],visited_list[length-3])<0.3)|(calculate_dist_visitlist(visited_list[length-2],visited_list[length-3])<0.3))==True:

        flag = 1
        
        F_att_x, F_att_y = goal.get_attraction_force(agent.position)
        cos_value = F_att_x / math.sqrt(F_att_x ** 2 + F_att_y ** 2)  # 求出来的是值
        sin_value = F_att_y / math.sqrt(F_att_x ** 2 + F_att_y ** 2)
        theta = calculate_angle(cos_value, sin_value)
        if theta > 2 * math.pi:
            theta -= 2 * math.pi
        elif theta < 0:
            theta += 2 * math.pi

        # 拿到theta后，找到目标一侧的障碍物组
        oneside_obstacles = find_oneside_obstacle(agent, goal, theta, obstacles)
        # 在将目标点和当前位置连线，找到障碍物少的一侧
        goal_left = Goal(Position(agent.position.x + 3 * math.cos(theta + math.pi/2), agent.position.y + 3 * math.sin(theta + math.pi/2)))
        target_left = find_oneside_obstacle(agent, goal_left, theta + math.pi/2, oneside_obstacles) #注意：这里只是一边的障碍物
        goal_right = Goal(Position(agent.position.x + 3 * math.cos(theta - math.pi/2), agent.position.y + 3 * math.sin(theta - math.pi/2)))
        target_right = find_oneside_obstacle(agent, goal_right, theta - math.pi/2, oneside_obstacles)  # 注意：这里只是一边的障碍物
        # 判断那边的障碍物少，并找到障碍物少的一侧的最近障碍物：

        if len(target_left) >= len(target_right):
            # 判断该侧障碍物的个数是否为零
            if len(target_right) == 0:
                theta2=theta-math.pi/4
                if theta2 > 2 * math.pi:
                    theta2 -= 2 * math.pi
                elif theta2 < 0:
                    theta2 += 2 * math.pi
                min_obs = Obstacle(Position(agent.position.x + 2 * math.cos(theta2),
                                            agent.position.y + 2 * math.sin(theta2)))
            else:
                min_obs = nearest_of_Obstacles(agent, target_right)
        else:
            if len(target_left) == 0:
                theta2 = theta + math.pi / 4
                if theta2 > 2 * math.pi:
                    theta2 -= 2 * math.pi
                elif theta2 < 0:
                    theta2 += 2 * math.pi
                min_obs = Obstacle(Position(agent.position.x + 2 * math.cos(theta2),
                                            agent.position.y + 2 * math.sin(theta2)))
            else:
                min_obs = nearest_of_Obstacles(agent, target_left)
        # 当前点与最近障碍物连线，计算角度后在偏移角度，类似于做切线
        alpha = angle_of_ObstoGoal(agent, min_obs)  # 这是两者连线的角度，还需要往切线偏移的角度
        L = Position.calculate_distance(agent.position, min_obs.position)
        alpha_s = calculate_angle(math.sqrt(L**2-1**2)/L, 1/L)+0.002
        # 根据障碍物多少来判断角度往那边走
        if len(target_left) >= len(target_right):
            final_alpha = alpha - alpha_s
        else:
            final_alpha = alpha + alpha_s
        # 设置虚拟目标点， 到最近障碍物的距离+4倍步长
        spot = Goal(Position(agent.position.x + (L+2) * math.cos(final_alpha),
                             agent.position.y + (L+2) * math.sin(final_alpha)))
        # 判断虚拟目标点是否与障碍物重合
        UnSafe = 0
        for obstacle in obstacles:
            if Position.calculate_distance(obstacle.position, spot.position) < obstacle.size:
                UnSafe = 1
                break
        while UnSafe == 1:
            spot.position.x += 0.2
            spot.position.y += 0.2
            UnSafe = 0
            for obstacle in obstacles:
                if Position.calculate_distance(obstacle.position, spot.position) < obstacle.size:
                    UnSafe = 1
                    break
    return flag, spot


# 判断障碍物在agent和goal连线的哪边
def which_side_of_obs(agent,goal,obstacles):
    count_less, count_more = 0, 0
    block_more, block_less = [], []
    for obstacle in obstacles:
        if which_side(agent.position, goal.position, obstacle.position) >= 0:
            count_more += 1
            block_more.append(obstacle)
        elif which_side(agent.position, goal.position, obstacle.position) < 0:
            count_less += 1
            block_less.append(obstacle)
    return count_less, count_more, block_less, block_more,


# 计算离agent和goal连线最近的障碍物
def calculate_obs_of_nearest(agent,goal,obstacles):
    the_obs = obstacles[0]
    the_dis = calculate_Safe_dist(agent.position, goal.position, the_obs.position)
    for obstacle in obstacles:
        if calculate_Safe_dist(agent.position, goal.position, obstacle.position) > the_dis:
            the_obs = obstacle
            the_dis = calculate_Safe_dist(agent.position, goal.position, obstacle.position)
    return the_obs


def who_is_the_min_of_two_sides(agent,goal,block_less, block_more):
    obs_of_less = block_less[0]
    dis_of_less = calculate_Safe_dist(agent.position, goal.position, obs_of_less.position)
    for obstacle in block_less:
        dis = calculate_Safe_dist(agent.position, goal.position, obstacle.position)
        if dis > dis_of_less:
            obs_of_less = obstacle
            dis_of_less = dis

    obs_of_more = block_more[0]
    dis_of_more = calculate_Safe_dist(agent.position, goal.position, obs_of_more.position)
    for obstacle in block_more:
        dis = calculate_Safe_dist(agent.position, goal.position, obstacle.position)
        if dis > dis_of_more:
            obs_of_more = obstacle
            dis_of_more = dis

    if dis_of_more > dis_of_less:
        return obs_of_less
    else:
        return obs_of_more


def make_map(X,Y):
    map_list = []
    for i in range(Y):
        for j in range(X):
            x = j
            y = i
            map_list.append((x,y))
    return map_list


def position_to_lnglat(visited_list, Y, df):
    position = []
    for item in visited_list:
        num = position_to_LngLatNum(item,Y)
        position.append((df['lng'][num], df['lat'][num]))
    return position


def lnglat_to_XY(lnglat, df, Y):
    lng = lnglat[0]
    lat = lnglat[1]
    up = 0
    down = len(df) - 1
    while (up <= down):
        mid = up + (down - up) // 2
        if ((df['lng'][mid] - lng < 0.000139) & (df['lng'][mid] - lng > -0.000139)):
            # 经度符合
            lng = df['lng'][mid]
            break
        if (df['lng'][mid] - lng > 0.000139):
            down = mid - 1
        if (df['lng'][mid] - lng < -0.000139):
            up = mid + 1
        # 找到所有经度等于lng的df，在挨个遍历直到找到该点，此时返回index
    df_lat = df[df['lng'] == lng]
    index = 0
    indexs = list(df_lat.index.values)  # 找到df_lat的所有index

    # 开始查找纬度符合的点
    up = indexs[0]
    down = indexs[len(indexs)-1]
    while (up <= down):
        mid = up + (down - up) // 2
        if ((df['lat'][mid] - lat < 0.000139) & (df['lat'][mid] - lat > -0.000139)):
            # 经度符合
            index = mid
            break
        if (df['lat'][mid] - lat > 0.000139):
            up = mid + 1
        if (df['lat'][mid] - lat < -0.000139):
            down = mid - 1
    x = math.floor(index / Y)
    y = Y - index % Y - 1
    return (x*6,y*6)


# 把map中的index转为xy的形式
def index_to_XY(list_nums, Y):
    res = []
    for item in list_nums:
        x = math.floor(item/Y)
        y = Y-item%Y-1
        res.append((x,y))
    return res


# 将position (x,y)如(0,1)转为经纬度表的序号
def XY_to_index(position, Y):
    x = position[0]
    y = position[1]
    num = x*Y + Y-y-1 # 因为从零开始,所以减1
    return num


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
    else:
        # 下坡
        tan_p = 30.9/(curr_h-next_h)
        if tan_p > math.tan(math.pi/3):
            return 1
        else:
            return 0


# 去掉坡度太陡的可能路线
def dropout_gradient(agent_position,possible_moves_list,Y,df):
    # 将xy形式的点转化为map表中的index
    curr_index = XY_to_index(agent_position, Y)
    curr_h = df['height'][curr_index]

    for item in possible_moves_list:
        next_index = XY_to_index(item, Y)
        next_h = df['height'][next_index]
        if(calculate_gradient(curr_h,next_h)==0):
            possible_moves_list.remove(item)
    return possible_moves_list


# 将输入的障碍物转化成XY的形式，并加入到obs_XY中
def dynamic_obs_to_obs_XY(dynamic_obs, obs_XY, df, Y):
    # 首先将经纬度映射到df中的点，在根据index转换为（x,y）
    list_index = []
    for item in dynamic_obs:
        # 先二分找经度item[0]
        up = 0
        down = len(df)-1
        lng = item[0]
        lat = item[1]
        while(up<=down):
            mid = up + (down - up)//2
            if( (df['lng'][mid]-item[0]<0.000139) & (df['lng'][mid]-item[0]>-0.000139) ):
                # 经度符合
                lng = df['lng'][mid]
                break
            if(df['lng'][mid]-item[0]>0.000139):
                down = mid - 1
            if(df['lng'][mid]-item[0]<-0.000139):
                up = mid + 1
        # 找到所有经度等于lng的df，在挨个遍历直到找到该点，此时返回index
        df_lat = df[df['lng'] == lng]
        index = 0
        indexs = list(df_lat.index.values)  # 找到df_lat的所有index
        # 开始查找纬度符合的点
        up = indexs[0]
        down = indexs[len(indexs) - 1]
        while (up <= down):
            mid = up + (down - up) // 2
            if ((df['lat'][mid] - item[1] < 0.000139) & (df['lat'][mid] - item[1] > -0.000139)):
                # 经度符合
                index = mid
                break
            if (df['lat'][mid] - item[1] > 0.000139):
                up = mid + 1
            if (df['lat'][mid] - item[1] < -0.000139):
                down = mid - 1
        list_index.append(index)
    # 最后的index为该点的index，此时需要转化为（x，y）的形式
    res_XY = index_to_XY(list_index, Y)

    # 将其加入到obs_XY中
    for item in res_XY:
        obs_XY.append(item)
    return obs_XY


def input_obs_to_xy(dynamic_obs, obs_XY, lnglat_range):
    for obstacle in dynamic_obs:
        obstacle_xy = Utils.lnglat_to_xy(obstacle, lnglat_range)
        obs_XY.append(obstacle_xy)

    return obs_XY



def enemys_to_enemy_XY(enemys,df,Y):
    # 首先将经纬度映射到df中的点，在根据index转换为（x,y）
    list_index = []
    for item in enemys:
        # 先二分找经度item[0]
        up = 0
        down = len(df) - 1
        lng = item[0]
        lat = item[1]
        while (up < down):
            mid = up + (down - up) // 2
            if ((df['lng'][mid] - item[0] < 0.000139) & (df['lng'][mid] - item[0] > -0.000139)):
                # 经度符合
                lng = df['lng'][mid]
                break
            if (df['lng'][mid] - item[0] > 0.000139):
                down = mid - 1
            if (df['lng'][mid] - item[0] < -0.000139):
                up = mid + 1
        # 找到所有经度等于lng的df，在挨个遍历直到找到该点，此时返回index
        df_lat = df[df['lng'] == lng]
        # 开始查找纬度符合的点
        up = 0
        down = len(df_lat) - 1
        index = 0
        while (up <= down):
            mid = up + (down - up) // 2
            if ((df['lat'][mid] - item[1] < 0.000139) & (df['lat'][mid] - item[1] > -0.000139)):
                # 经度符合
                index = mid
                break
            if (df['lat'][mid] - item[1] > 0.000139):
                up = mid + 1
            if (df['lat'][mid] - item[1] < -0.000139):
                down = mid - 1
        list_index.append(index)
    # 最后的index为该点的index，此时需要转化为（x，y）的形式
    res_XY = index_to_XY(list_index, Y)
    return res_XY


def enemy_XY_to_enemys_XY(enemy_XY, X, Y):
    size = Enemy(Position(1, 1)).size
    res = []
    for enemy in enemy_XY:
        # 周围填障碍物
        for i in range(-size,size):
            for j in range(-size,size):
                if(calculate_dist_visitlist(enemy,(enemy[0]+i,enemy[1]+j))<size):
                    if enemy[0]+i < 0 or enemy[0]+i > X:
                        continue
                    if enemy[1]+j < 0 or enemy[1]+j > Y:
                        continue
                    res.append((enemy[0]+i, enemy[1]+j))
    return res


def drawAll(obs_XY, enemy_XY, map_list, start_position, end_position,visited_list):
    color_start = '#FFFFFF' #起点颜色
    color_end = '#FF0000'  #终点颜色
    colors1 = '#A2B5CD'  # 原始点的颜色
    colors2 = '#66FF99'  # agent每步的颜色
    colors3 = '#000000'  # 障碍物颜色
    obstacles = []
    for item in obs_XY:
        obstacles.append(Obstacle(Position(item[0], item[1])))

    enemys = []
    for item in enemy_XY:
        enemys.append(Enemy(Position(item[0], item[1])))

    # 画出所有的7000个点、障碍物、起始点位置
    for item in map_list:
        plt.scatter(item[0], item[1], c=colors1)

    # 画出障碍物
    for obstacle in obstacles:
        obstacle.draw_four(colors3)

    # 画出敌军
    for enemy in enemys:
        enemy.draw_four()

    for item in visited_list:
        plt.scatter(item[0], item[1], color=colors2)

    # 画出起终点位置
    plt.scatter(start_position[0], start_position[1], color=color_start)
    plt.scatter(end_position[0], end_position[1], color=color_end)
    plt.show()


def visited_list_to_res(visited_list):
    temp = []
    for item in visited_list:
        temp.append((round(item[0]), round(item[1])))

    # 去掉重复的
    res = []
    for i in range(0, len(temp)):
        if (temp[i][0] == temp[i-1][0]) & (temp[i][1] == temp[i-1][1]):
            continue
        else:
            res.append(temp[i])
    # print(res)
    return res


def sysIN(a):
    start = eval(a[0])
    end = eval(a[1])

    dynamic_obs = []
    for item in eval(a[2]):
        dynamic_obs.append(item)

    enemys = []
    for item in eval(a[3]):
        enemys.append(item)

    return start, end, dynamic_obs, enemys


def gradient_to_use(startXY, endXY):
    # 先对起终点的坐标进行处理，需要将起终点画一个矩形框，将该范围内的障碍物取出
    # 找到该矩形的左上和右下点
    left, up, right, down = 0, 0, 0, 0
    if startXY[0] <= endXY[0]:
        left = startXY[0]
        right = endXY[0]
    else:
        left = endXY[0]
        right = startXY[0]

    if startXY[1] <= endXY[1]:
        down = startXY[1]
        up = endXY[1]
    else:
        down = endXY[1]
        up = startXY[1]

    left_up = (left, up)  # 左上
    right_down = (right, down)  # 右下

    df_grad = pd.read_csv(r'C:\D-drive-37093\PycharmWorkSpace\apf_enemy\gradient.csv', encoding='gbk')
    # 二分查找能使用的障碍物,先找left_up这个点
    s = 0  # start
    e = len(df_grad)-1  # end
    while s <= e:
        mid = (s + e)//2
        if df_grad['x'][mid] >= left:
            e = mid - 1
        else:
            s = mid + 1
    # 结果为e
    df_y = df_grad[df_grad['x'] == df_grad['x'][e]]

    indexs = list(df_y.index.values)  # 找到df_lat的所有index
    s = indexs[0]
    e = indexs[len(indexs) - 1]
    while s <= e:
        mid = (s + e) // 2
        if df_grad['y'][mid] > up:
            s = mid + 1
        else:
            e = mid - 1
    left_up_index = s

    # 二分查找能使用的障碍物,再找right_down这个点
    s = 0  # start
    e = len(df_grad) - 1  # end
    while s <= e:
        mid = (s + e) // 2
        if df_grad['x'][mid] >= right:
            e = mid - 1
        else:
            s = mid + 1
    # 结果为e
    df_y = df_grad[df_grad['x'] == df_grad['x'][e]]

    indexs = list(df_y.index.values)  # 找到df_lat的所有index
    s = indexs[0]
    e = indexs[len(indexs) - 1]

    while s <= e:
        mid = (s + e) // 2
        if df_grad['y'][mid] > down:
            s = mid + 1
        else:
            e = mid - 1
    right_down_index = s

    # res = df_grad[df_grad.index>=left_up_index]
    # res = res[res.index <= right_down_index]
    gradients = []
    for i in range(left_up_index, right_down_index+1):
        gradients.append(Obstacle(Position(df_grad['x'][i], df_grad['y'][i])))
    return gradients
