import os

import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd

from rasterio.mask import mask
from rasterio.windows import Window
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference

datas = os.listdir(r"F:\Projetos\Projeto Geadas no Café\Codigos\Mapas\Bandas")

geometrias:gpd.GeoDataFrame = gpd.read_file("Mapas/CafeNDVI.geojson") #"Mapas/cafePequeno.geojson")

geometrias.to_crs("EPSG:32723", inplace=True)

for data in datas:
    geometrias[f"NDVI_{data}"] = 0

valores = {"Data":[]}

for n, data_geom in enumerate(geometrias.itertuples()):
    index = data_geom.Index
    geom = data_geom.geometry

    valores[str(n+1)] = []

    for i, data in enumerate(datas):
        print(data)
        if data.replace("_", "/") not in valores["Data"]:
            valores["Data"].append(data.replace("_", "/"))

        ndvi = rasterio.open(r"F:/Projetos/Projeto Geadas no Café/Codigos/Mapas/Bandas/" + data + "/NDVI.tif")

        clipped_ndvi, transformed = mask(ndvi, geom, crop=True)
        clipped_ndvi = clipped_ndvi[0]

        clipped_ndvi[clipped_ndvi == 0] = np.nan
        mediana = np.nanmedian(clipped_ndvi)

        geometrias.at[index, f"NDVI_{data}"] = mediana
        valores[str(n+1)].append(mediana)

        # clipped_raster_meta = ndvi.meta

        # clipped_raster_meta.update({
        #     "driver": "GTiff",
        #     "height": clipped_ndvi.shape[1],
        #     "width": clipped_ndvi.shape[2],
        #     "transform": transformed
        # })

        # with rasterio.open(f"Mapas/{data}_NDVI.tif", 'w', **clipped_raster_meta) as dst:
        #     dst.write(clipped_ndvi.astype(rasterio.float32), 1)
        # dst.close()

geometrias.to_file("Mapas/CafeNDVI.geojson", driver="GeoJSON")
pd.DataFrame(valores).to_excel("NVDI_data.xlsx")