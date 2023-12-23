import os
import pandas as pd
import re
import json
import Constantes as Const

RUTA_CARPETA_SALIDA = "Output_fatigue"
RUTA_CARPETA_JSON = RUTA_CARPETA_SALIDA + "\Jsons" 
RUTA_CSV = RUTA_CARPETA_SALIDA + "\output.csv"

def comprobar_y_crear_carpeta():
    if not os.path.exists(RUTA_CARPETA_SALIDA):
        os.makedirs(RUTA_CARPETA_SALIDA)
    if not os.path.exists(RUTA_CARPETA_JSON):
        os.makedirs(RUTA_CARPETA_JSON)

def obtener_csv_output() -> pd.core.frame.DataFrame:
    try:
        df = pd.read_csv(RUTA_CSV)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['nombre_paciente','ruta_json', 'valor_fatiga'])
    return df

def modificar_csv_output(nombre_paciente:str, ruta_json:str, valor_fatiga: float):
    df = obtener_csv_output()
    nueva_fila = {'nombre_paciente': nombre_paciente, 'ruta_json': ruta_json, 'valor_fatiga': valor_fatiga}
    df = df._append(nueva_fila, ignore_index=True)
    df.to_csv(RUTA_CSV, index=False)


def crear_ruta_json(ruta_datos_originales: str, user: str):
    patron = re.compile(r'CSVs/TrackingData/OculusTracking_(.*?).csv')
    fecha = patron.search(ruta_datos_originales)
    return RUTA_CARPETA_JSON + str("\Fatigue_") + user + "_" + str(fecha.group(1)) + ".json"

def obtener_json_output(ruta_json: str) -> pd.core.frame.DataFrame:
    archivo_json = None
    if os.path.exists(ruta_json):
        # Leer el contenido del archivo
        with open(ruta_json, 'r') as archivo:
            archivo_json = json.load(archivo)
    else:
        archivo_json = {"repeticiones": []}
        with open(ruta_json, 'w') as archivo:
            json.dump(archivo_json, archivo, indent=2)
    return archivo_json

def modificar_json_output(ruta_json: str, datos_a_escribir:dict, valores_fatiga: [float]):
    datos_fichero_json = obtener_json_output(ruta_json)
    datos_fichero_json = escribir_datos_json(datos_fichero_json, datos_a_escribir, valores_fatiga)
    with open(ruta_json, 'w') as archivo:
            json.dump(datos_fichero_json, archivo, indent=2)

def escribir_datos_json(datos_fichero_json: dict, datos_a_escribir: dict, valores_fatiga:[float])-> dict:
    i = 0
    for repeticion, fatiga in datos_a_escribir.items():
        nueva_repeticion = {
            "num_repeticion": repeticion,
            "fatiga_repeticion": valores_fatiga[i],
            "fatiga_metricas": fatiga, 
            "avisos": escribir_mensajes_fatiga(fatiga)
        }
        datos_fichero_json["repeticiones"].append(nueva_repeticion)
        i += 1
    return datos_fichero_json

def escribir_mensajes_fatiga(fatiga: dict):
    mensajes = []
    for nombre, valor in fatiga["FATIGA"].items():
        if valor > 0.5:
            mensajes.append("El paciente ha disminuido su rendimiento en "  + str(nombre))
    if fatiga[Const.FATIGA_NUM_CAIDAS_BLOQUE]>0:
        mensajes.append("Al paciente se le ha caido el bloque: "+ str(fatiga[Const.FATIGA_NUM_CAIDAS_BLOQUE]) + " veces")
    if fatiga[Const.FATIGA_MOVIMIENTO_INCORRECTO]:
        mensajes.append("El paciente ha dejado el objeto fuera de la caja")
    return mensajes

 





