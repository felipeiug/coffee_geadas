import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#Show shapely polygon with matplotlib and atualize data

cafes = r"F:\Projetos\Projeto Geadas no Café\Codigos\Mapas\CAFE-MG_Safra_2017.zip"
municipiosComGeada = r"F:\Projetos\Projeto Geadas no Café\Codigos\Mapas\arquivos.gpkg"

cafes:gpd.GeoDataFrame = gpd.read_file(cafes)
municipiosComGeada:gpd.GeoDataFrame = gpd.read_file(municipiosComGeada, driver="GPKG", layer="municipios_mg_com_geada")


fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)

def getData(i):
    cafe = cafes.loc[i]
    if cafe.empty:
        #ani.event_source.stop()
        return

    geom = cafe.geometry
    x, y = geom.exterior.xy

    #Representação Gráfica
    message = f"Café {i} de {len(cafes.index)} - {round(i*100/len(cafes.index))}%"
    ax.set_title(message)
    print(message)

    # Ajusta os limites do eixo X para mostrar apenas os últimos 10 valores
    ax.set_xlim(min(x), max(x))

    # Ajusta os limites do eixo Y para mostrar todos os valores do eixo Y
    ax.set_ylim(min(y), max(y))

    line.set_data(x, y)
    return line,

ani = animation.FuncAnimation(fig, getData, interval=0, blit=True, frames=len(cafes.index))

plt.show()