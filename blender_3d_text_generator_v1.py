# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 16:13:05 2023

@author: Martin-PC
"""

import bpy
import json
import os
import time

with open('C:\\Users\\Martin-PC\\ROS2\\ros_objekti_v2.txt', encoding='ansi') as f:
    lines = f.readlines()
    lines = lines[0].replace('\\u010d','c').replace('\\u017e','z')
    
traces_mapping_dict = json.loads(lines)
plotly_sklop_content_inner = traces_mapping_dict[1]
plotly_sklop_content_inner_instances = {k:v for k,v in plotly_sklop_content_inner.items() if not k in ['colors','number_of_traces','traces_list','legend_instances']}


machines = [k for k in plotly_sklop_content_inner_instances.keys() if len(k) >= 3]

mat = bpy.data.materials.new(name="WhiteMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)  # RGBA for white


def create_3d_text(machine, export_path, base_path):
    # Delete all objects from the scene

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Create the 3D text object
    bpy.ops.object.text_add()
    text_obj = bpy.context.active_object
    text_obj.data.body = machine
    text_obj.data.extrude = 0.03  # Set the extrusion value (depth of the 3D text)
    
    text_obj.rotation_euler = (0, 0, 0)  # Reset rotations; adjust if needed
    text_obj.scale = (1, 1, 1)  # Scale uniformly in all three axes; adjust if needed
    text_obj.location = (0, 0, 0)  # Position the object at the world origin; adjust if needed
    
    # Center the origin to the geometry of the 3D text
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')

    model_dir = os.path.join(base_path, machine)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        
    # Write the model.config file
    config_content = """
    <model>
      <name>{machine}</name>
      <version>1.0</version>
      <sdf version='1.6'>{machine}.sdf</sdf>
      <author>
        <name>Martin-PC</name>
        <email>youremail@example.com</email>
      </author>
      <description></description>
    </model>
    """.format(machine=machine)

    with open(os.path.join(model_dir, "model.config"), 'w') as f:
        f.write(config_content)
        
     # You also need to generate an SDF description file here (model.sdf)
    # This is a simplified version:
    sdf_content = """
    <?xml version='1.0'?>
    <sdf version='1.6'>
      <model name='{machine}'>
        <link name='link'>
          <visual name='visual'>
            <geometry>
              <mesh>
                <uri>model://localros/text_3d_models/{machine}/{machine}.dae</uri>
              </mesh>
            </geometry>
          </visual>
        </link>
      </model>
    </sdf>
    """.format(machine=machine)

    with open(os.path.join(model_dir, f"{machine}.sdf"), 'w') as f:
        f.write(sdf_content.strip())
        
        
    # Update the scene
    bpy.context.view_layer.update()

    # Select and make the text object active
    bpy.context.view_layer.objects.active = text_obj
    text_obj.select_set(True)
    
    # Export the model
    bpy.ops.export_scene.obj(filepath=export_path)
    # bpy.ops.wm.collada_export(filepath=export_path)



base_path = "C:\\Users\\Martin-PC\\ROS2\\text_3d_models"
for machine in machines:
    export_path = f"C:\\Users\\Martin-PC\\ROS2\\text_3d_models\\{machine}\\{machine}.obj"
    create_3d_text(machine, export_path, base_path)