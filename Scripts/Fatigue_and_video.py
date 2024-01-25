import Fatigue_analysis as Fatigue_analysis
import Video.Fatigue_report_video as Fatigue_report_video
import Video.edit_video as edit_video
import argparse

def obtener_argumentos_entrada():
    parser = argparse.ArgumentParser(description='Fatigue and video arguments.')
    parser.add_argument('--user', type=str,required=True, help='User name.')
    parser.add_argument('--date', type=str,required=True, help='Date of the exercise with format: YYYYMMDD_HHMMSS.')
    parser.add_argument('--read_oculus', type=int, help='Read files from oculus. 0: No, 1: Yes.')
    parser.add_argument('--directory', type=str, help='Main directory of saved files from Rehab-Immersive.')
    parser.add_argument('--output_video', type=str, help='Directory to save output video')
    parser.add_argument('--oculus_video', type=str, help='Directory of oculus video')
    parser.add_argument('--webcam_video', type=str, help='Directory of webcam video')
    args = parser.parse_args()
    return args.user, args.date, args.read_oculus, args.directory, args.webcam_video, args.oculus_video, args.output_video

def main():
    user, date, read_oculus, directory, ruta_webcam, ruta_oculus, ruta_salida = obtener_argumentos_entrada()
    json_output = Fatigue_analysis.main(user, date, read_oculus, directory)
    fatigue_video = Fatigue_report_video.main(json_output)
    edit_video.edit_video(ruta_webcam, ruta_oculus, ruta_salida, fatigue_video)

if __name__ == "__main__":
    main()
