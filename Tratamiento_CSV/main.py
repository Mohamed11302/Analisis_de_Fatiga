import Tratamiento_CSV
import CalculoFatigas
import Constantes
import fichero_salida
def main():
    ruta = 'CSVs/OculusTracking_20231203_193853.csv'
    user = "default"
    porcentaje = 30
    df = Tratamiento_CSV.leercsv(ruta)
    df1 = Tratamiento_CSV.dividir_en_repeticiones(df)

    fichero_salida.comprobar_y_crear_carpeta()
    preprocesado_fatiga  = CalculoFatigas.preprocesado_indice_fatiga(df1, porcentaje)
    ruta_json = fichero_salida.crear_ruta_json(ruta, user)
    fatiga_por_repeticion = CalculoFatigas.CalcularFatiga_PorRepeticion(preprocesado_fatiga)
    fatiga_serie = CalculoFatigas.CalcularFatiga_Serie(fatiga_por_repeticion)
    fichero_salida.modificar_json_output(ruta_json, preprocesado_fatiga)
    fichero_salida.modificar_csv_output(user, ruta_json, fatiga_serie)
if __name__ == "__main__":
    main()
