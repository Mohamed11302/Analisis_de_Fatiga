import Variables_Globales
import pandas as pd
import CalculoDatos
import math
FATIGA_RENDIMIENTO_LEVE = 15
FATIGA_RENDIMIENTO_MODERADA = 30
FATIGA_RENDIMIENTO_AGUDA = 40
FATIGA_RENDIMIENTO_GRAVE = 60
FATIGA_INDICE_LEVE = 0.1
FATIGA_INDICE_MODERADA = 0.3
FATIGA_INDICE_AGUDA = 0.4
FATIGA_INDICE_GRAVE = 0.6
def fatiga_calculo(valor_medio:float, valor_a_comparar:float, tipo:str)->float:
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
    if tipo == Variables_Globales.FATIGA_VELOCIDAD or tipo == Variables_Globales.FATIGA_STRENGTH:
        fatiga = -((valor_a_comparar-valor_medio)/valor_medio)*100
    if tipo == Variables_Globales.FATIGA_TIEMPO:
        fatiga = ((valor_a_comparar-valor_medio)/valor_medio)*100
        
    return fatiga

def fatiga_calculo_headposition(datos_iniciales_paciente:dict, fatiga_headposition:dict, repeticion:int, df:pd.core.frame.DataFrame)-> float:
    # DISTANCIA EUCLIDIANA
    indice_fatiga = 0    
    valor_medio_x = round((fatiga_headposition[Variables_Globales.MAX_HP_X][repeticion]+fatiga_headposition[Variables_Globales.MIN_HP_X][repeticion])/2, 2)
    valor_medio_y = round((fatiga_headposition[Variables_Globales.MAX_HP_Y][repeticion]+fatiga_headposition[Variables_Globales.MIN_HP_Y][repeticion])/2, 2)
    valor_medio_z = round((fatiga_headposition[Variables_Globales.MAX_HP_Z][repeticion]+fatiga_headposition[Variables_Globales.MIN_HP_Z][repeticion])/2, 2)

    if valor_medio_x<datos_iniciales_paciente[Variables_Globales.MIN_HP_X] or valor_medio_x>datos_iniciales_paciente[Variables_Globales.MAX_HP_X] or valor_medio_y<datos_iniciales_paciente[Variables_Globales.MIN_HP_Y] or valor_medio_y>datos_iniciales_paciente[Variables_Globales.MAX_HP_Y] or valor_medio_z<datos_iniciales_paciente[Variables_Globales.MIN_HP_Z] or valor_medio_z>datos_iniciales_paciente[Variables_Globales.MAX_HP_Z]:
        distancia_head_hand = 99999
        filas_repeticion = df[df[Variables_Globales.NUMREPETICION] == repeticion]
        for _, fila in filas_repeticion.iterrows():
            distancia = distancia_euclidiana((round((datos_iniciales_paciente[Variables_Globales.MAX_HP_X]+datos_iniciales_paciente[Variables_Globales.MIN_HP_X])/2, 2),round((datos_iniciales_paciente[Variables_Globales.MAX_HP_Y]+datos_iniciales_paciente[Variables_Globales.MIN_HP_Y])/2, 2),round((datos_iniciales_paciente[Variables_Globales.MAX_HP_Z]+datos_iniciales_paciente[Variables_Globales.MIN_HP_Z])/2, 2)), (fila[Variables_Globales.HANDPOSITION_X], fila[Variables_Globales.HANDPOSITION_Y], fila[Variables_Globales.HANDPOSITION_Z]))
            if distancia_head_hand > distancia:
                distancia_head_hand = distancia
        if distancia_head_hand < 0.4:
            indice_fatiga = 0.1
        if distancia_head_hand < 0.35:
            indice_fatiga = 0.3
        if distancia_head_hand < 0.3:
            indice_fatiga = 0.5
        #print("DISTANCIA MINIMA: " + str(round(distancia_head_hand,2)) + " en repeticion: " + str(repeticion) + ". Fatiga: " + str(indice_fatiga))
    return indice_fatiga

def distancia_euclidiana(punto1, punto2):
    x1, y1, z1 = punto1
    x2, y2, z2 = punto2

    distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distancia



def reweighting(valores_fatiga: dict):
    pesos_fatiga = {
        Variables_Globales.FATIGA_HEADPOSITION : Variables_Globales.OWA_HEADPOSITION,
        Variables_Globales.FATIGA_STRENGTH : Variables_Globales.OWA_STRENGTH,
        Variables_Globales.FATIGA_VELOCIDAD : Variables_Globales.OWA_VELOCIDAD,
        Variables_Globales.FATIGA_TIEMPO : Variables_Globales.OWA_TIEMPO
    }
    nuevos_pesos = {}
    suma_nuevos_pesos = 0
    for tipo_fatiga, valor_fatiga in valores_fatiga.items():
        if valor_fatiga > FATIGA_INDICE_AGUDA:
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
            Variables_Globales.OWA_HEADPOSITION = nuevos_pesos[Variables_Globales.FATIGA_HEADPOSITION]
            Variables_Globales.OWA_STRENGTH = nuevos_pesos[Variables_Globales.FATIGA_STRENGTH] 
            Variables_Globales.OWA_TIEMPO = nuevos_pesos[Variables_Globales.FATIGA_TIEMPO]
            Variables_Globales.OWA_VELOCIDAD = nuevos_pesos[Variables_Globales.FATIGA_VELOCIDAD]


        