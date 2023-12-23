import socket
import time

def cliente():
    host = '192.168.1.145'
    puerto = 12345

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((host, puerto))

    # Enviar mensaje para iniciar la grabación
    cliente.sendall('OCULUS FINALIZAR VIDEO'.encode('utf-8'))
    print("Enviando mensaje iniciar")
    # Esperar unos segundos simulando la grabación
    #time.sleep(7)
    #Hay 3 segundos de delay hasta que se enciende la camara

    # Enviar mensaje para detener la grabación
    #cliente.sendall('detener'.encode('utf-8'))
    #print("Enviando mensaje detener")
    cliente.close()

if __name__ == "__main__":
    cliente()
