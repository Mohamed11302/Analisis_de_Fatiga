import Tratamiento_CSV
import CalculoFatigas


def main():
    archivo = 'OculusTracking_20230928_135634.csv'
    porcentaje = 30
    df = Tratamiento_CSV.leercsv(archivo)
    df1 = Tratamiento_CSV.dividir_en_repeticiones(df)

    fatiga = CalculoFatigas.indice_fatiga(df1, porcentaje)
    Tratamiento_CSV.escribircsv(df1)
    #CalculoFatigas.representar_fatiga(fatiga, porcentaje)
    #CalculoDatos.datos_posicion_cabeza_por_repeticion(df, 2, 5)
    CalculoFatigas.ValorUnicoFatiga(fatiga)

    CalculoFatigas.mediahistorica(df1)

if __name__ == "__main__":
    main()
