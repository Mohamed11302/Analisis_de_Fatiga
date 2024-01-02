# mi_script.py

import argparse
import Constantes.Configuracion as Config


parser = argparse.ArgumentParser(description='Argumentos Análisis de fatiga.')
parser.add_argument('--leer_de_oculus', type=int, help='Leer ficheros desde un directorio de oculus. 0: No, 1: Si.')
parser.add_argument('--directorio', type=str, help='Directorio donde están almacenados los ficheros.')

args = parser.parse_args()

if args.leer_de_oculus != None:
    Config.LEER_FICHEROS_OCULUS = bool(args.leer_de_oculus)
if args.directorio != None:
    Config.DIRECTORIO_UTILIZADO = args.directorio
elif Config.LEER_FICHEROS_OCULUS == True:
    Config.DIRECTORIO_UTILIZADO = Config.DIRECTORIO_FICHEROS_GENERADOS_OCULUS
elif Config.LEER_FICHEROS_OCULUS == False:
    Config.DIRECTORIO_UTILIZADO = Config.DIRECTORIO_FICHEROS_GENERADOS_LOCAL
print(f"Leer De Oculus: {Config.LEER_FICHEROS_OCULUS}")
print(f"Directorio: {Config.DIRECTORIO_UTILIZADO}")
