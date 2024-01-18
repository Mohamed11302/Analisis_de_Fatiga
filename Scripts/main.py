import argparse

import auxiliares as aux
import Constantes.Constantes as Const
import Constantes.Configuracion as Config
import IO.Escribir_Ficheros as Escribir_Ficheros
import pre_requisitos
from Juegos.BBT import bucleBBT





def obtener_argumentos_entrada():
    parser = argparse.ArgumentParser(description='Fatigue analyzation arguments.')
    parser.add_argument('--user', type=str,required=True, help='User name.')
    parser.add_argument('--date', type=str,required=True, help='Date of the exercise with format: YYYYMMDD_HHMMSS.')
    parser.add_argument('--leer_oculus', type=int, help='Read files from oculus. 0: No, 1: Yes.')
    parser.add_argument('--directorio', type=str, help='Main directory of saved files from Rehab-Immersive.')
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
        if pre_requisitos.prerequisitos(user):
            print("Prerequisites completed")
            ejecutar_juego(date, user, juego)
        else:
            print("Please, complete the prerequisites and try again.")
    else:
        ejecutar_juego(date, user, juego)
        
    
if __name__ == "__main__":
    main()

