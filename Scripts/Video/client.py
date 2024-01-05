import socket

##Cliente para probar la conexion al servidor

def cliente():
    host = '192.168.18.177'
    #host = '127.0.0.1'
    puerto = 5000

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((host, puerto))

    #cliente.sendall('GRABAR'.encode('utf-8'))
    cliente.sendall('TERMINAR'.encode('utf-8'))    

    #Hay 3 segundos de delay hasta que se enciende la camara
    cliente.close()

if __name__ == "__main__":
    cliente()
