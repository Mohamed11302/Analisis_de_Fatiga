import os
import pandas as pd
import re
import json
import Constantes.Configuracion as Config
import Constantes.Constantes as Const


def generar_Salida(juego):
    comprobar_y_crear_carpeta(juego.user)
    ruta_json = crear_ruta_json(juego.date, juego.user)
    modificar_csv_output(juego)  
    modificar_json_output(ruta_json, juego)
    

def escribir_datos_json(datos_fichero_json: dict, juego)-> dict:
    i = 0
    for repeticion, fatiga in juego.fatiga_por_metrica.items():
        nueva_repeticion = {
            Const.SALIDA_NUMREPETICION: repeticion,
            Const.SALIDA_FATIGA_REPETICION: juego.fatiga_por_repeticion[i],
            Const.SALIDA_FATIGA_METRICAS: fatiga, 
            Const.SALIDA_AVISOS: escribir_mensajes_fatiga(fatiga, juego.metricas)
        }
        datos_fichero_json[Const.SALIDA_REPETICIONES].append(nueva_repeticion)
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

def crear_ruta_json(date: str, user:str):
    return Config.RUTA_CARPETA_SALIDA + user + "/" + Config.RUTA_CARPETA_JSON + Config.PREFIJO_FICHEROS + date + ".json"

def comprobar_y_crear_carpeta(user:str):
    if not os.path.exists(Config.RUTA_CARPETA_SALIDA):
        os.makedirs(Config.RUTA_CARPETA_SALIDA)
    if not os.path.exists(Config.RUTA_CARPETA_SALIDA + user):
        os.makedirs(Config.RUTA_CARPETA_SALIDA + user)
    if not os.path.exists(Config.RUTA_CARPETA_SALIDA + user + "/" + Config.RUTA_CARPETA_JSON):
        os.makedirs(Config.RUTA_CARPETA_SALIDA + user + "/" + Config.RUTA_CARPETA_JSON)

def obtener_csv_output(user: str) -> pd.core.frame.DataFrame:
    try:
        df = pd.read_csv(Config.RUTA_CARPETA_SALIDA + user + "/" + Config.RUTA_CSV, index_col=Const.SALIDA_INDICE)
    except:
        df = pd.DataFrame(columns=[Const.SALIDA_USER,Const.SALIDA_DATE, Const.SALIDA_FATIGA])
    return df

def modificar_csv_output(juego):
    df = obtener_csv_output(juego.user)
    if df[Const.SALIDA_DATE].isnull().all() or  df[Const.SALIDA_DATE].max() <= juego.date:
        for juego_historico in juego.data_BBT_historico:
            df = modificar_linea_csv(df, juego_historico.user, juego_historico.date, juego_historico.fatiga_serie)
        df = modificar_linea_csv(df, juego.user, juego.date, juego.fatiga_serie)
        df = df.sort_values(Const.SALIDA_DATE)
        df = df.reset_index(drop=True) 
        df.index.name = Const.SALIDA_INDICE
        df.to_csv(Config.RUTA_CARPETA_SALIDA + juego.user + "/" + Config.RUTA_CSV, index=True, index_label=Const.SALIDA_INDICE)

def modificar_linea_csv(df, user, date, fatiga):
    filtro = df[Const.SALIDA_DATE].eq(date).any()
    if filtro:
        df.loc[df[Const.SALIDA_DATE] == date, Const.SALIDA_FATIGA] = fatiga
    else:
        nueva_fila2 = {Const.SALIDA_USER:user, Const.SALIDA_DATE: date, Const.SALIDA_FATIGA: fatiga}
        df = df._append(nueva_fila2, ignore_index=True)
    return df


def obtener_json_output(ruta_json: str) -> pd.core.frame.DataFrame:
    archivo_json = {Const.SALIDA_REPETICIONES: []}
    with open(ruta_json, 'w') as archivo:
        json.dump(archivo_json, archivo, indent=2)
    return archivo_json




 




