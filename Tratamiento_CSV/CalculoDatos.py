import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import Variables_Globales


def obtener_datos_paciente(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int) -> dict:
    datos_paciente = {
        Variables_Globales.FATIGA_WRIST : datos_flexion_muneca_por_repeticion(df, inicio_rep, final_rep),
        Variables_Globales.FATIGA_STRENGTH : datos_fuerza_por_repeticion(df, inicio_rep, final_rep),
        Variables_Globales.FATIGA_TIEMPO : datos_tiempo_por_repeticion(df, inicio_rep, final_rep),
        Variables_Globales.FATIGA_VELOCIDAD : datos_velocidad_por_repeticion(df, inicio_rep, final_rep),
        Variables_Globales.FATIGA_HEADPOSITION : datos_posicion_cabeza_por_repeticion(df, inicio_rep, final_rep),
        Variables_Globales.FATIGA_CURVATURA_MANO : datos_curvatura(df, inicio_rep, final_rep)
    }
    return datos_paciente

def datos_iniciales_paciente(df:pd.core.frame.DataFrame, porcentaje: int)->dict:
    INICIO_REPES = 2
    datos_de_fatiga ={}
    num_repeticiones = df[Variables_Globales.NUMREPETICION].max()
    num_rep_iniciales = round(num_repeticiones * (porcentaje/100))
    _datos_paciente = obtener_datos_paciente(df, INICIO_REPES, INICIO_REPES+num_rep_iniciales)
    fatiga_headposition = media_datos(_datos_paciente[Variables_Globales.FATIGA_HEADPOSITION])
    fatiga_curvatura_mano = media_datos(_datos_paciente[Variables_Globales.FATIGA_CURVATURA_MANO])

    for columna in [Variables_Globales.FATIGA_WRIST, Variables_Globales.FATIGA_STRENGTH, Variables_Globales.FATIGA_TIEMPO, Variables_Globales.FATIGA_VELOCIDAD]:
        datos_de_fatiga[columna] = round(sum(_datos_paciente[columna])/len(_datos_paciente[columna]), 3)
    
    datos_fatiga_posicion_cabeza = {}
    for columna in [Variables_Globales.HEADPOSITION_MAX_X, Variables_Globales.HEADPOSITION_MIN_X,
                    Variables_Globales.HEADPOSITION_MAX_Y, Variables_Globales.HEADPOSITION_MIN_Y,
                    Variables_Globales.HEADPOSITION_MAX_Z, Variables_Globales.HEADPOSITION_MIN_Z]:
        datos_fatiga_posicion_cabeza[columna] = fatiga_headposition[columna]

    datos_fatiga_curvatura_mano = {}
    for columna in [Variables_Globales.CURVATURA_PUNTO_MAS_ALTO_Y_IDA, Variables_Globales.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA,
                    Variables_Globales.CURVATURA_SOLTAR_BLOQUE_X, Variables_Globales.CURVATURA_SOLTAR_BLOQUE_Y,
                    Variables_Globales.CURVATURA_TOMAR_BLOQUE_Y]:
        datos_fatiga_curvatura_mano[columna] = fatiga_curvatura_mano[columna]

    datos_de_fatiga[Variables_Globales.FATIGA_HEADPOSITION] = datos_fatiga_posicion_cabeza
    datos_de_fatiga[Variables_Globales.FATIGA_CURVATURA_MANO] = datos_fatiga_curvatura_mano
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
        Variables_Globales.HEADPOSITION_MAX_X: [],
        Variables_Globales.HEADPOSITION_MIN_X: [],
        Variables_Globales.HEADPOSITION_MAX_Y: [],
        Variables_Globales.HEADPOSITION_MIN_Y: [],
        Variables_Globales.HEADPOSITION_MAX_Z: [],
        Variables_Globales.HEADPOSITION_MIN_Z: []
    }
    for i in range(inicio_rep, final_rep):
        head_position[Variables_Globales.HEADPOSITION_MAX_X].append(df[df[Variables_Globales.NUMREPETICION]==i][Variables_Globales.HEADPOSITION_X].max())
        head_position[Variables_Globales.HEADPOSITION_MIN_X].append(df[df[Variables_Globales.NUMREPETICION]==i][Variables_Globales.HEADPOSITION_X].min())

        head_position[Variables_Globales.HEADPOSITION_MAX_Y].append(df[df[Variables_Globales.NUMREPETICION]==i][Variables_Globales.HEADPOSITION_Y].max())
        head_position[Variables_Globales.HEADPOSITION_MIN_Y].append(df[df[Variables_Globales.NUMREPETICION]==i][Variables_Globales.HEADPOSITION_Y].min())

        head_position[Variables_Globales.HEADPOSITION_MAX_Z].append(df[df[Variables_Globales.NUMREPETICION]==i][Variables_Globales.HEADPOSITION_Z].max())
        head_position[Variables_Globales.HEADPOSITION_MIN_Z].append(df[df[Variables_Globales.NUMREPETICION]==i][Variables_Globales.HEADPOSITION_Z].min())
    
    return head_position

def media_datos(diccionario: dict):
    nuevo_diccionario = {}
    for clave, lista in diccionario.items():
        nuevo_diccionario[clave] = sum(lista) / len(lista)
    return nuevo_diccionario


############################ DATOS CURVATURA ######################################
def datos_curvatura(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)-> dict:
    curvatura = {
        Variables_Globales.CURVATURA_TOMAR_BLOQUE_Y: [],
        Variables_Globales.CURVATURA_PUNTO_MAS_ALTO_Y_IDA: [],
        Variables_Globales.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA: [],
        Variables_Globales.CURVATURA_SOLTAR_BLOQUE_Y: [],
        Variables_Globales.CURVATURA_SOLTAR_BLOQUE_X: [],
    }
    for repeticion in range(inicio_rep, final_rep):
        rep_data = df[df[Variables_Globales.NUMREPETICION] == repeticion]

        datos_ida = rep_data[rep_data[Variables_Globales.ISPINCHGRABBING] == True]
        datos_vuelta = rep_data[rep_data[Variables_Globales.ISPINCHGRABBING] == False]

        curvatura[Variables_Globales.CURVATURA_TOMAR_BLOQUE_Y].append(datos_ida[Variables_Globales.HANDPOSITION_Y].iloc[0])
        curvatura[Variables_Globales.CURVATURA_PUNTO_MAS_ALTO_Y_IDA].append(datos_ida[Variables_Globales.HANDPOSITION_Y].max())
        curvatura[Variables_Globales.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA].append(datos_vuelta[Variables_Globales.HANDPOSITION_Y].max())
        curvatura[Variables_Globales.CURVATURA_SOLTAR_BLOQUE_Y].append(datos_vuelta[Variables_Globales.HANDPOSITION_Y].iloc[0])
        curvatura[Variables_Globales.CURVATURA_SOLTAR_BLOQUE_X].append(datos_vuelta[Variables_Globales.HANDPOSITION_X].iloc[0])

    return curvatura