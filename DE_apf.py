from Position import *
from Agent_Obstacle_Goal import *


def de_apf(start, end, obs_XY, enemy_XY, k_att, k_rep, r_eff, r_pred):  # k_att 引力争议系数 k_rep 斥力争议系数 r_eff 障碍物影响范围 r_pred 障碍物预测距离
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    agent = Agent(Position(start[0], start[1]))
    goal = Goal(Position(end[0], end[1]), sigma=k_att)
    print(1)

    # 将传入的障碍物和敌军加入到obstacles中
    obstacles = []
    for item in obs_XY:
        obstacles.append(Obstacle(Position(item[0], item[1]), sigma=k_rep, effect_radius=r_eff))
    for item in enemy_XY:
        obstacles.append(Enemy(Position(item[0], item[1])))

    # agent.draw()
    #
    # goal.draw()
    # for i in range(len(obstacles)):
    #     obstacles[i].draw(ax)

    visited_list = []
    step_count = 0
    while Position.calculate_distance(agent.position, goal.position) >= 0.5:
        if step_count>1500:
            print(2)
            return 1500, visited_list
        # 统计在预测范围内的障碍物
        dists_pred = []
        # 统计在影响范围内的障碍物
        dists_effect = []
        for obstacle in obstacles:
            dist = Position.calculate_distance(agent.position, obstacle.position)
            if dist <= r_pred:  # 小于预测范围
                dists_pred.append(obstacle)
            if dist <= r_eff:  # 小于影响范围
                dists_effect.append(obstacle)

        F_att_x, F_att_y = goal.get_attraction_force(agent.position)
        cos_value = F_att_x / math.sqrt(F_att_x ** 2 + F_att_y ** 2)  # 求出来的是值
        sin_value = F_att_y / math.sqrt(F_att_x ** 2 + F_att_y ** 2)
        theta = calculate_angle(cos_value, sin_value)

        # 预测范围内的障碍物是否阻碍当前路径（计算障碍物到当前点与目标连线的距离）,1是不安全
        UnSafe = 0
        oneside_pred = find_oneside_obstacle(agent, goal, theta, dists_pred)
        for obstacle in oneside_pred:
            if calculate_Safe_dist(agent.position, goal.position, obstacle.position) < obstacle.size:
                UnSafe = 1
                break

        # 影响范围内的障碍物是否阻碍当前路径（计算障碍物到当前点与目标连线的距离）,1是影响（当前路径不安全）
        isEffect = 0
        oneside_effect = find_oneside_obstacle(agent, goal, theta, dists_effect)
        for obstacle in oneside_effect:
            if calculate_Safe_dist(agent.position, goal.position, obstacle.position) < obstacle.size:
                isEffect = 1
                break

        # 移动机器人在障碍物预测范围之外或者移动机器人前进方向安全时,受到的斥力为0,在引力的作用下前进
        if (len(oneside_pred) == 0) | ((isEffect == 0) & (UnSafe == 0)):
            agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
            agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
            step_count += 1  # 纪录一下总共走了多少步
            visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
            # agent.draw()
        # 障碍物在预测范围内，不在影响范围内，且路径不安全。此时需要旋转角度
        elif (len(oneside_pred) != 0) & (len(oneside_effect) == 0) & (UnSafe == 1):
            # 应找到阻碍前进方向的障碍物
            block_obs = []
            for obstacle in obstacles:
                if Position.calculate_distance(oneside_pred[0].position, obstacle.position) <= r_pred:
                    block_obs.append(obstacle)
            # 计算阻挡了前进方向且距离无人车最近的障碍物（fisrt_obstacle）
            # TODO 分为单个障碍物阻挡和多个障碍物阻挡
            if len(block_obs) > 1:
                # 多个障碍物，判断障碍物组在连线的哪边
                count_less, count_more, block_less, block_more = which_side_of_obs(agent, goal, obstacles)
                if count_more == count_less:
                    nearest_ob = who_is_the_min_of_two_sides(agent, goal, block_less, block_more)
                    alpha = angle_of_ObstoGoal(nearest_ob, goal)
                    if theta > alpha:
                        temp = Goal(Position(agent.position.x, agent.position.y))
                        while UnSafe == 1:
                            theta += 0.22
                            temp.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                            temp.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                            UnSafe = 0
                            for obstacle in obstacles:
                                if calculate_Safe_dist(agent.position, temp.position,obstacle.position) < obstacle.size:
                                    UnSafe = 1
                                    break
                        count = 0
                        while count < (int)((r_pred-3)/0.5):  # 预测5，但如果存在enemy，只能走距离2，agent步长0.5
                            agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                            agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                            count += 1
                            step_count += 1
                            visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                            # agent.draw()
                    else:
                        temp = Goal(Position(agent.position.x, agent.position.y))
                        while UnSafe == 1:
                            theta -= 0.22
                            temp.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                            temp.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                            UnSafe = 0
                            for obstacle in obstacles:
                                if calculate_Safe_dist(agent.position, temp.position,obstacle.position) < obstacle.size:
                                    UnSafe = 1
                                    break
                        count = 0
                        while count < (int)((r_pred-3)/0.5):  # 预测5，但如果存在enemy，只能走距离2，agent步长0.5
                            agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                            agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                            count += 1
                            step_count += 1
                            visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                            # agent.draw()
                elif count_more > count_less:
                    # todo 大体方向这边，还应找到最近障碍物？
                    temp = Goal(Position(agent.position.x, agent.position.y))
                    while UnSafe == 1:
                        theta -= 0.22
                        temp.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        temp.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        UnSafe = 0
                        for obstacle in oneside_pred:
                            if calculate_Safe_dist(agent.position, temp.position,obstacle.position) < obstacle.size:
                                UnSafe = 1
                                break
                    count = 0
                    while count < (int)((r_pred-3)/0.5):  # 预测5，但如果存在enemy，只能走距离2，agent步长0.5
                        agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        count += 1
                        step_count += 1
                        visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                        # agent.draw()
                else:
                    # todo 大体方向这边，还应找到最近障碍物？
                    temp = Goal(Position(agent.position.x, agent.position.y))
                    while UnSafe == 1:
                        theta += 0.22
                        temp.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        temp.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        UnSafe = 0
                        for obstacle in oneside_pred:
                            if calculate_Safe_dist(agent.position, temp.position,obstacle.position) < obstacle.size:
                                UnSafe = 1
                                break
                    count = 0
                    while count < (int)((r_pred-3)/0.5):  # 预测5，但如果存在enemy，只能走距离2，agent步长0.5
                        agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        count += 1
                        step_count += 1
                        visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                        # agent.draw()
            else:
                # 单个障碍物阻碍，直接按照alpha和theta来前进
                fisrt_obstacle = nearest_of_Obstacles(agent, block_obs)
                alpha = angle_of_ObstoGoal(fisrt_obstacle, goal)
                if alpha < theta:
                    temp = Goal(Position(agent.position.x, agent.position.y))
                    while UnSafe == 1:
                        theta -= 0.22
                        temp.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        temp.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        UnSafe = 0
                        for obstacle in oneside_pred:
                            if calculate_Safe_dist(agent.position, temp.position, obstacle.position) < obstacle.size:
                                UnSafe = 1
                                break
                    count = 0
                    while count < (int)((r_pred-3)/0.5):  # 预测5，但如果存在enemy，只能走距离2，agent步长0.5
                        agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        count += 1
                        step_count += 1
                        visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                        # agent.draw()
                else:
                    temp = Goal(Position(agent.position.x, agent.position.y))
                    while UnSafe == 1:
                        theta += 0.22
                        temp.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        temp.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        UnSafe = 0
                        for obstacle in oneside_pred:
                            if calculate_Safe_dist(agent.position, temp.position, obstacle.position) < obstacle.size:
                                UnSafe = 1
                                break
                    count = 0
                    while count < (int)((r_pred-3)/0.5):  # 预测5，但如果存在enemy，只能走距离2，agent步长0.5
                        agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        step_count += 1
                        count += 1
                        visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                        # agent.draw()
        # 在障碍物影响范围内,且前进路线不安全
        else:
            F_rep_x = 0
            F_rep_y = 0
            for obstacle in dists_pred:
                F_x, F_y = obstacle.get_repulsion_force(agent.position)
                F_rep_x += F_x  # x方向上的斥力
                F_rep_y += F_y  # y方向上的斥力
            F_att_x += F_rep_x  # x方向上的力
            F_att_y += F_rep_y  # y方向上的力
            cos_value = F_att_x / math.sqrt(F_att_x ** 2 + F_att_y ** 2)  # 求出来的是值
            sin_value = F_att_y / math.sqrt(F_att_x ** 2 + F_att_y ** 2)
            theta = calculate_angle(cos_value, sin_value)
            best_move, flag = agent.best_move(theta, dists_pred)

            while flag == 0:
                theta += 0.22
                best_move, flag = agent.best_move(theta, dists_pred)

            agent.position = best_move

            step_count += 1  # 纪录一下总共走了多少步

            visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
            # agent.draw()
        is_trap = 0
        spot = goal.position
        if (len(visited_list) > 4) & (len(dists_pred) != 0):
            is_trap, spot = out_to_trap(agent, goal, visited_list, obstacles)
        # TODO 陷入最小值区域（注意visited_list的值为3/10有错误）
        if is_trap == 1:
            print(2)
            return 1500, visited_list
    print(2)
    # ax.axis('equal')
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_minus'] = False
    # plt.show()
    if Position.calculate_distance(agent.position, goal.position) >= 0.5:
        return 1500, visited_list
    else:
        return step_count, visited_list




