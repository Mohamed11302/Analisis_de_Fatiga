import os
import pandas as pd
import re
import json
import Constantes.Configuracion as Config
import Constantes.Constantes as Const


def generar_Salida(user:str, juego):
    comprobar_y_crear_carpeta()
    ruta_json = crear_ruta_json(juego.date)
    modificar_csv_output(user, ruta_json, juego)  
    modificar_json_output(ruta_json, juego)
    

def escribir_datos_json(datos_fichero_json: dict, juego)-> dict:
    i = 0
    for repeticion, fatiga in juego.fatiga_por_metrica.items():
        nueva_repeticion = {
            "num_repeticion": repeticion,
            "fatiga_repeticion": juego.fatiga_por_repeticion[i],
            "fatiga_metricas": fatiga, 
            "avisos": escribir_mensajes_fatiga(fatiga, juego.metricas)
        }
        datos_fichero_json["repeticiones"].append(nueva_repeticion)
        i += 1
    return datos_fichero_json

def escribir_mensajes_fatiga(fatiga: dict, metricas:dict):
    mensajes = []
    for nombre, _ in metricas.items():
        if fatiga[nombre] > 0.5:
            mensajes.append("El paciente ha disminuido su rendimiento en "  + str(nombre))
    if fatiga[Const.PENALIZACION_NUM_CAIDAS_BLOQUE]>0:
        mensajes.append("Al paciente se le ha caido el bloque: "+ str(fatiga[Const.PENALIZACION_NUM_CAIDAS_BLOQUE]) + " veces")
    if fatiga[Const.PENALIZACION_MOVIMIENTO_INCORRECTO]:
        mensajes.append("El paciente ha dejado el objeto fuera de la caja")
    return mensajes


def modificar_json_output(ruta_json: str, datos_a_escribir:dict):
    datos_fichero_json = obtener_json_output(ruta_json)
    datos_fichero_json = escribir_datos_json(datos_fichero_json, datos_a_escribir)
    with open(ruta_json, 'w') as archivo:
            json.dump(datos_fichero_json, archivo, indent=2)

def crear_ruta_json(date: str):
    return Config.RUTA_CARPETA_JSON + Config.PREFIJO_FICHEROS + date + ".json"

def comprobar_y_crear_carpeta():
    if not os.path.exists(Config.RUTA_CARPETA_SALIDA):
        os.makedirs(Config.RUTA_CARPETA_SALIDA)
    if not os.path.exists(Config.RUTA_CARPETA_JSON):
        os.makedirs(Config.RUTA_CARPETA_JSON)

def obtener_csv_output() -> pd.core.frame.DataFrame:
    try:
        df = pd.read_csv(Config.RUTA_CSV)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['nombre_paciente','ruta_json', 'valor_fatiga'])
    return df

def modificar_csv_output(nombre_paciente:str, ruta_json:str, juego):
    df = obtener_csv_output()
    nueva_fila = {'nombre_paciente': nombre_paciente, 'ruta_json': ruta_json, 'valor_fatiga': juego.fatiga_serie}
    if ruta_json not in df['ruta_json'].values:
        df = df._append(nueva_fila, ignore_index=True)
    for juego_historico in juego.data_BBT_historico:
        ruta_json = crear_ruta_json(juego_historico.date)
        df.loc[df['ruta_json'] == ruta_json, 'valor_fatiga'] = juego_historico.fatiga_serie
    df.to_csv(Config.RUTA_CSV, index=False)




def obtener_json_output(ruta_json: str) -> pd.core.frame.DataFrame:
    archivo_json = {"repeticiones": []}
    with open(ruta_json, 'w') as archivo:
        json.dump(archivo_json, archivo, indent=2)
    return archivo_json




 





