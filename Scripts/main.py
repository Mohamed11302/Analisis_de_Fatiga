import Constantes.Constantes as Const
import Constantes.Configuracion as Config
import IO.Leer_ficheros as Leer_ficheros
from Juegos.BBT import BBT, bucleBBT
import IO.Escribir_Ficheros as Escribir_Ficheros
import subprocess
import shutil
import argparse
import auxiliares as aux

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

def obtener_argumentos_entrada():
    parser = argparse.ArgumentParser(description='Argumentos Análisis de fatiga.')
    parser.add_argument('--user', type=str,required=True, help='Nombre del usuario que quieres analizar.')
    parser.add_argument('--date', type=str,required=True, help='Fecha en la que se realizó el ejercicio.')
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
    return args.user, args.date


def ejecutar_juego(nombre_intento, user, juego):
    print(f"Starting fatigue calculation for user {user}")
    juegos = aux.obtener_historico(user, nombre_intento)
    if juego == Const.JUEGO_BBT:
        mygame = bucleBBT(juegos, user)
    print("Saving results")
    Escribir_Ficheros.generar_salida(mygame) 
    print("Concluding program...")


def main():
    user, date = obtener_argumentos_entrada()
    juego = Const.JUEGO_BBT
    #nombre_intento = "20231230_182344"
    #user = "siham"
    #nombre_intento = "20231226_204637"
    #user = "default"
    #nombre_intento = "20240116_164720"
    #user = "miguel"
    #nombre_intento = "20240116_184911"
    #user = "raul"
    
    if Config.LEER_FICHEROS_OCULUS:
        if prerequisitos(user):
            print("Prerequisitos completados")
            ejecutar_juego(date, user, juego)
        else:
            print("Faltan prerequisitos por completar")
    else:
        ejecutar_juego(date, user, juego)
        
    
if __name__ == "__main__":
    main()

