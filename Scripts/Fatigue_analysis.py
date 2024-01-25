import argparse

import Utils.auxiliares as aux
import Constantes.Constantes as Const
import Constantes.Configuracion as Config
import IO.Escribir_Ficheros as Escribir_Ficheros
import Utils.pre_requisitos as pre_requisitos
from Fatigue_Games.BBT import bucleBBT





def obtener_argumentos_entrada():
    parser = argparse.ArgumentParser(description='Fatigue analyzation arguments.')
    parser.add_argument('--user', type=str,required=True, help='User name.')
    parser.add_argument('--date', type=str,required=True, help='Date of the exercise with format: YYYYMMDD_HHMMSS.')
    parser.add_argument('--read_oculus', type=int, help='Read files from oculus. 0: No, 1: Yes.')
    parser.add_argument('--directory', type=str, help='Main directory of saved files from Rehab-Immersive.')
    args = parser.parse_args()
    return args.user, args.date, args.read_oculus, args.directory

def asignar_argumentos(read_oculus, directory):
    if read_oculus != None:
        Config.LEER_FICHEROS_OCULUS = bool(read_oculus)
    if directory != None:
        Config.DIRECTORIO_UTILIZADO = directory
    elif Config.LEER_FICHEROS_OCULUS == True:
        Config.DIRECTORIO_UTILIZADO = Config.DIRECTORIO_FICHEROS_GENERADOS_OCULUS
    elif Config.LEER_FICHEROS_OCULUS == False:
        Config.DIRECTORIO_UTILIZADO = Config.DIRECTORIO_FICHEROS_GENERADOS_LOCAL
    Config.DIRECTORIO_UTILIZADO +="/"


def ejecutar_juego(nombre_intento, user, juego):
    print(f"Starting fatigue calculation for user {user}")
    juegos = aux.obtener_historico(user, nombre_intento)
    if juego == Const.JUEGO_BBT:
        mygame = bucleBBT(juegos, user)
    print("Saving results")
    json_output = Escribir_Ficheros.generar_salida(mygame) 
    print("Concluding program...")
    return json_output


def main(user, date, read_oculus, directory):
    try:
        asignar_argumentos(read_oculus, directory)
        juego = Const.JUEGO_BBT
        
        if Config.LEER_FICHEROS_OCULUS:
            if pre_requisitos.prerequisitos(user):
                print("Prerequisites completed")
                json_output = ejecutar_juego(date, user, juego)
            else:
                raise RuntimeError("Please, complete the prerequisites and try again.")
        else:
            json_output = ejecutar_juego(date, user, juego)
        return json_output
    except: 
        print("Something went wrong")
        
    
if __name__ == "__main__":
    user, date, read_oculus, directory = obtener_argumentos_entrada()
    main(user, date, read_oculus, directory)

