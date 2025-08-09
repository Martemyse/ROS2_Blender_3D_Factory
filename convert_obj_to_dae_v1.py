"""
Created on Tue Aug 15 17:54:58 2023
@author: Martin-PC
"""

import os
import glob
import bpy

def convert_obj_to_dae(obj_path):
    # Construct the full path to the output .dae file in the same directory as the .obj file
    dae_path = os.path.splitext(obj_path)[0] + '.dae'
    
    # Delete all objects in the current scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Import the .obj file
    bpy.ops.import_scene.obj(filepath=obj_path)
    
    # Recenter origin for each object in the scene
    for obj in bpy.context.scene.objects:
        bpy.context.view_layer.objects.active = obj  # Set the current object as active
        obj.select_set(True)  # Select the current object
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
        obj.select_set(False)  # Deselect the current object

    # Export the model as .dae
    bpy.ops.wm.collada_export(filepath=dae_path)
    
    # Export the model as .dae
    bpy.ops.wm.collada_export(filepath=dae_path)

    print(f"Converted {obj_path} to {dae_path}")


def main():
    # Define the directories
    input_directory = 'C:\\Users\\Martin-PC\\ROS2\\'
    # output_directory = 'C:\\Users\\Martin-PC\\ROS2\\converted_dae\\'  # Change this to your desired output directory
    
    # If the output directory doesn't exist, create it
    # if not os.path.exists(output_directory):
    #     os.makedirs(output_directory)

    # Use glob to recursively find all .obj files starting from the input directory
    obj_files = glob.glob(os.path.join(input_directory, '**/*.obj'), recursive=True)

    for obj_file in obj_files:
        convert_obj_to_dae(obj_file)
        os.remove(obj_file)

    print("Conversion finished.")

if __name__ == "__main__":
    main()
