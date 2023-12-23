import pandas as pd
import math
import Constantes as Const
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



def CalcularFatiga_PorRepeticion(preprocesado_fatiga: dict)-> [float]:
    fatiga_por_repeticion = []
    for _, valor_de_fatiga in preprocesado_fatiga.items():
        fatiga = ponderacion_owa(valor_de_fatiga["FATIGA"])
        fatiga = PenalizacionErrores(fatiga, valor_de_fatiga[Const.FATIGA_NUM_CAIDAS_BLOQUE], valor_de_fatiga[Const.FATIGA_MOVIMIENTO_INCORRECTO])
        fatiga_por_repeticion.append(round(fatiga, 3))
    return fatiga_por_repeticion

def PenalizacionErrores(fatiga, num_caidas_bloque, movimiento_incorrecto):
    fatiga = fatiga + fatiga*(num_caidas_bloque*Const.MULTIPLICACION_CAIDA_DEL_BLOQUE)
    if movimiento_incorrecto == True:
        fatiga = fatiga + fatiga*Const.MULTIPLICACION_CAIDA_DEL_BLOQUE
    return fatiga


def CalcularFatiga_Serie(fatiga:[float]):
    fatiga = quitar_porcentaje_mas_bajo(fatiga, 30)
    return fatiga.mean()


def preprocesado_indice_fatiga(df:pd.core.frame.DataFrame, porcentaje:int, user:str)->[float]:
    _datos_iniciales_paciente = ExtraerDatos.datos_iniciales_paciente(df,porcentaje, user)
    datos_paciente = ExtraerDatos.obtener_datos_paciente(df, 1, df[Const.NUMREPETICION].max())
    preprocesado_fatiga = {}
    for repeticion in range(0, len(datos_paciente[Const.FATIGA_TIEMPO])):
        preprocesado_fatiga[repeticion+1] = (extraer_fatigas(_datos_iniciales_paciente, datos_paciente, df, repeticion))
    return preprocesado_fatiga


def extraer_fatigas(_datos_iniciales_paciente: dict, datos_paciente: dict, df: pd.core.frame.DataFrame, repeticion:int)-> dict:
    fatigas = {
            Const.FATIGA_TIEMPO : fatiga_calculo_general(_datos_iniciales_paciente[Const.FATIGA_TIEMPO], datos_paciente[Const.FATIGA_TIEMPO][repeticion], Const.FATIGA_TIEMPO),
            Const.FATIGA_STRENGTH : fatiga_calculo_general(_datos_iniciales_paciente[Const.FATIGA_STRENGTH], datos_paciente[Const.FATIGA_STRENGTH][repeticion], Const.FATIGA_STRENGTH),
            Const.FATIGA_VELOCIDAD : fatiga_calculo_general(_datos_iniciales_paciente[Const.FATIGA_VELOCIDAD], datos_paciente[Const.FATIGA_VELOCIDAD][repeticion], Const.FATIGA_VELOCIDAD),
            Const.FATIGA_HEADPOSITION : fatiga_calculo_headposition(_datos_iniciales_paciente[Const.FATIGA_HEADPOSITION], datos_paciente[Const.FATIGA_HEADPOSITION], repeticion, df),
            Const.FATIGA_CURVATURA_MANO : fatiga_calculo_curvatura_mano(_datos_iniciales_paciente[Const.FATIGA_CURVATURA_MANO], datos_paciente[Const.FATIGA_CURVATURA_MANO], repeticion)
        }
    datos_repeticion = {}
    datos_repeticion[Const.FATIGA_MOVIMIENTO_INCORRECTO] = datos_paciente[Const.FATIGA_MOVIMIENTO_INCORRECTO][repeticion]
    datos_repeticion[Const.FATIGA_NUM_CAIDAS_BLOQUE] = datos_paciente[Const.FATIGA_NUM_CAIDAS_BLOQUE][repeticion]
    datos_repeticion["FATIGA"] = fatigas
    return datos_repeticion

def ponderacion_owa(fatigas) -> float:
    reweighting(fatigas)
    fatiga = (fatigas[Const.FATIGA_TIEMPO] * Const.OWA_TIEMPO +
              fatigas[Const.FATIGA_STRENGTH] * Const.OWA_STRENGTH +
              fatigas[Const.FATIGA_VELOCIDAD] * Const.OWA_VELOCIDAD +
              fatigas[Const.FATIGA_HEADPOSITION] * Const.OWA_HEADPOSITION +
              fatigas[Const.FATIGA_CURVATURA_MANO] * Const.OWA_CURVATURA_MANO
            )
    return fatiga

def reweighting(valores_fatiga: dict):
    """ Reajuste de los pesos para cada métrica de fatiga si se detecta que alguna llega al valor Grave """
    pesos_fatiga = {
        Const.FATIGA_HEADPOSITION : Const.OWA_HEADPOSITION,
        Const.FATIGA_STRENGTH : Const.OWA_STRENGTH,
        Const.FATIGA_VELOCIDAD : Const.OWA_VELOCIDAD,
        Const.FATIGA_TIEMPO : Const.OWA_TIEMPO,
        Const.FATIGA_CURVATURA_MANO : Const.OWA_CURVATURA_MANO
    }
    nuevos_pesos = {}
    suma_nuevos_pesos = 0
    for tipo_fatiga, valor_fatiga in valores_fatiga.items():
        if valor_fatiga > FATIGA_INDICE_GRAVE:
            for tipo,peso in pesos_fatiga.items():
                A = 1 - peso
                B = A - peso
                if B <= 0:
                    nuevos_pesos[tipo] = valor_fatiga
                    suma_nuevos_pesos += valor_fatiga
                else:
                    nuevos_pesos[tipo] = valor_fatiga + B
                    suma_nuevos_pesos += valor_fatiga + B
            for tipo, valor in nuevos_pesos.items():
                nuevos_pesos[tipo] = round(valor/suma_nuevos_pesos, 2)
            ajustar_nuevos_pesos(nuevos_pesos)
    
def ajustar_nuevos_pesos(nuevos_pesos: dict):
    Const.OWA_HEADPOSITION = nuevos_pesos[Const.FATIGA_HEADPOSITION]
    Const.OWA_STRENGTH = nuevos_pesos[Const.FATIGA_STRENGTH]
    Const.OWA_TIEMPO = nuevos_pesos[Const.FATIGA_TIEMPO]
    Const.OWA_VELOCIDAD = nuevos_pesos[Const.FATIGA_VELOCIDAD]
    Const.OWA_CURVATURA_MANO = nuevos_pesos[Const.FATIGA_CURVATURA_MANO]

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

def fatiga_calculo_headposition(datos_iniciales_paciente:dict, fatiga_headposition:dict, repeticion:int, df:pd.core.frame.DataFrame)-> float:
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
    
    rendimiento_punto_mas_alto_y_ida = round(fatiga_curvatura_mano[Const.CURVATURA_PUNTO_MAS_ALTO_Y_IDA][repeticion]/
                                             datos_iniciales_paciente[Const.CURVATURA_PUNTO_MAS_ALTO_Y_IDA], 3)*100
    rendimiento_punto_mas_alto_y_vuelta = round(fatiga_curvatura_mano[Const.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA][repeticion]/
                                                datos_iniciales_paciente[Const.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA], 3)*100
    rendimiento_soltar_bloque_x = round(abs(fatiga_curvatura_mano[Const.CURVATURA_SOLTAR_BLOQUE_X][repeticion])/
                                        abs(datos_iniciales_paciente[Const.CURVATURA_SOLTAR_BLOQUE_X]), 3)*100
    
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

def representar_fatiga(fatiga:[float], porcentaje:int):
    print(fatiga)
    repeticiones = list(range(len(fatiga)))
    plt.bar(repeticiones, fatiga)
    plt.title('FATIGA CON '+str(porcentaje)+str('%'))
    plt.show()


def quitar_porcentaje_mas_bajo(fatiga:[], porcentaje:int):
    elementos_a_conservar = aux.quitar_porcentaje(fatiga, porcentaje, False)
    return elementos_a_conservar

def quitar_porcentaje_mas_alto(fatiga:[], porcentaje:int):
    elementos_a_conservar = aux.quitar_porcentaje(fatiga, porcentaje, True)
    return elementos_a_conservar

