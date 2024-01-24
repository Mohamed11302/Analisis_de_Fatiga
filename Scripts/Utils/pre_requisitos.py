import subprocess
import shutil
import Constantes.Configuracion as Config
import IO.Leer_ficheros as Leer_ficheros


def prerequisitos(user):
    prerequisitos_completados = True
    if shutil.which('adb') is None:
        print("Install adb and add to environment paths")
        prerequisitos_completados = False
    else:
        try:
            salida = subprocess.check_output(['adb', 'devices'], universal_newlines=True)
            lineas = salida.strip().split('\n')    
            if len(lineas) <= 1:
                print("VR device is not connected")
                prerequisitos_completados = False
        except subprocess.CalledProcessError:
            print("Error executing: adb devices")
            prerequisitos_completados = False
    
    if prerequisitos_completados:
        try:
            ruta = Config.DIRECTORIO_UTILIZADO + user + "/" + Config.DIRECTORIO_HISTORICAL
            df = Leer_ficheros.leer_csv(ruta)
        except subprocess.CalledProcessError as e:
            print(f'Error executing adb shell: {e}')
    return prerequisitos_completados