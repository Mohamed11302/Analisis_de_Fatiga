import pandas as pd
import matplotlib.pyplot as plt
import Constantes
import CalculoDatos
import CalculoFatigas

def LeerDatosHistoricos(user: str) -> dict:
    df = pd.read_csv('CSVs/Historical.csv', encoding='UTF-8', sep=';', index_col=False)
    intentos = df[df['USER']==user]['DATE']
    csvs = {}
    for intento in intentos.values:
        try:
            ruta = 'CSVs/OculusTracking_' + str(intento) + ".csv"
            csvs[intento] = leercsv(ruta)
        except:
            print("[ERROR]No existe el fichero: " + str(intento))
    print(len(csvs))
    return csvs

def SacarMediaHistorica(csvs: dict):
    media_historica = {}
    for clave, df in csvs.items():
        df1 = dividir_en_repeticiones(df)
        media_historica[clave] = CalculoFatigas.mediahistorica(df1)
    print(media_historica)
 
def sustituir_comas(df:pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    columnas_a_seleccionar = df.select_dtypes(exclude=['int', 'bool']).columns
    df[columnas_a_seleccionar] = df[columnas_a_seleccionar].applymap(lambda x:
                                        float(str(x).replace(',', '.')) if pd.notnull(x) else x)
    return df

def leercsv(archivo_csv: str) -> pd.core.frame.DataFrame:
    df = pd.read_csv(archivo_csv, encoding='UTF-8', sep=';', index_col=False)
    df = sustituir_comas(df)
    return df

def escribircsv(df:pd.core.frame.DataFrame, archivo:str):
    archivo = archivo.split('.csv')
    df.to_csv(archivo[0] + str("_modificado.csv"), sep=";", decimal=',')

def dividir_en_repeticiones(df: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    agarrando_objeto = False
    num_repeticion = 1
    columna_repeticion = []
    for i in range(0, len(df)):
        if (df.at[i, Constantes.ISPINCHGRABBING]) and agarrando_objeto == False:
            num_repeticion += 1
            agarrando_objeto = True
        elif (df.at[i, Constantes.ISPINCHGRABBING] == False) and agarrando_objeto == True:
            agarrando_objeto = False
        columna_repeticion.append(num_repeticion)
    df[Constantes.NUMREPETICION] = columna_repeticion
    return df


def dividir_en_repeticiones_2(df: pd.core.frame.DataFrame, archivo: str) -> pd.core.frame.DataFrame:
    primer_objeto_agarrado = False
    inicio_ejercicio = False
    num_repeticion = 1
    mano_derecha = False
    #mitad_caja = tomarposicion_hmd(archi7vo)
    mitad_caja = -0.0027808845043182375
    Condiciones = [False, False] #1º ESPERAR HASTA QUE SUELTES EL BLOQUE 2º ESPERAR HASTA QUE COJAS OTRO BLOQUE
    columna_repeticion = []
    for i in range(0, len(df)):
        if inicio_ejercicio:
            if Condiciones[0] == False:
                if (df.at[i, Constantes.ISPINCHGRABBING] == False) and (df.at[i, Constantes.ISPALMGRABBING]==False):
                    Condiciones[0]=True
            if Condiciones[0]:
                if (df.at[i, Constantes.ISPINCHGRABBING]) or (df.at[i, Constantes.ISPALMGRABBING]):
                    Condiciones[1]=True
            if Condiciones[0] and Condiciones[1]:
                if (mano_derecha and df.at[i, Constantes.HANDPOSITION_X]<mitad_caja) or (mano_derecha == False and df.at[i, Constantes.HANDPOSITION_X]>mitad_caja):
                    num_repeticion += 1
                    Condiciones = [False, False]
        if (df.at[i, Constantes.ISPINCHGRABBING] or df.at[i, Constantes.ISPALMGRABBING]) and primer_objeto_agarrado == False and inicio_ejercicio == False:
            primer_objeto_agarrado = True
            print(df.at[i, Constantes.FRAME])
            if df.at[i, Constantes.HANDPOSITION_X] > mitad_caja:
                mano_derecha = True
        if primer_objeto_agarrado:
            if (mano_derecha and df.at[i, Constantes.HANDPOSITION_X]<mitad_caja) or (mano_derecha == False and df.at[i, Constantes.HANDPOSITION_X]>mitad_caja):
                inicio_ejercicio = True
                primer_objeto_agarrado = False
                print(df.at[i, Constantes.HANDPOSITION_X])
                print(df.at[i, Constantes.FRAME])
        columna_repeticion.append(num_repeticion)
    if primer_objeto_agarrado:
        print("PRIMER OBJETO AGARRADO")
    if inicio_ejercicio:
        print("EJERCICIO INICIADO")
    if Condiciones[0] and Condiciones[1]:
        print("CONDICIONES CUMPLIDAS")
    df[Constantes.NUMREPETICION] = columna_repeticion
    return df


def tomarposicion_hmd(archivo:str):
    archivo = archivo.removeprefix('CSVs/OculusTracking_').removesuffix('.csv')
    df = pd.read_csv('CSVs/Historical.csv', encoding='UTF-8', sep=';', index_col=False)
    hmd_x = df[df['DATE']==archivo]['HMD_POSITION_X'].values[0]
    hmd_x = float(hmd_x.replace(',', '.'))
    return hmd_x

def representacion_handposition_por_repeticiones(df:pd.core.frame.DataFrame):
    ejes_verticales = []
    repeticion = 0
    ejes_verticales.append(0)
    for i in range(0, len(df)):
        if df.at[i, Constantes.NUMREPETICION]> repeticion:
            repeticion+=1
            ejes_verticales.append(i)
    print(ejes_verticales)


    vector = CalculoDatos.vectorizar(df[Constantes.HANDPOSITION_X],
                                     df[Constantes.HANDPOSITION_Y],
                                     df[Constantes.HANDPOSITION_Z])
    for line in ejes_verticales:
        plt.axvline(x=line, color='k', linestyle='--', label=f'X = {line:.2f}')

    plt.plot(vector)
    plt.title('Division por Repeticiones')
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid()
    plt.show()



