import Constantes.Constantes as Const
import Procesadores.ExtraerFatigas as ExtraerFatigas

FATIGA_INDICE_GRAVE = 0.7
class Procesador_Fatigas:
    def __init__(self):
        pass
    def fatiga_por_repeticion(self, valor_medio, valor_a_comparar, metrica:str, atributo_opcional=0):
        fatiga = -1
        if metrica == Const.FATIGA_VELOCIDAD:
            fatiga = ExtraerFatigas.fatiga_calculo_general(valor_medio, valor_a_comparar, metrica)
        if metrica == Const.FATIGA_TIEMPO:
            fatiga = ExtraerFatigas.fatiga_calculo_general(valor_medio, valor_a_comparar, metrica)
        if metrica == Const.FATIGA_STRENGTH:
            fatiga = ExtraerFatigas.fatiga_calculo_general(valor_medio, valor_a_comparar, metrica)
        if metrica == Const.FATIGA_CURVATURA_MANO:
            fatiga = ExtraerFatigas.fatiga_calculo_curvatura_mano(valor_medio, valor_a_comparar, atributo_opcional)
        if metrica == Const.FATIGA_HEADPOSITION:
            fatiga = ExtraerFatigas.fatiga_calculo_headposition(valor_medio, valor_a_comparar, atributo_opcional)
        if metrica == Const.FATIGA_WRIST:
            pass
        return fatiga
    def ponderacion_owa(self, fatigas, metricas) -> float:
        nuevas_metricas = self.reweighting(fatigas, metricas)
        #nuevas_metricas = metricas
        valor_fatiga = 0
        for clave, valor in nuevas_metricas.items():
            valor_fatiga += fatigas[clave] * valor
        return valor_fatiga, nuevas_metricas
    def reweighting(self, valores_fatiga: dict, metricas:dict):
        """ Reajuste de los pesos para cada métrica de fatiga si se detecta que alguna llega al valor Grave """
        nuevos_pesos = {}
        suma_nuevos_pesos = 0
        for tipo_fatiga, valor_fatiga in valores_fatiga.items():
            if valor_fatiga > FATIGA_INDICE_GRAVE:
                for tipo,peso in metricas.items():
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
        if len(nuevos_pesos)==0:
            nuevos_pesos = metricas
    
        return nuevos_pesos
