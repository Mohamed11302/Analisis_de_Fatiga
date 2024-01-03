import Constantes.Constantes as Const
import Constantes.Configuracion as Config
import IO.Leer_ficheros as Leer_ficheros
from Juegos.BBT import BBT
import IO.Escribir_Ficheros as Escribir_Ficheros
import subprocess
import shutil
import argparse
import Procesadores.ExtraerDatos as ExtraerDatos

def elegir_clase_juego(juego, df, porcentaje, nombre_intento, user):
    if juego == Const.JUEGO_BBT:
        myBBT = BBT(df, porcentaje, nombre_intento, user, False)
    return myBBT

def prerequisitos(user):
    prerequisitos_completados = True
    if shutil.which('adb') is None:
        print("Debes instalar adb y añadirlo al path en tu ordenador")
        prerequisitos_completados = False
    else:
        try:
            salida = subprocess.check_output(['adb', 'devices'], universal_newlines=True)
            lineas = salida.strip().split('\n')    
            if len(lineas) <= 1:
                print("El dispositivo de realidad virtual no esta conectado ")
                prerequisitos_completados = False
        except subprocess.CalledProcessError:
            print("Ha ocurrido un error el comando adb devices")
            prerequisitos_completados = False
    
    if prerequisitos_completados:
        try:
            ruta = Config.DIRECTORIO_UTILIZADO + user + "/" + Config.DIRECTORIO_HISTORICAL
            df = Leer_ficheros.leer_csv(ruta)
        except subprocess.CalledProcessError as e:
            print(f'Error al ejecutar el comando adb shell: {e}')
    return prerequisitos_completados

def obtener_primer_juego_comparacion(user, date):
    diccionario_df = {}
    ruta = Config.DIRECTORIO_UTILIZADO + user + "/" + Config.DIRECTORIO_HISTORICAL
    df_historico = Leer_ficheros.leer_csv(ruta)
    df_serie = Leer_ficheros.leercsv_serie(date, user)
    df_serie = ExtraerDatos.dividir_en_repeticiones(df_serie)
    es_mano_derecha = ExtraerDatos.mano_derecha(df_serie)
    df_historico = df_historico[df_historico[Const.HIST_DATE]<=date]
    i = len(df_historico)-1
    while len(diccionario_df)<Config.MAXIMO_FICHEROS_HISTORICOS and i>=0:
        df = Leer_ficheros.leercsv_serie(df_historico.at[i, Const.HIST_DATE], user)
        df = ExtraerDatos.dividir_en_repeticiones(df)
        mano = ExtraerDatos.mano_derecha(df_serie)
        if mano == es_mano_derecha:
            diccionario_df[df_historico.at[i, Const.HIST_DATE]] = df
        i = i-1
    diccionario_df[date] = df_serie ## Añadimos el dataframe de la serie que vamos a estudiar
    diccionario_df = dict(reversed(diccionario_df.items())) #Le damos la vuelta a las claves del diccionario para tenerlos ordenados
    return diccionario_df

def bucleBBT(juegos, user):
    lista_juegos = list(juegos.keys())
    if len(lista_juegos)>1:
        dates = lista_juegos[1:-1]
        myBBT = BBT(juegos[lista_juegos[0]], Config.PORCENTAJE_COMPARACION, lista_juegos[0], user, None)
        for date in dates:
            myBBT = BBT(juegos[date], Config.PORCENTAJE_COMPARACION, date, user, myBBT)
        myBBT = BBT(juegos[lista_juegos[-1]], Config.PORCENTAJE_COMPARACION, lista_juegos[-1], user, myBBT)
        myBBT.normalizar_datos()
        hijo = myBBT.hijo
        print(f"{myBBT.date} = {myBBT.fatiga_serie}")
        while hijo != None:
            print(f"{hijo.date} = {hijo.fatiga_serie}")
            hijo = hijo.hijo
    else:
        myBBT = BBT(juegos[lista_juegos[0]], Config.PORCENTAJE_COMPARACION, lista_juegos[0], user, None)
        print(myBBT.fatiga_serie)

def ejecutar_juego(nombre_intento, user, juego):
    print("Iniciando el cálculo de fatiga")
    df = Leer_ficheros.leercsv_serie(nombre_intento, user)
    juegos = obtener_primer_juego_comparacion(user, nombre_intento)
    bucleBBT(juegos, user)
    #mygame = elegir_clase_juego(juego, df, Config.PORCENTAJE_COMPARACION, nombre_intento, user)
    #print("Guardando resultados")
    #Escribir_Ficheros.generar_Salida(mygame) 

def obtener_argumentos_entrada():
    parser = argparse.ArgumentParser(description='Argumentos Análisis de fatiga.')
    parser.add_argument('--leer_oculus', type=int, help='Leer ficheros desde un directorio de oculus. 0: No, 1: Si.')
    parser.add_argument('--directorio', type=str, help='Directorio donde están almacenados los ficheros.')
    args = parser.parse_args()
    if args.leer_oculus != None:
        Config.LEER_FICHEROS_OCULUS = bool(args.leer_oculus)
    if args.directorio != None:
        Config.DIRECTORIO_UTILIZADO = args.directorio
    elif Config.LEER_FICHEROS_OCULUS == True:
        Config.DIRECTORIO_UTILIZADO = Config.DIRECTORIO_FICHEROS_GENERADOS_OCULUS
    elif Config.LEER_FICHEROS_OCULUS == False:
        Config.DIRECTORIO_UTILIZADO = Config.DIRECTORIO_FICHEROS_GENERADOS_LOCAL
def main():
    obtener_argumentos_entrada()
    #nombre_intento = "20231230_182344"
    #nombre_intento = "20231230_181725"
    #user = "siham"
    nombre_intento = "20231226_205101"
    user = "default"
    juego = Const.JUEGO_BBT
    if Config.LEER_FICHEROS_OCULUS:
        if prerequisitos(user):
            print("Prerequisitos completados")
            ejecutar_juego(nombre_intento, user, juego)
        else:
            print("Faltan prerequisitos por completar")
    else:
        ejecutar_juego(nombre_intento, user, juego)
        
    
if __name__ == "__main__":
    main()

