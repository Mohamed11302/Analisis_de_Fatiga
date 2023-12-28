import pandas as pd
import math
import Constantes.Constantes as Const
import ExtraerDatos
import numpy as np
import matplotlib.pyplot as plt
import auxiliares as aux

FATIGA_RENDIMIENTO_LEVE = 15
FATIGA_RENDIMIENTO_MODERADA = 30
FATIGA_RENDIMIENTO_AGUDA = 40
FATIGA_RENDIMIENTO_GRAVE = 60
FATIGA_INDICE_LEVE = 0.1
FATIGA_INDICE_MODERADA = 0.3
FATIGA_INDICE_AGUDA = 0.4
FATIGA_INDICE_GRAVE = 0.6




def fatiga_calculo_general(valor_medio:float, valor_a_comparar:float, tipo:str)->float:
    fatiga = aux.valor_de_fatiga(valor_medio, valor_a_comparar, tipo)
    indice_fatiga = 0
    if fatiga > FATIGA_RENDIMIENTO_LEVE:
        indice_fatiga = FATIGA_INDICE_LEVE
    if fatiga > FATIGA_RENDIMIENTO_MODERADA:
        indice_fatiga = FATIGA_INDICE_MODERADA
    if fatiga > FATIGA_RENDIMIENTO_AGUDA:
        indice_fatiga = FATIGA_INDICE_AGUDA
    if fatiga > FATIGA_RENDIMIENTO_GRAVE:
        indice_fatiga = FATIGA_INDICE_GRAVE
    return indice_fatiga

def fatiga_calculo_headposition(fatiga_headposition:dict,datos_iniciales_paciente:dict, rep_df)-> float:
    repeticion = rep_df['repeticion']
    df = rep_df['df']
    # DISTANCIA EUCLIDIANA
    indice_fatiga = 0    
    valor_medio_x = round((fatiga_headposition[Const.HEADPOSITION_MAX_X][repeticion]+
                           fatiga_headposition[Const.HEADPOSITION_MIN_X][repeticion])/2, 2)
    valor_medio_y = round((fatiga_headposition[Const.HEADPOSITION_MAX_Y][repeticion]+
                           fatiga_headposition[Const.HEADPOSITION_MIN_Y][repeticion])/2, 2)
    valor_medio_z = round((fatiga_headposition[Const.HEADPOSITION_MAX_Z][repeticion]+
                           fatiga_headposition[Const.HEADPOSITION_MIN_Z][repeticion])/2, 2)

    if (valor_medio_x<datos_iniciales_paciente[Const.HEADPOSITION_MIN_X] or 
        valor_medio_x>datos_iniciales_paciente[Const.HEADPOSITION_MAX_X] or 
        valor_medio_y<datos_iniciales_paciente[Const.HEADPOSITION_MIN_Y] or 
        valor_medio_y>datos_iniciales_paciente[Const.HEADPOSITION_MAX_Y] or 
        valor_medio_z<datos_iniciales_paciente[Const.HEADPOSITION_MIN_Z] or 
        valor_medio_z>datos_iniciales_paciente[Const.HEADPOSITION_MAX_Z]):

        distancia_head_hand = 99999
        filas_repeticion = df[df[Const.NUMREPETICION] == repeticion]
        for _, fila in filas_repeticion.iterrows():
            distancia = aux.distancia_euclidiana((round((datos_iniciales_paciente[Const.HEADPOSITION_MAX_X]+
                                                     datos_iniciales_paciente[Const.HEADPOSITION_MIN_X])/2, 2),round((datos_iniciales_paciente[Const.HEADPOSITION_MAX_Y]+datos_iniciales_paciente[Const.HEADPOSITION_MIN_Y])/2, 2),round((datos_iniciales_paciente[Const.HEADPOSITION_MAX_Z]+datos_iniciales_paciente[Const.HEADPOSITION_MIN_Z])/2, 2)), (fila[Const.HANDPOSITION_X], fila[Const.HANDPOSITION_Y], fila[Const.HANDPOSITION_Z]))
            if distancia_head_hand > distancia:
                distancia_head_hand = distancia

        if distancia_head_hand < 0.4:
            indice_fatiga = 0.1
        if distancia_head_hand < 0.35:
            indice_fatiga = 0.3
        if distancia_head_hand < 0.3:
            indice_fatiga = 0.5
    return indice_fatiga

def fatiga_calculo_curvatura_mano(datos_iniciales_paciente:dict, fatiga_curvatura_mano:dict, repeticion:int)->float:
    fatiga_soltar_bloque_x = 0
    fatiga_punto_mas_alto_ida = 0
    fatiga_punto_mas_alto_vuelta = 0
    fatiga = 0
    rendimiento_punto_mas_alto_y_ida = round(fatiga_curvatura_mano[Const.CURVATURA_PUNTO_MAS_ALTO_Y_IDA]/
                                             datos_iniciales_paciente[Const.CURVATURA_PUNTO_MAS_ALTO_Y_IDA][repeticion], 3)*100
    rendimiento_punto_mas_alto_y_vuelta = round(fatiga_curvatura_mano[Const.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA]/
                                                datos_iniciales_paciente[Const.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA][repeticion], 3)*100
    rendimiento_soltar_bloque_x = round(abs(fatiga_curvatura_mano[Const.CURVATURA_SOLTAR_BLOQUE_X])/
                                        abs(datos_iniciales_paciente[Const.CURVATURA_SOLTAR_BLOQUE_X][repeticion]), 3)*100
    
    #if fatiga_curvatura_mano[Const.CURVATURA_SOLTAR_BLOQUE_X][repeticion] > 0: #HA TIRADO EL BLOQUE
    #    fatiga_soltar_bloque_x = 1
    if rendimiento_soltar_bloque_x<60:
        fatiga_soltar_bloque_x = 0.5
    elif rendimiento_soltar_bloque_x<80:
        fatiga_soltar_bloque_x = 0.3
    elif rendimiento_soltar_bloque_x<90:
        fatiga_soltar_bloque_x = 0.1

    if rendimiento_punto_mas_alto_y_ida<98:
        fatiga_punto_mas_alto_ida = 0.1
    if rendimiento_punto_mas_alto_y_ida<96:
        fatiga_punto_mas_alto_ida = 0.3
    if rendimiento_punto_mas_alto_y_ida<94:
        fatiga_punto_mas_alto_ida = 0.6
    if rendimiento_punto_mas_alto_y_ida<92:
        fatiga_punto_mas_alto_ida = 0.8

    if rendimiento_punto_mas_alto_y_vuelta<98:
        fatiga_punto_mas_alto_vuelta = 0.1
    if rendimiento_punto_mas_alto_y_vuelta<96:
        fatiga_punto_mas_alto_vuelta = 0.3
    if rendimiento_punto_mas_alto_y_vuelta<94:
        fatiga_punto_mas_alto_vuelta = 0.6
    if rendimiento_punto_mas_alto_y_vuelta<92:
        fatiga_punto_mas_alto_vuelta = 0.8

    valores_no_cero = [valor for valor in [fatiga_punto_mas_alto_ida, fatiga_punto_mas_alto_vuelta, fatiga_soltar_bloque_x] if valor != 0]
    if valores_no_cero:
        fatiga = sum(valores_no_cero) / len(valores_no_cero)

    return fatiga


def quitar_porcentaje_mas_bajo(fatiga:[], porcentaje:int):
    elementos_a_conservar = aux.quitar_porcentaje(fatiga, porcentaje, False)
    return elementos_a_conservar

def quitar_porcentaje_mas_alto(fatiga:[], porcentaje:int):
    elementos_a_conservar = aux.quitar_porcentaje(fatiga, porcentaje, True)
    return elementos_a_conservar

