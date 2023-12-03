import pandas as pd
import matplotlib.pyplot as plt
import Constantes
import CalculoDatos


def sustituir_comas(df:pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    columnas_a_seleccionar = df.select_dtypes(exclude=['int', 'bool']).columns
    df[columnas_a_seleccionar] = df[columnas_a_seleccionar].applymap(lambda x:
                                        float(str(x).replace(',', '.')) if pd.notnull(x) else x)
    return df

def leercsv(archivo_csv: str) -> pd.core.frame.DataFrame:
    df = pd.read_csv(archivo_csv, encoding='UTF-8', sep=';', index_col=False)
    df = sustituir_comas(df)
    return df

def escribircsv(df:pd.core.frame.DataFrame):
    df.to_csv('OculusTracking_modificado.csv', sep=";", decimal=',')

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


def dividir_en_repeticiones_2(df: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    primer_objeto_agarrado = False
    inicio_ejercicio = False
    num_repeticion = 1
    mano_derecha = False
    Condiciones = [False, False] #1º ESPERAR HASTA QUE SUELTES EL BLOQUE 2º ESPERAR HASTA QUE COJAS OTRO BLOQUE
    columna_repeticion = []
    for i in range(0, len(df)):
        if inicio_ejercicio:
            if Condiciones[0] == False:
                if (df.at[i, Constantes.ISPINCHGRABBING] == False) and (df.at[i, Constantes.ISPALMGRABBING]==False):
                    Condiciones[0]=True
                    print(df.at[i, Constantes.FRAME])
            if Condiciones[0]:
                if (df.at[i, Constantes.ISPINCHGRABBING]) or (df.at[i, Constantes.ISPALMGRABBING]):
                    Condiciones[1]=True
                    print(df.at[i, Constantes.FRAME])
            if Condiciones[0] and Condiciones[1]:
                if (mano_derecha and df.at[i, Constantes.HANDPOSITION_X]<0) or (mano_derecha == False and df.at[i, Constantes.HANDPOSITION_X]>0):
                    print(df.at[i, Constantes.FRAME])
                    num_repeticion += 1
                    print(num_repeticion)
                    Condiciones = [False, False]
        if (df.at[i, Constantes.ISPINCHGRABBING] or df.at[i, Constantes.ISPALMGRABBING]) and primer_objeto_agarrado == False and inicio_ejercicio == False:
            primer_objeto_agarrado = True
            if df.at[i, Constantes.HANDPOSITION_X] > 0:
                mano_derecha = True
                print(df.at[i, Constantes.FRAME])
        if primer_objeto_agarrado:
            if (mano_derecha and df.at[i, Constantes.HANDPOSITION_X]<0) or (mano_derecha == False and df.at[i, Constantes.HANDPOSITION_X]>0):
                inicio_ejercicio = True
                primer_objeto_agarrado = False
                print(df.at[i, Constantes.FRAME])
        
        columna_repeticion.append(num_repeticion)
    df[Constantes.NUMREPETICION] = columna_repeticion
    return df

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



