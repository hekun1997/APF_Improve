import numpy as np
import geopandas
import matplotlib.pyplot as plt

n_path = 'yourpath/nodes.shp'

node_shp_df = geopandas.GeoDataFrame.from_file(n_path) #读取nodes.shp数据
e_path = 'yourpath/edges.shp'
edge_shp_df = geopandas.GeoDataFrame.from_file(e_path) #读取edges.shp数据
n = edge_shp_df.shape[0]
npoint = node_shp_df.shape[0]
# 建立起点到所有点的权重矩阵
weight = [([float('Inf')] * npoint) for i in range(npoint)]
for i in range(n):
    idFrom = edge_shp_df.iloc[i]['from']
    nodeFrom = node_shp_df[node_shp_df['osmid'] == idFrom]
    nodeFromIndex = nodeFrom.index.tolist()[0]
    idTo = edge_shp_df.iloc[i]['to']
    nodeTo = node_shp_df[node_shp_df['osmid'] == idTo]
    nodeToIndex = nodeTo.index.tolist()[0]
    # weight[nodeFromIndex][nodeToIndex] = edge_shp_df.iloc[i]['maxtime'] + np.array(nodeTo).tolist()[0][0]
    weight[nodeFromIndex][nodeToIndex] = edge_shp_df.iloc[i]['maxtime']
    if edge_shp_df.iloc[i]['oneway'] == 'False':
        # weight[nodeToIndex][nodeFromIndex] = edge_shp_df.iloc[i]['maxtime'] + np.array(nodeFrom).tolist()[0][0]
        weight[nodeToIndex][nodeFromIndex] = edge_shp_df.iloc[i]['maxtime']

from shapely.geometry import Point, Polygon


# dijkstra算法
def dijkstraPath(weight, point, start, end):
    n = point.shape[0]
    shortPath = [0] * n
    path = [0] * n
    for i in range(n):
        path[i] = str(start) + '-->' + str(i)
    visited = [0] * n

    shortPath[start] = 0
    visited[start] = 1

    for count in range(1, n):
        k = -1
        dmin = float('Inf')
        for i in range(n):
            if (visited[i] == 0) & (weight[start][i] < dmin):
                dmin = weight[start][i]
                k = i
        shortPath[k] = dmin
        visited[k] = 1
        for i in range(n):
            if (visited[i] == 0) & (weight[start][k] + weight[k][i] < weight[start][i]):
                weight[start][i] = weight[start][k] + weight[k][i]
                path[i] = path[k] + '-->' + str(i)
    return path


# 调用dijkstra函数计算最短路径
from shapely.geometry import Point, Polygon

start = node_shp_df[node_shp_df['geometry'] == Point(-117.103363, 32.740292)]
start = start.index.tolist()[0]
end = node_shp_df[node_shp_df['geometry'] == Point(-117.240753, 32.789948)]
end = end.index.tolist()[0]
pointid = node_shp_df.iloc[start]['osmid']
path = dijkstraPath(weight, node_shp_df, start, end)
path[end]
# 将点好转换为x,y坐标
pathcoor = []
path = path[end].split('-->')
for i in path:
    x = node_shp_df.iloc[int(i)]['geometry'].x
    y = node_shp_df.iloc[int(i)]['geometry'].y
    pathcoor.append([y, x])
pathcoor