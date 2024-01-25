from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
import json


clips = []
def crear_clip_de_texto(inicio, fin, mensaje):
    # Crear un clip de texto con un tamaño de fuente más pequeño y centrado
    clip = TextClip(mensaje, fontsize=30, color='black', align='center').set_duration(fin - inicio).set_start(inicio).set_position('center')
    # Almacenar el clip en la lista global
    clips.append(clip)


def dividir_cadena(cadena, max_caracteres=40):
    palabras = cadena.split()
    lineas = []
    linea_actual = palabras[0]

    for palabra in palabras[1:]:
        if len(linea_actual + ' ' + palabra) <= max_caracteres:
            linea_actual += ' ' + palabra
        else:
            lineas.append(linea_actual)
            linea_actual = palabra

    # Agregar la última línea
    lineas.append(linea_actual)

    return '\n'.join(lineas)



def crear_clips(datos):
    for repeticion in range(0, len(datos['Repetitions'])-1):
        cadena = ""
        for warning in datos['Repetitions'][repeticion]['Fatigue warnings']:
            cadena += "* " +  dividir_cadena(warning) +"\n"
        if cadena == "":
            cadena = "No fatigue errors"
        #print(cadena)
        crear_clip_de_texto(datos['Repetitions'][repeticion]['Inicio_Seg'], datos['Repetitions'][repeticion+1]['Inicio_Seg'], cadena)
        #print(f"{datos['Repetitions'][repeticion]['Inicio_Seg']} - {datos['Repetitions'][repeticion+1]['Inicio_Seg']}")
    cadena = ""
    for warning in datos['Repetitions'][len(datos['Repetitions'])-1]['Fatigue warnings']:
        cadena += "* " + dividir_cadena(warning) +"\n"
    if cadena == "":
        cadena = "No fatigue errors"
    crear_clip_de_texto(datos['Repetitions'][len(datos['Repetitions'])-1]['Inicio_Seg'], 60, cadena)
    #print(f"{datos['Repetitions'][len(datos['Repetitions'])-1]['Inicio_Seg']} - 60")





def main(url):
    with open(url, 'r') as archivo_json:
        datos = json.load(archivo_json)
    crear_clips(datos)

    fondo = ColorClip((720, 720), color=(255, 255, 255)).set_duration(60)

    video = CompositeVideoClip([fondo] + clips)

    video = video.resize(height=720)
    return video
    #video.write_videofile("output.mp4", fps=24)

if __name__ == "__main__":
    json_data = 'C:\\Users\mohae\Desktop\Beca De Colaboracion\Repositorio\Output_fatigue\prueba\Jsons\OculusTracking_20240123_172111.json'
    #output_path = "Fatigue_reportoutput.mp4"
    main(json_data)