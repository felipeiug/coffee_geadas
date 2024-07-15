import time
import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import datetime

datas = [
    "01-06-2021",
    "16-06-2021",
    "01-07-2021", # 30 para 01 - Primeira Geada
    "20-07-2021", # 19 para 20 - Segunda Geada
    "30-07-2021", # 29 para 30 - Terceira Geada
    "16-08-2021",
    "01-09-2021",
    "16-09-2021",
    "01-10-2021",
    "16-10-2021",
    "01-11-2021",
    "16-11-2021",
    "01-12-2021",
    "16-12-2021",
    "31-12-2021", #Ultimo dia
]

print("Lendo os dados de café com NDVI")
timeinit = time.time()
dados_cafe:gpd.GeoDataFrame = gpd.read_parquet(r"F:\Projetos\Projeto Geadas no Café\Codigos\Mapas\CafeNDVI.parquet")
print(f"Dados dos cafés lidos em {time.time() - timeinit}")


print("Configurando as datas")

dataAns = None
cafesMedia = pd.DataFrame()

for data in datas:
    data = pd.to_datetime(data, format="%d-%m-%Y")

    if dataAns == None:
        dataAns = data
        continue

    datas_formatadas = pd.date_range(dataAns, data).strftime("%Y%m%d").to_list()
    datas_formatadas.pop(-1)

    datas_formatadas = [data_formatada for data_formatada in datas_formatadas if data_formatada in dados_cafe.columns]

    colunas = dados_cafe.loc[:, datas_formatadas]

    for coluna in colunas.columns.to_list():
        colunas[coluna] = pd.to_numeric(colunas[coluna], errors='coerce')

    medias = colunas.mean(axis=1, skipna=True)

    cafesMedia[data.strftime("%d-%m-%Y")] = medias

    #Datas
    dataAns = data

print("Salvando o arquivo")
cafesMedia = gpd.GeoDataFrame(cafesMedia, geometry=dados_cafe.geometry, crs = dados_cafe.crs.srs)
cafesMedia.to_file(r"F:\Projetos\Projeto Geadas no Café\Codigos\Mapas\cafe_media.gpkg", driver="GPKG", layer = "media")