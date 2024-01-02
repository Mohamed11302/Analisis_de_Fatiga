import time
import socket
import threading
import signal
import ctypes
import grabacion as grabacion
import psutil
process = None

def is_process_running(process):
    if process is None:
        return False
    return psutil.pid_exists(process.pid) and process.poll() is None


def handle_client(client_socket, evento):
    global process
    request = client_socket.recv(1024).decode('utf-8')

    if request == "GRABAR":
        process = grabacion.grabar_oculus(process)
        grabacion.grabar_webcam(evento)

    elif request == "TERMINAR":
        process = grabacion.finalizar_grabacion_oculus(process)
        evento.set()
        time.sleep(1)
        evento.clear()

    client_socket.close()


def signal_handler(sig, frame):
    global process
    if is_process_running(process):
        ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, process.pid)
        process.wait()
        print(f"[*] Proceso con PID {process.pid} terminado por señal.")
        process = None

def start_server():
    host = '192.168.18.177'
    port = 5000

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
