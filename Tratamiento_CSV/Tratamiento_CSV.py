import pandas as pd
import matplotlib.pyplot as plt
import Variables_Globales
import CalculoDatos
import CalculoFatigas
def sustituir_comas(df:pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    columnas_a_seleccionar = df.select_dtypes(exclude=['int', 'bool']).columns
    df[columnas_a_seleccionar] = df[columnas_a_seleccionar].applymap(lambda x: float(str(x).replace(',', '.')) if pd.notnull(x) else x)
    return df

def leercsv(archivo_csv: str) -> pd.core.frame.DataFrame:
    df = pd.read_csv(archivo_csv, encoding='UTF-8', sep=';', index_col=False)
    df = sustituir_comas(df)
    return df


def dividir_en_repeticiones(df: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    agarrando_objeto = False
    num_repeticion = 1
    columna_repeticion = []
    for i in range(0, len(df)):
        columna_repeticion.append(num_repeticion)
        if (df.at[i, Variables_Globales.ISPINCHGRABBING] == True) and agarrando_objeto == False:
            num_repeticion += 1
            agarrando_objeto = True
        elif (df.at[i, Variables_Globales.ISPINCHGRABBING] == False) and agarrando_objeto == True:
            agarrando_objeto = False
    df[Variables_Globales.NUMREPETICION] = columna_repeticion
    return df

def representacion_por_repeticiones(df:pd.core.frame.DataFrame):
    ejes_verticales = []
    repeticion = 0
    ejes_verticales.append(0)
    for i in range(0, len(df)):
        if df.at[i, Variables_Globales.NUMREPETICION]> repeticion:
            repeticion+=1
            ejes_verticales.append(i)
    print(ejes_verticales)
    
    
    vector = CalculoDatos.vectorizar(df[Variables_Globales.HANDPOSITION_X],df[Variables_Globales.HANDPOSITION_Y], df[Variables_Globales.HANDPOSITION_Z])
    for line in ejes_verticales:
        plt.axvline(x=line, color='k', linestyle='--', label=f'X = {line:.2f}')
    
    plt.plot(vector) 
    plt.title('Division por Repeticiones')
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid()
    plt.show()

def obtener_datos_paciente(df:pd.core.frame.DataFrame, inicio_rep:int, final_rep:int) -> dict:
    fatiga_wrist_twist = CalculoDatos.datos_flexion_muneca_por_repeticion(df, inicio_rep, final_rep)
    fatiga_strength = CalculoDatos.datos_fuerza_por_repeticion(df, inicio_rep, final_rep)
    fatiga_tiempo = CalculoDatos.datos_tiempo_por_repeticion(df, inicio_rep, final_rep)
    fatiga_velocidad = CalculoDatos.datos_velocidad_por_repeticion(df, inicio_rep, final_rep)
    fatiga_headposition = CalculoDatos.datos_posicion_cabeza_por_repeticion(df, inicio_rep, final_rep)
    datos_paciente = {
        Variables_Globales.FATIGA_WRIST : fatiga_wrist_twist,
        Variables_Globales.FATIGA_STRENGTH : fatiga_strength,
        Variables_Globales.FATIGA_TIEMPO : fatiga_tiempo,
        Variables_Globales.FATIGA_VELOCIDAD : fatiga_velocidad,
        Variables_Globales.FATIGA_HEADPOSITION : fatiga_headposition
    }
    return datos_paciente

def datos_iniciales_paciente(df:pd.core.frame.DataFrame, porcentaje: int)->dict:
    INICIO_REPES = 1
    datos_iniciales_paciente ={}
    num_repeticiones = df[Variables_Globales.NUMREPETICION].max()
    num_rep_iniciales = round(num_repeticiones * (porcentaje/100))
    _datos_paciente = obtener_datos_paciente(df, INICIO_REPES, INICIO_REPES+num_rep_iniciales)
    fatiga_headposition = CalculoDatos.media_datos_posicion_cabeza(_datos_paciente[Variables_Globales.FATIGA_HEADPOSITION])
    datos_iniciales_paciente[Variables_Globales.FATIGA_WRIST] = round(sum(_datos_paciente[Variables_Globales.FATIGA_WRIST])/len(_datos_paciente[Variables_Globales.FATIGA_WRIST]), 3)
    datos_iniciales_paciente[Variables_Globales.FATIGA_STRENGTH] = round(sum(_datos_paciente[Variables_Globales.FATIGA_STRENGTH])/len(_datos_paciente[Variables_Globales.FATIGA_STRENGTH]), 3)
    datos_iniciales_paciente[Variables_Globales.FATIGA_TIEMPO] = round(sum(_datos_paciente[Variables_Globales.FATIGA_TIEMPO])/len(_datos_paciente[Variables_Globales.FATIGA_TIEMPO]), 3)
    datos_iniciales_paciente[Variables_Globales.FATIGA_VELOCIDAD] = round(sum(_datos_paciente[Variables_Globales.FATIGA_VELOCIDAD])/len(_datos_paciente[Variables_Globales.FATIGA_VELOCIDAD]), 3)
    datos_iniciales_paciente[Variables_Globales.MAX_HP_X] = fatiga_headposition[Variables_Globales.MAX_HP_X]
    datos_iniciales_paciente[Variables_Globales.MIN_HP_X] = fatiga_headposition[Variables_Globales.MIN_HP_X]
    datos_iniciales_paciente[Variables_Globales.MAX_HP_Y] = fatiga_headposition[Variables_Globales.MAX_HP_Y]
    datos_iniciales_paciente[Variables_Globales.MIN_HP_Y] = fatiga_headposition[Variables_Globales.MIN_HP_Y]
    datos_iniciales_paciente[Variables_Globales.MAX_HP_Z] = fatiga_headposition[Variables_Globales.MAX_HP_Z]
    datos_iniciales_paciente[Variables_Globales.MIN_HP_Z] = fatiga_headposition[Variables_Globales.MIN_HP_Z]

    datos_iniciales_paciente = {
        'NUM_REP_INICIALES' : num_rep_iniciales,
        'NUM_REP' : num_repeticiones,
        'DATOS_INICIALES_PACIENTE' : datos_iniciales_paciente
    }
    return datos_iniciales_paciente

def ponderacion_owa_fatiga(fatigas) -> float:
    CalculoFatigas.reweighting(fatigas)
    fatiga = fatigas[Variables_Globales.FATIGA_TIEMPO] * Variables_Globales.OWA_TIEMPO + fatigas[Variables_Globales.FATIGA_STRENGTH] * Variables_Globales.OWA_STRENGTH + fatigas[Variables_Globales.FATIGA_VELOCIDAD] * Variables_Globales.OWA_VELOCIDAD + fatigas[Variables_Globales.FATIGA_HEADPOSITION] * Variables_Globales.OWA_HEADPOSITION
    return fatiga

def indice_fatiga(df:pd.core.frame.DataFrame, porcentaje:int):
    _datos_iniciales_paciente = datos_iniciales_paciente(df, porcentaje)
    datos_paciente = obtener_datos_paciente(df, 1, _datos_iniciales_paciente['NUM_REP'])
    fatiga = []
    for i in range(0, len(datos_paciente[Variables_Globales.FATIGA_TIEMPO])):
        fatigas = {
            Variables_Globales.FATIGA_TIEMPO : CalculoFatigas.fatiga_calculo(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Variables_Globales.FATIGA_TIEMPO], datos_paciente[Variables_Globales.FATIGA_TIEMPO][i], Variables_Globales.FATIGA_TIEMPO),
            Variables_Globales.FATIGA_STRENGTH : CalculoFatigas.fatiga_calculo(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Variables_Globales.FATIGA_STRENGTH], datos_paciente[Variables_Globales.FATIGA_STRENGTH][i], Variables_Globales.FATIGA_STRENGTH),
            Variables_Globales.FATIGA_VELOCIDAD : CalculoFatigas.fatiga_calculo(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Variables_Globales.FATIGA_VELOCIDAD], datos_paciente[Variables_Globales.FATIGA_VELOCIDAD][i], Variables_Globales.FATIGA_VELOCIDAD),
            Variables_Globales.FATIGA_HEADPOSITION : CalculoFatigas.fatiga_calculo_headposition(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'], datos_paciente[Variables_Globales.FATIGA_HEADPOSITION], i, df)
        }
        f = ponderacion_owa_fatiga(fatigas)
        fatiga.append(round(f, 3))
    
    print(fatiga)
    plt.plot(fatiga)
    plt.title('FATIGA CON '+str(porcentaje)+str('%'))
    plt.show()

def main():
    archivo = 'OculusTracking_20230928_135634.csv'
    df = leercsv(archivo)
    df = dividir_en_repeticiones(df)
    indice_fatiga(df, 30)

if __name__ == '__main__':
    main()
