import numpy as np
import pandas as pd
import os
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.ops import unary_union
from shapely.geometry import box

path_pontos = 'D:\Projetos\Interpolate-carbono\Dados vetoriais\Pontos amostrais_Piracicaba\Dados_227pts_original_06_03_2021.shp'
pontos_pira = gpd.read_file(path_pontos)
path_pira = 'D:\Projetos\Interpolate-carbono\Dados vetoriais\Piracicaba\Perimetro_Piracicaba.shp'
perimetro_pira = gpd.read_file(path_pira)

xizes = []
ypsolons = []

for geom in perimetro_pira.exterior:
    if(geom == None):
        continue
    xizes.append(geom.coords.xy[0])
    ypsolons.append(geom.coords.xy[1])

xizes = list(np.concatenate(xizes).flat)
ypsolons = list(np.concatenate(ypsolons).flat)

all_dots = [list(xy) for xy in zip(xizes, ypsolons)]

# split the data into featutes and target variable seperately
variaveis = pontos_pira.iloc[:, [1,2]].values # features set
argila = pontos_pira.iloc[:, 6].values # set of study variable

dataframe_with_values = pd.DataFrame({'longitude':list(zip(*variaveis))[0], 'latitude':list(zip(*variaveis))[1], 'argila': argila})
dataframe_coords = pd.DataFrame({'longitude':list(zip(*variaveis))[0], 'latitude':list(zip(*variaveis))[1]})

min_x, min_y, max_x, max_y = perimetro_pira.total_bounds

xx_grid = np.linspace(min_x, max_x, 500)
yy_grid = np.linspace(min_y, max_y, 500)

mesh_grid = np.meshgrid(xx_grid, yy_grid)

perimetro_pira["constant"] = 1
perimetro_pira_dissolved = perimetro_pira.dissolve(by = "constant").reset_index(drop = True)



def plotOnPira(dataFrameGerado):
    mapa_gerado = gpd.GeoDataFrame(dataFrameGerado, 
    geometry=gpd.points_from_xy(dataFrameGerado.X, dataFrameGerado.Y), 
    crs = perimetro_pira.crs)
    return mapa_gerado

def generateDataframe(xs, ys, argilas):
    return pd.DataFrame({'X': xs, 'Y': ys, 'Argila': argilas})

def generate_grid_with_cell(spacing, polygon):
    # Convert the GeoDataFrame to a single polygon
    poly_in = unary_union([poly for poly in polygon.geometry])

    # Get the bounds of the polygon
    minx, miny, maxx, maxy = poly_in.bounds    
    
    # Now generate the entire grid
    grid = np.array([])
    for x in np.arange(minx, maxx, spacing): #min, max step
        for y in np.arange(miny, maxy, spacing): #min, max step
            cell = box(x,y, x+spacing, y+spacing)
            grid = np.append(grid, cell)
            
    # Finally only keep the points within the polygon
    list_of_points = [point for point in grid if point.within(poly_in)]

    return list_of_points

def generate_grid_in_polygon(spacing, polygon):
    ''' This Function generates evenly spaced points within the given GeoDataFrame.
        The parameter 'spacing' defines the distance between the points in coordinate units. '''
    
    # Convert the GeoDataFrame to a single polygon
    poly_in = unary_union([poly for poly in polygon.geometry])

    # Get the bounds of the polygon
    minx, miny, maxx, maxy = poly_in.bounds    
    
    # Now generate the entire grid
    x_coords = list(np.arange(np.floor(minx), int(np.ceil(maxx)), spacing))
    y_coords = list(np.arange(np.floor(miny), int(np.ceil(maxy)), spacing))
    
    grid = [Point(x) for x in zip(np.meshgrid(x_coords, y_coords)[0].flatten(), np.meshgrid(x_coords, y_coords)[1].flatten())]

    # Finally only keep the points within the polygon
    list_of_points = [point for point in grid if point.within(poly_in)]
    # list_of_points = [point for point in grid if poly_in.intersects(point)]

    return list_of_points

def getPointlistInPira(spacing):
    points_in_poly = generate_grid_in_polygon(spacing, perimetro_pira_dissolved)
    points_in_poly_gdf = gpd.GeoDataFrame(geometry=points_in_poly)

    pointList = [[point.x, point.y] for point in points_in_poly]

    xgerados = [point.x for point in points_in_poly]
    ygerados = [point.y for point in points_in_poly]
    return [xgerados, ygerados]