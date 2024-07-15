# Este script tem como objetivo obter o uso e ocupação do solo para todo o estado de mionas gerais, para iste será realizada
# uma consulta ao Earth Engine utilizando todos os municípios de minas gerais para criar diversos arquivos pequenos.s

import ee
import os
import json
import time
import string
import geopandas as gpd
import concurrent.futures

from unidecode import unidecode
from datetime import datetime, timedelta

#Variáveis de controle

# Data do estudo
data_estudo = "08-02-2022"

#Quantidade de meses para pegar os dados
meses_ans = 6

# Pasta no drive para salvar os arquivos
driver_fold = "geadas_cafe"

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

# Filtra imagens da coleção no período escolhido
# O Período pode ser alterado abaixo. Não esqueça de inserir um período que esteja compreendido
# no tempo mínimo de um estudo de Uso e Ocupação da Terra para o ZAP (6 meses anterior ao estudo)
# Formato no earth engine: ANO-MÊS-DIA

data_estudo = datetime.strptime(data_estudo, "%d-%m-%Y")
data_ans = data_estudo - timedelta(days=30*meses_ans)

str_data_estudo = data_estudo.strftime("%Y-%m-%d")
str_data_ans = data_ans.strftime("%Y-%m-%d")

sentinel:ee.Image = ee.ImageCollection("COPERNICUS/S2_SR").filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 10).filterDate(str_data_ans, str_data_estudo).median()


# Lendo o shape com os múnicípios de minas gearais
municipios_mg:gpd.GeoDataFrame = gpd.read_file(r"E:\ProjetosOff\Projeto Geadas no Café\Codigos\Mapas\arquivos.gpkg", driver="GPKG", layer="municipios_mg")

# Tasks rodando
tasks = {}

#Erros nas tasks
errors = ""

#Gerando as tasks
tam_municipios = len(municipios_mg.index)
count = 0

#Para criar um nome seguro
special_chars = " ".join(string.punctuation) + "".join(string.whitespace) + "".join(string.digits)

#Ultima task a gerar
task_name = ""

with concurrent.futures.ThreadPoolExecutor() as executor:
    def print_status():
        global errors
        global tasks
        global tam_municipios
        global task_name
        global count

        while True:
           
            tasks_len = tam_municipios
            status_ready_count = 0
            status_running_count = 0
            status_complete_count = 0
            status_failed_count = 0

            message = ""
            
            message += f"Gerando {len(tasks)} de {tasks_len}\n"
            if task_name != "":
                message += f"{task_name}\n"
            
            message += "Status:\n"

            try:
                for nome, task_status in tasks.items():
                    #task_status = task.status()

                    if task_status['state'] == 'READY':
                        status_ready_count += 1
                    elif task_status['state'] == 'RUNNING':
                        status_running_count += 1
                    elif task_status['state'] == "COMPLETED":
                        status_complete_count += 1
                    else:
                        status_failed_count += 1
                        errors += f"{nome}: Erro '{task_status['error_message']}'\n"
            except RuntimeError as e:
                pass
            except Exception as e:
                print(e)
                continue
                
            # Exibindo quantos processos correram
            status_finaly_count = status_complete_count + status_failed_count
            porc = round((((status_finaly_count)/tasks_len)*100), 2)
            message += f"{status_finaly_count} de {tasks_len} - {porc}%\n"

            #Adicionando a quantidade de processos
            message += f"{status_ready_count} processos iniciando\n"
            message += f"{status_running_count} processos rodando\n"
            message += f"{status_complete_count} processos concluidos\n"
            message += f"{status_failed_count} processos com erro\n"

            os.system('cls' if os.name == 'nt' else 'clear')
            print(message)
            time.sleep(0.5)

            if status_finaly_count == tasks_len:
                break

    def init_task(row):
        global count
        global tasks
        global task_name

        multi_list = []
        geom = row.geometry
        nome:str = row.NM_MUN

        task_name = nome

        translate_table = nome.maketrans("", "", special_chars)
        nome = nome.translate(translate_table)
        nome = unidecode(nome)

        if geom.geom_type == "MultiPolygon":
            for poly in geom.geoms:
                multi_list.extend(poly.exterior.coords[:-1])
        elif geom.geom_type == "Polygon":
            multi_list.extend(geom.exterior.coords[:-1])

        if len(multi_list) == 0:
            return

        area = ee.Geometry.Polygon(multi_list)

        # Recorta a imagem sentinel na área de interesse
        clipped = sentinel.clip(area)

        task = ee.batch.Export.image.toDrive(
            image=clipped,
            description=nome,
            scale=10,
            region=area,
            folder=driver_fold,
        )

        task.start()
        tasks[nome] = task.status()

        count += 1

    executor.submit(print_status)

    for row in municipios_mg.itertuples():
        executor.submit(init_task, row)
    
    task_name = ""
    executor.shutdown(wait=True)

os.system('cls' if os.name == 'nt' else 'clear')
print(f"Finalizado \n{errors}")