import time
import socket
import threading
import signal
import ctypes
import grabacion as grabacion
import psutil
import subprocess
import Constantes as Const
import argparse
process = None
grabando_video = False

def obtener_argumentos_entrada():
    parser = argparse.ArgumentParser(description='Argumentos Análisis de fatiga.')
    parser.add_argument('--ruta_oculus', type=str, help='Ruta donde escribir el fichero con host y puerto en las oculus quest')
    parser.add_argument('--video_oculus', type=str, help='Ruta donde guardar el video de las oculus')
    parser.add_argument('--video_webcam', type=str, help='Ruta donde guardar el video de la webcam')
    args = parser.parse_args()
    if args.video_webcam != None:
        Const.RUTA_VIDEO_WEBCAM = args.video_webcam
    if args.video_oculus != None:
        Const.RUTA_VIDEO_OCULUS = args.video_oculus
    if args.ruta_oculus != None:
        Const.FICHERO_OCULUS = args.ruta_oculus

def encontrar_puerto_libre(host, puerto_inicial=5000):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((host, puerto_inicial))
            s.close()
            return puerto_inicial
        except socket.error:
            puerto_inicial += 1

def is_process_running(process):
    if process is None:
        return False
    return psutil.pid_exists(process.pid) and process.poll() is None

def handle_client(client_socket, evento):
    global process
    global grabando_video
    request = client_socket.recv(1024).decode('utf-8')

    if request == "GRABAR":
        process = grabacion.grabar_oculus(process)
        if grabando_video == False:
            threading.Thread(target=grabacion.grabar_webcam, args=(evento,)).start()
        grabando_video = True

    elif request == "TERMINAR":
        evento.set()
        grabando_video = False
        process = grabacion.finalizar_grabacion_oculus(process)
        time.sleep(0.1)
        evento.clear()

    client_socket.close()


def signal_handler(sig, frame):
    global process
    if is_process_running(process):
        pid = process.pid
        ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, pid)
        process.wait()
        print(f"[*] Proceso con PID {pid} terminado por señal.")
        process = None

def exportar_info_servidor(content):
    command = ["adb", "shell", f"echo '{content}' > {Const.FICHERO_OCULUS}"]
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando el comando '{e.cmd}': {e.stderr}")
        return None

def start_server():
    host = socket.gethostbyname(socket.gethostname())
    port = encontrar_puerto_libre(host)
    file_content = f"{host}\n{port}"
    exportar_info_servidor(file_content)
    #host = '192.168.18.177'
    #port = 5000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")

    signal.signal(signal.SIGINT, signal_handler)
    evento = threading.Event()
    while True:
        client, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

        client_handler = threading.Thread(target=handle_client, args=(client,evento))
        client_handler.start()

if __name__ == "__main__":
    obtener_argumentos_entrada()
    start_server()
