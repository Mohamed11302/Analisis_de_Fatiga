import bpy
##PRUEBA
# Configurar la escena
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250

# Añadir un objeto metaball
bpy.ops.object.metaball_add(type='BALL', radius=1, location=(0, 0, 0))
metaball_obj = bpy.context.active_object

# Configurar una animación simple
metaball_obj.location.x += 5  # Mover el objeto en el primer frame
metaball_obj.location.x -= 5  # Mover el objeto en el último frame

# Configurar la cámara
bpy.ops.object.camera_add(location=(0, -10, 5), rotation=(1.0472, 0, 0))
camera_obj = bpy.context.active_object
bpy.context.scene.camera = camera_obj

# Configurar el renderizado
bpy.context.scene.render.image_settings.file_format = 'AVI_JPEG'
bpy.context.scene.render.filepath = 'C:/Users/mohae/Desktop/output.avi'

# Renderizar la animación
bpy.ops.render.render(animation=True)
