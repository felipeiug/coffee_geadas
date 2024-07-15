# Importando arquivos
import os
import pandas as pd
import geopandas as gpd
import datetime

from time import sleep
from shapely.geometry import Point
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

username = "felipeiug"
password = "Felipe@33611541"

startDate = '20210601'
endDate = '20210815'

api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')

footprint = geojson_to_wkt(read_geojson('F:\Projetos\Projeto Geadas no Café\Codigos\Mapas\cafePequeno.geojson'))
products = api.query(
    footprint,
    date=(startDate, endDate),
    platformname='Sentinel-2',
    cloudcoverpercentage=(0, 100)
)

os.makedirs(r'F:\Projetos\Projeto Geadas no Café\Codigos\downloadsSentinel/', exist_ok=True)

datas = {}
sair = False
while not sair:
    sair = False

    for product_id, data in products.items():
        titulo = data["title"] + ".zip"
        gen_date = data['generationdate']
        data_dias = datetime.datetime(year=gen_date.year, month=gen_date.month, day=gen_date.day)

        if data_dias in datas and datas[data_dias]:
            continue
        elif not data_dias in datas:
            datas[data_dias] = False

        product_info = api.get_product_odata(product_id)
        is_online = product_info['Online']

        try:
            files = os.listdir(r'F:\Projetos\Projeto Geadas no Café\Codigos\downloadsSentinel/')
            if titulo in files:
                datas[data_dias] = True
                continue

            api.download(product_id, directory_path=r'F:\Projetos\Projeto Geadas no Café\Codigos\downloadsSentinel/')
            datas[data_dias] = True
        except Exception as e:
            print(e)

    for key, value in datas.items():
        key:datetime.datetime = key
        print(key.strftime("%d/%m/%Y"), value)

    for key, val in datas.items():
        if val == False:
            break
    else:
        sair = True

from get_data_zip import *