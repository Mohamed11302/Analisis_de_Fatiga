import pandas as pd
import Constantes.Constantes as Const
import Procesadores.ExtraerDatos as ExtraerDatos 
import Excepciones
class Procesador_Datos:
    def __init__(self):
        pass
    def datos_por_repeticion(self, dataframe: pd.DataFrame, metrica:str, inicio_rep:int, final_rep:int):
        if metrica == Const.FATIGA_VELOCIDAD:
            data = ExtraerDatos.datos_velocidad_por_repeticion(dataframe, inicio_rep, final_rep)
        elif metrica == Const.FATIGA_WRIST:
            data = ExtraerDatos.datos_flexion_muneca_por_repeticion(dataframe, inicio_rep, final_rep)
        elif metrica == Const.FATIGA_HEADPOSITION:
            data = ExtraerDatos.datos_posicion_cabeza_por_repeticion(dataframe, inicio_rep, final_rep)
        elif metrica == Const.FATIGA_CURVATURA_MANO:
            data = ExtraerDatos.datos_curvatura_por_repeticion(dataframe, inicio_rep, final_rep)
        elif metrica == Const.PENALIZACION_MOVIMIENTO_INCORRECTO:
            data = ExtraerDatos.datos_movimiento_incorrecto_por_repeticion(dataframe, inicio_rep, final_rep)
        elif metrica == Const.PENALIZACION_NUM_CAIDAS_BLOQUE:
            data = ExtraerDatos.datos_caida_del_bloque_por_repeticion(dataframe, inicio_rep, final_rep)
        elif metrica == Const.FATIGA_STRENGTH:
            data = ExtraerDatos.datos_fuerza_por_repeticion_por_repeticion(dataframe, inicio_rep, final_rep)
        elif metrica == Const.FATIGA_TIEMPO:
            data = ExtraerDatos.datos_tiempo_por_repeticion_por_repeticion(dataframe, inicio_rep, final_rep)
        else:
            raise Excepciones.ErrorNombre("Esa métrica no se mide en el programa")
        return data
    
    def obtener_datos_paciente(self, dataframe: pd.DataFrame, metricas: [str], inicio_rep: int, final_rep: int) -> dict:
        data = {}
        for metrica in metricas:
            data[metrica] = self.datos_por_repeticion(dataframe, metrica, inicio_rep, final_rep)
        return data

    def obtener_media(self, data_serie: dict, metricas: [str]):
        data_media = {}
        for metrica in metricas:
            if isinstance(data_serie[metrica], list) and (
                metrica != Const.PENALIZACION_MOVIMIENTO_INCORRECTO
                and metrica != Const.PENALIZACION_NUM_CAIDAS_BLOQUE
            ):
                data_media[metrica] = sum(data_serie[metrica]) / len(data_serie[metrica])

            if metrica in {Const.FATIGA_HEADPOSITION, Const.FATIGA_CURVATURA_MANO}:
                data_media[metrica] = {
                    clave: max(data_serie[metrica][clave]) if 'MAX' in clave else min(data_serie[metrica][clave])
                    for clave in data_serie[metrica]
                }

        return data_media
    def mano_derecha(self, df):
        mano_derecha = True 
        indice_primera_fila = df[Const.GRABIDENTIFIER].first_valid_index()
        df_resultado = df.iloc[indice_primera_fila:]
        fila_primer_valor = df_resultado.iloc[0][Const.HANDPOSITION_X]
        idx_first_empty_row = df[df_resultado[Const.GRABIDENTIFIER].isnull()].index[0]
        if idx_first_empty_row >= 0:
            previous_row = df_resultado.iloc[idx_first_empty_row-1][Const.HANDPOSITION_X]
            if fila_primer_valor - previous_row < 0:
                mano_derecha = False
        return mano_derecha
