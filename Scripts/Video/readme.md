Pasos a seguir para ejecutar el programa:

1. Ejecutamos el comando python3 -m pip install -r requirements.txt

2. (Opcional) Descargar las mismas versiones del software utilizado que se encuentra en Software.txt 

3.  Ejecutamos el programa del servidor que tiene 3 atributos (podemos verlo mejor si escribimos el comando "server.py -h"):
    *   --ruta_oculus : Ruta donde escribir el fichero con host y puerto en las oculus quest
    *   --video_oculus : Ruta donde guardar el video de las oculus
    *   --video_webcam : Ruta donde guardar el video de la webcam

4.  Ejecutamos el proyecto de unity pasandole como argumento la ruta del fichero de los datos del servidor (el mismo definido en 
    ruta_oculus) con -e ruta "ruta"

5.  Utilizando el trigger del mando derecho de oculus quest si pulsamos Iniciar Grabación se iniciará la grabación y si pulsamos
    finalizar Grabación se finalizará la grabación y se escribirá en la ruta marcada en el primer paso

6.  Para juntar los videos utilizamos el script editar_video.py que te generará un video uniendo y sincronizando ambas partes. Tiene 3 atributos (podemos verlo mejor si escribimos el comando "editar_video.py -h"):
    *   --video_salida : Ruta donde guardar el video de salida
    *   --video_oculus : Ruta donde esta el video de las oculus
    *   --video_webcam : Ruta donde esta el video de la webcam


Un ejemplo de ejecución sería:
```
python3 -m pip install -r requirements.txt

python3 .\Scripts\Video\server.py --ruta_oculus "/sdcard/Android/data/com.DefaultCompany.Prueba_ClienteServidor2/servidor.txt" --video_oculus "video_oculus.mkv" --video_webcam "video_webcam.avi"
```

Ahora ejecutaríamos la grabación desde el programa de unity 

```
adb shell am start -n com.DefaultCompany.Prueba_ClienteServidor2/com.unity3d.player.UnityPlayerActivity -e ruta "/sdcard/Android/data/com.DefaultCompany.Prueba_ClienteServidor2/servidor.txt"
```

Por último, una vez creado el video podríamos editarlo de esta manera

```
python3 .\Scripts\Video\editar_video.py --video_salida "video_salida.mp4" --video_oculus "video_oculus.mkv" --video_webcam "video_webcam.avi"
```