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
        Constantes.FATIGA_CURVATURA_MANO : datos_curvatura(df, inicio_rep, final_rep),
        Constantes.FATIGA_NUM_CAIDAS_BLOQUE : datos_caida_del_bloque(df, inicio_rep, final_rep),
        Constantes.FATIGA_MOVIMIENTO_INCORRECTO : datos_movimiento_correcto(df, inicio_rep, final_rep)
    }
    return datos_paciente

def datos_iniciales_paciente(df:pd.core.frame.DataFrame, porcentaje: int)->dict:
    INICIO_REPES = 1
    num_repeticiones = df[Constantes.NUMREPETICION].max()
    num_rep_iniciales = round(num_repeticiones * (porcentaje/100))
    _datos_paciente = obtener_datos_paciente(df, INICIO_REPES, INICIO_REPES+num_rep_iniciales)
    
    #Sacamos la media de los valores
    _datos_paciente[Constantes.FATIGA_HEADPOSITION] = aux_media_dict(_datos_paciente[Constantes.FATIGA_HEADPOSITION])
    _datos_paciente[Constantes.FATIGA_CURVATURA_MANO] = aux_media_dict(_datos_paciente[Constantes.FATIGA_CURVATURA_MANO])
    for columna in [Constantes.FATIGA_WRIST, Constantes.FATIGA_STRENGTH, Constantes.FATIGA_TIEMPO, Constantes.FATIGA_VELOCIDAD]:
        _datos_paciente[columna] = sum(_datos_paciente[columna])/len(_datos_paciente[columna])

    return _datos_paciente


############################ DATOS VELOCIDAD ######################################
def velocidad_media_por_repeticion(df:pd.core.frame.DataFrame, repeticion: int)-> [float]:
    hand_velocity_x = (df[df[Constantes.NUMREPETICION] == repeticion][Constantes.HANDVELOCITY_X]).values
    hand_velocity_y = (df[df[Constantes.NUMREPETICION] == repeticion][Constantes.HANDVELOCITY_Y]).values
    hand_velocity_z = (df[df[Constantes.NUMREPETICION] == repeticion][Constantes.HANDVELOCITY_Z]).values
    speed = []
    for i in range(0, len(hand_velocity_x)):
        speed.append(aux_calcular_magnitud(hand_velocity_x[i], hand_velocity_y[i], hand_velocity_z[i]))
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
        time = (df[df[Constantes.NUMREPETICION] == i][Constantes.TIME]).values
        tiempo_por_repeticion.append(round(max(time)-min(time), 3))
    return tiempo_por_repeticion

############################ DATOS STRENGTH ######################################

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

def datos_fuerza_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)->[float]:
    #  Criterio: Se toman los valores mayores a 0 y se calcula su media
    fuerza_de_agarre = []
    variables_a_considerar = metricas_de_agarre()
    for rep in range(inicio_rep, final_rep):
        fuerza_dedo = []
        for variable_a_considerar in variables_a_considerar:
            fuerza_dedo.append((df[(df[Constantes.NUMREPETICION] == rep) & (df[variable_a_considerar] > 0)][variable_a_considerar]).values)
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

############################ DATOS CAIDA DEL BLOQUE ######################################

def datos_caida_del_bloque(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)->[int]:
    caida_del_bloque = []
    for rep in range(inicio_rep, final_rep):
        df = df[df[Constantes.NUMREPETICION]== rep]
        num_intentos = 0
        moviendo_objeto = False
        for valor in df[Constantes.GRABIDENTIFIER]:
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
        df = df[df[Constantes.NUMREPETICION]== rep]
        mov_correcto = False
        if df[Constantes.MOVEDCORRECTLY].any():
            mov_correcto = True
        movimiento_correcto.append(mov_correcto)
    return movimiento_correcto

############################ AUXILIARES ######################################
def aux_calcular_magnitud(velocidad_x: float, velocidad_y: float, velocidad_z: float) -> float:
    magnitud = round(math.sqrt(velocidad_x**2 + velocidad_y**2 + velocidad_z**2), 2)
    return magnitud

def aux_vectorizar(x: float, y:float, z:float) -> [float]:
    vector = []
    for i in range(0, len(x)):
        vector.append(aux_calcular_magnitud(x.values[i],y.values[i],z.values[i]))
    return vector

def aux_media_dict(diccionario: dict)->dict:
    nuevo_diccionario = {}
    for clave, lista in diccionario.items():
        nuevo_diccionario[clave] = sum(lista) / len(lista)
    return nuevo_diccionario