from Position import *
from Agent_Obstacle_Goal import *
from Run_DE import run_de
from DE_apf import de_apf


def apf(X, Y, start, end, obs_XY, enemy_XY, df):
    # 起始点传入的是经纬度,转为成（1，1）这种形式
    startXY = lnglat_to_XY(start, df, Y)
    endXY = lnglat_to_XY(end, df, Y)

    agent = Agent(Position(startXY[0], startXY[1]))
    goal = Goal(Position(endXY[0], endXY[1]))

    # todo 5-13 获取当前坡度中的障碍物,加入之后运行时间会变慢
    gradients = gradient_to_use(startXY, endXY)

    obstacles = gradients
    for item in obs_XY:
        obstacles.append(Obstacle(Position(item[0]*6, item[1]*6)))
    for item in enemy_XY:
        obstacles.append(Enemy(Position(item[0]*6, item[1]*6)))

    visited_list = []
    visited_list.append(PtoXY(agent.position))
    step_count = 0

    while Position.calculate_distance(agent.position, goal.position) >= 0.5:
        # 统计在预测范围内的障碍物
        dists_pred = []
        # 统计在影响范围内的障碍物
        dists_effect = []
        for obstacle in obstacles:
            dist = Position.calculate_distance(agent.position, obstacle.position)
            if dist <= 5:  # 小于预测范围
                dists_pred.append(obstacle)
            if dist <= 3:  # 小于影响范围
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
            if calculate_Safe_dist(agent.position, goal.position, obstacle.position) < obstacle.size:  # 小于安全距离
                isEffect = 1
                break

        # 移动机器人在障碍物预测范围之外或者移动机器人前进方向安全时,受到的斥力为0,在引力的作用下前进
        if (len(oneside_pred) == 0) | ((isEffect == 0) & (UnSafe == 0)):
            # print("在引力作用下前进", step_count)
            agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
            agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
            step_count += 1  # 纪录一下总共走了多少步
            visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
            agent.draw()
        # 障碍物在预测范围内，不在影响范围内，且路径不安全。此时需要旋转角度
        elif (len(oneside_pred) != 0) & (len(oneside_effect) == 0) & (UnSafe == 1):
            # print("障碍物在预测范围内，不在影响范围内", step_count)
            # 应找到阻碍前进方向的障碍物
            block_obs = []
            for obstacle in obstacles:
                if Position.calculate_distance(oneside_pred[0].position, obstacle.position) <= 5:
                    block_obs.append(obstacle)
            # 计算阻挡了前进方向且距离无人车最近的障碍物（fisrt_obstacle）
            # TODO 分为单个障碍物阻挡和多个障碍物阻挡
            if len(block_obs) > 1:
                # 多个障碍物，判断障碍物组在连线的哪边
                count_less, count_more, block_less, block_more = which_side_of_obs(agent, goal, obstacles)
                if count_more == count_less:
                    # print("左右障碍物个数相等")
                    # 2020-12-28 比较block_less中距离中线最远、block_more中距离中线最远的障碍物中的较小值来进行方向旋转
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
                                if calculate_Safe_dist(agent.position, temp.position,
                                                       obstacle.position) < obstacle.size:  # 小于安全距离
                                    UnSafe = 1
                                    break
                        count = 0
                        while count < 4:  # 预测5，但如果存在enemy，只能走距离2，agent步长0.5
                            agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                            agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                            count += 1
                            step_count += 1
                            visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                            agent.draw()
                    else:
                        temp = Goal(Position(agent.position.x, agent.position.y))
                        while UnSafe == 1:
                            theta -= 0.22
                            temp.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                            temp.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                            UnSafe = 0
                            for obstacle in obstacles:
                                if calculate_Safe_dist(agent.position, temp.position,
                                                       obstacle.position) < obstacle.size:  # 小于安全距离
                                    UnSafe = 1
                                    break
                        count = 0
                        while count < 4:  # 预测5，但如果存在enemy，只能走距离2，agent步长0.5
                            agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                            agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                            count += 1
                            step_count += 1
                            visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                            agent.draw()
                elif count_more > count_less:
                    # todo 大体方向这边，还应找到最近障碍物？
                    temp = Goal(Position(agent.position.x, agent.position.y))
                    while UnSafe == 1:
                        theta -= 0.22
                        temp.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        temp.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        UnSafe = 0
                        for obstacle in oneside_pred:
                            if calculate_Safe_dist(agent.position, temp.position,
                                                   obstacle.position) < obstacle.size:  # 小于安全距离
                                UnSafe = 1
                                break
                    count = 0
                    while count < 4:  # 预测5，但如果存在enemy，只能走距离2，agent步长0.5
                        agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        count += 1
                        step_count += 1
                        visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                        agent.draw()
                else:
                    # todo 大体方向这边，还应找到最近障碍物？
                    temp = Goal(Position(agent.position.x, agent.position.y))
                    while UnSafe == 1:
                        theta += 0.22
                        temp.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        temp.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        UnSafe = 0
                        for obstacle in oneside_pred:
                            if calculate_Safe_dist(agent.position, temp.position,
                                                   obstacle.position) < obstacle.size:  # 小于安全距离
                                UnSafe = 1
                                break
                    count = 0
                    while count < 4:  # 预测5，但如果存在enemy，只能走距离2，agent步长0.5
                        agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        count += 1
                        step_count += 1
                        visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                        agent.draw()
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
                    while count < 4:  # 预测5，但如果存在enemy，只能走距离2，agent步长0.5
                        agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        count += 1
                        step_count += 1
                        visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                        agent.draw()
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
                    # print(theta)
                    while count < 4:  # 预测5，但如果存在enemy，只能走距离2，agent步长0.5
                        # print("2-2")
                        agent.position.x = agent.position.x + agent.move_radius * math.cos(theta)
                        agent.position.y = agent.position.y + agent.move_radius * math.sin(theta)
                        step_count += 1
                        count += 1
                        visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                        agent.draw()
        # 在障碍物影响范围内,且前进路线不安全
        else:
            # print("在障碍物影响范围内,且前进路线不安全", step_count)
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
            agent.draw()
        is_trap = 0
        spot = goal.position
        if (len(visited_list) > 4) & (len(dists_pred) != 0):
            is_trap, spot = out_to_trap(agent, goal, visited_list, obstacles)
        # TODO 陷入最小值区域（注意visited_list的值为3/10有错误）
        if is_trap == 1:
            while Position.calculate_distance(agent.position, spot.position) >= 0.5:
                dists_pred = []
                for obstacle in obstacles:
                    dist = Position.calculate_distance(agent.position, obstacle.position)
                    if dist <= 5:  # 小于预测范围
                        dists_pred.append(obstacle)
                F_att_x, F_att_y = spot.get_attraction_force(agent.position)
                for obstacle in dists_pred:
                    F_rep_x, F_rep_y = obstacle.get_repulsion_force(agent.position)
                    F_att_x += F_rep_x  # x方向上的力
                    F_att_y += F_rep_y  # y方向上的力
                cos_value = F_att_x / math.sqrt(F_att_x ** 2 + F_att_y ** 2)  # 求出来的是值
                sin_value = F_att_y / math.sqrt(F_att_x ** 2 + F_att_y ** 2)
                theta = calculate_angle(cos_value, sin_value)
                best_move, flag = agent.best_move(theta, dists_pred)
                if flag == 1:
                    agent.position = best_move
                else:
                    while flag == 0:
                        theta = theta + 0.22
                        best_move, flag = agent.best_move(theta, dists_pred)
                    agent.position = best_move
                step_count += 1  # 纪录一下总共走了多少步
                visited_list.append(PtoXY(agent.position))  # 记录经过的点的位置
                agent.draw2()
                # print("虚拟目标点", step_count)
                # todo 如果步数过多，则调用De算法来优化参数并输出
                if step_count >= 1500:
                    params = run_de()
                    step_count, visited_list = de_apf(start, end, obs_XY, enemy_XY, params[0], params[1], params[2], params[3])
                    return visited_list_to_res(visited_list)

    # 这里的visited_list还不是整数，需要转换成整数,并去重
    res = visited_list_to_res(visited_list)
    return res
