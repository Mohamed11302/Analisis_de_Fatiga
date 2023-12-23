import cv2
import socket
import threading

def grabar_video(evento):
    cap = cv2.VideoCapture(0)

    ancho = int(cap.get(3))
    alto = int(cap.get(4))
    fps = 25
    video = cv2.VideoWriter('Scripts/Servidor/video_grabado.avi', cv2.VideoWriter_fourcc(*'XVID'), fps, (ancho, alto))

    while not evento.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar el fotograma.")
            break
        video.write(frame)

    print("Deteniendo grabación de video")
    cap.release()
    video.release()

def manejar_cliente(conn, evento):
    mensaje = conn.recv(1024).decode('utf-8')
    if mensaje == 'OCULUS INICIAR VIDEO':
        print("Iniciando grabación de video")
        evento.clear()  # Limpiar el evento para permitir la grabación
        grabar_video(evento)
        print("Grabación de video finalizada")
    elif mensaje == 'OCULUS FINALIZAR VIDEO':
        evento.set()  # Establecer el evento para detener la grabación
    conn.close()


def servidor():
    host = '192.168.1.145'
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
