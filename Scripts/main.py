import Constantes.Constantes as Const
import Constantes.Configuracion as Config
import IO.Leer_ficheros as Leer_ficheros
from Juegos.BBT import BBT
import IO.Escribir_Ficheros as Escribir_Ficheros
import subprocess
import shutil



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

def main():
    #nombre_intento = "20231230_182344"
    #nombre_intento = "20231230_181725"
    #user = "siham"
    nombre_intento = "20231226_205101"
    user = "default"
    juego = Const.JUEGO_BBT
    if Config.LEER_FICHEROS_OCULUS:
        Config.DIRECTORIO_UTILIZADO = Config.DIRECTORIO_FICHEROS_GENERADOS_OCULUS
        if prerequisitos(user):
            print("Prerequisitos completados")
            print("Iniciando el cálculo de fatiga")
            df = Leer_ficheros.leercsv_serie(nombre_intento, user)
            mygame = elegir_clase_juego(juego, df, Config.PORCENTAJE_COMPARACION, nombre_intento, user)
            print("Guardando resultados")
            Escribir_Ficheros.generar_Salida(mygame) 
            mygame.dataframe.to_csv("prueba4.csv", sep=";")
        else:
            print("Faltan prerequisitos por completar")
    else:
            Config.DIRECTORIO_UTILIZADO = Config.DIRECTORIO_FICHEROS_GENERADOS_LOCAL
            print("Iniciando el cálculo de fatiga")
            df = Leer_ficheros.leercsv_serie(nombre_intento, user)
            mygame = elegir_clase_juego(juego, df, Config.PORCENTAJE_COMPARACION, nombre_intento, user)
            print("Guardando resultados")
            Escribir_Ficheros.generar_Salida(mygame) 
        
    
if __name__ == "__main__":
    main()

