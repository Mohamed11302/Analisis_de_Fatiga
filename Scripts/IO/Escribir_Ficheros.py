import os
import pandas as pd
import json
import Constantes.Configuracion as Config
import Constantes.Constantes as Const
import Constantes.Constantes_Output as Const_output

def generar_salida(juego):
    comprobar_y_crear_carpeta(juego.user)
    modificar_csv_output(juego)  
    modificar_json_output(juego)
    print(f"Results saved in {Const_output.OUTPUT_FOLDER}{juego.user}")
    return crear_ruta_json(juego.date, juego.user)

def escribir_datos_json(datos_fichero_json: dict, juego)-> dict:
    i = 0
    for repeticion, fatiga in juego.fatiga_por_metrica.items():
        repeticion = repeticion +1
        inicio_seg =  juego.dataframe[juego.dataframe[Const.NUMREPETICION]==repeticion][Const.TIME]
        #print(repeticion)
        #print(inicio_seg.values[0])
        nueva_repeticion = {
            Const_output.OUTPUT_NUMREPETITION: repeticion,
            Const_output.OUTPUT_FATIGUE_REPETITION: juego.fatiga_por_repeticion[i],
            Const_output.OUTPUT_FATIGUE_METRICS: fatiga, 
            Const_output.OUTPUT_WARNINGS: escribir_mensajes_fatiga(fatiga, juego.metricas),
            Const_output.OUTPUT_INICIO_SEG: inicio_seg.values[0]
        }
        datos_fichero_json[Const_output.OUTPUT_REPETITIONS].append(nueva_repeticion)
        i += 1
    return datos_fichero_json

def escribir_mensajes_fatiga(fatiga: dict, metricas:dict):
    mensajes = []
    for nombre in metricas:
        if fatiga[nombre] > 0.5:
            mensajes.append("The patient has experienced a decrease in performance "  + str(nombre))
    if fatiga[Const.PENALIZATION_BLOCK_DROP]>0:
        mensajes.append("The patient has drop the block "+ str(fatiga[Const.PENALIZATION_BLOCK_DROP]) + " times")
    if fatiga[Const.PENALIZATION_INCORRECT_MOVEMENT]:
        mensajes.append("Incorrect movement. The patient has placed the object outside of the box")
    return mensajes


def modificar_json_output(juego:dict):
    juego_copia = juego
    while juego_copia:
        ruta_json = crear_ruta_json(juego_copia.date, juego_copia.user)
        datos_fichero_json = obtener_json_output(ruta_json)
        datos_fichero_json = escribir_datos_json(datos_fichero_json, juego_copia)
        with open(ruta_json, 'w') as archivo:
                json.dump(datos_fichero_json, archivo, indent=2)
        juego_copia = juego_copia.hijo

def crear_ruta_json(date: str, user:str):
    return Const_output.OUTPUT_FOLDER + user + "/" + Const_output.OUTPUT_JSON_FOLDER + Config.PREFIJO_FICHEROS + date + ".json"

def comprobar_y_crear_carpeta(user:str):
    if not os.path.exists(Const_output.OUTPUT_FOLDER):
        os.makedirs(Const_output.OUTPUT_FOLDER)
    if not os.path.exists(Const_output.OUTPUT_FOLDER + user):
        os.makedirs(Const_output.OUTPUT_FOLDER + user)
    if not os.path.exists(Const_output.OUTPUT_FOLDER + user + "/" + Const_output.OUTPUT_JSON_FOLDER):
        os.makedirs(Const_output.OUTPUT_FOLDER + user + "/" + Const_output.OUTPUT_JSON_FOLDER)

def obtener_csv_output(user: str) -> pd.core.frame.DataFrame:
    try:
        df = pd.read_csv(Const_output.OUTPUT_FOLDER + user + "/" + Const_output.CSV_NAME, index_col=Const_output.OUTPUT_INDEX)
    except:
        df = pd.DataFrame(columns=[Const_output.OUTPUT_USER,Const_output.OUTPUT_DATE, Const_output.OUTPUT_FATIGUE_VALUE, Const_output.OUTPUT_FATIGUE_CLASIFICATION])
    return df

def modificar_csv_output(juego):
    df = obtener_csv_output(juego.user)
    
    if df[Const_output.OUTPUT_DATE].isnull().all() or  df[Const_output.OUTPUT_DATE].max() <= juego.date:
        juego_copia = juego
        while juego_copia:
            df = modificar_registro_csv(df, juego_copia)
            juego_copia = juego_copia.hijo
        df = df.sort_values(Const_output.OUTPUT_DATE)
        df = df.reset_index(drop=True) 
        df.index.name = Const_output.OUTPUT_INDEX
        df.to_csv(Const_output.OUTPUT_FOLDER + juego.user + "/" + Const_output.CSV_NAME, index=True, index_label=Const_output.OUTPUT_INDEX, sep=';')

def modificar_registro_csv(df, juego):
    filtro = df[Const_output.OUTPUT_DATE].eq(juego.date).any()
    if filtro:
        df.loc[df[Const_output.OUTPUT_DATE] == juego.date, Const_output.OUTPUT_FATIGUE_VALUE] = juego.fatiga_serie_num
        df.loc[df[Const_output.OUTPUT_DATE] == juego.date, Const_output.OUTPUT_FATIGUE_CLASIFICATION] = juego.fatiga_serie_clasificacion
    else:
        nueva_fila2 = {Const_output.OUTPUT_USER:juego.user, Const_output.OUTPUT_DATE: juego.date, Const_output.OUTPUT_FATIGUE_VALUE: juego.fatiga_serie_num, Const_output.OUTPUT_FATIGUE_CLASIFICATION: juego.fatiga_serie_clasificacion}
        df = df._append(nueva_fila2, ignore_index=True)
    return df


def obtener_json_output(ruta_json: str) -> pd.core.frame.DataFrame:
    archivo_json = {Const_output.OUTPUT_REPETITIONS: []}
    with open(ruta_json, 'w') as archivo:
        json.dump(archivo_json, archivo, indent=2)
    return archivo_json




 





