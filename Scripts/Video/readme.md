1.  Execute the command python3 -m pip install -r requirements.txt

2.  (Optional) Download the same versions of the software used, which are listed in Software.txt.

3.  Execute the server program with 3 attributes (for a better view, use the command "server.py -h"):
    -   --ruta_oculus: Path to write the file with host and port on Oculus Quest.
    -   --video_oculus: Path to save the Oculus video.
    -   --video_webcam: Path to save the webcam video.

4.  Run the Unity project, passing the server data file path (defined in ruta_oculus) as an argument with -e ruta "ruta."

5.  Using the trigger of the right Oculus Quest controller, if we press "Start Recording," the recording will begin, and if we press "Finish Recording," the recording will end, and the file will be written to the path specified in the first step.

6.  To merge the videos, use the script editar_video.py, which will generate a video by combining and synchronizing both parts. It has 3 attributes (for a better view, use the command "editar_video.py -h"):
    -   --video_salida: Path to save the output video.
    -   --video_oculus: Path where the Oculus video is located.
    -   --video_webcam: Path where the webcam video is located.

An example of execution would be:
´´´
python3 -m pip install -r requirements.txt

python3 .\Scripts\Video\server.py --oculus_directory "/sdcard/Android/data/com.DefaultCompany.Prueba_ClienteServidor2/servidor.txt" --oculus_video_directory "video_oculus.mkv" --webcam_video_directory "video_webcam.avi"
´´´
Now, run the recording from the Unity program:

´´´
adb shell am start -n com.DefaultCompany.Prueba_ClienteServidor2/com.unity3d.player.UnityPlayerActivity -e ruta "/sdcard/Android/data/com.DefaultCompany.Prueba_ClienteServidor2/servidor.txt"

´´´
Finally, once the video is created, you can edit it as follows:
´´´
python3 .\Scripts\Video\edit_video.py --output_video "video_salida.mp4" --oculus_video "video_oculus.mkv" --webcam_video "video_webcam.avi"
´´´




