import pandas as pd
import Constantes.Configuracion as Config
import Constantes.Constantes as Const
import subprocess
from io import StringIO


def leer_csv(ruta:str):
    if Config.LEER_FICHEROS_OCULUS:
        try:
            comando_adb_cat = f'adb shell cat ' + ruta
            contenido_csv = subprocess.check_output(comando_adb_cat, shell=True)
            df = pd.read_csv(StringIO(contenido_csv.decode('utf-8')), sep=";", index_col=False)            
            return df
        except: 
            print(f"Ha ocurrido un error tratando de leer adb shell cat {ruta}")
            raise SystemExit(0)
    else:
        try:
            df = pd.read_csv(ruta, sep=";", index_col=False)            
            return df
        except: 
            print(f"Ha ocurrido un error tratando de leer {ruta}")
            raise SystemExit(0)


def leercsv_serie(date: str, user:str) -> pd.core.frame.DataFrame:
    ruta = Config.DIRECTORIO_UTILIZADO + user + Config.DIRECTORIO_TRACKING_DATA + Config.PREFIJO_FICHEROS + date + Config.EXTENSION_FICHEROS
    df = leer_csv(ruta)
    df = df[df[Const.HIGHCONFIDENCE] == True]
    df = df.reset_index()
    df = df.drop(columns=['index'])
    df = sustituir_comas(df)
    return df

def escribircsv(df:pd.core.frame.DataFrame, ruta_original:str):
    ruta_original = ruta_original.split(Config.EXTENSION_FICHEROS)
    df.to_csv(ruta_original[0] + str("_modificado"+ Config.EXTENSION_FICHEROS), sep=";", decimal=',')


def LeerDatosHistoricos(date:str, user:str) -> dict:
    ruta = Config.DIRECTORIO_UTILIZADO + user + "/" + Config.DIRECTORIO_HISTORICAL
    df = leer_csv(ruta)
    intentos = df[df[Const.HIST_DATE] < date][Const.HIST_DATE].sort_values(ascending=False)
    csvs = {}
    for intento in intentos.values:
        csvs[intento] = leercsv_serie(intento, user)
    return csvs


def sustituir_comas(df:pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    columnas_a_seleccionar = df.select_dtypes(exclude=['int', 'bool']).columns
    columnas_a_seleccionar = columnas_a_seleccionar[~columnas_a_seleccionar.isin(['GrabIdentifier'])]
    df[columnas_a_seleccionar] = df[columnas_a_seleccionar].applymap(lambda x:
                                        float(str(x).replace(',', '.')) if pd.notnull(x) else x)
    return df
