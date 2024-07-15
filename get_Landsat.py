# Importando arquivos
import ee
import pandas as pd
import geopandas as gpd

from time import sleep
from shapely.geometry import Point
from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer

token_ee = "ldnkNL1lv7ysvpj6MI1IZB!DRGgF3v6UJvwclo2RtyzCMVYdEw00fb@TsVeoM8YZ"

username = "Felipeiug"
password = "Felipe@33611541"

api = API(username, password)
ee = EarthExplorer(username, password)

startDate = '2021-06-01'
endDate = '2021-07-30'

scenes = api.search(
    dataset='landsat_ot_c2_l2',
    latitude=-19.21362,
    longitude=-46.22103,
    start_date=startDate,
    end_date=endDate,
    max_cloud_cover=100
)

for scene in scenes:
    ID = scene['landsat_product_id']
    ee.download(ID, output_dir='downloads/')


# Determinando os valores do que é ou não café
# Abridno o arquivo com os poligonos datados
# cafes:gpd.GeoDataFrame = gpd.read_file("Mapas/arquivos.gpkg", driver="GPKG", layer = "cafe")

# for cafe in cafes.itertuples():
#     coords = [list(cafe.geometry.envelope.exterior.coords)]
#     ee_polygon = ee.Geometry.Polygon(coords)
    
#     clip = landsat.clip(ee_polygon)

#     # NVDI = clip.expression("(nir-red)/(nir+red)",
#     # {
#     #     "nir":clip.select("B5"),
#     #     "red":clip.select("B4"),
#     # })

#     task = ee.batch.Export.image.toDrive(
#         image=clip,
#         description='Landsat_NVDI',
#         folder='TestesCafe',
#         fileNamePrefix='image',
#         egion=ee_polygon,
#         scale=12  # Resolution in meters
#     )

#     task.start()

#     # Esperar a finalização da tarefa de exportação
#     status = task.status()
#     while status['state'] in ['READY', 'RUNNING']:
#         status = task.status()
#         print(status['state'])
#         sleep(5)

#     # Obter informações sobre a tarefa de exportação
#     task_info = ee.data.getTaskStatus(task.id)[0]

#     # Verificar se a tarefa foi concluída com sucesso
#     if task_info['state'] == 'COMPLETED':
#         # Obter o ID do arquivo exportado
#         download_url = task.status()['sourceUrl']

#         # Imprimir o link de download
#         print('Link de download:', download_url)
#     else:
#         print('A tarefa de exportação não foi concluída com sucesso.')