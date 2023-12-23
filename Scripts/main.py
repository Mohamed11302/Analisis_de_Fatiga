import Tratamiento_CSV
import CalculoFatigas
import fichero_salida

def main():
    ### DATOS DE INICIO
    ruta = 'CSVs/TrackingData/OculusTracking_20231216_120552.csv'
    user = "default"
    porcentaje = 30

    df = Tratamiento_CSV.leercsv(ruta)
    df1 = Tratamiento_CSV.dividir_en_repeticiones(df)
    preprocesado_fatiga  = CalculoFatigas.preprocesado_indice_fatiga(df1, porcentaje, user)
    fatiga_por_repeticion = CalculoFatigas.CalcularFatiga_PorRepeticion(preprocesado_fatiga)
    fatiga_serie = CalculoFatigas.CalcularFatiga_Serie(fatiga_por_repeticion)
    print(fatiga_serie)

    ### SALIDA    
    fichero_salida.comprobar_y_crear_carpeta()
    ruta_json = fichero_salida.crear_ruta_json(ruta, user)
    fichero_salida.modificar_json_output(ruta_json, preprocesado_fatiga, fatiga_por_repeticion)
    fichero_salida.modificar_csv_output(user, ruta_json, fatiga_serie)

if __name__ == "__main__":
    main()
