import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Variables_Globales


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
    hand_velocity_x = (df[df[Variables_Globales.NUMREPETICION] == repeticion][Variables_Globales.HANDVELOCITY_X]).values
    hand_velocity_y = (df[df[Variables_Globales.NUMREPETICION] == repeticion][Variables_Globales.HANDVELOCITY_Y]).values
    hand_velocity_z = (df[df[Variables_Globales.NUMREPETICION] == repeticion][Variables_Globales.HANDVELOCITY_Z]).values
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
        time = (df[df[Variables_Globales.NUMREPETICION] == i][Variables_Globales.TIME]).values
        tiempo_por_repeticion.append(max(time)-min(time))
    return tiempo_por_repeticion

############################ DATOS STRENGTH ######################################

def tipo_agarre(df:pd.core.frame.DataFrame)->[str]:
    tipos_agarre = []
    if df[Variables_Globales.ISPINCHGRABBING].any():
        tipos_agarre.append(Variables_Globales.ISPINCHGRABBING)
    if df[Variables_Globales.ISPALMGRABBING].any():
        tipos_agarre.append(Variables_Globales.ISPALMGRABBING)
    if df[Variables_Globales.ISAUTOGRIPGRABBING].any():
        tipos_agarre.append(Variables_Globales.ISAUTOGRIPGRABBING)
    return tipos_agarre

def metricas_de_agarre(tipo_agarre):
    variables_a_considerar = []
    if tipo_agarre==Variables_Globales.ISPINCHGRABBING:
        variables_a_considerar = [
            Variables_Globales.STRENGTHTHUMBINDEX,
            Variables_Globales.STRENGTHTHUMB_MIDDLE,
            Variables_Globales.STRENGTHTHUMB_RING,
            Variables_Globales.STRENGTHTHUMB_PINKY,
        ]
    elif tipo_agarre == Variables_Globales.ISPALMGRABBING:
        variables_a_considerar = [
            Variables_Globales.STRENGTHPALM_INDEX,
            Variables_Globales.STRENGTHPALM_MIDDLE,
            Variables_Globales.STRENGTHPALM_RING,
            Variables_Globales.STRENGTHPALM_PINKY
        ]
    return variables_a_considerar

def fuerza_de_agarre(df:pd.core.frame.DataFrame, tipo_agarre, inicio_rep:int, final_rep:int):
    #  Criterio: Se toman los valores mayores a 0 y se calcula su media
    fuerza_de_agarre = []
    variables_a_considerar = metricas_de_agarre(tipo_agarre)
    for i in range(inicio_rep, final_rep):
        fuerza_dedo = []
        for j in variables_a_considerar:
            fuerza_dedo.append((df[(df[Variables_Globales.NUMREPETICION] == i) & (df[j] > 0)][j]).values)
        fuerza_dedo = np.concatenate(fuerza_dedo)
        if (len(fuerza_dedo)>0):
            fuerza_de_agarre.append(sum(fuerza_dedo)/len(fuerza_dedo))

        fuerza_dedo = []
    return fuerza_de_agarre

def datos_fuerza_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    tipos_agarre = [Variables_Globales.ISPINCHGRABBING]
    fatiga_por_repeticion = []
    if len(tipos_agarre) == 2:
        fatiga_1 = fuerza_de_agarre(df, tipos_agarre[0], inicio_rep, final_rep)
        fatiga_2 = fuerza_de_agarre(df, tipos_agarre[1], inicio_rep, final_rep)
        print(fatiga_1)
        print("---")
        print(fatiga_2)
        ##COMPROBAR ESTO
    else:
        fatiga_por_repeticion.append(fuerza_de_agarre(df, tipos_agarre[0], inicio_rep, final_rep))
        fatiga_por_repeticion = np.concatenate(fatiga_por_repeticion)
    #plt.show()
    return fatiga_por_repeticion.tolist()


############################ DATOS WRISTTWIST ######################################

def datos_flexion_muneca_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    flexion_muneca = []
    for i in range(inicio_rep, final_rep):
        twist = (df[df[Variables_Globales.NUMREPETICION] == i][Variables_Globales.WRISTTWIST]).values
        flexion_muneca.append(round(sum(twist)/len(twist), 3))
    return flexion_muneca


############################ DATOS CABEZA ######################################
def datos_posicion_cabeza_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)-> dict:
    head_position = {
        Variables_Globales.MAX_HP_X: [],
        Variables_Globales.MIN_HP_X: [],
        Variables_Globales.MAX_HP_Y: [],
        Variables_Globales.MIN_HP_Y: [],
        Variables_Globales.MAX_HP_Z: [],
        Variables_Globales.MIN_HP_Z: []
    }
    for i in range(inicio_rep, final_rep):
        head_position[Variables_Globales.MAX_HP_X].append(df[df[Variables_Globales.NUMREPETICION]==i][Variables_Globales.HEADPOSITION_X].max())
        head_position[Variables_Globales.MIN_HP_X].append(df[df[Variables_Globales.NUMREPETICION]==i][Variables_Globales.HEADPOSITION_X].min())

        head_position[Variables_Globales.MAX_HP_Y].append(df[df[Variables_Globales.NUMREPETICION]==i][Variables_Globales.HEADPOSITION_Y].max())
        head_position[Variables_Globales.MIN_HP_Y].append(df[df[Variables_Globales.NUMREPETICION]==i][Variables_Globales.HEADPOSITION_Y].min())

        head_position[Variables_Globales.MAX_HP_Z].append(df[df[Variables_Globales.NUMREPETICION]==i][Variables_Globales.HEADPOSITION_Z].max())
        head_position[Variables_Globales.MIN_HP_Z].append(df[df[Variables_Globales.NUMREPETICION]==i][Variables_Globales.HEADPOSITION_Z].min())
    
    return head_position

def media_datos_posicion_cabeza(posicion_cabeza: dict):
    array = [Variables_Globales.MAX_HP_X, Variables_Globales.MIN_HP_X, Variables_Globales.MAX_HP_Y, Variables_Globales.MIN_HP_Y, Variables_Globales.MAX_HP_Z, Variables_Globales.MIN_HP_Z]

    for i in array:
        posicion_cabeza[i] = round(sum(posicion_cabeza[i])/len(posicion_cabeza[i]), 3)
    return posicion_cabeza