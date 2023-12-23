import pandas as pd
import matplotlib.pyplot as plt
import Constantes as Const
import ExtraerDatos
import CalculoFatigas


def leercsv(archivo_csv: str) -> pd.core.frame.DataFrame:
    df = pd.read_csv(archivo_csv, encoding='UTF-8', sep=';', index_col=False)
    df = sustituir_comas(df)
    return df

def escribircsv(df:pd.core.frame.DataFrame, ruta_original:str):
    ruta_original = ruta_original.split('.csv')
    df.to_csv(ruta_original[0] + str("_modificado.csv"), sep=";", decimal=',')

def RegistroHistoricoPaciente(user:str):
    csvs = LeerDatosHistoricos(user)
    media_historica = SacarMediaHistorica(csvs)
    return media_historica

def LeerDatosHistoricos(user: str) -> dict:
    df = pd.read_csv('CSVs/Historical.csv', encoding='UTF-8', sep=';', index_col=False)
    #intentos = df[df['USER'] == user].drop(df.index[-1])['DATE']
    intentos = df[df['USER'] == user]['DATE']
    csvs = {}
    for intento in intentos.values:
        try:
            ruta = 'CSVs/TrackingData/OculusTracking_' + str(intento) + ".csv"
            csvs[intento] = leercsv(ruta)
        except:
            print("[ERROR]No existe el fichero: " + str(intento))
    return csvs

def SacarMediaHistorica(csvs: dict):
    media_historica = {}
    for clave, df in csvs.items():
        df1 = dividir_en_repeticiones(df)
        media_historica[clave] = ExtraerDatos.mediahistorica(df1)
    media_historica = dict(sorted(media_historica.items(), key=lambda item: item[0], reverse=True))
    media_historica = ExtraerDatos.ponderar_media_historica(media_historica)
    return media_historica


def dividir_en_repeticiones(df: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    unique_blocks = df[Const.GRABIDENTIFIER].dropna().unique()
    num_repeticion = 0
    columna_repeticion = []
    for i in range(0, len(df)):
        try:
            if df.at[i, Const.GRABIDENTIFIER] == unique_blocks[num_repeticion]:
                num_repeticion += 1
                columna_repeticion.append(num_repeticion)
            else:
                columna_repeticion.append(num_repeticion)
        except:
            columna_repeticion.append(num_repeticion)
    df[Const.NUMREPETICION] = columna_repeticion    
    df = df[df[Const.NUMREPETICION] != 0]
    return df

def representacion_handposition_por_repeticiones(df:pd.core.frame.DataFrame):
    ejes_verticales = []
    repeticion = 0
    ejes_verticales.append(0)
    for i in range(0, len(df)):
        if df.at[i, Const.NUMREPETICION]> repeticion:
            repeticion+=1
            ejes_verticales.append(i)
    print(ejes_verticales)


    vector = ExtraerDatos.aux_vectorizar(df[Const.HANDPOSITION_X],
                                     df[Const.HANDPOSITION_Y],
                                     df[Const.HANDPOSITION_Z])
    for line in ejes_verticales:
        plt.axvline(x=line, color='k', linestyle='--', label=f'X = {line:.2f}')

    plt.plot(vector)
    plt.title('Division por Repeticiones')
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid()
    plt.show()

def sustituir_comas(df:pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    columnas_a_seleccionar = df.select_dtypes(exclude=['int', 'bool']).columns
    columnas_a_seleccionar = columnas_a_seleccionar[~columnas_a_seleccionar.isin(['GrabIdentifier'])]
    df[columnas_a_seleccionar] = df[columnas_a_seleccionar].applymap(lambda x:
                                        float(str(x).replace(',', '.')) if pd.notnull(x) else x)
    return df

def tomarposicion_hmd(archivo:str):
    archivo = archivo.removeprefix('CSVs/OculusTracking_').removesuffix('.csv')
    df = pd.read_csv('CSVs/Historical.csv', encoding='UTF-8', sep=';', index_col=False)
    hmd_x = df[df['DATE']==archivo]['HMD_POSITION_X'].values[0]
    hmd_x = float(hmd_x.replace(',', '.'))
    return hmd_x
