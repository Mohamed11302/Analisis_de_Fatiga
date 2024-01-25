# Fatigue analysis 
Model to assess fatigue experienced by a patient in the Box and Box game developed in Rehab-Immersive. The model returns a label (Low, Moderate, High, Very High) indicating the level of fatigue the patient has experienced in that exercise series.


# Run Fatigue_analysis program:
Steps to run program:
1.  Install python 3.11.7 and add to the environment path
2.  Go to the root folder of the repository
3.  Install the dependencies
```
python3 -m pip install -r requirements.txt
```

4.  Set up the folder with the data from RI. In this example, the folder is RI_Data.
5.  Locate the execution date and the user you want to analyse.
6.  Run the main program. The arguments of the program are (You can check running "python3 Fatigue_analysis.py --h"):
    -   (Required) user : The user you want to analyse
    -   (Required) date : The date of the analysis
    -   (Optional) read_oculus : 0 if your data is on the device 1 if your data is on the Oculus Quest Storage
    -   (Optional) directory : Define the directory with the RI Data

Example of an execution with user: default ; date: 20231226_204637 ; read_oculus : 0 ; directory : RI_Data

```
python3 .\Scripts\Fatigue_analysis.py --user default --date 20231226_204637 --read_oculus 0 --directory "RI_Data"
```

This will generate a new folder Output_fatigue with the results for the analysis.


# Run Server and create the Fatigue video
1.  Install the dependencies
```
python3 -m pip install -r Scripts/Video/requirements.txt
```

2.  (Optional) Download the same versions of the software used, which are listed in Software.txt.

3.  Run the BBT apk, you can define the name of the user

4.  Execute the server program with 3 attributes (for a better view, use the command "server.py -h"):
    -   --oculus_directory: Path to write the file with host and port on Oculus Quest.
    -   --oculus_video_directory: Path to save the Oculus video.
    -   --webcam_video_directory: Path to save the webcam video.

5.  Play in the BBT Program and after the finalization of an exercise two new videos will be created with the webcam video and the oculus video.


6.  To analyse the data and create the fatigue report video, use the script Fatigue_and_video.py, which will generate a video by combining and synchronizing all the parts. It has 7 attributes (for a better view, use the command "Scripts/Fatigue_and_video.py -h"):
    -   --user USER : User name.
    -   --date DATE : Date of the exercise with format: YYYYMMDD_HHMMSS.
    -   --read_oculus READ_OCULUS : Read files from oculus. 0: No, 1: Yes.
    -   --directory DIRECTORY : Main directory of saved files from Rehab-Immersive.
    -   --output_video OUTPUT_VIDEO : Directory to save output video
    -   --oculus_video OCULUS_VIDEO : Directory of oculus video
    -   --webcam_video WEBCAM_VIDEO :Directory of webcam video

An example of execution would be:
```
python3 -m pip install -r Scripts/Video/requirements.txt
```

Now, run the recording from the BBT program:
```
adb shell am start -n com.DefaultCompany.Prueba_ClienteServidor2/com.unity3d.player.UnityPlayerActivity -e ruta "/sdcard/Android/data/com.DefaultCompany.Prueba_ClienteServidor2/servidor.txt"
```
Now start the server:
```
python3 .\Scripts\server.py --oculus_directory "/sdcard/Android/data/com.DefaultCompany.Prueba_ClienteServidor2/servidor.txt" --oculus_video_directory "video_oculus.mkv" --webcam_video_directory "video_webcam.avi"
```

Finally, once the video is created, you can generate the fatigue report video as it follows:

```
python3 .\Scripts\Fatigue_and_video.py --user prueba --date 20240123_172111 --read_oculus 1 --directory "/sdcard/Android/data/com.RehabImmersive.BBT_2023_12_BodyCalibration/BoxAndBlock" --output_video "fatigue_video.mp4" --oculus_video "video_oculus.mkv" --webcam_video "video_webcam.avi"
```


