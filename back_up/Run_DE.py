from DE import DE
# import numpy as np
# from DE_apf import de_apf


def run_de():
    dim = 4
    size = 15
    iter_num = 10
    x_min = [0, 0, 3, 3]
    x_max = [10, 100, 10, 10]

    start = (1, 1)
    end = (30, 30)
    obs_XY = []
    enemy_XY = [(7, 7)]

    de = DE(start, end, obs_XY, enemy_XY, dim, size, iter_num, x_min, x_max)
    fit_var_list, best_pos = de.update(start, end, obs_XY, enemy_XY)
    # print("DE最优位置:" + str(best_pos))
    # print("DE最优解:" + str(fit_var_list[-1]))
    return best_pos

# de_apf(start, end, obs_XY, enemy_XY,2.4198919158102266, 27.354939391179446, 3.152453397027412, 9.556400203793041)
