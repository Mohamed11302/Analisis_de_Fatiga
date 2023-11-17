import pandas as pd
import matplotlib.pyplot as plt
from Variables_Globales import *
from CalculoDatos import *
from CalculoFatigas import *
import numpy as np
def SustituirComas(df:pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    columnas_a_seleccionar = df.select_dtypes(exclude=['int', 'bool']).columns
    df[columnas_a_seleccionar] = df[columnas_a_seleccionar].map(lambda x: float(str(x).replace(',', '.')) if pd.notnull(x) else x)
    return df

def leercsv(archivo_csv: str) -> pd.core.frame.DataFrame:
    df = pd.read_csv(archivo_csv, encoding='UTF-8', sep=';', index_col=False)
    df = SustituirComas(df)
    return df


def Dividir_Repeticiones(df: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    agarrando_objeto = False
    num_repeticion = 1
    columna_repeticion = []
    for i in range(0, len(df)):
        columna_repeticion.append(num_repeticion)
        if (df.at[i, ISPINCHGRABBING] == True) and agarrando_objeto == False:
            num_repeticion += 1
            agarrando_objeto = True
        elif (df.at[i, ISPINCHGRABBING] == False) and agarrando_objeto == True:
            agarrando_objeto = False
    df[NUMREPETICION] = columna_repeticion
    return df

def representacion_por_repeticiones(df:pd.core.frame.DataFrame):
    ejes_verticales = []
    repeticion = 0
    ejes_verticales.append(0)
    for i in range(0, len(df)):
        if df.at[i, NUMREPETICION]> repeticion:
            repeticion+=1
            ejes_verticales.append(i)
    print(ejes_verticales)
    
    
    vector = vectorizar(df[HANDPOSITION_X],df[HANDPOSITION_Y], df[HANDPOSITION_Z])
    for line in ejes_verticales:
        plt.axvline(x=line, color='k', linestyle='--', label=f'X = {line:.2f}')
    
    plt.plot(vector) 
    #plt.xlabel('X')
    #plt.ylabel('Y')
    plt.title('Division por Repeticiones')
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid()
    plt.show()

def ObtenerDatos_Paciente(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int):
    fatiga_wristTwist = Datos_WristTwistPR(df, inicio_rep, final_rep)
    fatiga_strength = Datos_StrengthPR(df, inicio_rep, final_rep)
    fatiga_tiempo = Datos_TiempoPR(df, inicio_rep, final_rep)
    fatiga_velocidad = Datos_VelocidadPR(df, inicio_rep, final_rep)
    return fatiga_wristTwist, fatiga_strength, fatiga_tiempo, fatiga_velocidad

def Datos_Iniciales_Paciente(df:pd.core.frame.DataFrame, porcentaje: int)->dict:
    INICIO_REPES = 1
    datos_iniciales_paciente ={}
    num_repeticiones = df[NUMREPETICION].max()
    num_rep_iniciales = round(num_repeticiones * (porcentaje/100))
    fatiga_wristTwist, fatiga_strength, fatiga_tiempo, fatiga_velocidad = ObtenerDatos_Paciente(df, INICIO_REPES, INICIO_REPES+num_rep_iniciales)

    datos_iniciales_paciente[FATIGA_WRIST] = round(sum(fatiga_wristTwist)/len(fatiga_wristTwist), 3)
    datos_iniciales_paciente[FATIGA_STRENGTH] = round(sum(fatiga_strength)/len(fatiga_strength), 3)
    datos_iniciales_paciente[FATIGA_TIEMPO] = round(sum(fatiga_tiempo)/len(fatiga_tiempo), 3)
    datos_iniciales_paciente[FATIGA_VELOCIDAD] = round(sum(fatiga_velocidad)/len(fatiga_velocidad), 3)
    print(datos_iniciales_paciente)
    return num_rep_iniciales, num_repeticiones, datos_iniciales_paciente

def CalcularFatiga(df:pd.core.frame.DataFrame, porcentaje:int):
    num_rep_iniciales_fatiga, num_rep_finales_fatiga, datos_iniciales_paciente = Datos_Iniciales_Paciente(df, porcentaje)
    fatiga_wristTwist, fatiga_strength, fatiga_tiempo, fatiga_velocidad = ObtenerDatos_Paciente(df, num_rep_iniciales_fatiga, num_rep_finales_fatiga)
    cont_fatiga = 0
    for i in range(0, len(fatiga_tiempo)):
        print(str(i+num_rep_iniciales_fatiga) + ": " +str(datos_iniciales_paciente[FATIGA_TIEMPO]) + "-" + str(fatiga_tiempo[i]))
        if datos_iniciales_paciente[FATIGA_TIEMPO]<fatiga_tiempo[i]:
            cont_fatiga += 1
        if datos_iniciales_paciente[FATIGA_VELOCIDAD]>fatiga_velocidad[i]:
            cont_fatiga += 1
        if datos_iniciales_paciente[FATIGA_STRENGTH]>fatiga_strength[i]:
            cont_fatiga += 1
        if cont_fatiga>1:
            print("FATIGA EN " + str(i+num_rep_iniciales_fatiga))
            pass
        cont_fatiga = 0
    
def Prueba(df:pd.core.frame.DataFrame, porcentaje:int):
    num_rep_iniciales_fatiga, num_rep_finales_fatiga, datos_iniciales_paciente = Datos_Iniciales_Paciente(df, porcentaje)
    fatiga_wristTwist, fatiga_strength, fatiga_tiempo, fatiga_velocidad = ObtenerDatos_Paciente(df, num_rep_iniciales_fatiga, num_rep_finales_fatiga)
    cont_fatiga = 0
    fatiga = []
    for i in range(0, len(fatiga_tiempo)):
        f_tiempo = Fatiga_Calculo(datos_iniciales_paciente[FATIGA_TIEMPO], fatiga_tiempo[i], FATIGA_TIEMPO)
        f_strength = Fatiga_Calculo(datos_iniciales_paciente[FATIGA_STRENGTH], fatiga_strength[i], FATIGA_STRENGTH)
        f_velocidad = Fatiga_Calculo(datos_iniciales_paciente[FATIGA_VELOCIDAD], fatiga_velocidad[i], FATIGA_VELOCIDAD)
        f = f_tiempo * 0.3 + f_strength * 0.3 + f_velocidad * 0.3
        fatiga.append(f)
    
    print(fatiga)
    plt.plot(fatiga)
    plt.show()

def main():
    archivo = 'OculusTracking_20230928_135634.csv'
    df = leercsv(archivo)
    df = Dividir_Repeticiones(df)
    Prueba(df, 30)

if __name__ == '__main__':
    main()
