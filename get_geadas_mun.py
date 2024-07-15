import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np

#Abrindo o shape com os municípios de minas gerais
municipios_mg:gpd.GeoDataFrame = gpd.read_file(r"C:\Users\felip\Downloads\ide_1103_mg_municipios_pol.zip")#"Mapas/arquivos.gpkg", driver="GPKG", layer = "municipios_mg")
municipios_mg.to_crs("EPSG:31983", inplace=True)

# Abridno o arquivo com os poligonos da temperatura media
temperatura:gpd.GeoDataFrame = gpd.read_file("Mapas/arquivos.gpkg", driver="GPKG", layer = "temp_med")
temperatura.to_crs("EPSG:31983", inplace=True)

temp10 = temperatura[temperatura["tempMéd"] == "10"].geometry.values[0]
temp7 = temperatura[temperatura["tempMéd"] == "3-7"].geometry.values[0]
temp0 = temperatura[temperatura["tempMéd"] == "0"].geometry.values[0]

municipios_mg["temp_med"] = np.nan

for index, row in municipios_mg.iterrows():
	#Checar se uma Series esta em um DataFrame
	geom = row.geometry

	if temp0.contains(geom) or temp0.intersects(geom):
		municipios_mg.at[index, "temp_med"] = 0

	elif temp7.contains(geom) or temp7.intersects(geom):
		municipios_mg.at[index, "temp_med"] = 7

	elif temp10.contains(geom) or temp10.intersects(geom):
		municipios_mg.at[index, "temp_med"] = 10
	
	else:
		municipios_mg.at[index, "temp_med"] = 9999

municipios_mg.to_crs("EPSG:31983", inplace=True)
temperatura.to_crs("EPSG:31983", inplace=True)

municipios_mg.to_file("Mapas/arquivos.gpkg", driver="GPKG", layer = "municipios_mg")

com_geada = municipios_mg[municipios_mg["temp_med"]!=9999]
com_geada.to_file("Mapas/arquivos.gpkg", driver="GPKG", layer = "municipios_mg_com_geada")
	
	
