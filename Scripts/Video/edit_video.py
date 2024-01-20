from moviepy.editor import VideoFileClip, clips_array
import argparse
import Constantes as Const
def edit_video(ruta_webcam, ruta_oculus, ruta_salida):
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
    parser = argparse.ArgumentParser(description='Edit video arguments.')
    parser.add_argument('--output_video', type=str, help='Directory to save output video')
    parser.add_argument('--oculus_video', type=str, help='Directory of oculus video')
    parser.add_argument('--webcam_video', type=str, help='Directory of webcam video')
    args = parser.parse_args()
    if args.webcam_video != None:
        Const.RUTA_VIDEO_WEBCAM = args.webcam_video
    if args.oculus_video != None:
        Const.RUTA_VIDEO_OCULUS = args.oculus_video
    if args.output_video != None:
        Const.RUTA_VIDEO_SALIDA = args.output_video


if __name__ == "__main__":
    obtener_argumentos_entrada()
    edit_video(Const.RUTA_VIDEO_WEBCAM, Const.RUTA_VIDEO_OCULUS, Const.RUTA_VIDEO_SALIDA)