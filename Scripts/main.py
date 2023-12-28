import pandas as pd
import Constantes as Const
import Tratamiento_CSV
from BBT import BBT
import fichero_salida



def elegir_clase_juego(juego, df, porcentaje, nombre_intento):
    if juego == Const.JUEGO_BBT:
        myBBT = BBT(df, 30, nombre_intento, False)
    return myBBT
    
def main():
    nombre_intento = "20231226_204929"
    porcentaje = 20
    df = Tratamiento_CSV.leercsv(nombre_intento)
    juego, user = Tratamiento_CSV.obtener_juego_y_user(nombre_intento)
    mygame = elegir_clase_juego(juego, df, porcentaje, nombre_intento)
    fichero_salida.generar_Salida(user, mygame)
    
if __name__ == "__main__":
    main()

