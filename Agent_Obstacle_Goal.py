import math
import numpy as np
import matplotlib.pyplot as plt

color_a = '#000000'  # 无人车的颜色
color_g = '#000000'  # 目标点的颜色
color_o = '#000000'  # 障碍物颜色


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def calculate_distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def calculate_distance_squared(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2


class Agent:
    def __init__(self, position, move_radius=0.5):
        self.position = position
        self.move_radius = move_radius

    def draw(self):
        plt.scatter(self.position.x, self.position.y, c='red', s=25, marker='.')

    def draw2(self):
        plt.scatter(self.position.x, self.position.y, c=color_a, s=25, marker='.')

    def best_move(self, angle, obstacles):
        best_move = Position(self.position.x + self.move_radius * math.cos(angle),
                             self.position.y + self.move_radius * math.sin(angle))
        flag = 1
        for obstacle in obstacles:
            if Position.calculate_distance(obstacle.position, best_move) <= obstacle.size:
                # flag为0代表下一步会碰撞障碍物，不能取
                flag = 0
                break
        if flag == 1:
            return best_move, flag
        else:
            return self.position, flag


class Obstacle:
    # 障碍物draw_radius+无人车的draw_radius的和为安全半径,effect_radius为障碍物的影响半径，pred_radius为障碍物的预测半径
    def __init__(self, position, sigma=200, size=2, effect_radius=3):
        self.position = position
        self.sigma = sigma
        self.size = size
        self.effect_radius = effect_radius

    def draw(self, ax):
        r = self.size
        theta = np.arange(0, 2 * np.pi, 0.01)
        x = self.position.x + r * np.cos(theta)
        y = self.position.y + r * np.sin(theta)
        ax.plot(x, y, c=color_o)

    def draw_four(self, color):
        x1 = self.position.x
        y1 = self.position.y
        plt.scatter(x1, y1, c=color_o)

    def draw_legend(self, ax):
        r = self.size
        theta = np.arange(0, 2 * np.pi, 0.01)
        x = self.position.x + r * np.cos(theta)
        y = self.position.y + r * np.sin(theta)
        ax.plot(x, y, c=color_o, label='障碍物实际体积')

    def draw_effect(self, ax):
        r = self.effect_radius
        theta = np.arange(0, 2 * np.pi, 0.01)
        x = self.position.x + r * np.cos(theta)
        y = self.position.y + r * np.sin(theta)
        ax.plot(x, y, c=color_o, linestyle=':')

    def draw_effect_legend(self, ax):
        r = self.effect_radius
        theta = np.arange(0, 2 * np.pi, 0.01)
        x = self.position.x + r * np.cos(theta)
        y = self.position.y + r * np.sin(theta)
        ax.plot(x, y, c=color_o, linestyle=':', label='障碍物影响范围')

    def get_repulsion_force(self, position):
        p_current = Position.calculate_distance(self.position, position)  # 障碍物到无人车的距离
        if p_current <= self.effect_radius:
            Frep_x = self.sigma * (1 / p_current - 1 / self.effect_radius) * (1 / (p_current ** 3)) * (
                        position.x - self.position.x)  # x方向上的斥力
            Frep_y = self.sigma * (1 / p_current - 1 / self.effect_radius) * (1 / (p_current ** 3)) * (
                        position.y - self.position.y)  # y方向上的斥力
            return Frep_x, Frep_y
        else:
            return 0, 0

    def get_repulsion_force_old(self, position):
        p_current = Position.calculate_distance(self.position, position)  # 障碍物到无人车的距离
        if p_current <= self.effect_radius:
            Frep_x = self.sigma * (1 / p_current - 1 / self.effect_radius) * (1 / (p_current ** self.effect_radius)) * (
                        position.x - self.position.x)  # x方向上的斥力
            Frep_y = self.sigma * (1 / p_current - 1 / self.effect_radius) * (1 / (p_current ** self.effect_radius)) * (
                        position.y - self.position.y)  # y方向上的斥力
            return Frep_x, Frep_y
        else:
            return 0, 0


class Goal:
    def __init__(self, position, sigma=1):
        self.position = position
        self.sigma = sigma

    def draw(self):
        plt.scatter(self.position.x, self.position.y, c=color_g, s=50, marker='*')

    def draw_spot(self):
        plt.scatter(self.position.x, self.position.y, c=color_g, s=50, marker='8',label='虚拟目标点')

    def get_attraction_force(self, position):
        Fatt_x = -self.sigma * (position.x - self.position.x)
        Fatt_y = -self.sigma * (position.y - self.position.y)
        return Fatt_x, Fatt_y

    def get_attraction_force_old(self, position):
        # 传统APF就只与距离有关
        Fatt_x = -self.sigma * (position.x - self.position.x)
        Fatt_y = -self.sigma * (position.y - self.position.y)
        return Fatt_x, Fatt_y


class Enemy:
    # 敌军effect_radius为障碍物的影响半径，值为3。 size为实际上的体积3
    def  __init__(self, position, sigma=200, effect_radius=3, size=3):
        self.position = position
        self.sigma = sigma
        self.effect_radius = effect_radius
        self.size = size

    def draw(self, ax):
        r = self.size
        theta = np.arange(0, 2 * np.pi, 0.01)
        x = self.position.x + r * np.cos(theta)
        y = self.position.y + r * np.sin(theta)
        ax.plot(x, y, c='b')

    def draw_four(self):
        x1 = self.position.x
        y1 = self.position.y
        plt.scatter(x1, y1, c='b')

    def get_repulsion_force(self, position):
        p_current = Position.calculate_distance(self.position, position)  # 敌军到无人车的距离
        if p_current <= self.effect_radius:
            Frep_x = self.sigma * (1 / p_current - 1 / self.effect_radius) * (1 / (p_current ** 3)) * (
                        position.x - self.position.x)  # x方向上的斥力
            Frep_y = self.sigma * (1 / p_current - 1 / self.effect_radius) * (1 / (p_current ** 3)) * (
                        position.y - self.position.y)  # y方向上的斥力
            return Frep_x, Frep_y
        else:
            return 0, 0