import cv2
import subprocess
import ctypes
import server as server
import Video.Constantes as Const


def record_oculus(process):
    cmd = F"scrcpy --crop=2000:2000:0:0 --record={Const.RUTA_VIDEO_OCULUS} --record-format=mkv  --no-playback --kill-adb-on-close --max-fps=30 --display-buffer=50"
    if server.is_process_running(process):
        print("[!] Ya hay un proceso en ejecución. No se puede iniciar otro.")
    else:
        process = subprocess.Popen(cmd, shell=True)
        print(f"[*] Proceso iniciado con PID: {process.pid}")
    return process

def finish_oculus_recording(process):
    if server.is_process_running(process):
        ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, process.pid)
        process.wait()
        print(f"[*] Proceso con PID {process.pid} terminado.")
        process = None
    else:
        print("[!] No hay ningún proceso en ejecución.")
    return process


def record_webcam(evento):
    cap = cv2.VideoCapture(0)

    ancho = int(cap.get(3))
    alto = int(cap.get(4))
    fps = 30
    video = cv2.VideoWriter(Const.RUTA_VIDEO_WEBCAM, cv2.VideoWriter_fourcc(*'XVID'), fps, (ancho, alto))

    while not evento.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar el fotograma.")
            break
        video.write(frame)

    print("Deteniendo grabación de webcam")
    evento.clear()
    cap.release()
    video.release()