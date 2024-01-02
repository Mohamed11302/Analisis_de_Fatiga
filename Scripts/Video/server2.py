import socket
import subprocess
import threading
import psutil
import signal
import ctypes
import grabar_video
# Variable global para almacenar el objeto del proceso
process = None
import time
def is_process_running(process):
    if process is None:
        return False
    return psutil.pid_exists(process.pid) and process.poll() is None

def handle_client(client_socket, evento):
    global process

    request = client_socket.recv(1024).decode('utf-8')

    if request == "GRABAR":
        cmd = "scrcpy --crop=2000:2000:0:0 --record=prueba_oculus.mkv --record-format=mkv  --no-playback --kill-adb-on-close --max-fps=30"
        if is_process_running(process):
            print("[!] Ya hay un proceso en ejecución. No se puede iniciar otro.")
        else:
            process = subprocess.Popen(cmd, shell=True)
            print(f"[*] Proceso iniciado con PID: {process.pid}")
        grabar_video.grabar_webcam(evento)

    elif request == "TERMINAR":
        # Detener la grabación cerrando la terminal con ctrl+c
        if is_process_running(process):
            ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, process.pid)
            process.wait()
            print(f"[*] Proceso con PID {process.pid} terminado.")
            process = None
        else:
            print("[!] No hay ningún proceso en ejecución.")
        evento.set()
    client_socket.close()
    time.sleep(1)
    evento.clear()

def start_server():
    host = '192.168.18.177'
    port = 5000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")

    def signal_handler(sig, frame):
        global process
        if is_process_running(process):
            ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, process.pid)
            process.wait()
            print(f"[*] Proceso con PID {process.pid} terminado por señal.")
            process = None

    signal.signal(signal.SIGINT, signal_handler)
    evento = threading.Event()
    while True:
        client, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

        client_handler = threading.Thread(target=handle_client, args=(client,evento))
        client_handler.start()

if __name__ == "__main__":
    start_server()
