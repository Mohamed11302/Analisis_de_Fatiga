import pandas as pd
import Constantes.Constantes as Const
import Constantes.Configuracion as Config
from Procesadores.Procesador_Datos import Procesador_Datos
from Procesadores.Procesador_Fatigas import Procesador_Fatigas
from Juegos.JUEGO import JUEGO
import auxiliares as aux
import numpy as np
class BBT(JUEGO):
    def __init__(self, dataframe:pd.DataFrame, porcentaje:int, date:str, user:str, hijo, fatiga_serie=None):
        super().__init__(date, user, fatiga_serie)
        self.user = user
        self.porcentaje = porcentaje
        self.date = date
        self.dataframe = dataframe
        self.hijo = hijo

        self.metricas = Const.METRICAS_FATIGA_BBT
        self.penalizaciones = Const.PENALIZACIONES_FATIGA_BBT
        self.Procesador_Datos = Procesador_Datos()
        self.Procesador_Fatigas = Procesador_Fatigas()
        
        self.datos_serie = {}
        self.datos_comparacion = {}
        self.fatiga_por_metrica = {}
        self.fatiga_por_repeticion = {}
        self.fatiga_serie_num = -1
        self.fatiga_serie_clasificacion = 'ERROR'
        #self.main()

    def main(self):
        self.extraer_datos_serie()        
        self.extraer_datos_comparacion()
        self.fatigas_por_metricas()
        self.obtener_fatiga_por_repeticion()
        self.obtener_fatiga_serie()

    def normalizar_datos(self):
        self.normalizar_repeticiones()
        self.normalizar_serie()

    def normalizar_repeticiones(self):
        valor_max = max(self.fatiga_por_repeticion)
        valor_min = min(self.fatiga_por_repeticion)
        hijo = self.hijo 
        while hijo != None:
            _max = max(hijo.fatiga_por_repeticion)
            _min = max(hijo.fatiga_por_repeticion)
            if valor_max < _max:
                valor_max = _max
            if valor_min > _min:
                valor_min = _min
            hijo = hijo.hijo
        hijo = self.hijo
        while hijo != None:
            data_norm = np.round((np.array(hijo.fatiga_por_repeticion) - valor_min) / (valor_max - valor_min), 3)
            hijo.fatiga_por_repeticion = data_norm.tolist()
            hijo = hijo.hijo
        data_norm = np.round((np.array(self.fatiga_por_repeticion) - valor_min) / (valor_max - valor_min), 3)
        self.fatiga_por_repeticion = data_norm.tolist()
    def normalizar_serie(self):
        valor_max = self.fatiga_serie_num
        valor_min = self.fatiga_serie_num
        hijo = self.hijo 
        while hijo != None:
            _max = hijo.fatiga_serie_num
            _min = hijo.fatiga_serie_num
            if valor_max < _max:
                valor_max = _max
            if valor_min > _min:
                valor_min = _min
            hijo = hijo.hijo
        hijo = self.hijo
        while hijo != None:
            fatiga_serie_normalizado = round(((hijo.fatiga_serie_num)-valor_min) / (valor_max - valor_min), 3)
            hijo.fatiga_serie_num = fatiga_serie_normalizado
            hijo = hijo.hijo
        fatiga_serie_normalizado = round(((self.fatiga_serie_num)-valor_min) / (valor_max - valor_min), 3)
        self.fatiga_serie_num = fatiga_serie_normalizado

    def extraer_datos_serie(self):
        _, num_repeticiones = self.num_repeticiones()
        _metricas = set(self.metricas.keys()) | set(self.penalizaciones.keys())
        self.datos_serie = self.Procesador_Datos.obtener_datos_paciente(self.dataframe, _metricas, 
                                                                        Const.INICIO_REPES, 
                                                                        num_repeticiones+1)
    def extraer_datos_comparacion(self):
        data_inicio_reps = self.procesar_datos_iniciales()
        if self.hijo == None:
            self.datos_comparacion = data_inicio_reps
        else:
            datos_historico = {}
            hijo = self.hijo
            while hijo != None:
                datos_serie_hijo = hijo.datos_serie
                datos_serie_hijo = aux.quitar_porcentaje_dict(datos_serie_hijo, 20, self.metricas)
                data_inicio_reps = self.Procesador_Datos.obtener_media(datos_serie_hijo, self.metricas)
                datos_historico[hijo.date] = self.calcular_media_comparacion(hijo.datos_comparacion, data_inicio_reps, 50)
                hijo = hijo.hijo
            datos_historico = self.calcular_media_historica(datos_historico)
            self.datos_comparacion = data_inicio_reps
            self.datos_comparacion = self.calcular_media_comparacion(datos_historico, data_inicio_reps, 50)


    def procesar_datos_iniciales(self):
        num_rep_iniciales, num_repeticiones = self.num_repeticiones()
        _data_rep_iniciales = self.Procesador_Datos.obtener_datos_paciente(self.dataframe, 
                                                                        self.metricas.keys(),
                                                                        num_rep_iniciales, 
                                                                        num_repeticiones)
        data_inicio_reps = self.Procesador_Datos.obtener_media(_data_rep_iniciales, self.metricas)
        return data_inicio_reps


    def calcular_media_historica(self, datos_historico):
        pesos = aux.crear_pesos(len(datos_historico))
        datos_historico = list(datos_historico.values())
        datos_historico = {clave: aux.media_ponderada_lista_diccionarios(datos_historico, clave, pesos) for clave in self.metricas.keys()}
        return datos_historico
    

    def calcular_media_comparacion(self, datos_historico, data_inicio_reps, proporcion=50):
        datos_comparacion = {}
        for clave, valor in datos_historico.items():
            if isinstance(valor, (int, float)):
                datos_comparacion[clave] = datos_historico[clave]*((100-proporcion)/100)+data_inicio_reps[clave]*(proporcion/100)
            if isinstance(valor, dict):
                datos_comparacion[clave] = {}
                for subclave, _ in valor.items():
                    datos_comparacion[clave][subclave] = datos_historico[clave][subclave]*((100-proporcion)/100)+ data_inicio_reps[clave][subclave]*(proporcion/100)
        return datos_comparacion

    def num_repeticiones(self):
        num_repeticiones = self.dataframe[Const.NUMREPETICION].max()
        num_rep_iniciales = round(num_repeticiones * (self.porcentaje/100)) + Const.INICIO_REPES #Ignoramos rep 0
        return num_rep_iniciales, num_repeticiones

    def fatigas_por_metricas(self):
        fatigas = {}
        for f in range(0, self.dataframe[Const.NUMREPETICION].max()):
            fatigas[f] = self.fatiga_por_metrica_rep(f)
        self.fatiga_por_metrica = fatigas
    def fatiga_por_metrica_rep(self, repeticion):
        fatigas = {}
        for clave in self.metricas.keys():
            if isinstance(self.datos_serie[clave], list):
                fatigas[clave] = self.Procesador_Fatigas.fatiga_por_repeticion(self.datos_serie[clave][repeticion], self.datos_comparacion[clave], clave)
            elif clave==Const.FATIGA_CURVATURA_MANO:
                fatigas[clave] = self.Procesador_Fatigas.fatiga_por_repeticion(self.datos_serie[clave], self.datos_comparacion[clave], clave, repeticion)
            elif clave==Const.FATIGA_HEADPOSITION:
                fatigas[clave] = self.Procesador_Fatigas.fatiga_por_repeticion(self.datos_serie[clave], self.datos_comparacion[clave], clave, {'repeticion': repeticion, 'df':self.dataframe})
        for clave in self.penalizaciones.keys():
            fatigas[clave] = self.datos_serie[clave][repeticion]
        return fatigas

    def obtener_fatiga_por_repeticion(self):
        fatigas = []
        for f in range(0, self.dataframe[Const.NUMREPETICION].max()):
            valor_fatiga, nuevas_metricas = self.Procesador_Fatigas.ponderacion_owa(self.fatiga_por_metrica[f], self.metricas)
            self.metricas = nuevas_metricas
            valor_fatiga = self.aplicar_penalizacion(valor_fatiga, f)
            fatigas.append(valor_fatiga)

        self.fatiga_por_repeticion = fatigas


    def aplicar_penalizacion(self, valor_fatiga:int, repeticion):
        for clave, valor in self.penalizaciones.items():
            if clave==Const.PENALIZACION_NUM_CAIDAS_BLOQUE:
                valor_fatiga += valor_fatiga*(self.fatiga_por_metrica[repeticion][clave]*valor)
            if clave==Const.PENALIZACION_MOVIMIENTO_INCORRECTO and self.fatiga_por_metrica[repeticion][clave]:
                valor_fatiga += valor_fatiga*valor       
        return valor_fatiga

    def obtener_fatiga_serie(self):
        data_sin_valores_bajos =aux.quitar_porcentaje_mas_bajo(self.fatiga_por_repeticion, 20)
        valor_fatiga_serie = sum(data_sin_valores_bajos)/len(data_sin_valores_bajos)        
        hijo = self.hijo
        while hijo:
            multiplicador_fatiga_acumulada = self.fatiga_acumulada(hijo)
            valor_fatiga_serie = valor_fatiga_serie + multiplicador_fatiga_acumulada*self.hijo.fatiga_serie_num
            if multiplicador_fatiga_acumulada != 0 and False:
                print(multiplicador_fatiga_acumulada, end=" ")
                print(f"[{aux.calcular_diferencia_en_segundos(self.date, hijo.date)}]", end= " ")
                print(f"({valor_fatiga_serie})")
            hijo = hijo.hijo
        #print()
        self.fatiga_serie_num = valor_fatiga_serie  

    def fatiga_acumulada(self, hijo):
        diferencia = aux.calcular_diferencia_en_segundos(self.date, hijo.date)
        if diferencia<400:
            if diferencia-60>=0:
                multiplicador_fatiga_acumulada = aux.fuzzy_tiempo_descanso((diferencia-60))
            else:
                multiplicador_fatiga_acumulada = aux.fuzzy_tiempo_descanso(0)
        else:
            multiplicador_fatiga_acumulada = 0
        return multiplicador_fatiga_acumulada
    def clasificar_fatigas(self):
        bbt = self
        while bbt:
            bbt.fatiga_serie_clasificacion = self.indicador_clasificacion(bbt.fatiga_serie_num)
            bbt = bbt.hijo

    def indicador_clasificacion(self, valor):
        clasificacion = 'ERROR'
        if valor>=0 and valor <=0.3:
            clasificacion = Const.FATIGA_LOW
        elif valor>0.3 and valor<=0.6:
            clasificacion = Const.FATIGA_MODERATE
        elif valor>0.6 and valor<=0.9:
            clasificacion = Const.FATIGA_HIGH
        elif valor>0.9 and valor<=1:
            clasificacion = Const.FATIGA_VERY_HIGH
        return clasificacion

def bucleBBT(juegos, user):
    lista_juegos = list(juegos.keys())
    myBBT = None
    for date in reversed(lista_juegos):
        myBBT = BBT(juegos[date], Config.PORCENTAJE_COMPARACION, date, user, myBBT)
        myBBT.main()
    bbt = myBBT
    if len(lista_juegos)>1:
        myBBT.normalizar_datos()
        myBBT.clasificar_fatigas()
    bbt = myBBT
    valores_de_fatiga = []
    outputs = []
    while bbt:
        output = f"{bbt.date} = {bbt.fatiga_serie_num:<6} {bbt.fatiga_serie_clasificacion}"
        outputs.append(output)
        valores_de_fatiga.append(bbt.fatiga_serie_num)
        bbt = bbt.hijo
    for output in outputs[::-1]:
        print(output)
    print(valores_de_fatiga[::-1])
    return myBBT


        
