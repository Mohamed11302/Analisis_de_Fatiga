import pandas as pd
import matplotlib.pyplot as plt
import Constantes as Const
import ExtraerDatos
import ExtraerFatigas
import Excepciones

def leercsv(date: str) -> pd.core.frame.DataFrame:
    try:
        ruta = Const.DIRECTORIO_TRACKING_DATA + Const.PREFIJO_FICHEROS + date + Const.EXTENSION_FICHEROS
        df = pd.read_csv(ruta, encoding='UTF-8', sep=';', index_col=False)
    except:
        raise Excepciones.ErrorRuta("No se pudo encontrar el fichero: " + str(ruta))
    df = df[df[Const.HIGHCONFIDENCE] == True]
    df = df.reset_index()
    df = df.drop(columns=['index'])
    df = sustituir_comas(df)
    return df

def escribircsv(df:pd.core.frame.DataFrame, ruta_original:str):
    ruta_original = ruta_original.split(Const.EXTENSION_FICHEROS)
    df.to_csv(ruta_original[0] + str("_modificado"+ Const.EXTENSION_FICHEROS), sep=";", decimal=',')

def obtener_juego_y_user(nombre):
    df = pd.read_csv(Const.DIRECTORIO_HISTORICAL, sep=";", index_col=False)
    df = df[df[Const.HIST_DATE]==nombre]
    if not df.empty:
        game = df.iloc[0][Const.HIST_GAME]
        user = df.iloc[0][Const.HIST_USER]
    return game, user

def RegistroHistoricoPaciente(user:str):
    csvs = LeerDatosHistoricos(user)
    media_historica = SacarMediaHistorica(csvs)
    return media_historica

def LeerDatosHistoricos(date:str) -> dict:
    game, user = obtener_juego_y_user(date)

    df = pd.read_csv(Const.DIRECTORIO_HISTORICAL, encoding='UTF-8', sep=';', index_col=False)
    intentos = df[(df[Const.HIST_USER] == user) & (df[Const.HIST_GAME]==game) & (df[Const.HIST_DATE]<date)][Const.HIST_DATE]
    csvs = {}
    for intento in intentos.values:
        csvs[intento] = leercsv(intento)
    return csvs

def SacarMediaHistorica(csvs: dict):
    media_historica = {}
    for clave, df in csvs.items():
        df1 = dividir_en_repeticiones(df)
        media_historica[clave] = ExtraerDatos.mediahistorica(df1)
    media_historica = dict(sorted(media_historica.items(), key=lambda item: item[0], reverse=True))
    media_historica = ExtraerDatos.ponderar_media_historica(media_historica)
    return media_historica


def dividir_en_repeticiones(df: pd.DataFrame) -> pd.DataFrame:
    unique_blocks = df[Const.GRABIDENTIFIER].dropna().unique()
    num_repeticion = 0
    columna_repeticion = []

    for i in range(len(df)):
        if pd.notnull(df.at[i, Const.GRABIDENTIFIER]):
            if num_repeticion < len(unique_blocks) and df.at[i, Const.GRABIDENTIFIER] == unique_blocks[num_repeticion]:
                num_repeticion += 1
            columna_repeticion.append(num_repeticion)
        else:
            columna_repeticion.append(num_repeticion)

    df[Const.NUMREPETICION] = columna_repeticion
    df = df[df[Const.NUMREPETICION] != 0]

    return df

def sustituir_comas(df:pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    columnas_a_seleccionar = df.select_dtypes(exclude=['int', 'bool']).columns
    columnas_a_seleccionar = columnas_a_seleccionar[~columnas_a_seleccionar.isin(['GrabIdentifier'])]
    df[columnas_a_seleccionar] = df[columnas_a_seleccionar].applymap(lambda x:
                                        float(str(x).replace(',', '.')) if pd.notnull(x) else x)
    return df

"""
def tomarposicion_hmd(archivo:str):
    archivo = archivo.removeprefix('CSVs/OculusTracking_').removesuffix('.csv')
    df = pd.read_csv('CSVs/Historical.csv', encoding='UTF-8', sep=';', index_col=False)
    hmd_x = df[df['DATE']==archivo]['HMD_POSITION_X'].values[0]
    hmd_x = float(hmd_x.replace(',', '.'))
    return hmd_x
"""
