import math
import Constantes as Const
import numpy as np



def calcular_magnitud(velocidad_x: float, velocidad_y: float, velocidad_z: float) -> float:
    magnitud = round(math.sqrt(velocidad_x**2 + velocidad_y**2 + velocidad_z**2), 2)
    return magnitud

def vectorizar(x: float, y:float, z:float) -> [float]:
    vector = []
    for i in range(0, len(x)):
        vector.append(calcular_magnitud(x.values[i],y.values[i],z.values[i]))
    return vector

def media_dict(diccionario: dict)->dict:
    nuevo_diccionario = {}
    for clave, lista in diccionario.items():
        nuevo_diccionario[clave] = sum(lista) / len(lista)
    return nuevo_diccionario

def distancia_euclidiana(punto1, punto2):
    x1, y1, z1 = punto1
    x2, y2, z2 = punto2

    distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distancia

def quitar_porcentaje(fatiga:[], porcentaje:int, mas_alto):
    num_elementos_a_conservar = int((1 - porcentaje/100) * len(fatiga))
    array_ordenado = np.sort(fatiga)
    if mas_alto:
        elementos_a_conservar = array_ordenado[:num_elementos_a_conservar]
    else:
        elementos_a_conservar = array_ordenado[len(fatiga)-num_elementos_a_conservar:]
    return elementos_a_conservar

def valor_de_fatiga(valor_medio:float, valor_a_comparar:float, tipo:str):
    fatiga = 0
    if tipo in (Const.FATIGA_VELOCIDAD, Const.FATIGA_STRENGTH):
        fatiga = -((valor_a_comparar-valor_medio)/valor_medio)*100
    if tipo == Const.FATIGA_TIEMPO:
        fatiga = ((valor_a_comparar-valor_medio)/valor_medio)*100
    return fatiga


def normalizar_list(data:[]):
    min_val = np.min(data)
    max_val = np.max(data)
    
    # Aplica la fórmula de normalización Min-Max
    data_norm = (data - min_val) / (max_val - min_val)
    
    return data_norm.tolist()

def normalizar_dict(data:dict):
    for clave, valor in data.items():
        data[clave] = normalizar_list(valor)
    return data