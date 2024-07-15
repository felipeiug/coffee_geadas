import ee
import os
import json
import time
import string
import geopandas as gpd
import concurrent.futures

from shapely.geometry import Polygon
from unidecode import unidecode
from datetime import datetime, timedelta
from ee.image import Image

#Variáveis de controle
iteracoes_por_amostragem = 1

############################################### Código ##################################################

#Initializing earth engine
# link_cred = "testestcc@reg-vaz.iam.gserviceaccount.com"
# cred = ee.ServiceAccountCredentials(link_cred, r"Secrets/reg-vaz-9444ac120e33.json")
# ee.Initialize(cred)
try:
    ee.Initialize()
except Exception as e:
    print(e)
    ee.Authenticate()
    ee.Initialize()

cafes_com_geada:gpd.GeoDataFrame = gpd.read_file(r"F:\Projetos\Projeto Geadas no Café\Codigos\Mapas\cafe_geadas.gpkg", driver="GPKG", layer="cafe")

#Transformando um polygono do Shapely em um poligono EE
def shapely_to_ee_polygon(shapely_polygon:Polygon):
    coordinates = shapely_polygon.exterior.coords
    ee_coords = [[coord[0], coord[1]] for coord in coordinates]
    return ee.Geometry.Polygon(ee_coords)

def processar_NDVI(image)->ee.Image:
    image = ee.Image(image)

    nir = image.select("B5")
    red = image.select("B4")

    ndvi = nir.subtract(red).divide(nir.add(red)).rename("NDVI")

    image = image.addBands(ndvi)
    return image

def converter_tempo(segundos):
    # Calcular o número de dias, horas, minutos e segundos
    dias = segundos // (24 * 3600)
    segundos %= (24 * 3600)
    horas = segundos // 3600
    segundos %= 3600
    minutos = segundos // 60
    segundos %= 60

    # Formatar a saída como uma string
    tempo_formatado = "{:02d}d {:02d}h {:02d}m {:02d}s".format(int(dias), int(horas), int(minutos), int(segundos))

    return tempo_formatado


cafes_com_geada["erro"] = False

inicio = time.time()

with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
    for cafe in cafes_com_geada.itertuples():
        index = cafe.Index
        geom = cafe.geometry
        geom_type = cafe.geometry.geom_type
        
        if index % iteracoes_por_amostragem == 0:
            tempo_decorrido = time.time() - inicio
            progresso = max(index / len(cafes_com_geada.index), 0.000000001)
            tempo_restante_estimado = (tempo_decorrido / progresso) * (1 - progresso)
            os.system("cls")
            print(f"{index+1} de {len(cafes_com_geada.index)} - {round(index*100/len(cafes_com_geada.index), 4)}%")
            print(f"Progresso: {progresso:.4%} Tempo restante estimado: {converter_tempo(tempo_restante_estimado)}")

        geometry = shapely_to_ee_polygon(geom)

        collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA').filterBounds(geometry).filterDate("2021-06-01", "2021-12-30")
        collection_info = collection.getInfo()

        tarefas = []
        for n, feature in enumerate(collection_info["features"]):
            def tarefa(n, feature):
                
                try:
                    imageName = feature["id"]
                    image = ee.Image(imageName)
                    data = imageName.split("_")[-1]
                    dia = data[6:8]
                    mes = data[4:6]
                    ano = data[0:4]

                    if data not in cafes_com_geada.columns.to_list():
                        cafes_com_geada[data] = None

                    image = processar_NDVI(image)
                    # bandas = image.bandNames()
                    # bandas = bandas.getInfo()

                    # Reduzir a coleção de imagens para a área do polígono e calcular o valor médio do NDVI
                    reduced_ndvi = image.select('NDVI').reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=30)

                    # Obter o valor médio do NDVI para a área do polígono
                    ndvi_value = reduced_ndvi.get('NDVI').getInfo()

                    cafes_com_geada.at[index, data] = ndvi_value

                    return True
                except Exception as e:
                    print(e)
                    cafes_com_geada.at[index, "erro"] = True
                    return False

            tarefas.append(executor.submit(tarefa, *(n, feature)))

        for future in concurrent.futures.as_completed(tarefas):
            # if future.result():
            #     print("OK")
            # else:
            #     print("Não OK")
            pass
            

cafes_com_geada.to_file(r"F:\Projetos\Projeto Geadas no Café\Codigos\Mapas\cafe_geadas.gpkg", driver="GPKG", layer="NDVI")