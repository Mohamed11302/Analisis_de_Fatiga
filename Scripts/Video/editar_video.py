from moviepy.editor import VideoFileClip, clips_array
import argparse
import Constantes as Const
def editar_video(ruta_webcam, ruta_oculus, ruta_salida):
    try:
        video_webcam = VideoFileClip(ruta_webcam)
        video_oculus = VideoFileClip(ruta_oculus)
        min_duration = min(video_webcam.duration, video_oculus.duration)
        if video_webcam.duration < video_oculus.duration:
            inicio = video_oculus.duration - min_duration
            video_oculus = video_oculus.subclip(inicio, video_oculus.duration)
        else:
            inicio = video_webcam.duration - min_duration
            video_webcam = video_webcam.subclip(inicio, video_webcam.duration)
        videos_concatenados = clips_array([[video_webcam, video_oculus]])
        videos_concatenados.write_videofile(ruta_salida, codec="libx264", fps=15)
    except:
        print(f"Las rutas \n\t{ruta_webcam}\n\t{ruta_oculus}\nno están bien definidas")

def obtener_argumentos_entrada():
    parser = argparse.ArgumentParser(description='Argumentos Análisis de fatiga.')
    parser.add_argument('--video_salida', type=str, help='Ruta donde guardar el video de salida')
    parser.add_argument('--video_oculus', type=str, help='Ruta donde esta el video de las oculus')
    parser.add_argument('--video_webcam', type=str, help='Ruta donde esta el video de la webcam')
    args = parser.parse_args()
    if args.video_webcam != None:
        Const.RUTA_VIDEO_WEBCAM = args.video_webcam
    if args.video_oculus != None:
        Const.RUTA_VIDEO_OCULUS = args.video_oculus
    if args.video_salida != None:
        Const.RUTA_VIDEO_SALIDA = args.video_salida


if __name__ == "__main__":
    obtener_argumentos_entrada()
    editar_video(Const.RUTA_VIDEO_WEBCAM, Const.RUTA_VIDEO_OCULUS, Const.RUTA_VIDEO_SALIDA)