import socket

def iniciar_servidor():
    # Configurar el servidor
    host = '192.168.1.145'
    puerto = 12345

    # Crear un socket
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Enlace del socket a una dirección y puerto
    servidor.bind((host, puerto))

    # Escuchar conexiones entrantes
    servidor.listen()

    print(f"Servidor escuchando en {host}:{puerto}")

    while True:
        # Esperar una conexión
        cliente, direccion = servidor.accept()
        print(f"Conexión establecida desde {direccion}")

        # Recibir y mostrar mensajes
        while True:
            datos = cliente.recv(1024)
            if not datos:
                break
            mensaje = datos.decode('utf-8')
            print(f"Mensaje recibido: {mensaje}")

        # Cerrar la conexión con el cliente
        cliente.close()

if __name__ == "__main__":
    iniciar_servidor()
