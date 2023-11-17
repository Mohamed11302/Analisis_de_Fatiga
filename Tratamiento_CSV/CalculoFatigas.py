from Variables_Globales import *

FATIGA_RENDIMIENTO_LEVE = 15
FATIGA_RENDIMIENTO_MODERADA = 30
FATIGA_RENDIMIENTO_AGUDA = 50

FATIGA_INDICE_LEVE = 0.1
FATIGA_INDICE_MODERADA = 0.3
FATIGA_INDICE_AGUDA = 0.5
def Fatiga_Calculo(valor_medio:float, valor_a_comparar:float, tipo:str)->float:
    fatiga = Valor_De_Fatiga(valor_medio, valor_a_comparar, tipo)
    #print(str(valor_medio) + " - " + str(round(valor_a_comparar, 2)) + ": " + str(round(fatiga,2)), end = " - ")
    indice_fatiga = 0
    if fatiga > FATIGA_RENDIMIENTO_LEVE:
        indice_fatiga = FATIGA_INDICE_LEVE
    if fatiga > FATIGA_RENDIMIENTO_MODERADA:
        indice_fatiga = FATIGA_INDICE_MODERADA
    if fatiga > FATIGA_RENDIMIENTO_AGUDA:
        indice_fatiga = FATIGA_INDICE_AGUDA
    #print(indice_fatiga)
    return indice_fatiga

def Valor_De_Fatiga(valor_medio:float, valor_a_comparar:float, tipo:str):
    fatiga = 0
    if tipo == FATIGA_VELOCIDAD or tipo == FATIGA_STRENGTH:
        fatiga = -((valor_a_comparar-valor_medio)/valor_medio)*100
    if tipo == FATIGA_TIEMPO:
        fatiga = ((valor_a_comparar-valor_medio)/valor_medio)*100
    return fatiga