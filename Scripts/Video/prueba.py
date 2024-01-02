import socket

def encontrar_puerto_libre(host, puerto_inicial=5000):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((host, puerto_inicial))
            s.close()
            return puerto_inicial
        except socket.error:
            puerto_inicial += 1

# Obtén la dirección IP local que no sea de loopback
host = socket.gethostbyname(socket.gethostname())
puerto = encontrar_puerto_libre(host)

print(f'Puerto libre encontrado: {puerto} en el host {host}')
