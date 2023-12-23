import cv2

def grabar_video():
    # Configuración del video
    ancho = 640
    alto = 480
    fps = 25

    # Crear el objeto VideoWriter
    video = cv2.VideoWriter('Scripts/Servidor/video_grabado.avi', cv2.VideoWriter_fourcc(*'XVID'), fps, (ancho, alto))

    # Inicializar la cámara
    cap = cv2.VideoCapture(0)

    # Verificar si la cámara se abrió correctamente
    if not cap.isOpened():
        print("Error al abrir la cámara.")
        exit()

    while True:
        # Capturar el fotograma de la cámara
        ret, frame = cap.read()

        if not ret:
            print("Error al capturar el fotograma.")
            break

        # Mostrar el fotograma en una ventana (opcional)
        cv2.imshow('Video', frame)

        # Escribir el fotograma en el archivo de video
        video.write(frame)

        # Salir si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar recursos
    cap.release()
    video.release()
    cv2.destroyAllWindows()
