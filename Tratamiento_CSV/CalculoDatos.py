import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Constantes


def obtener_datos_paciente(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int) -> dict:
    datos_paciente = {
        Constantes.FATIGA_WRIST : datos_flexion_muneca_por_repeticion(df, inicio_rep, final_rep),
        Constantes.FATIGA_STRENGTH : datos_fuerza_por_repeticion(df, inicio_rep, final_rep),
        Constantes.FATIGA_TIEMPO : datos_tiempo_por_repeticion(df, inicio_rep, final_rep),
        Constantes.FATIGA_VELOCIDAD : datos_velocidad_por_repeticion(df, inicio_rep, final_rep),
        Constantes.FATIGA_HEADPOSITION : datos_posicion_cabeza_por_repeticion(df, inicio_rep, final_rep),
        Constantes.FATIGA_CURVATURA_MANO : datos_curvatura(df, inicio_rep, final_rep)
    }
    return datos_paciente

def datos_iniciales_paciente(df:pd.core.frame.DataFrame, porcentaje: int)->dict:
    INICIO_REPES = 2
    datos_de_fatiga ={}
    num_repeticiones = df[Constantes.NUMREPETICION].max()
    num_rep_iniciales = round(num_repeticiones * (porcentaje/100))
    _datos_paciente = obtener_datos_paciente(df, INICIO_REPES, INICIO_REPES+num_rep_iniciales)
    fatiga_headposition = media_datos(_datos_paciente[Constantes.FATIGA_HEADPOSITION])
    fatiga_curvatura_mano = media_datos(_datos_paciente[Constantes.FATIGA_CURVATURA_MANO])

    for columna in [Constantes.FATIGA_WRIST, Constantes.FATIGA_STRENGTH, Constantes.FATIGA_TIEMPO, Constantes.FATIGA_VELOCIDAD]:
        datos_de_fatiga[columna] = round(sum(_datos_paciente[columna])/len(_datos_paciente[columna]), 3)
    
    datos_fatiga_posicion_cabeza = {}
    for columna in [Constantes.HEADPOSITION_MAX_X, Constantes.HEADPOSITION_MIN_X,
                    Constantes.HEADPOSITION_MAX_Y, Constantes.HEADPOSITION_MIN_Y,
                    Constantes.HEADPOSITION_MAX_Z, Constantes.HEADPOSITION_MIN_Z]:
        datos_fatiga_posicion_cabeza[columna] = fatiga_headposition[columna]

    datos_fatiga_curvatura_mano = {}
    for columna in [Constantes.CURVATURA_PUNTO_MAS_ALTO_Y_IDA, Constantes.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA,
                    Constantes.CURVATURA_SOLTAR_BLOQUE_X, Constantes.CURVATURA_SOLTAR_BLOQUE_Y,
                    Constantes.CURVATURA_TOMAR_BLOQUE_Y]:
        datos_fatiga_curvatura_mano[columna] = fatiga_curvatura_mano[columna]

    datos_de_fatiga[Constantes.FATIGA_HEADPOSITION] = datos_fatiga_posicion_cabeza
    datos_de_fatiga[Constantes.FATIGA_CURVATURA_MANO] = datos_fatiga_curvatura_mano
    datos_iniciales_paciente = {
        'NUM_REP_INICIALES' : num_rep_iniciales,
        'NUM_REP' : num_repeticiones,
        'DATOS_INICIALES_PACIENTE' : datos_de_fatiga
    }
    return datos_iniciales_paciente


############################ DATOS VELOCIDAD ######################################
def calcular_magnitud(velocidad_x: float, velocidad_y: float, velocidad_z: float) -> float:
    magnitud = round(math.sqrt(velocidad_x**2 + velocidad_y**2 + velocidad_z**2), 2)
    return magnitud

def vectorizar(handvelocity_x: float, handvelocity_y:float, handvelocity_z:float) -> [float]:
    vector = []
    for i in range(0, len(handvelocity_x)):
        vector.append(calcular_magnitud(handvelocity_x.values[i],handvelocity_y.values[i],handvelocity_z.values[i]))
    return vector

def velocidad_media_por_repeticion(df:pd.core.frame.DataFrame, repeticion: int):
    hand_velocity_x = (df[df[Constantes.NUMREPETICION] == repeticion][Constantes.HANDVELOCITY_X]).values
    hand_velocity_y = (df[df[Constantes.NUMREPETICION] == repeticion][Constantes.HANDVELOCITY_Y]).values
    hand_velocity_z = (df[df[Constantes.NUMREPETICION] == repeticion][Constantes.HANDVELOCITY_Z]).values
    speed = []
    for i in range(0, len(hand_velocity_x)):
        speed.append(calcular_magnitud(hand_velocity_x[i], hand_velocity_y[i], hand_velocity_z[i]))
    average_speed = sum(speed)/len(speed)
    return average_speed


def datos_velocidad_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    velocidad = []
    for i in range(inicio_rep, final_rep):
        velocidad.append(velocidad_media_por_repeticion(df, i))
    return velocidad

############################ DATOS TIEMPO ######################################
def datos_tiempo_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    tiempo_por_repeticion = []
    for i in range(inicio_rep, final_rep):
        time = (df[df[Constantes.NUMREPETICION] == i][Constantes.TIME]).values
        tiempo_por_repeticion.append(max(time)-min(time))
    return tiempo_por_repeticion

############################ DATOS STRENGTH ######################################

def tipo_agarre(df:pd.core.frame.DataFrame)->[str]:
    tipos_agarre = []
    if df[Constantes.ISPINCHGRABBING].any():
        tipos_agarre.append(Constantes.ISPINCHGRABBING)
    if df[Constantes.ISPALMGRABBING].any():
        tipos_agarre.append(Constantes.ISPALMGRABBING)
    if df[Constantes.ISAUTOGRIPGRABBING].any():
        tipos_agarre.append(Constantes.ISAUTOGRIPGRABBING)
    return tipos_agarre

""" def metricas_de_agarre(tipo_agarre):
    variables_a_considerar = []
    if tipo_agarre==Constantes.ISPINCHGRABBING:
        variables_a_considerar = [
            Constantes.STRENGTHTHUMBINDEX,
            Constantes.STRENGTHTHUMB_MIDDLE,
            Constantes.STRENGTHTHUMB_RING,
            Constantes.STRENGTHTHUMB_PINKY,
        ]
    elif tipo_agarre == Constantes.ISPALMGRABBING:
        variables_a_considerar = [
            Constantes.STRENGTHPALM_INDEX,
            Constantes.STRENGTHPALM_MIDDLE,
            Constantes.STRENGTHPALM_RING,
            Constantes.STRENGTHPALM_PINKY
        ]
    return variables_a_considerar """

def metricas_de_agarre():
    variables_a_considerar = [
        Constantes.STRENGTHTHUMBINDEX,
        Constantes.STRENGTHTHUMB_MIDDLE,
        Constantes.STRENGTHTHUMB_RING,
        Constantes.STRENGTHTHUMB_PINKY,
        Constantes.STRENGTHPALM_INDEX,
        Constantes.STRENGTHPALM_MIDDLE,
        Constantes.STRENGTHPALM_RING,
        Constantes.STRENGTHPALM_PINKY
    ]
    return variables_a_considerar

def fuerza_de_agarre(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    #  Criterio: Se toman los valores mayores a 0 y se calcula su media
    fuerza_de_agarre = []
    variables_a_considerar = metricas_de_agarre()
    for i in range(inicio_rep, final_rep):
        fuerza_dedo = []
        for j in variables_a_considerar:
            fuerza_dedo.append((df[(df[Constantes.NUMREPETICION] == i) & (df[j] > 0)][j]).values)
        fuerza_dedo = np.concatenate(fuerza_dedo)
        if (len(fuerza_dedo)>0):
            fuerza_de_agarre.append(sum(fuerza_dedo)/len(fuerza_dedo))
        else:
            fuerza_de_agarre.append(0)
        fuerza_dedo = []
    return fuerza_de_agarre

def datos_fuerza_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    fatiga_por_repeticion = []
    fatiga_por_repeticion.append(fuerza_de_agarre(df, inicio_rep, final_rep))
    fatiga_por_repeticion = np.concatenate(fatiga_por_repeticion)
    #plt.show()
    return fatiga_por_repeticion.tolist()


############################ DATOS WRISTTWIST ######################################

def datos_flexion_muneca_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    flexion_muneca = []
    for i in range(inicio_rep, final_rep):
        twist = (df[df[Constantes.NUMREPETICION] == i][Constantes.WRISTTWIST]).values
        flexion_muneca.append(round(sum(twist)/len(twist), 3))
    return flexion_muneca


############################ DATOS CABEZA ######################################
def datos_posicion_cabeza_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)-> dict:
    head_position = {
        Constantes.HEADPOSITION_MAX_X: [],
        Constantes.HEADPOSITION_MIN_X: [],
        Constantes.HEADPOSITION_MAX_Y: [],
        Constantes.HEADPOSITION_MIN_Y: [],
        Constantes.HEADPOSITION_MAX_Z: [],
        Constantes.HEADPOSITION_MIN_Z: []
    }
    for i in range(inicio_rep, final_rep):
        head_position[Constantes.HEADPOSITION_MAX_X].append(df[df[Constantes.NUMREPETICION]==i][Constantes.HEADPOSITION_X].max())
        head_position[Constantes.HEADPOSITION_MIN_X].append(df[df[Constantes.NUMREPETICION]==i][Constantes.HEADPOSITION_X].min())

        head_position[Constantes.HEADPOSITION_MAX_Y].append(df[df[Constantes.NUMREPETICION]==i][Constantes.HEADPOSITION_Y].max())
        head_position[Constantes.HEADPOSITION_MIN_Y].append(df[df[Constantes.NUMREPETICION]==i][Constantes.HEADPOSITION_Y].min())

        head_position[Constantes.HEADPOSITION_MAX_Z].append(df[df[Constantes.NUMREPETICION]==i][Constantes.HEADPOSITION_Z].max())
        head_position[Constantes.HEADPOSITION_MIN_Z].append(df[df[Constantes.NUMREPETICION]==i][Constantes.HEADPOSITION_Z].min())
    
    return head_position

def media_datos(diccionario: dict):
    nuevo_diccionario = {}
    for clave, lista in diccionario.items():
        nuevo_diccionario[clave] = sum(lista) / len(lista)
    return nuevo_diccionario


############################ DATOS CURVATURA ######################################
def datos_curvatura(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)-> dict:
    curvatura = {
        Constantes.CURVATURA_TOMAR_BLOQUE_Y: [],
        Constantes.CURVATURA_PUNTO_MAS_ALTO_Y_IDA: [],
        Constantes.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA: [],
        Constantes.CURVATURA_SOLTAR_BLOQUE_Y: [],
        Constantes.CURVATURA_SOLTAR_BLOQUE_X: [],
    }
    for repeticion in range(inicio_rep, final_rep):
        rep_data = df[df[Constantes.NUMREPETICION] == repeticion]

        datos_ida = rep_data[rep_data[Constantes.ISPINCHGRABBING] == True]
        datos_vuelta = rep_data[rep_data[Constantes.ISPINCHGRABBING] == False]

        curvatura[Constantes.CURVATURA_TOMAR_BLOQUE_Y].append(datos_ida[Constantes.HANDPOSITION_Y].iloc[0])
        curvatura[Constantes.CURVATURA_PUNTO_MAS_ALTO_Y_IDA].append(datos_ida[Constantes.HANDPOSITION_Y].max())
        curvatura[Constantes.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA].append(datos_vuelta[Constantes.HANDPOSITION_Y].max())
        curvatura[Constantes.CURVATURA_SOLTAR_BLOQUE_Y].append(datos_vuelta[Constantes.HANDPOSITION_Y].iloc[0])
        curvatura[Constantes.CURVATURA_SOLTAR_BLOQUE_X].append(datos_vuelta[Constantes.HANDPOSITION_X].iloc[0])

    return curvatura