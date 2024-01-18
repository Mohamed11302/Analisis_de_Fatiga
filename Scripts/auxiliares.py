import math
import Constantes.Constantes as Const
import numpy as np
from datetime import datetime
import Constantes.Configuracion as Config
import IO.Leer_ficheros as Leer_ficheros
import Procesadores.ExtraerDatos as ExtraerDatos
import skfuzzy as fuzz

def calcular_magnitud(velocidad_x: float, velocidad_y: float, velocidad_z: float) -> float:
    magnitud = round(math.sqrt(velocidad_x**2 + velocidad_y**2 + velocidad_z**2), 2)
    return magnitud

def vectorizar(x: float, y:float, z:float) -> [float]:
    vector = []
    for i in range(0, len(x)):
        vector.append(calcular_magnitud(x.values[i],y.values[i],z.values[i]))
    return vector

def media_dict_lista(diccionario: dict)->dict:
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
    return elementos_a_conservar.tolist()

def quitar_porcentaje_mas_bajo(fatiga:[], porcentaje:int):
    elementos_a_conservar = quitar_porcentaje(fatiga, porcentaje, False)
    return elementos_a_conservar

def quitar_porcentaje_mas_alto(fatiga:[], porcentaje:int):
    elementos_a_conservar = quitar_porcentaje(fatiga, porcentaje, True)
    return elementos_a_conservar


def quitar_porcentaje_dict(diccionario:dict, porcentaje:int, metricas):
    resultado = {}
    for clave in metricas:
        if isinstance(diccionario[clave], list):
            resultado[clave] = quitar_porcentaje_mas_alto(diccionario[clave], porcentaje)
            resultado[clave] = quitar_porcentaje_mas_bajo(diccionario[clave], porcentaje)

        if isinstance(diccionario[clave], dict):
            resultado[clave] = {}
            for subclave, valor2 in diccionario[clave].items():
                resultado[clave][subclave] = quitar_porcentaje_mas_alto(diccionario[clave][subclave], porcentaje)
                resultado[clave][subclave] = quitar_porcentaje_mas_bajo(diccionario[clave][subclave], porcentaje)
    return resultado



def valor_de_fatiga(valor_medio:float, valor_a_comparar:float, tipo:str):
    fatiga = 0
    if tipo in (Const.FATIGUE_VELOCITY, Const.FATIGUE_STRENGTH):
        fatiga = -((valor_a_comparar-valor_medio)/valor_medio)*100
    if tipo == Const.FATIGUE_TIME:
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

def crear_pesos(n):
    pesos = [i / sum(range(1, n + 1)) for i in range(n, 0, -1)]
    return pesos



def media_ponderada_lista_diccionarios(lista_diccionarios, clave, pesos):
    valores_por_diccionario = [d.get(clave) for d in lista_diccionarios if isinstance(d.get(clave), (int, float, dict))]
    if valores_por_diccionario and isinstance(valores_por_diccionario[0], (int, float)):
        return calcular_media_ponderada(valores_por_diccionario, pesos)
    elif valores_por_diccionario and isinstance(valores_por_diccionario[0], dict):
        return calcular_media_ponderada_dict(valores_por_diccionario, pesos)

def calcular_media_ponderada(valores_por_diccionario, pesos):
    valores_por_diccionario = valores_por_diccionario[::-1]
    if len(valores_por_diccionario) != len(pesos):
        raise ValueError("Las listas de valores y pesos deben tener la misma longitud.")
    return sum(v * p for v, p in zip(valores_por_diccionario, pesos))

def calcular_media_ponderada_dict(valores_por_diccionario, pesos):
    _media_clave = {}
    for clav, valor in valores_por_diccionario[0].items(): 
        _media_clave[clav] = media_ponderada_lista_diccionarios(valores_por_diccionario, clav, pesos)
    return _media_clave


def encontrar_extremos(instance, attribute):
    valor_max = getattr(instance, attribute)
    valor_min = getattr(instance, attribute)
    hijo = instance.hijo

    while hijo is not None:
        _max = getattr(hijo, attribute)
        _min = getattr(hijo, attribute)
        
        valor_max = max(valor_max, _max)
        valor_min = min(valor_min, _min)

        hijo = hijo.hijo

    return valor_max, valor_min

def normalizar_atributo(instance, attribute, valor_max, valor_min):
    hijo = instance.hijo

    while hijo is not None:
        print(len(np.array(getattr(hijo, attribute))))
        print(len(valor_min))
        data_norm = np.round((np.array(getattr(hijo, attribute)) - valor_min) / (valor_max - valor_min), 3)
        setattr(hijo, attribute, data_norm.tolist())
        hijo = hijo.hijo

    data_norm = np.round((np.array(getattr(instance, attribute)) - valor_min) / (valor_max - valor_min), 3)
    setattr(instance, attribute, data_norm.tolist())

def calcular_diferencia_en_segundos(fecha1, fecha2):
    # Convertir las cadenas de fecha a objetos datetime
    fecha_objeto1 = datetime.strptime(fecha1, '%Y%m%d_%H%M%S')
    fecha_objeto2 = datetime.strptime(fecha2, '%Y%m%d_%H%M%S')

    # Calcular la diferencia en segundos
    diferencia = fecha_objeto2 - fecha_objeto1
    segundos_totales = abs(diferencia.total_seconds())
    return segundos_totales


def obtener_historico(user, date):
    diccionario_df = {}
    ruta = f"{Config.DIRECTORIO_UTILIZADO}{user}/{Config.DIRECTORIO_HISTORICAL}"
    df_historico = Leer_ficheros.leer_csv(ruta)
    df_serie = ExtraerDatos.dividir_en_repeticiones(Leer_ficheros.leercsv_serie(date, user))
    es_mano_derecha = ExtraerDatos.mano_derecha(df_serie)
    
    df_historico = df_historico[df_historico[Const.HIST_DATE] <= date]
    
    for i in reversed(range(len(df_historico))):
        df = ExtraerDatos.dividir_en_repeticiones(Leer_ficheros.leercsv_serie(df_historico.at[i, Const.HIST_DATE], user))
        mano = ExtraerDatos.mano_derecha(df)
        
        if mano == es_mano_derecha and len(diccionario_df) < Config.MAXIMO_FICHEROS_HISTORICOS:
            diccionario_df[df_historico.at[i, Const.HIST_DATE]] = df
    
    diccionario_df[date] = df_serie
    return diccionario_df


def fuzzy_tiempo_descanso(valor):
    x = np.arange(0, 700, 1)

    mf1 = fuzz.trapmf(x, [0, 0, 60, 120])
    mf2 = fuzz.trimf(x, [60, 120, 180])
    mf3 = fuzz.trimf(x, [180, 240, 300])
    mf4 = fuzz.trapmf(x, [240, 360, 400, 400])

    pertenencia_mf1 = fuzz.interp_membership(x, mf1, valor)
    pertenencia_mf2 = fuzz.interp_membership(x, mf2, valor)
    pertenencia_mf3 = fuzz.interp_membership(x, mf3, valor)
    pertenencia_mf4 = fuzz.interp_membership(x, mf4, valor)

    valor_borroso_mf1 = pertenencia_mf1 * 0.5
    valor_borroso_mf2 = pertenencia_mf2 * 0.25
    valor_borroso_mf3 = pertenencia_mf3 * 0.15
    valor_borroso_mf4 = pertenencia_mf4 * 0.1

    valor_borroso_total = valor_borroso_mf1 + valor_borroso_mf2 + valor_borroso_mf3 + valor_borroso_mf4 
    return valor_borroso_total