import time
import socket
import threading
import signal
import ctypes
import grabacion as grabacion
import psutil
import subprocess

process = None
grabando_video = False

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

def adb_command(command):
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command '{e.cmd}': {e.stderr}")
        return None

def create_file_on_oculus(file_path, content):
    # Comando para escribir el contenido en un archivo en Oculus Quest
    adb_command(["adb", "shell", f"echo '{content}' > {file_path}"])

def start_server():
    host = socket.gethostbyname(socket.gethostname())
    port = encontrar_puerto_libre(host)
    oculus_file_path = "/sdcard/Android/data/com.DefaultCompany.Prueba_ClienteServidor2/servidor.txt"
    file_content = f"{host}\n{port}"
    create_file_on_oculus(oculus_file_path, file_content)
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
    start_server()
