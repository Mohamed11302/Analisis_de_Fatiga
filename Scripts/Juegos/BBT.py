import pandas as pd
import Constantes.Constantes as Const
import Constantes.Configuracion as Config
from Procesadores.Procesador_Datos import Procesador_Datos
from Procesadores.Procesador_Fatigas import Procesador_Fatigas
from Juegos.JUEGO import JUEGO
import IO.Leer_ficheros as Leer_ficheros
import auxiliares as aux
import numpy as np
class BBT(JUEGO):
    def __init__(self, dataframe:pd.DataFrame, porcentaje:int, date:str, user:str, bbt_historico:bool, fatiga_serie=None):
        super().__init__(date, user, fatiga_serie)
        self.user = user
        self.bbt_historico = bbt_historico
        self.metricas = Const.METRICAS_FATIGA_BBT
        self.penalizaciones = Const.PENALIZACIONES_FATIGA_BBT
        self.porcentaje = porcentaje
        self.date = date
        self.Procesador_Datos = Procesador_Datos()
        self.Procesador_Fatigas = Procesador_Fatigas()
        self.dataframe = dataframe
        self.dividir_en_repeticiones()
        self.mano_derecha = self.Procesador_Datos.mano_derecha(self.dataframe)
        self.datos_serie = {}
        self.datos_comparacion = {}
        self.data_BBT_historico = []
        self.fatiga_por_metrica = {}
        self.fatiga_por_repeticion = {}
        self.fatiga_serie = -1
        self.extraer_datos_serie()
        
        self.extraer_datos_comparacion()
        self.fatigas_por_metricas()
        self.obtener_fatiga_por_repeticion()
        if not self.bbt_historico:
            self.obtener_fatiga_serie()
            #print(self.datos_comparacion)
            #print(self.fatiga_por_metrica)
            #self.dataframe.to_csv('prueba2.csv', sep= ";")


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
        columna_repeticion = self.comprobar_repeticiones(columna_repeticion)
        self.dataframe[Const.NUMREPETICION] = columna_repeticion
        self.dataframe = self.dataframe[self.dataframe[Const.NUMREPETICION] != 0]
        self.dataframe = self.dataframe.reset_index(drop=True)
    def comprobar_repeticiones(self, columna):
        for i in set(columna):
            if columna.count(i) == 1:
                for j in range(len(columna)):
                    if columna[j] == i:
                        columna[j] += 1
        i = 0
        while i < len(columna) - 1:
            if columna[i+1] - columna[i] == 2:
                for j in range(i+1, len(columna)):
                    columna[j] -= 1
            i += 1
        return columna



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
            else:
                self.datos_comparacion = data_inicio_reps


    def extraer_datos_historicos(self):
        data_historico = Leer_ficheros.LeerDatosHistoricos(self.date, self.user)
        for date, data in data_historico.items():
            if len(self.data_BBT_historico) < Config.MAXIMO_FICHEROS_HISTORICOS:
                BBT_date = BBT(data, 20, date, self.user, True)
                if BBT_date.mano_derecha == self.mano_derecha:
                    self.data_BBT_historico.append(BBT_date)
            else:
                break

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
        valor_min = min(fatigas)
        valor_max = max(fatigas)
        if not self.bbt_historico:
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
            if len(self.data_BBT_historico)>1:
                data_norm = np.round((np.array(fatigas) - valor_min) / (valor_max - valor_min), 3)
                fatigas = data_norm.tolist()

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

        data_sin_valores_bajos =aux.quitar_porcentaje_mas_bajo(self.fatiga_por_repeticion, 20)
        valor_fatiga_serie = sum(data_sin_valores_bajos)/len(data_sin_valores_bajos)

        valor_min = valor_fatiga_serie
        valor_max = valor_fatiga_serie
        for i in self.data_BBT_historico:
            data_sin_valores_bajos =aux.quitar_porcentaje_mas_bajo(i.fatiga_por_repeticion, 20)
            valor_fatiga_historico = sum(data_sin_valores_bajos)/len(data_sin_valores_bajos)
            if valor_fatiga_historico < valor_min:
                valor_min = valor_fatiga_historico 
            if valor_fatiga_historico > valor_max:
                valor_max = valor_fatiga_historico 
            i.fatiga_serie = valor_fatiga_historico
        
        if len(self.data_BBT_historico)>1:
            for i in self.data_BBT_historico: ##ACABAR, SOLO QUEDA NORMALIZAR LOS DATOS DEL HISTORICO Y CALCULAR EL DE ESTA SERIE
                fatiga_serie_normalizado = round(((i.fatiga_serie)-valor_min) / (valor_max - valor_min), 3)
                i.fatiga_serie = fatiga_serie_normalizado
                print(f"{i.date}: {fatiga_serie_normalizado}")
        
            valor_fatiga_serie = round(((valor_fatiga_serie)-valor_min) / (valor_max - valor_min), 3)
        
        self.fatiga_serie = valor_fatiga_serie        
        print(f"{self.date}: {self.fatiga_serie}")



        
        
