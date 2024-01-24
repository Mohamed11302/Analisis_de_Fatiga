import Constantes.Constantes as Const
import Utils.auxiliares as aux
import numpy as np
import skfuzzy as fuzz

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
    indice_fatiga = fuzzy_general(fatiga)
    return indice_fatiga

def fuzzy_general(valor):
    x = np.arange(0, 101, 1)

    mf1 = fuzz.trapmf(x, [0, 0, 15, 30])
    mf2 = fuzz.trimf(x, [15, 30, 40])
    mf3 = fuzz.trimf(x, [30, 40, 60])
    mf4 = fuzz.trapmf(x, [40, 60, 100, 100])

    pertenencia_mf1 = fuzz.interp_membership(x, mf1, valor)
    pertenencia_mf2 = fuzz.interp_membership(x, mf2, valor)
    pertenencia_mf3 = fuzz.interp_membership(x, mf3, valor)
    pertenencia_mf4 = fuzz.interp_membership(x, mf4, valor)

    valor_borroso_mf1 = pertenencia_mf1 * 0.1
    valor_borroso_mf2 = pertenencia_mf2 * 0.3
    valor_borroso_mf3 = pertenencia_mf3 * 0.4
    valor_borroso_mf4 = pertenencia_mf4 * 0.6

    valor_borroso_total = valor_borroso_mf1 + valor_borroso_mf2 + valor_borroso_mf3 + valor_borroso_mf4

    return valor_borroso_total



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
        indice_fatiga = fuzzy_headposition(distancia_head_hand)
    return indice_fatiga

def fuzzy_headposition(valor):
    x = np.arange(0, 1.01, 0.01)

    mf1 = fuzz.trapmf(x, [0, 0, 0.3, 0.35])
    mf2 = fuzz.trimf(x, [0.3, 0.35, 0.4])
    mf3 = fuzz.trapmf(x, [0.35, 0.4, 1, 1])

    # Calcular grados de pertenencia a cada conjunto difuso
    pertenencia_mf1 = fuzz.interp_membership(x, mf1, valor)
    pertenencia_mf2 = fuzz.interp_membership(x, mf2, valor)
    pertenencia_mf3 = fuzz.interp_membership(x, mf3, valor)

    valor_borroso_mf1 = pertenencia_mf1 * 0.5
    valor_borroso_mf2 = pertenencia_mf2 * 0.3
    valor_borroso_mf3 = pertenencia_mf3 * 0.1


    valor_borroso_total = valor_borroso_mf1 + valor_borroso_mf2 + valor_borroso_mf3

    return valor_borroso_total



def fatiga_calculo_curvatura_mano(datos_iniciales_paciente:dict, fatiga_curvatura_mano:dict, repeticion:int)->float:
    fatiga_soltar_bloque_x = 0
    fatiga_punto_mas_alto_ida = 0
    fatiga_punto_mas_alto_vuelta = 0
    fatiga = 0
    rendimiento_punto_mas_alto_y = round(fatiga_curvatura_mano[Const.CURVATURA_PUNTO_MAS_ALTO_Y]/
                                             datos_iniciales_paciente[Const.CURVATURA_PUNTO_MAS_ALTO_Y][repeticion], 3)*100    
    rendimiento_soltar_bloque_x = round(abs(fatiga_curvatura_mano[Const.CURVATURA_SOLTAR_BLOQUE_X])/
                                        abs(datos_iniciales_paciente[Const.CURVATURA_SOLTAR_BLOQUE_X][repeticion]), 3)*100

    fatiga_soltar_bloque_x = fuzzy_curvatura_x(rendimiento_soltar_bloque_x)
    fatiga_punto_mas_alto_ida = fuzzy_curvatura_y(rendimiento_punto_mas_alto_y)

    valores_no_cero = [valor for valor in [fatiga_punto_mas_alto_ida, fatiga_punto_mas_alto_vuelta, fatiga_soltar_bloque_x] if valor != 0]
    if valores_no_cero:
        fatiga = sum(valores_no_cero) / len(valores_no_cero)

    return fatiga


def fuzzy_curvatura_x(valor):
    x = np.arange(0, 101, 1)

    mf1 = fuzz.trapmf(x, [0, 0, 60, 80])
    mf2 = fuzz.trimf(x, [60, 80, 90])
    mf3 = fuzz.trapmf(x, [80, 90, 100, 100])

    pertenencia_mf1 = fuzz.interp_membership(x, mf1, valor)
    pertenencia_mf2 = fuzz.interp_membership(x, mf2, valor)
    pertenencia_mf3 = fuzz.interp_membership(x, mf3, valor)

    valor_borroso_mf1 = pertenencia_mf1 * 0.5
    valor_borroso_mf2 = pertenencia_mf2 * 0.3
    valor_borroso_mf3 = pertenencia_mf3 * 0.1

    valor_borroso_total = valor_borroso_mf1 + valor_borroso_mf2 + valor_borroso_mf3
    return valor_borroso_total

def fuzzy_curvatura_y(valor):
    x = np.arange(0, 101, 1)

    mf1 = fuzz.trapmf(x, [0, 0, 92, 94])
    mf2 = fuzz.trimf(x, [92, 94, 96])
    mf3 = fuzz.trimf(x, [94, 96, 98])
    mf4 = fuzz.trapmf(x, [96, 98, 100, 100])

    pertenencia_mf1 = fuzz.interp_membership(x, mf1, valor)
    pertenencia_mf2 = fuzz.interp_membership(x, mf2, valor)
    pertenencia_mf3 = fuzz.interp_membership(x, mf3, valor)
    pertenencia_mf4 = fuzz.interp_membership(x, mf4, valor)

    valor_borroso_mf1 = pertenencia_mf1 * 1.0
    valor_borroso_mf2 = pertenencia_mf2 * 0.6
    valor_borroso_mf3 = pertenencia_mf3 * 0.3
    valor_borroso_mf4 = pertenencia_mf4 * 0.1

    valor_borroso_total = valor_borroso_mf1 + valor_borroso_mf2 + valor_borroso_mf3 + valor_borroso_mf4

    return valor_borroso_total


def quitar_porcentaje_mas_bajo(fatiga:[], porcentaje:int):
    elementos_a_conservar = aux.quitar_porcentaje(fatiga, porcentaje, False)
    return elementos_a_conservar

def quitar_porcentaje_mas_alto(fatiga:[], porcentaje:int):
    elementos_a_conservar = aux.quitar_porcentaje(fatiga, porcentaje, True)
    return elementos_a_conservar

