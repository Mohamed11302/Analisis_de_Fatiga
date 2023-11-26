import pandas as pd
import matplotlib.pyplot as plt
import Variables_Globales
import CalculoDatos
import CalculoFatigas
def sustituir_comas(df:pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    columnas_a_seleccionar = df.select_dtypes(exclude=['int', 'bool']).columns
    df[columnas_a_seleccionar] = df[columnas_a_seleccionar].applymap(lambda x:
                                        float(str(x).replace(',', '.')) if pd.notnull(x) else x)
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
        if (df.at[i, Variables_Globales.ISPINCHGRABBING] == True) and agarrando_objeto == False:
            num_repeticion += 1
            agarrando_objeto = True
        elif (df.at[i, Variables_Globales.ISPINCHGRABBING] == False) and agarrando_objeto == True:
            agarrando_objeto = False
        columna_repeticion.append(num_repeticion)
    df[Variables_Globales.NUMREPETICION] = columna_repeticion
    return df

def representacion_handposition_por_repeticiones(df:pd.core.frame.DataFrame):
    ejes_verticales = []
    repeticion = 0
    ejes_verticales.append(0)
    for i in range(0, len(df)):
        if df.at[i, Variables_Globales.NUMREPETICION]> repeticion:
            repeticion+=1
            ejes_verticales.append(i)
    print(ejes_verticales)


    vector = CalculoDatos.vectorizar(df[Variables_Globales.HANDPOSITION_X],
                                     df[Variables_Globales.HANDPOSITION_Y],
                                     df[Variables_Globales.HANDPOSITION_Z])
    for line in ejes_verticales:
        plt.axvline(x=line, color='k', linestyle='--', label=f'X = {line:.2f}')

    plt.plot(vector)
    plt.title('Division por Repeticiones')
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid()
    plt.show()



def ponderacion_owa_fatiga(fatigas) -> float:
    CalculoFatigas.reweighting(fatigas)
    fatiga = (fatigas[Variables_Globales.FATIGA_TIEMPO] * Variables_Globales.OWA_TIEMPO + 
              fatigas[Variables_Globales.FATIGA_STRENGTH] * Variables_Globales.OWA_STRENGTH + 
              fatigas[Variables_Globales.FATIGA_VELOCIDAD] * Variables_Globales.OWA_VELOCIDAD + 
              fatigas[Variables_Globales.FATIGA_HEADPOSITION] * Variables_Globales.OWA_HEADPOSITION + 
              fatigas[Variables_Globales.FATIGA_CURVATURA_MANO] * Variables_Globales.OWA_CURVATURA_MANO
            )
    return fatiga

def indice_fatiga(df:pd.core.frame.DataFrame, porcentaje:int):
    _datos_iniciales_paciente = CalculoDatos.datos_iniciales_paciente(df, porcentaje)
    datos_paciente = CalculoDatos.obtener_datos_paciente(df, 2, _datos_iniciales_paciente['NUM_REP'])
    fatiga = []
    for repeticion in range(0, len(datos_paciente[Variables_Globales.FATIGA_TIEMPO])):
        fatigas = {
            Variables_Globales.FATIGA_TIEMPO : CalculoFatigas.fatiga_calculo_general(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Variables_Globales.FATIGA_TIEMPO], datos_paciente[Variables_Globales.FATIGA_TIEMPO][repeticion], Variables_Globales.FATIGA_TIEMPO),
            Variables_Globales.FATIGA_STRENGTH : CalculoFatigas.fatiga_calculo_general(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Variables_Globales.FATIGA_STRENGTH], datos_paciente[Variables_Globales.FATIGA_STRENGTH][repeticion], Variables_Globales.FATIGA_STRENGTH),
            Variables_Globales.FATIGA_VELOCIDAD : CalculoFatigas.fatiga_calculo_general(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Variables_Globales.FATIGA_VELOCIDAD], datos_paciente[Variables_Globales.FATIGA_VELOCIDAD][repeticion], Variables_Globales.FATIGA_VELOCIDAD),
            Variables_Globales.FATIGA_HEADPOSITION : CalculoFatigas.fatiga_calculo_headposition(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Variables_Globales.FATIGA_HEADPOSITION], datos_paciente[Variables_Globales.FATIGA_HEADPOSITION], repeticion, df),
            Variables_Globales.FATIGA_CURVATURA_MANO : CalculoFatigas.fatiga_calculo_curvatura_mano(_datos_iniciales_paciente['DATOS_INICIALES_PACIENTE'][Variables_Globales.FATIGA_CURVATURA_MANO], datos_paciente[Variables_Globales.FATIGA_CURVATURA_MANO], repeticion)
        }
        f = ponderacion_owa_fatiga(fatigas)
        fatiga.append(round(f, 3))
    
    print(fatiga)
    repeticiones = list(range(len(datos_paciente[Variables_Globales.FATIGA_TIEMPO])))
    plt.bar(repeticiones, fatiga)
    plt.title('FATIGA CON '+str(porcentaje)+str('%'))
    plt.show()

def main():
    archivo = 'OculusTracking_20230928_135634.csv'
    df = leercsv(archivo)
    df = dividir_en_repeticiones(df)
    #df.to_csv('Tratamiento_CSV/OculusTracking_modificado.csv', sep=";")
    indice_fatiga(df, 30)
    #CalculoDatos.datos_posicion_cabeza_por_repeticion(df, 2, 5)

if __name__ == '__main__':
    main()
