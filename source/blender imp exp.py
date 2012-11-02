# import all dae files and export as ogre
import bpy.ops
import glob
files = glob.glob("c:/*.dae")
for file in files:
    bpy.ops.scene.delete()
    bpy.ops.object.select_all()
    bpy.ops.object.delete()
    bpy.ops.wm.collada_import("EXEC_DEFAULT",filepath=file)
    bpy.ops.ogre.export("EXEC_DEFAULT",filepath=file)
    bpy.ops.scene.delete()
    bpy.ops.object.select_all()
    bpy.ops.object.delete()

