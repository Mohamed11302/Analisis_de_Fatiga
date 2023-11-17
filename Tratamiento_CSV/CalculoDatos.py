import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Variables_Globales import *


############################ FATIGA VELOCIDAD ######################################
def calcular_magnitud(velocidad_x: float, velocidad_y: float, velocidad_z: float) -> float:
    magnitud = round(math.sqrt(velocidad_x**2 + velocidad_y**2 + velocidad_z**2), 2)
    return magnitud

def vectorizar(handvelocity_x: float, handvelocity_y:float, handvelocity_z:float) -> [float]:
    vector = []
    for i in range(0, len(handvelocity_x)):
        vector.append(calcular_magnitud(handvelocity_x.values[i],handvelocity_y.values[i],handvelocity_z.values[i]))
    return vector

def VelocidadMediaPorRepeticion(df:pd.core.frame.DataFrame, repeticion: int):
    hand_velocity_x = (df[df[NUMREPETICION] == repeticion][HANDVELOCITY_X]).values
    hand_velocity_y = (df[df[NUMREPETICION] == repeticion][HANDVELOCITY_Y]).values
    hand_velocity_z = (df[df[NUMREPETICION] == repeticion][HANDVELOCITY_Z]).values
    speed = []
    for i in range(0, len(hand_velocity_x)):
        speed.append(calcular_magnitud(hand_velocity_x[i], hand_velocity_y[i], hand_velocity_z[i]))
    average_speed = sum(speed)/len(speed)
    return average_speed


def Datos_VelocidadPR(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    num_repeticiones = df[NUMREPETICION].max()
    velocidad = []
    for i in range(inicio_rep, final_rep):
        velocidad.append(VelocidadMediaPorRepeticion(df, i))
    #plt.plot(velocidad)
    #plt.title("Velocidad Media Por Repeticion")
    #plt.yticks((0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1))
    #plt.show()
    return velocidad

############################ FATIGA TIEMPO ######################################
def Datos_TiempoPR(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    num_repeticiones = df[NUMREPETICION].max()
    tiempo_por_repeticion = []
    for i in range(inicio_rep, final_rep):
        time = (df[df[NUMREPETICION] == i][TIME]).values
        tiempo_por_repeticion.append(max(time)-min(time))
    return tiempo_por_repeticion
    '''
    plt.plot(tiempo_por_repeticion)
    maximo = max(tiempo_por_repeticion)
    minimo = min(tiempo_por_repeticion)
    print(maximo)
    print(minimo)
    eje_y = []
    i = minimo
    while i<maximo:
        eje_y.append(i)
        i +=0.3
    plt.yticks(eje_y)
    plt.title("Tiempo por Repeticion")
    plt.show()
    '''


############################ FATIGA STRENGTH ######################################

def Comprobar_Tipo_Agarre(df:pd.core.frame.DataFrame)->[str]:
    Tipos_Agarre = []
    if df[ISPINCHGRABBING].any():
        Tipos_Agarre.append(ISPINCHGRABBING)
    if df[ISPALMGRABBING].any():
        Tipos_Agarre.append(ISPALMGRABBING)
    if df[ISAUTOGRIPGRABBING].any():
        Tipos_Agarre.append(ISAUTOGRIPGRABBING)
    return Tipos_Agarre

def Variables_A_Considerar(tipo_agarre):
    variables_a_considerar = []
    if tipo_agarre==ISPINCHGRABBING:
        variables_a_considerar = [
            STRENGTHTHUMBINDEX,
            STRENGTHTHUMB_MIDDLE,
            STRENGTHTHUMB_RING,
            STRENGTHTHUMB_PINKY,
        ]
    elif tipo_agarre == ISPALMGRABBING:
        variables_a_considerar = [
            STRENGTHPALM_INDEX,
            STRENGTHPALM_MIDDLE,
            STRENGTHPALM_RING,
            STRENGTHPALM_PINKY
        ]
    return variables_a_considerar

def Fuerza_De_Agarre(df:pd.core.frame.DataFrame, tipo_agarre, inicio_rep:int, final_rep:int):
    #  Criterio: Se toman los valores mayores a 0 y se calcula su media
    num_repeticiones = df[NUMREPETICION].max()
    Fuerza_De_Agarre = []
    variables_a_considerar = Variables_A_Considerar(tipo_agarre)
    for i in range(inicio_rep, final_rep):
        fuerza_dedo = []
        for j in variables_a_considerar:
            fuerza_dedo.append((df[(df[NUMREPETICION] == i) & (df[j] > 0)][j]).values)
        fuerza_dedo = np.concatenate(fuerza_dedo)
        if (len(fuerza_dedo)>0):
            Fuerza_De_Agarre.append(sum(fuerza_dedo)/len(fuerza_dedo))

        fuerza_dedo = []
    return Fuerza_De_Agarre

def Datos_StrengthPR(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    #Tipos_Agarre = Comprobar_Tipo_Agarre(df)
    Tipos_Agarre = [ISPINCHGRABBING]
    Fatiga_Por_Repeticion = []
    if len(Tipos_Agarre) == 2:
        Fatiga1 = Fuerza_De_Agarre(df, Tipos_Agarre[0], inicio_rep, final_rep)
        Fatiga2 = Fuerza_De_Agarre(df, Tipos_Agarre[1], inicio_rep, final_rep)
        print(Fatiga1)
        print("---")
        print(Fatiga2)
        ##COMPROBAR ESTO
    else:
        Fatiga_Por_Repeticion.append(Fuerza_De_Agarre(df, Tipos_Agarre[0], inicio_rep, final_rep))
        Fatiga_Por_Repeticion = np.concatenate(Fatiga_Por_Repeticion)
    #plt.plot(Fatiga_Por_Repeticion)
    #plt.show()
    return Fatiga_Por_Repeticion.tolist()


############################ FATIGA WRISTTWIST ######################################

def Datos_WristTwistPR(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    WristTwist = []
    for i in range(inicio_rep, final_rep):
        twist = (df[df[NUMREPETICION] == i][WRISTTWIST]).values
        WristTwist.append(round(sum(twist)/len(twist), 3))
    return WristTwist