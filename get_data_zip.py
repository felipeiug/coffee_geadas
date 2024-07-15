import os
import shutil
import zipfile
import xmltodict
import xml.etree.ElementTree as ET
import rasterio
import numpy as np

def copiar_arquivo(origem, destino):
    shutil.copy(origem, destino)

def xml_to_dict(xml_string):
    root = ET.fromstring(xml_string)
    data = {}

    for child in root:
        data[child] = child.text

    return data

# Exemplo de uso
path_inicial = r"F:\Projetos\Projeto Geadas no Café\Codigos\downloadsSentinel"
arquivos = os.listdir(path_inicial)

temp_dir = "temp"
for arquivo in arquivos:
    data = arquivo[11:26]
    data_name = arquivo[11:15] + "_" + arquivo[15:17] + "_" + arquivo[17:19]
    with zipfile.ZipFile(path_inicial + f"/{arquivo}", 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    for path in os.listdir(temp_dir + "/"):
        if data in path:
            p1 = path
            break
    else:
        raise Exception("Erro")

    f1 = os.listdir(f"{temp_dir}/{p1}/GRANULE")[0]
    f2 = os.listdir(f"{temp_dir}/{p1}/GRANULE/{f1}/IMG_DATA")
    tem_20 = False
    if "R20m" in f2:
        files_copy = os.listdir(f"{temp_dir}/{p1}/GRANULE/{f1}/IMG_DATA/R20m")
        tem_20 = True
    else:
        files_copy = f2

    #Pegando a irradiância
    try:
        with open(f"{temp_dir}/{p1}/MTD_MSIL2A.xml", "r") as arq:
            data_vals = xmltodict.parse(arq.read())
        arq.close()
        data_vals = data_vals[list(data_vals.keys())[0]]
        quantification_AOT = float(data_vals['n1:General_Info']["Product_Image_Characteristics"]["QUANTIFICATION_VALUES_LIST"]["AOT_QUANTIFICATION_VALUE"]["#text"])

    except FileNotFoundError as e:
        with open(f"{temp_dir}/{p1}/MTD_MSIL1C.xml", "r") as arq:
            data_vals = xmltodict.parse(arq.read())
        arq.close()
        data_vals = data_vals[list(data_vals.keys())[0]]
        quantification_AOT = float(data_vals['n1:General_Info']["Product_Image_Characteristics"]["QUANTIFICATION_VALUE"]["#text"])

    data_foi = []
    contains_8A = False
    for file in files_copy:
        banda = file.replace("_20m", "").split("_")[-1]
        path_file = f"{temp_dir}/{p1}/GRANULE/{f1}/IMG_DATA/R20m/{file}" if tem_20 else f"{temp_dir}/{p1}/GRANULE/{f1}/IMG_DATA/{file}"
        
        if data_name + banda not in data_foi:
            data_foi.append(data_name+banda)
            os.makedirs(f"Mapas/Bandas/{data_name}", exist_ok=True)

        with rasterio.open(path_file, "r") as src:
            raster_val = src.read(1)
            meta = src.meta
        src.close()

        meta.update(driver='GTiff', dtype=rasterio.float32, count=1)

        if banda.replace(".jp2", "") in ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B10", "B11", "B12"]:
            if banda.replace(".jp2", "") == "B8A":
                contains_8A = True

            DN = raster_val/quantification_AOT

            banda = banda.replace(".jp2", ".tif")
            with rasterio.open(f"Mapas/Bandas/{data_name}/{banda}", 'w', **meta) as dst:
                dst.write(DN.astype(rasterio.float32), 1)
            dst.close()
        else:
            DN = raster_val
            with rasterio.open(f"Mapas/Bandas/{data_name}/{banda}", 'w', **meta) as dst:
                dst.write(DN.astype(rasterio.float32), 1)
            dst.close()
    
    with rasterio.open(f"Mapas/Bandas/{data_name}/B04.tif") as src:
        red_band = src.read(1)
    src.close()

    if contains_8A and red_band.shape[0] != 10980:
        nirBand = f"Mapas/Bandas/{data_name}/B8A.tif"
    else:
        nirBand = f"Mapas/Bandas/{data_name}/B08.tif"

    with rasterio.open(nirBand) as src:
        nir_band = src.read(1)
        meta = src.meta
    src.close()

    #np.seterr(divide="ignore", invalid="ignore")
    ndvi = (nir_band - red_band)/(nir_band + red_band)

    ndvi[np.isnan(ndvi)] = -1

    meta.update(driver='GTiff', dtype=rasterio.float32, count=1)

    # Salvar o NDVI em um novo arquivo raster
    with rasterio.open(f"Mapas/Bandas/{data_name}/NDVI.tif", 'w', **meta) as dst:
        dst.write(ndvi.astype(rasterio.float32), 1)
    dst.close()