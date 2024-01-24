import pandas as pd
import numpy as np
import Constantes.Constantes as Const
import Utils.auxiliares as aux


############################ DIVIDIR EN REPETICIONES ######################################

def dividir_en_repeticiones(dataframe):
    unique_blocks = dataframe[Const.GRABIDENTIFIER].dropna().unique()
    num_repeticion = 0
    columna_repeticion = []
    for i in range(len(dataframe)):
        if pd.notnull(dataframe[Const.GRABIDENTIFIER].iloc[i]):
            if ((num_repeticion < len(unique_blocks)) and 
                (dataframe[Const.GRABIDENTIFIER].iloc[i] == unique_blocks[num_repeticion])):
                num_repeticion += 1
            columna_repeticion.append(num_repeticion)
        else:
            columna_repeticion.append(num_repeticion)
    columna_repeticion = comprobar_repeticiones(columna_repeticion)
    dataframe[Const.NUMREPETICION] = columna_repeticion
    dataframe = dataframe[dataframe[Const.NUMREPETICION] != 0]
    dataframe = dataframe.reset_index(drop=True)
    return dataframe

def comprobar_repeticiones(columna):
    for i in set(columna):
        if columna.count(i) == 1:
            for j in range(len(columna)):
                if columna[j] == i:
                    columna[j] += 1
    i = 0
    while i < len(columna) - 1:
        if columna[i+1] - columna[i] == 2:
            for j in range(i+1, len(columna)):
                columna[j] -= 1
        i += 1
    return columna

############################ SE ESTA USANDO MANO DERECHA ######################################
def mano_derecha(df):
    mano_derecha = True 
    indice_primera_fila = df[Const.GRABIDENTIFIER].first_valid_index()
    df_resultado = df.iloc[indice_primera_fila:]
    fila_primer_valor = df_resultado.iloc[0][Const.HANDPOSITION_X]
    idx_first_empty_row = df[df_resultado[Const.GRABIDENTIFIER].isnull()].index[0]
    if idx_first_empty_row >= 0:
        previous_row = df_resultado.iloc[idx_first_empty_row-1][Const.HANDPOSITION_X]
        if fila_primer_valor - previous_row < 0:
            mano_derecha = False
    return mano_derecha

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
def datos_tiempo_por_repeticion_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)->[float]:
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

def datos_fuerza_por_repeticion_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)->[float]:
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
def datos_curvatura_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)-> dict:
    curvatura = {
        Const.CURVATURA_TOMAR_BLOQUE_Y: [],
        Const.CURVATURA_PUNTO_MAS_ALTO_Y: [],
        Const.CURVATURA_SOLTAR_BLOQUE_Y: [],
        Const.CURVATURA_SOLTAR_BLOQUE_X: [],
    }
    for repeticion in range(inicio_rep, final_rep):
        rep_data = df[df[Const.NUMREPETICION] == repeticion]
        datos_ida = rep_data[(rep_data[Const.ISPINCHGRABBING] == True) | (rep_data[Const.ISPALMGRABBING]==True)]

        curvatura[Const.CURVATURA_TOMAR_BLOQUE_Y].append(datos_ida[Const.HANDPOSITION_Y].iloc[0])
        curvatura[Const.CURVATURA_PUNTO_MAS_ALTO_Y].append(datos_ida[Const.HANDPOSITION_Y].max())
        curvatura[Const.CURVATURA_SOLTAR_BLOQUE_Y].append(datos_ida[Const.HANDPOSITION_Y].iloc[-1])
        curvatura[Const.CURVATURA_SOLTAR_BLOQUE_X].append(datos_ida[Const.HANDPOSITION_X].iloc[-1])

    return curvatura

############################ DATOS CAIDA DEL BLOQUE ######################################

def datos_caida_del_bloque_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)->[int]:
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
def datos_movimiento_incorrecto_por_repeticion(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int)-> [bool]:
    movimiento_correcto = []
    for rep in range(inicio_rep, final_rep):
        df = df[df[Const.NUMREPETICION]== rep]
        mov_correcto = False
        if df[Const.MOVEDCORRECTLY].any():
            mov_correcto = True
        movimiento_correcto.append(mov_correcto)
    return movimiento_correcto



############################ DATOS MOVIMIENTO CORRECTO ######################################



