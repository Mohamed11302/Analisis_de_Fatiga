import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Constantes as Const
import CalculoFatigas
import auxiliares as aux
import Tratamiento_CSV

def obtener_datos_paciente(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int) -> dict:
    datos_paciente = {
        Const.FATIGA_WRIST : datos_flexion_muneca_por_repeticion(df, inicio_rep, final_rep),
        Const.FATIGA_STRENGTH : datos_fuerza_por_repeticion(df, inicio_rep, final_rep),
        Const.FATIGA_TIEMPO : datos_tiempo_por_repeticion(df, inicio_rep, final_rep),
        Const.FATIGA_VELOCIDAD : datos_velocidad_por_repeticion(df, inicio_rep, final_rep),
        Const.FATIGA_HEADPOSITION : datos_posicion_cabeza_por_repeticion(df, inicio_rep, final_rep),
        Const.FATIGA_CURVATURA_MANO : datos_curvatura(df, inicio_rep, final_rep),
        Const.FATIGA_NUM_CAIDAS_BLOQUE : datos_caida_del_bloque(df, inicio_rep, final_rep),
        Const.FATIGA_MOVIMIENTO_INCORRECTO : datos_movimiento_correcto(df, inicio_rep, final_rep)
    }
    return normalizar_datos_paciente(datos_paciente)

def datos_iniciales_paciente(df:pd.core.frame.DataFrame, porcentaje:int, user:str):
    datos_historico = Tratamiento_CSV.RegistroHistoricoPaciente(user)
    datos_primeras_reps = datos_primeras_repeticiones_paciente(df, porcentaje)
    if datos_historico != None:
        datos_a_comparar = weight_historic_initial(datos_historico, datos_primeras_reps)
        return datos_a_comparar
    else:
        return datos_primeras_reps

def weight_historic_initial(df_historico:pd.core.frame.DataFrame, df_primeras_reps:pd.core.frame.DataFrame)->pd.core.frame.DataFrame:
    df_datos_a_comparar = {}
    for clave, valor in df_historico.items():
        df_datos_a_comparar[clave] = media_historic_initial(valor, df_primeras_reps[clave])
    return df_datos_a_comparar


def media_historic_initial(valor_historico, valor_primeras_reps):
    if isinstance(valor_historico, dict) or isinstance(valor_primeras_reps, dict):
        valores_por_subclave = {}
        for clave, valor in valor_historico.items():
            if clave not in valores_por_subclave:
                valores_por_subclave[clave] = []
            valores_por_subclave[clave].append(valor)
            valores_por_subclave[clave].append(valor_primeras_reps[clave])
        media = aux.media_dict(valores_por_subclave)
    else:
        media = (valor_historico+valor_primeras_reps)/2
    return media


def datos_primeras_repeticiones_paciente(df:pd.core.frame.DataFrame, porcentaje: int)->dict:
    INICIO_REPES = 1
    num_repeticiones = df[Const.NUMREPETICION].max()
    num_rep_iniciales = round(num_repeticiones * (porcentaje/100))
    _datos_paciente = obtener_datos_paciente(df, INICIO_REPES, INICIO_REPES+num_rep_iniciales)
    
    #Sacamos la media de los valores
    _datos_paciente[Const.FATIGA_HEADPOSITION] = aux.media_dict(_datos_paciente[Const.FATIGA_HEADPOSITION])
    _datos_paciente[Const.FATIGA_CURVATURA_MANO] = aux.media_dict(_datos_paciente[Const.FATIGA_CURVATURA_MANO])
    for columna in [Const.FATIGA_WRIST, Const.FATIGA_STRENGTH, Const.FATIGA_TIEMPO, Const.FATIGA_VELOCIDAD]:
        _datos_paciente[columna] = sum(_datos_paciente[columna])/len(_datos_paciente[columna])


    if Const.FATIGA_MOVIMIENTO_INCORRECTO in _datos_paciente:
        del _datos_paciente[Const.FATIGA_MOVIMIENTO_INCORRECTO]
    if Const.FATIGA_NUM_CAIDAS_BLOQUE in _datos_paciente:
        del _datos_paciente[Const.FATIGA_NUM_CAIDAS_BLOQUE]
    
    return _datos_paciente


def normalizar_datos_paciente(datos:dict):
    for clave, valor in datos.items():
        if clave != Const.FATIGA_MOVIMIENTO_INCORRECTO and clave != Const.FATIGA_NUM_CAIDAS_BLOQUE and clave != Const.FATIGA_HEADPOSITION:
            if isinstance(valor, list):
                datos[clave] = aux.normalizar_list(valor)
            if isinstance(valor, dict):
                datos[clave] = aux.normalizar_dict(valor)
    return datos




############################ DATOS VELOCIDAD ######################################
def velocidad_media_por_repeticion(df:pd.core.frame.DataFrame, repeticion: int)-> [float]:
    hand_velocity_x = (df[df[Const.NUMREPETICION] == repeticion][Const.HANDVELOCITY_X]).values
    hand_velocity_y = (df[df[Const.NUMREPETICION] == repeticion][Const.HANDVELOCITY_Y]).values
    hand_velocity_z = (df[df[Const.NUMREPETICION] == repeticion][Const.HANDVELOCITY_Z]).values
    speed = []
    for i in range(0, len(hand_velocity_x)):
        speed.append(aux.calcular_magnitud(hand_velocity_x[i], hand_velocity_y[i], hand_velocity_z[i]))
    average_speed = sum(speed)/len(speed)
    return average_speed


def datos_velocidad_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int) -> [float]:
    velocidad = []
    for i in range(inicio_rep, final_rep):
        velocidad.append(round(velocidad_media_por_repeticion(df, i), 3))
    return velocidad

############################ DATOS TIEMPO ######################################
def datos_tiempo_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)->[float]:
    tiempo_por_repeticion = []
    for i in range(inicio_rep, final_rep):
        time = (df[df[Const.NUMREPETICION] == i][Const.TIME]).values
        tiempo_por_repeticion.append(round(max(time)-min(time), 3))
    return tiempo_por_repeticion

############################ DATOS STRENGTH ######################################

def metricas_de_agarre():
    variables_a_considerar = [
        Const.STRENGTHTHUMBINDEX,
        Const.STRENGTHTHUMB_MIDDLE,
        Const.STRENGTHTHUMB_RING,
        Const.STRENGTHTHUMB_PINKY,
        Const.STRENGTHPALM_INDEX,
        Const.STRENGTHPALM_MIDDLE,
        Const.STRENGTHPALM_RING,
        Const.STRENGTHPALM_PINKY
    ]
    return variables_a_considerar

def datos_fuerza_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)->[float]:
    #  Criterio: Se toman los valores mayores a 0 y se calcula su media
    fuerza_de_agarre = []
    variables_a_considerar = metricas_de_agarre()
    for rep in range(inicio_rep, final_rep):
        fuerza_dedo = []
        for variable_a_considerar in variables_a_considerar:
            fuerza_dedo.append((df[(df[Const.NUMREPETICION] == rep) & (df[variable_a_considerar] > 0)][variable_a_considerar]).values)
        fuerza_dedo = np.concatenate(fuerza_dedo)
        if (len(fuerza_dedo)>0):
            fuerza_de_agarre.append(sum(fuerza_dedo)/len(fuerza_dedo))
        else:
            fuerza_de_agarre.append(0)
        fuerza_dedo = []
    return fuerza_de_agarre

############################ DATOS WRISTTWIST ######################################

def datos_flexion_muneca_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    flexion_muneca = []
    for i in range(inicio_rep, final_rep):
        twist = (df[df[Const.NUMREPETICION] == i][Const.WRISTTWIST]).values
        flexion_muneca.append(round(sum(twist)/len(twist), 3))
    return flexion_muneca


############################ DATOS CABEZA ######################################
def datos_posicion_cabeza_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)-> dict:
    head_position = {
        Const.HEADPOSITION_MAX_X: [],
        Const.HEADPOSITION_MIN_X: [],
        Const.HEADPOSITION_MAX_Y: [],
        Const.HEADPOSITION_MIN_Y: [],
        Const.HEADPOSITION_MAX_Z: [],
        Const.HEADPOSITION_MIN_Z: []
    }
    for i in range(inicio_rep, final_rep):
        head_position[Const.HEADPOSITION_MAX_X].append(df[df[Const.NUMREPETICION]==i][Const.HEADPOSITION_X].max())
        head_position[Const.HEADPOSITION_MIN_X].append(df[df[Const.NUMREPETICION]==i][Const.HEADPOSITION_X].min())

        head_position[Const.HEADPOSITION_MAX_Y].append(df[df[Const.NUMREPETICION]==i][Const.HEADPOSITION_Y].max())
        head_position[Const.HEADPOSITION_MIN_Y].append(df[df[Const.NUMREPETICION]==i][Const.HEADPOSITION_Y].min())

        head_position[Const.HEADPOSITION_MAX_Z].append(df[df[Const.NUMREPETICION]==i][Const.HEADPOSITION_Z].max())
        head_position[Const.HEADPOSITION_MIN_Z].append(df[df[Const.NUMREPETICION]==i][Const.HEADPOSITION_Z].min())
    
    return head_position

############################ DATOS CURVATURA ######################################
def datos_curvatura(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)-> dict:
    curvatura = {
        Const.CURVATURA_TOMAR_BLOQUE_Y: [],
        Const.CURVATURA_PUNTO_MAS_ALTO_Y_IDA: [],
        Const.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA: [],
        Const.CURVATURA_SOLTAR_BLOQUE_Y: [],
        Const.CURVATURA_SOLTAR_BLOQUE_X: [],
    }
    for repeticion in range(inicio_rep, final_rep):
        rep_data = df[df[Const.NUMREPETICION] == repeticion]

        datos_ida = rep_data[rep_data[Const.ISPINCHGRABBING] == True]
        datos_vuelta = rep_data[rep_data[Const.ISPINCHGRABBING] == False]

        curvatura[Const.CURVATURA_TOMAR_BLOQUE_Y].append(datos_ida[Const.HANDPOSITION_Y].iloc[0])
        curvatura[Const.CURVATURA_PUNTO_MAS_ALTO_Y_IDA].append(datos_ida[Const.HANDPOSITION_Y].max())
        curvatura[Const.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA].append(datos_vuelta[Const.HANDPOSITION_Y].max())
        curvatura[Const.CURVATURA_SOLTAR_BLOQUE_Y].append(datos_vuelta[Const.HANDPOSITION_Y].iloc[0])
        curvatura[Const.CURVATURA_SOLTAR_BLOQUE_X].append(datos_vuelta[Const.HANDPOSITION_X].iloc[0])

    return curvatura

############################ DATOS CAIDA DEL BLOQUE ######################################

def datos_caida_del_bloque(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)->[int]:
    caida_del_bloque = []
    for rep in range(inicio_rep, final_rep):
        df = df[df[Const.NUMREPETICION]== rep]
        num_intentos = 0
        moviendo_objeto = False
        for valor in df[Const.GRABIDENTIFIER]:
            if valor != np.nan and moviendo_objeto==False:
                moviendo_objeto = True
                num_intentos += 1
            if valor == np.nan:
                moviendo_objeto = False
        caida_del_bloque.append(num_intentos)
        num_intentos = 0
    return caida_del_bloque

############################ DATOS MOVIMIENTO CORRECTO ######################################
def datos_movimiento_correcto(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)-> [bool]:
    movimiento_correcto = []
    for rep in range(inicio_rep, final_rep):
        df = df[df[Const.NUMREPETICION]== rep]
        mov_correcto = False
        if df[Const.MOVEDCORRECTLY].any():
            mov_correcto = True
        movimiento_correcto.append(mov_correcto)
    return movimiento_correcto




############################ DATOS MOVIMIENTO CORRECTO ######################################
def mediahistorica(df: pd.core.frame.DataFrame)-> dict:
    porcentaje_a_eliminar = 20
    datos = obtener_datos_paciente(df, 2, df[Const.NUMREPETICION].max())
    columnas_a_procesar = [
        Const.FATIGA_VELOCIDAD,
        Const.FATIGA_TIEMPO,
        Const.FATIGA_WRIST,
        Const.FATIGA_STRENGTH,
        Const.FATIGA_HEADPOSITION,
        Const.FATIGA_CURVATURA_MANO
    ]

    for columna in columnas_a_procesar:
        if isinstance(datos[columna], list):
            datos[columna] = CalculoFatigas.quitar_porcentaje_mas_alto(datos[columna], porcentaje_a_eliminar)
            datos[columna] = CalculoFatigas.quitar_porcentaje_mas_bajo(datos[columna], porcentaje_a_eliminar)
            datos[columna] = sum(datos[columna]) / len(datos[columna])

        if isinstance(datos[columna], pd.DataFrame):
            for subcolumna in datos[columna].columns:
                datos[columna][subcolumna] = CalculoFatigas.quitar_porcentaje_mas_alto(datos[columna][subcolumna], porcentaje_a_eliminar)
                datos[columna][subcolumna] = CalculoFatigas.quitar_porcentaje_mas_bajo(datos[columna][subcolumna], porcentaje_a_eliminar)

    for columna in [Const.FATIGA_HEADPOSITION, Const.FATIGA_CURVATURA_MANO]:
        datos[columna] = aux.media_dict(datos[columna])


    if Const.FATIGA_MOVIMIENTO_INCORRECTO in datos:
        del datos[Const.FATIGA_MOVIMIENTO_INCORRECTO]
    if Const.FATIGA_NUM_CAIDAS_BLOQUE in datos:
        del datos[Const.FATIGA_NUM_CAIDAS_BLOQUE]
    
    return datos


def ponderar_media_historica(datos:dict)->dict:
    """Dados los datos historicos, aplicaremos un valor ponderado de manera que los mas cercanos a la ejecucion que
       vamos a tratar tendrán mayor peso"""
    medias_por_componente = {}
    _isDict = False
    claves_disponibles = datos[list(datos.keys())[0]].keys()

    for clave in claves_disponibles:
        valores_por_fecha = []
        valores_por_subclave = {}
        for fecha in datos:
            valor = datos[fecha][clave]

            if isinstance(valor, dict):
                for c, v in valor.items():
                    if c not in valores_por_subclave:
                        valores_por_subclave[c] = []
                    valores_por_subclave[c].append(v)
                _isDict = True
            else:
                valores_por_fecha.append(valor)
                _isDict = False

        if _isDict:            
            medias_por_componente[clave] = aux.media_dict(valores_por_subclave)
        else: 
            media = int(np.mean(valores_por_fecha))
            medias_por_componente[clave] = media

    return medias_por_componente



