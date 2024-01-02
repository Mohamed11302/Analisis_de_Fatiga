import cv2
import psutil
import subprocess
import ctypes


def grabar_oculus(evento):
    cmd = "scrcpy --crop=2000:2000:0:0 --record=prueba_oculus.mkv --record-format=mkv  --no-playback --kill-adb-on-close --max-fps=30"
    process = subprocess.Popen(cmd, shell=True)
    print(f"[*] Proceso iniciado con PID: {process.pid}")
    while not evento.is_set():
        pass
    ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, process.pid)
    process.wait()
    print(f"[*] Proceso con PID {process.pid} terminado.")
    process = None


def grabar_webcam(evento):
    cap = cv2.VideoCapture(0)

    ancho = int(cap.get(3))
    alto = int(cap.get(4))
    fps = 30
    video = cv2.VideoWriter('prueba_webcam.avi', cv2.VideoWriter_fourcc(*'XVID'), fps, (ancho, alto))

    while not evento.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar el fotograma.")
            break
        video.write(frame)

    print("Deteniendo grabación de video")
    evento.clear()
    cap.release()
    video.release()