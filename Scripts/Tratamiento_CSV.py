import pandas as pd
import matplotlib.pyplot as plt
import Constantes.Configuracion as Config
import Constantes.Constantes as Const
import ExtraerDatos
import ExtraerFatigas
import Excepciones

def leercsv(date: str) -> pd.core.frame.DataFrame:
    try:
        ruta = Config.DIRECTORIO_TRACKING_DATA + Config.PREFIJO_FICHEROS + date + Config.EXTENSION_FICHEROS
        df = pd.read_csv(ruta, encoding='UTF-8', sep=';', index_col=False)
    except:
        raise Excepciones.ErrorRuta("No se pudo encontrar el fichero: " + str(ruta))
    df = df[df[Const.HIGHCONFIDENCE] == True]
    df = df.reset_index()
    df = df.drop(columns=['index'])
    df = sustituir_comas(df)
    return df

def escribircsv(df:pd.core.frame.DataFrame, ruta_original:str):
    ruta_original = ruta_original.split(Config.EXTENSION_FICHEROS)
    df.to_csv(ruta_original[0] + str("_modificado"+ Config.EXTENSION_FICHEROS), sep=";", decimal=',')

def obtener_juego_y_user(nombre):
    df = pd.read_csv(Config.DIRECTORIO_HISTORICAL, sep=";", index_col=False)
    df = df[df[Const.HIST_DATE]==nombre]
    if not df.empty:
        game = df.iloc[0][Const.HIST_GAME]
        user = df.iloc[0][Const.HIST_USER]
    return game, user

def LeerDatosHistoricos(date:str) -> dict:
    game, user = obtener_juego_y_user(date)

    df = pd.read_csv(Config.DIRECTORIO_HISTORICAL, encoding='UTF-8', sep=';', index_col=False)
    intentos = df[(df[Const.HIST_USER] == user) & (df[Const.HIST_GAME]==game) & (df[Const.HIST_DATE]<date)][Const.HIST_DATE]
    csvs = {}
    for intento in intentos.values:
        csvs[intento] = leercsv(intento)
    return csvs


def sustituir_comas(df:pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    columnas_a_seleccionar = df.select_dtypes(exclude=['int', 'bool']).columns
    columnas_a_seleccionar = columnas_a_seleccionar[~columnas_a_seleccionar.isin(['GrabIdentifier'])]
    df[columnas_a_seleccionar] = df[columnas_a_seleccionar].applymap(lambda x:
                                        float(str(x).replace(',', '.')) if pd.notnull(x) else x)
    return df
