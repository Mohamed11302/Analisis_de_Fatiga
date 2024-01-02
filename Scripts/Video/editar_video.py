from moviepy.editor import VideoFileClip, clips_array

# Rutas de los videos a concatenar
video1_path = "prueba_webcam.avi"
video2_path = "prueba_oculus.mkv"

video1 = VideoFileClip(video1_path)
video2 = VideoFileClip(video2_path)

# Obtener la duración mínima de ambos videos
min_duration = min(video1.duration, video2.duration)
print(video1.duration)
print(video2.duration)
if video1.duration < video2.duration:
    inicio = video2.duration - min_duration
    #video1 = video1.subclip(0, min_duration)
    video2 = video2.subclip(inicio, video2.duration)
    print("a")
else:
    inicio = video1.duration - min_duration
    video1 = video1.subclip(inicio, video1.duration)
    print("b")
    #video2 = video2.subclip(0, min_duration)
print(inicio)
# Concatenar horizontalmente (en una fila)
videos_concatenados = clips_array([[video1, video2]])

# Guardar el video resultante
videos_concatenados.write_videofile("video_concatenado.mp4", codec="libx264", fps=15)