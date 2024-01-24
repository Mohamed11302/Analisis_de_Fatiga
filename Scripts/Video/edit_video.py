from moviepy.editor import VideoFileClip, clips_array, concatenate_videoclips, CompositeVideoClip
import argparse
import Constantes as Const

def edit_video(ruta_webcam, ruta_oculus, ruta_salida, video_fatiga):
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

        if video_fatiga != None:
            video_fatiga = video_fatiga.subclip(inicio, video_fatiga.duration)
            combined = clips_array([[video_webcam], [video_fatiga]])
        
        else:
            combined = video_webcam

        videos_concatenados = clips_array([[combined, video_oculus]])
        # Escribir el nuevo video
        videos_concatenados.write_videofile(ruta_salida, codec="libx264", fps=15)
    except Exception as e:
        print(f"Ocurrió un error al procesar los videos: {str(e)}")




def obtener_argumentos_entrada():
    parser = argparse.ArgumentParser(description='Edit video arguments.')
    parser.add_argument('--output_video', type=str, help='Directory to save output video')
    parser.add_argument('--oculus_video', type=str, help='Directory of oculus video')
    parser.add_argument('--webcam_video', type=str, help='Directory of webcam video')
    args = parser.parse_args()
    return args.webcam_video, args.oculus_video, args.output_video

def asignar_argumentos(webcam_video, oculus_video, output_video):
    if webcam_video != None:
        Const.RUTA_VIDEO_WEBCAM = webcam_video
    if oculus_video != None:
        Const.RUTA_VIDEO_OCULUS = oculus_video
    if output_video != None:
        Const.RUTA_VIDEO_SALIDA = output_video


if __name__ == "__main__":
    try:
        webcam_video, oculus_video, output_video = obtener_argumentos_entrada()
        asignar_argumentos(webcam_video, oculus_video, output_video)
        edit_video(Const.RUTA_VIDEO_WEBCAM, Const.RUTA_VIDEO_OCULUS, Const.RUTA_VIDEO_SALIDA, None)
    except Exception as e:
        print(f"Ocurrió un error al procesar los videos: {str(e)}")