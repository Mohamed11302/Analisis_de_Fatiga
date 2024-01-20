import Constantes.Constantes as Const
import Procesadores.ExtraerFatigas as ExtraerFatigas


class Procesador_Fatigas:
    def __init__(self):
        pass
    def fatiga_por_repeticion(self, valor_medio, valor_a_comparar, metrica:str, atributo_opcional=0):
        fatiga = -1
        if metrica == Const.FATIGUE_VELOCITY:
            fatiga = ExtraerFatigas.fatiga_calculo_general(valor_medio, valor_a_comparar, metrica)
        if metrica == Const.FATIGUE_TIME:
            fatiga = ExtraerFatigas.fatiga_calculo_general(valor_medio, valor_a_comparar, metrica)
        if metrica == Const.FATIGUE_STRENGTH:
            fatiga = ExtraerFatigas.fatiga_calculo_general(valor_medio, valor_a_comparar, metrica)
        if metrica == Const.FATIGUE_HAND_TRAJECTORY:
            fatiga = ExtraerFatigas.fatiga_calculo_curvatura_mano(valor_medio, valor_a_comparar, atributo_opcional)
        if metrica == Const.FATIGUE_HEADPOSITION:
            fatiga = ExtraerFatigas.fatiga_calculo_headposition(valor_medio, valor_a_comparar, atributo_opcional)
        if metrica == Const.FATIGUE_WRIST:
            pass
        return fatiga
    def ponderacion_owa(self, fatigas, owa_operadores) -> float:
        owa_operadores = self.reweighting(fatigas, owa_operadores)
        fatigas_values = sorted(fatigas.values(), reverse=True)
        valor_fatiga = sum(fatiga * owa for fatiga, owa in zip(fatigas_values, owa_operadores))
        
        return valor_fatiga, owa_operadores

    def reweighting(self, valores_fatiga: dict, owa_operadores:list):
        """ Reajuste de los pesos para cada métrica de fatiga si se detecta que alguna llega al valor Grave """
        nuevos_pesos = []
        suma_nuevos_pesos = 0
        evaluado = False
        for _, valor_fatiga in valores_fatiga.items():
            if valor_fatiga > Const.ABNORMAL_FATIGUE and not evaluado:
                evaluado = True
                for peso in owa_operadores:
                    A = 1 - peso
                    B = A - peso
                    if B <= 0:
                        nuevos_pesos.append(valor_fatiga)
                        suma_nuevos_pesos += valor_fatiga
                    else:
                        nuevos_pesos.append(valor_fatiga + B)
                        suma_nuevos_pesos += valor_fatiga + B
                for valor in range(0, len(nuevos_pesos)):
                    nuevos_pesos[valor] = round(nuevos_pesos[valor]/suma_nuevos_pesos, 3)
        if len(nuevos_pesos)==0:
            nuevos_pesos = owa_operadores
    
        return nuevos_pesos
