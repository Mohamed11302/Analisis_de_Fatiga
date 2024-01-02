import socket
import threading
import Scripts.Video.grabacion as grabacion


def manejar_cliente(conn, evento):
    mensaje = conn.recv(1024).decode('utf-8')
    if mensaje == 'OCULUS INICIAR VIDEO':
        print("Iniciando grabación de video")
        evento.clear() 
        grabacion.grabar_webcam(evento)
        print("Grabación de video finalizada")
    elif mensaje == 'OCULUS FINALIZAR VIDEO':
        evento.set()  # Establecer el evento para detener la grabación
    conn.close()


def servidor():
    host = '127.0.0.1'
    puerto = 12345

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((host, puerto))
    servidor.listen()

    print(f"El servidor está escuchando en {host}:{puerto}")

    evento = threading.Event()

    while True:
        conn, addr = servidor.accept()
        print(f"Conexión establecida desde {addr}")
        # Manejar el cliente en un hilo separado
        hilo_cliente = threading.Thread(target=manejar_cliente, args=(conn, evento))
        hilo_cliente.start()

if __name__ == "__main__":
    servidor()
