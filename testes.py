import pandas as pd
import numpy as np

# Criar um DataFrame de exemplo com valores NaN e None
data = {'A': [1, 2, None, 4],
        'B': [None, 5, 6, 7],
        'C': [8, None, 9, 10]}

df = pd.DataFrame(data)

# Calcular a média das linhas, tratando None como 0
media_por_linha = df.mean(axis=1, skipna=True)

print(media_por_linha)