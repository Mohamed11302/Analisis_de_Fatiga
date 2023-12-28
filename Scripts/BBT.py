import pandas as pd
import Constantes as Const
from Procesador_Datos import Procesador_Datos
from Procesador_Fatigas import Procesador_Fatigas
import Tratamiento_CSV
import auxiliares as aux
import numpy as np
class BBT:
    def __init__(self, dataframe:pd.DataFrame, porcentaje:int, date:str, bbt_historico:bool):
        self.bbt_historico = bbt_historico
        self.metricas = Const.METRICAS_FATIGA_BBT
        self.penalizaciones = Const.PENALIZACIONES_FATIGA_BBT
        self.porcentaje = porcentaje
        self.date = date
        self.Procesador_Datos = Procesador_Datos()
        self.Procesador_Fatigas = Procesador_Fatigas()
        self.dataframe = dataframe
        self.dividir_en_repeticiones()
        
        self.datos_serie = {}
        self.datos_comparacion = {}
        self.data_BBT_historico = []
        self.fatiga_por_metrica = {}
        self.fatiga_por_repeticion = {}
        self.fatiga_serie = -99
        self.extraer_datos_serie()
        
        self.extraer_datos_comparacion()
        self.fatigas_por_metricas()
        self.obtener_fatiga_por_repeticion()
        if not self.bbt_historico:
            self.obtener_fatiga_serie()


    def dividir_en_repeticiones(self):
        unique_blocks = self.dataframe[Const.GRABIDENTIFIER].dropna().unique()
        num_repeticion = 0
        columna_repeticion = []

        for i in range(len(self.dataframe)):
            if pd.notnull(self.dataframe[Const.GRABIDENTIFIER].iloc[i]):
                if ((num_repeticion < len(unique_blocks)) and 
                    (self.dataframe[Const.GRABIDENTIFIER].iloc[i] == unique_blocks[num_repeticion])):
                    num_repeticion += 1
                columna_repeticion.append(num_repeticion)
            else:
                columna_repeticion.append(num_repeticion)

        self.dataframe[Const.NUMREPETICION] = columna_repeticion
        self.dataframe = self.dataframe[self.dataframe[Const.NUMREPETICION] != 0]
        self.dataframe = self.dataframe.reset_index(drop=True)


    def extraer_datos_serie(self):
        num_rep_iniciales, num_repeticiones = self.num_repeticiones()
        _metricas = set(self.metricas.keys()) | set(self.penalizaciones.keys())
        self.datos_serie = self.Procesador_Datos.obtener_datos_paciente(self.dataframe, _metricas, 
                                                                        Const.INICIO_REPES, 
                                                                        num_repeticiones+1)
    def extraer_datos_comparacion(self):
        data_inicio_reps = self.procesar_datos_iniciales()
        if self.bbt_historico:
            #print("Tomar solo las rep iniciales")
            self.datos_comparacion = data_inicio_reps
        else:
            self.extraer_datos_historicos()
            if len(self.data_BBT_historico)>0:
                #print("Media historica")
                datos_historico = self.calcular_media_datos_historicos()
                self.calcular_datos_comparacion(datos_historico, data_inicio_reps)

    def extraer_datos_historicos(self):
        data_historico = Tratamiento_CSV.LeerDatosHistoricos(self.date)
        for date, data in data_historico.items():
            BBT_date = BBT(data, 20, date, True)
            self.data_BBT_historico.append(BBT_date)

    def procesar_datos_iniciales(self):
        num_rep_iniciales, num_repeticiones = self.num_repeticiones()
        _data_rep_iniciales = self.Procesador_Datos.obtener_datos_paciente(self.dataframe, 
                                                                        self.metricas.keys(),
                                                                        num_rep_iniciales, 
                                                                        num_repeticiones)
        data_inicio_reps = self.Procesador_Datos.obtener_media(_data_rep_iniciales, self.metricas)
        return data_inicio_reps

    def calcular_media_datos_historicos(self):
        for bbt in self.data_BBT_historico:
            self.actualizar_datos_comparacion(bbt)
        datos_historico = self.calcular_datos_historicos()
        return datos_historico

    def actualizar_datos_comparacion(self, bbt):
        bbt.datos_comparacion = aux.quitar_porcentaje_dict(bbt.datos_serie, 20)
        bbt.datos_comparacion = bbt.Procesador_Datos.obtener_media(bbt.datos_comparacion, self.metricas)

    def calcular_datos_historicos(self):
        pesos = aux.crear_pesos(len(self.data_BBT_historico))
        _datos_bbt_historico = [bbt.datos_comparacion for bbt in self.data_BBT_historico]
        #primer_bbt = next(iter(self.data_BBT_historico.values()))
        #claves_del_primer_elemento_interno = list(primer_bbt.datos_comparacion.keys())
        datos_historico = {clave: aux.media_ponderada_lista_diccionarios(_datos_bbt_historico, clave, pesos) for clave in self.metricas.keys()}
        return datos_historico
    

    def calcular_datos_comparacion(self, datos_historico, data_inicio_reps):
        for clave, valor in datos_historico.items():
            if isinstance(valor, (int, float)):
                self.datos_comparacion[clave] = (datos_historico[clave]+data_inicio_reps[clave])/2
            if isinstance(valor, dict):
                self.datos_comparacion[clave] = {}
                for subclave, _ in valor.items():
                    self.datos_comparacion[clave][subclave] = (datos_historico[clave][subclave]+ data_inicio_reps[clave][subclave])/2


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
    
        if not self.bbt_historico:
            valor_min = 99999
            valor_max = -99999        
            for i in self.data_BBT_historico:
                _min = min(i.fatiga_por_repeticion)
                _max = max(i.fatiga_por_repeticion)     
                if _min < valor_min:
                    valor_min = _min 
                if _max > valor_max:
                    valor_max = _max          
            for i in self.data_BBT_historico:
                data_norm = np.round((np.array(i.fatiga_por_repeticion) - valor_min) / (valor_max - valor_min), 3)
                i.fatiga_por_repeticion = data_norm.tolist()
            data_norm = np.round((np.array(fatigas) - valor_min) / (valor_max - valor_min), 3)
            fatigas = data_norm.tolist()
            print(fatigas)
        self.fatiga_por_repeticion = fatigas


    def aplicar_penalizacion(self, valor_fatiga:int, repeticion):
        for clave, valor in self.penalizaciones.items():
            if clave==Const.PENALIZACION_NUM_CAIDAS_BLOQUE:
                valor_fatiga += valor_fatiga*(self.fatiga_por_metrica[repeticion][clave]*valor)
            if clave==Const.PENALIZACION_MOVIMIENTO_INCORRECTO and self.fatiga_por_metrica[repeticion][clave]:
                valor_fatiga += valor_fatiga*valor       
        return valor_fatiga

    def obtener_fatiga_serie(self):
        fatiga_serie = []
        valor_min=9999
        valor_max=-9999
        for i in self.data_BBT_historico:
            data_sin_valores_bajos =aux.quitar_porcentaje_mas_bajo(i.fatiga_por_repeticion, 20)
            valor_fatiga = sum(data_sin_valores_bajos)/len(data_sin_valores_bajos)
            if valor_fatiga < valor_min:
                valor_min = valor_fatiga 
            if valor_fatiga > valor_max:
                valor_max = valor_fatiga 
            i.fatiga_serie = valor_fatiga

        for i in self.data_BBT_historico: ##ACABAR, SOLO QUEDA NORMALIZAR LOS DATOS DEL HISTORICO Y CALCULAR EL DE ESTA SERIE
            fatiga_serie_normalizado = round(((i.fatiga_serie)-valor_min) / (valor_max - valor_min), 3)
            i.fatiga_serie = fatiga_serie_normalizado
            print(f"{i.date}: {fatiga_serie_normalizado}")
        
        data_sin_valores_bajos =aux.quitar_porcentaje_mas_bajo(self.fatiga_por_repeticion, 20)
        valor_fatiga = sum(data_sin_valores_bajos)/len(data_sin_valores_bajos)
        fatiga_serie_normalizado = round(((valor_fatiga)-valor_min) / (valor_max - valor_min), 3)
        self.fatiga_serie = fatiga_serie_normalizado
        print(f"{self.date}: {self.fatiga_serie}")


        
        
