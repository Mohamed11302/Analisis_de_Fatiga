import pandas as pd
import math
import Constantes
import CalculoDatos
import numpy as np
import matplotlib.pyplot as plt


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
    for repeticion, valor_de_fatiga in preprocesado_fatiga.items():
        fatiga = ponderacion_owa(valor_de_fatiga)
        fatiga_por_repeticion.append(round(fatiga, 3))
    return fatiga_por_repeticion


def CalcularFatiga_Serie(fatiga:[float]):
    fatiga = quitar_porcentaje_mas_bajo(fatiga, 30)
    return fatiga.mean()



def preprocesado_indice_fatiga(df:pd.core.frame.DataFrame, porcentaje:int)->[float]:
    _datos_iniciales_paciente = CalculoDatos.datos_iniciales_paciente(df, porcentaje)
    datos_paciente = CalculoDatos.obtener_datos_paciente(df, 2, _datos_iniciales_paciente['NUM_REP'])
    preprocesado_fatiga = {}
    for repeticion in range(0, len(datos_paciente[Constantes.FATIGA_TIEMPO])):
        preprocesado_fatiga[repeticion] = (extraer_fatigas(_datos_iniciales_paciente, datos_paciente, df, repeticion))
        #fatiga = ponderacion_owa(fatigas)
        #indice_fatiga.append(round(fatiga, 3))
    return preprocesado_fatiga





def extraer_fatigas(_datos_iniciales_paciente: dict, datos_paciente: dict, df: pd.core.frame.DataFrame, repeticion:int)-> dict:
    fatigas = {
            Constantes.FATIGA_TIEMPO : fatiga_calculo_general(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Constantes.FATIGA_TIEMPO], datos_paciente[Constantes.FATIGA_TIEMPO][repeticion], Constantes.FATIGA_TIEMPO),
            Constantes.FATIGA_STRENGTH : fatiga_calculo_general(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Constantes.FATIGA_STRENGTH], datos_paciente[Constantes.FATIGA_STRENGTH][repeticion], Constantes.FATIGA_STRENGTH),
            Constantes.FATIGA_VELOCIDAD : fatiga_calculo_general(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Constantes.FATIGA_VELOCIDAD], datos_paciente[Constantes.FATIGA_VELOCIDAD][repeticion], Constantes.FATIGA_VELOCIDAD),
            Constantes.FATIGA_HEADPOSITION : fatiga_calculo_headposition(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Constantes.FATIGA_HEADPOSITION], datos_paciente[Constantes.FATIGA_HEADPOSITION], repeticion, df),
            Constantes.FATIGA_CURVATURA_MANO : fatiga_calculo_curvatura_mano(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Constantes.FATIGA_CURVATURA_MANO], datos_paciente[Constantes.FATIGA_CURVATURA_MANO], repeticion)
        }
    return fatigas

def ponderacion_owa(fatigas) -> float:
    reweighting(fatigas)
    fatiga = (fatigas[Constantes.FATIGA_TIEMPO] * Constantes.OWA_TIEMPO +
              fatigas[Constantes.FATIGA_STRENGTH] * Constantes.OWA_STRENGTH +
              fatigas[Constantes.FATIGA_VELOCIDAD] * Constantes.OWA_VELOCIDAD +
              fatigas[Constantes.FATIGA_HEADPOSITION] * Constantes.OWA_HEADPOSITION +
              fatigas[Constantes.FATIGA_CURVATURA_MANO] * Constantes.OWA_CURVATURA_MANO
            )
    return fatiga

def existe_fatiga_grave(valores_fatiga: dict)-> bool:
    _existe_fatiga_grave = False
    for tipo_fatiga, valor_fatiga in valores_fatiga.items():
        if valor_fatiga > FATIGA_INDICE_GRAVE:
            _existe_fatiga_grave = True
    return _existe_fatiga_grave

def reweighting(valores_fatiga: dict):
    """ Reajuste de los pesos para cada métrica de fatiga si se detecta que alguna llega al valor Grave """
    pesos_fatiga = {
        Constantes.FATIGA_HEADPOSITION : Constantes.OWA_HEADPOSITION,
        Constantes.FATIGA_STRENGTH : Constantes.OWA_STRENGTH,
        Constantes.FATIGA_VELOCIDAD : Constantes.OWA_VELOCIDAD,
        Constantes.FATIGA_TIEMPO : Constantes.OWA_TIEMPO,
        Constantes.FATIGA_CURVATURA_MANO : Constantes.OWA_CURVATURA_MANO
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
    Constantes.OWA_HEADPOSITION = nuevos_pesos[Constantes.FATIGA_HEADPOSITION]
    Constantes.OWA_STRENGTH = nuevos_pesos[Constantes.FATIGA_STRENGTH]
    Constantes.OWA_TIEMPO = nuevos_pesos[Constantes.FATIGA_TIEMPO]
    Constantes.OWA_VELOCIDAD = nuevos_pesos[Constantes.FATIGA_VELOCIDAD]
    Constantes.OWA_CURVATURA_MANO = nuevos_pesos[Constantes.FATIGA_CURVATURA_MANO]



def representar_fatiga(fatiga:[float], porcentaje:int):
    print(fatiga)
    repeticiones = list(range(len(fatiga)))
    plt.bar(repeticiones, fatiga)
    plt.title('FATIGA CON '+str(porcentaje)+str('%'))
    plt.show()


def quitar_porcentaje_mas_bajo(fatiga:[], porcentaje:int):
    elementos_a_conservar = quitar_porcentaje(fatiga, porcentaje, False)
    return elementos_a_conservar

def quitar_porcentaje_mas_alto(fatiga:[], porcentaje:int):
    elementos_a_conservar = quitar_porcentaje(fatiga, porcentaje, True)
    return elementos_a_conservar

def quitar_porcentaje(fatiga:[], porcentaje:int, mas_alto):
    num_elementos_a_conservar = int((1 - porcentaje/100) * len(fatiga))
    array_ordenado = np.sort(fatiga)
    if mas_alto:
        elementos_a_conservar = array_ordenado[:num_elementos_a_conservar]
    else:
        elementos_a_conservar = array_ordenado[len(fatiga)-num_elementos_a_conservar:]
    return elementos_a_conservar

def fatiga_calculo_general(valor_medio:float, valor_a_comparar:float, tipo:str)->float:
    fatiga = valor_de_fatiga(valor_medio, valor_a_comparar, tipo)
    indice_fatiga = 0
    if fatiga > FATIGA_RENDIMIENTO_LEVE:
        indice_fatiga = FATIGA_INDICE_LEVE
    if fatiga > FATIGA_RENDIMIENTO_MODERADA:
        indice_fatiga = FATIGA_INDICE_MODERADA
    if fatiga > FATIGA_RENDIMIENTO_AGUDA:
        indice_fatiga = FATIGA_INDICE_AGUDA
    if fatiga > FATIGA_RENDIMIENTO_GRAVE:
        indice_fatiga = FATIGA_INDICE_GRAVE
    #print(indice_fatiga)
    return indice_fatiga

def valor_de_fatiga(valor_medio:float, valor_a_comparar:float, tipo:str):
    fatiga = 0
    if tipo in (Constantes.FATIGA_VELOCIDAD, Constantes.FATIGA_STRENGTH):
        fatiga = -((valor_a_comparar-valor_medio)/valor_medio)*100
    if tipo == Constantes.FATIGA_TIEMPO:
        fatiga = ((valor_a_comparar-valor_medio)/valor_medio)*100
    return fatiga

def fatiga_calculo_headposition(datos_iniciales_paciente:dict, fatiga_headposition:dict, repeticion:int, df:pd.core.frame.DataFrame)-> float:
    # DISTANCIA EUCLIDIANA
    indice_fatiga = 0    
    valor_medio_x = round((fatiga_headposition[Constantes.HEADPOSITION_MAX_X][repeticion]+
                           fatiga_headposition[Constantes.HEADPOSITION_MIN_X][repeticion])/2, 2)
    valor_medio_y = round((fatiga_headposition[Constantes.HEADPOSITION_MAX_Y][repeticion]+
                           fatiga_headposition[Constantes.HEADPOSITION_MIN_Y][repeticion])/2, 2)
    valor_medio_z = round((fatiga_headposition[Constantes.HEADPOSITION_MAX_Z][repeticion]+
                           fatiga_headposition[Constantes.HEADPOSITION_MIN_Z][repeticion])/2, 2)

    if (valor_medio_x<datos_iniciales_paciente[Constantes.HEADPOSITION_MIN_X] or 
        valor_medio_x>datos_iniciales_paciente[Constantes.HEADPOSITION_MAX_X] or 
        valor_medio_y<datos_iniciales_paciente[Constantes.HEADPOSITION_MIN_Y] or 
        valor_medio_y>datos_iniciales_paciente[Constantes.HEADPOSITION_MAX_Y] or 
        valor_medio_z<datos_iniciales_paciente[Constantes.HEADPOSITION_MIN_Z] or 
        valor_medio_z>datos_iniciales_paciente[Constantes.HEADPOSITION_MAX_Z]):

        distancia_head_hand = 99999
        filas_repeticion = df[df[Constantes.NUMREPETICION] == repeticion]
        for _, fila in filas_repeticion.iterrows():
            distancia = distancia_euclidiana((round((datos_iniciales_paciente[Constantes.HEADPOSITION_MAX_X]+
                                                     datos_iniciales_paciente[Constantes.HEADPOSITION_MIN_X])/2, 2),round((datos_iniciales_paciente[Constantes.HEADPOSITION_MAX_Y]+datos_iniciales_paciente[Constantes.HEADPOSITION_MIN_Y])/2, 2),round((datos_iniciales_paciente[Constantes.HEADPOSITION_MAX_Z]+datos_iniciales_paciente[Constantes.HEADPOSITION_MIN_Z])/2, 2)), (fila[Constantes.HANDPOSITION_X], fila[Constantes.HANDPOSITION_Y], fila[Constantes.HANDPOSITION_Z]))
            if distancia_head_hand > distancia:
                distancia_head_hand = distancia
        if distancia_head_hand < 0.4:
            indice_fatiga = 0.1
        if distancia_head_hand < 0.35:
            indice_fatiga = 0.3
        if distancia_head_hand < 0.3:
            indice_fatiga = 0.5
    return indice_fatiga

def distancia_euclidiana(punto1, punto2):
    x1, y1, z1 = punto1
    x2, y2, z2 = punto2

    distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distancia


def fatiga_calculo_curvatura_mano(datos_iniciales_paciente:dict, fatiga_curvatura_mano:dict, repeticion:int)->float:
    fatiga_soltar_bloque_x = 0
    fatiga_punto_mas_alto_ida = 0
    fatiga_punto_mas_alto_vuelta = 0
    fatiga = 0
    
    rendimiento_punto_mas_alto_y_ida = round(fatiga_curvatura_mano[Constantes.CURVATURA_PUNTO_MAS_ALTO_Y_IDA][repeticion]/
                                             datos_iniciales_paciente[Constantes.CURVATURA_PUNTO_MAS_ALTO_Y_IDA], 3)*100
    rendimiento_punto_mas_alto_y_vuelta = round(fatiga_curvatura_mano[Constantes.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA][repeticion]/
                                                datos_iniciales_paciente[Constantes.CURVATURA_PUNTO_MAS_ALTO_Y_VUELTA], 3)*100
    rendimiento_soltar_bloque_x = round(abs(fatiga_curvatura_mano[Constantes.CURVATURA_SOLTAR_BLOQUE_X][repeticion])/
                                        abs(datos_iniciales_paciente[Constantes.CURVATURA_SOLTAR_BLOQUE_X]), 3)*100
    
    if fatiga_curvatura_mano[Constantes.CURVATURA_SOLTAR_BLOQUE_X][repeticion] > 0: #HA TIRADO EL BLOQUE
        fatiga_soltar_bloque_x = 1
    elif rendimiento_soltar_bloque_x<60:
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

def mediahistorica(df: pd.core.frame.DataFrame)-> dict:
    porcentaje_a_eliminar = 20
    datos = CalculoDatos.obtener_datos_paciente(df, 2, df[Constantes.NUMREPETICION].max())
    columnas_a_procesar = [
        Constantes.FATIGA_VELOCIDAD,
        Constantes.FATIGA_TIEMPO,
        Constantes.FATIGA_WRIST,
        Constantes.FATIGA_STRENGTH,
        Constantes.FATIGA_HEADPOSITION,
        Constantes.FATIGA_CURVATURA_MANO
    ]

    for columna in columnas_a_procesar:
        if isinstance(datos[columna], list):
            datos[columna] = quitar_porcentaje_mas_alto(datos[columna], porcentaje_a_eliminar)
            datos[columna] = quitar_porcentaje_mas_bajo(datos[columna], porcentaje_a_eliminar)
            datos[columna] = sum(datos[columna]) / len(datos[columna])

        if isinstance(datos[columna], pd.DataFrame):
            for subcolumna in datos[columna].columns:
                datos[columna][subcolumna] = quitar_porcentaje_mas_alto(datos[columna][subcolumna], porcentaje_a_eliminar)
                datos[columna][subcolumna] = quitar_porcentaje_mas_bajo(datos[columna][subcolumna], porcentaje_a_eliminar)

    for columna in [Constantes.FATIGA_HEADPOSITION, Constantes.FATIGA_CURVATURA_MANO]:
        datos[columna] = CalculoDatos.media_datos(datos[columna])
    return datos

        