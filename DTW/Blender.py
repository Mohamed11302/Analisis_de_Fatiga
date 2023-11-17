import bpy
import math
import pandas as pd

archivo_csv = "C:\\Users\\mohae\\Desktop\\Beca De Colaboracion\\Pruebas\\OculusTracking_20230928_135634.csv"
df = pd.read_csv(archivo_csv, encoding='UTF-8', sep=';', index_col=False)
df['HandPosition_x'] = df['HandPosition_x'].str.replace(',', '.').astype(float)
df['HandPosition_y'] = df['HandPosition_y'].str.replace(',', '.').astype(float)
df['HandPosition_z'] = df['HandPosition_z'].str.replace(',', '.').astype(float)
df['HeadPosition_x'] = df['HeadPosition_x'].str.replace(',', '.').astype(float)
df['HeadPosition_y'] = df['HeadPosition_y'].str.replace(',', '.').astype(float)
df['HeadPosition_z'] = df['HeadPosition_z'].str.replace(',', '.').astype(float)
df['HeadRotation_x'] = df['HeadRotation_x'].str.replace(',', '.').astype(float)
df['HeadRotation_y'] = df['HeadRotation_y'].str.replace(',', '.').astype(float)
df['HeadRotation_z'] = df['HeadRotation_z'].str.replace(',', '.').astype(float)

min_frame = df['Frame'].min()

obj_Mball = bpy.data.objects['Mball']
obj_camera = bpy.context.scene.camera

for i in range(0, len(df)):
    frame_elegido = df.at[i, 'Frame'] - min_frame
    obj_Mball.location[0] = df.at[i, 'HandPosition_x']
    obj_Mball.location[1] = df.at[i, 'HandPosition_y']
    obj_Mball.location[2] = df.at[i, 'HandPosition_z']

    obj_camera.location[0] = df.at[i, 'HeadPosition_x']
    obj_camera.location[1] = df.at[i, 'HeadPosition_y']
    obj_camera.location[2] = df.at[i, 'HeadPosition_z']

    # Configura la rotación en radianes (ajusta a tus necesidades)
    obj_camera.rotation_euler[0] = math.radians(df.at[i, 'HeadRotation_x']) 
    obj_camera.rotation_euler[1] = math.radians(df.at[i, 'HeadRotation_y']) 
    obj_camera.rotation_euler[2] = math.radians(df.at[i, 'HeadRotation_z'])

    obj_Mball.keyframe_insert(data_path="location", frame=frame_elegido, index=0)
    obj_Mball.keyframe_insert(data_path="location", frame=frame_elegido, index=1)
    obj_Mball.keyframe_insert(data_path="location", frame=frame_elegido, index=2)

    obj_camera.keyframe_insert(data_path="location", frame=frame_elegido, index=0)
    obj_camera.keyframe_insert(data_path="location", frame=frame_elegido, index=1)
    obj_camera.keyframe_insert(data_path="location", frame=frame_elegido, index=2)

    # Asegúrate de configurar la interpolación y demás configuraciones adecuadas para tu animación
