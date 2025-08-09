# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 10:18:58 2023

@author: Martin-PC
"""

import xml.etree.ElementTree as ET
import json
from shapely.geometry import LineString


# with open(r'C:\Working Directory Investicije Ljubljana 2021-22\dash_podatki\Dash_Vzdrzevanje_Cilji.pickle', 'rb') as handle:
#     traces_mapping_dict = pickle.load(handle)

scale = 58.077784760408484

def scale_coordinates(data, scale_factor):
    # Check if data is a dictionary
    if isinstance(data, dict):
        # Iterate over dictionary
        for key, value in data.items():
            # Check for 'x' or 'y' keys and scale the coordinates
            if key in ['x', 'y'] and isinstance(value, list):
                data[key] = [(coord - 3) * scale_factor for coord in value]
            # Otherwise, recursively process the value
            else:
                scale_coordinates(value, scale_factor)
    # If data is a list, iterate over its items
    elif isinstance(data, list):
        for item in data:
            scale_coordinates(item, scale_factor)
    return data

with open('ROS_Objekti_v4.txt', encoding='ansi') as f:
    lines = f.readlines()
    lines = lines[0].replace('\\u010d','c').replace('\\u017e','z')
    
traces_mapping_dict = json.loads(lines)
plotly_sklop_content_inner = traces_mapping_dict[1]
scaled_dict = scale_coordinates(plotly_sklop_content_inner, scale)
plotly_sklop_content_inner_instances = {k:v for k,v in plotly_sklop_content_inner.items() if not k in ['colors','number_of_traces','traces_list','legend_instances']}


scale = 1

def plotly_to_gazebo(plotly_sklop_content_inner_instances):
    """
    Convert Plotly sklop_content_inner to Gazebo SDF format.
    """
    # Create a root SDF element
    # Create a root SDF element
    root = ET.Element('sdf', version='1.6')
    world = ET.SubElement(root, 'world', name='default')
    
    # Add global ambient light to the world
    # ambient = ET.SubElement(world, 'ambient')
    # ambient.text = '0.5 0.5 0.5 1'  # This value represents a mid-gray ambient light; adjust as needed.

    # Add Directional Light
    light = ET.SubElement(world, 'light', type='directional', name='sun')
    pose = ET.SubElement(light, 'pose')
    pose.text = '0 0 10 0 0 0'  # Adjust as needed
    diffuse = ET.SubElement(light, 'diffuse')
    # diffuse.text = '0.8 0.8 0.8 1'  # White light, you can adjust the RGB values as needed
    diffuse.text = '0.56 0.56 0.56 1'  # Reduced brightness white light
    specular = ET.SubElement(light, 'specular')
    specular.text = '0.2 0.2 0.2 1'  # Adjust the specular values as needed
    attenuation = ET.SubElement(light, 'attenuation')
    range_elem = ET.SubElement(attenuation, 'range')
    range_elem.text = '20'  # Adjust as needed
    direction = ET.SubElement(light, 'direction')
    direction.text = '0 0 -1'  # Light pointing downwards; adjust as necessary

    # Add ground plane
    # include = ET.SubElement(world, 'include')
    # uri = ET.SubElement(include, 'uri')
    # uri.text = "model://ground_plane"
    
    # Add ground plane to the SDF world
    ground_plane = ET.SubElement(world, 'model')
    ground_plane.set('name', 'ground_plane')
    ground_plane_static = ET.SubElement(ground_plane, 'static')
    ground_plane_static.text = 'true'

    ground_plane_link = ET.SubElement(ground_plane, 'link')
    ground_plane_link.set('name', 'link')

    ground_plane_collision = ET.SubElement(ground_plane_link, 'collision')
    ground_plane_collision.set('name', 'collision')
    
    ground_plane_geometry = ET.SubElement(ground_plane_collision, 'geometry')
    ground_plane_plane = ET.SubElement(ground_plane_geometry, 'plane')
    ground_plane_normal = ET.SubElement(ground_plane_plane, 'normal')
    ground_plane_normal.text = '0 0 1'
    
    # Here is the updated size for the collision property
    ground_plane_collision_size = ET.SubElement(ground_plane_plane, 'size')
    ground_plane_collision_size.text = '7500 7500'

    ground_plane_visual = ET.SubElement(ground_plane_link, 'visual')
    ground_plane_visual.set('name', 'visual')
    
    # Add the material tag here
    ground_plane_material = ET.SubElement(ground_plane_visual, 'material')
    ground_plane_ambient = ET.SubElement(ground_plane_material, 'ambient')
    ground_plane_ambient.text = '0.9608 0.9608 0.9608 1'  # RGB values for whitesmoke and an alpha of 1 for no transparency
    
    ground_plane_diffuse = ET.SubElement(ground_plane_material, 'diffuse')
    ground_plane_diffuse.text = '0.9608 0.9608 0.9608 1'  # RGB values for whitesmoke and an alpha of 1 for no transparency
    
    ground_plane_visual_geometry = ET.SubElement(ground_plane_visual, 'geometry')
    ground_plane_visual_plane = ET.SubElement(ground_plane_visual_geometry, 'plane')
    ground_plane_visual_normal = ET.SubElement(ground_plane_visual_plane, 'normal')
    ground_plane_visual_normal.text = '0 0 1'
    ground_plane_visual_size = ET.SubElement(ground_plane_visual_plane, 'size')
    ground_plane_visual_size.text = '7500 7500'



    # Convert plotly objects into gazebo objects
    for sklop_name,sklop_content_outer in plotly_sklop_content_inner_instances.items():
        
        object_type = list(sklop_content_outer.keys())[0]
        sklop_content_inner = list(sklop_content_outer.values())[0]

        # Create a Gazebo model for each plotly object
        model = ET.SubElement(world, 'model')
        model.set('name', f"{sklop_name}_{object_type.replace(' ','_')}")
        
        # Add static tag here for each model instance
        static_tag = ET.SubElement(model, 'static')
        static_tag.text = 'true'
        
        if object_type == 'Tlacni stroj':
            # For a filled cuboid, we need to get the bounding box of the machine.
            min_x, max_x = min(sklop_content_inner['x']), max(sklop_content_inner['x'])
            min_y, max_y = min(sklop_content_inner['y']), max(sklop_content_inner['y'])

            width = abs(max_x - min_x)
            length = abs(max_y - min_y)
            height = 2  # Adjust this if you want the height scaled as well.

            link = ET.SubElement(model, 'link', name=f"machine_link")

            # Calculating the midpoint for pose
            midpoint_x = (min_x + max_x) / 2
            midpoint_y = (min_y + max_y) / 2
            pose = ET.SubElement(link, 'pose')
            pose.text = f"{midpoint_x} {midpoint_y} {height/2} 0 0 0"

            # Generate the SDF for this machine
            collision = ET.SubElement(link, 'collision', name=f"collision")
            visual = ET.SubElement(link, 'visual', name=f"visual")

            geometry_collision = ET.SubElement(collision, 'geometry')
            geometry_visual = ET.SubElement(visual, 'geometry')

            box_collision = ET.SubElement(geometry_collision, 'box')
            box_visual = ET.SubElement(geometry_visual, 'box')

            size_collision = ET.SubElement(box_collision, 'size')
            size_collision.text = f"{width} {length} {height}"

            size_visual = ET.SubElement(box_visual, 'size')
            size_visual.text = f"{width} {length} {height}"

            # Optional: Set a blue color for the machine
            material = ET.SubElement(visual, 'material')
            ambient = ET.SubElement(material, 'ambient')
            ambient.text = "0.0 0.65098 1.0 1"  # RGBA for #00a6ff

            # Adding the 3D text model on top of the cuboid:
            text_visual = ET.SubElement(link, 'visual', name=f"{sklop_name}_text_visual")
            text_geometry = ET.SubElement(text_visual, 'geometry')
            text_mesh = ET.SubElement(text_geometry, 'mesh')
            text_uri = ET.SubElement(text_mesh, 'uri')
            text_uri.text = f"model://{sklop_name}/{sklop_name}.dae"
            # text_uri.text = f"model://{sklop_name}"
            # text_uri.text = f"model://localros/text_3d_models/{sklop_name}"
            # text_uri.text = f"/localros/text_3d_models/{sklop_name}"


            # text_scale_factor = 0.02  # adjust this as needed
            text_scale_factor = 2  # adjust this as needed
            text_scale = ET.SubElement(text_mesh, 'scale')
            text_scale.text = f"{text_scale_factor} {text_scale_factor} {text_scale_factor}"

            text_model_height = 0.03  # adjust this as per the height of your 3D text model
            adjusted_z = height/2 + text_model_height/2
            
            # Adjust X, Y, and Z positions
            scale_offset_x = -1.0
            scale_offset_y = -1.0
            offset_x, offset_y, offset_z = -2.5, -0.7, 0  # Adjust these offsets based on your observations
            
            text_pose = ET.SubElement(text_visual, 'pose')
            text_pose.text = f"{midpoint_x + midpoint_x*scale_offset_x + offset_x} {midpoint_y + midpoint_y*scale_offset_y + offset_y} {adjusted_z + offset_z} 0 0 0"



        elif object_type == 'Topilna pec':
            # For a filled cuboid, we need to get the bounding box of the machine.
            min_x, max_x = min(sklop_content_inner['x']), max(sklop_content_inner['x'])
            min_y, max_y = min(sklop_content_inner['y']), max(sklop_content_inner['y'])
        
            width = abs(max_x - min_x)
            length = abs(max_y - min_y)
            height = 2  # Adjust this if you want the height scaled as well.
        
            link = ET.SubElement(model, 'link', name=f"machine_link")
        
            # Calculating the midpoint for pose
            midpoint_x = (min_x + max_x) / 2
            midpoint_y = (min_y + max_y) / 2
            pose = ET.SubElement(link, 'pose')
            pose.text = f"{midpoint_x} {midpoint_y} {height/2} 0 0 0"
        
            # Generate the SDF for this machine
            collision = ET.SubElement(link, 'collision', name=f"collision")
            visual = ET.SubElement(link, 'visual', name=f"visual")
        
            geometry_collision = ET.SubElement(collision, 'geometry')
            geometry_visual = ET.SubElement(visual, 'geometry')
        
            box_collision = ET.SubElement(geometry_collision, 'box')
            box_visual = ET.SubElement(geometry_visual, 'box')
        
            size_collision = ET.SubElement(box_collision, 'size')
            size_collision.text = f"{width} {length} {height}"
            
            size_visual = ET.SubElement(box_visual, 'size')
            size_visual.text = f"{width} {length} {height}"

            # Optional: Set a blue color for the machine
            material = ET.SubElement(visual, 'material')
            ambient = ET.SubElement(material, 'ambient')
            ambient.text = "1.0, 0.5098, 0.5098, 1.0" # RGBA for #00a6ff
            
            # Adding the 3D text model on top of the cuboid:
            text_visual = ET.SubElement(link, 'visual', name=f"{sklop_name}_text_visual")
            text_geometry = ET.SubElement(text_visual, 'geometry')
            text_mesh = ET.SubElement(text_geometry, 'mesh')
            text_uri = ET.SubElement(text_mesh, 'uri')
            text_uri.text = f"model://{sklop_name}/{sklop_name}.dae"
            # text_uri.text = f"model://{sklop_name}"
            # text_uri.text = f"model://localros/text_3d_models/{sklop_name}"
            # text_uri.text = f"/localros/text_3d_models/{sklop_name}"

            # text_scale_factor = 0.02  # adjust this as needed
            text_scale_factor = 2  # adjust this as needed
            text_scale = ET.SubElement(text_mesh, 'scale')
            text_scale.text = f"{text_scale_factor} {text_scale_factor} {text_scale_factor}"

            text_model_height = 0.03  # adjust this as per the height of your 3D text model
            adjusted_z = height/2 + text_model_height/2
            
            # Adjust X, Y, and Z positions
            scale_offset_x = -1.0
            scale_offset_y = -1.0
            offset_x, offset_y, offset_z = -2.5, -0.7, 0  # Adjust these offsets based on your observations
            
            text_pose = ET.SubElement(text_visual, 'pose')
            text_pose.text = f"{midpoint_x + midpoint_x*scale_offset_x + offset_x} {midpoint_y + midpoint_y*scale_offset_y + offset_y} {adjusted_z + offset_z} 0 0 0"
                
        # Convert the plotly sklop_content_inner to relevant Gazebo SDF
        elif object_type == 'Zid':
            # Extracting and concatenating the x and y values from the 'steps' dictionary
            x_values = [item for step in sklop_content_inner['steps'].values() for item in step['x']]
            y_values = [item for step in sklop_content_inner['steps'].values() for item in step['y']]
        
            for i in range(len(x_values) - 1):
                
                x1, y1 = x_values[i], y_values[i]
                x2, y2 = x_values[i+1], y_values[i+1]
                
                # Create a shapely line from the start and end points
                line = LineString([(x1, y1), (x2, y2)])
                # Dilate the line to create the wall's thickness
                wall = line.buffer(0.1, cap_style=2, join_style=2)  # using butt cap for straight walls
                
                # Using the bounding box of the dilated wall to represent it
                minx, miny, maxx, maxy = wall.bounds
                
                width = maxx - minx
                length = maxy - miny
                height = 4  # As you've defined
                
                # Midpoint of the bounding box
                midpoint_x = (minx + maxx) / 2
                midpoint_y = (miny + maxy) / 2
                
                link = ET.SubElement(model, 'link', name=f"segment_{i}")
                
                pose = ET.SubElement(link, 'pose')
                pose.text = f"{midpoint_x} {midpoint_y} {height/2} 0 0 0"
                
                collision = ET.SubElement(link, 'collision', name=f"collision_{i}")
                visual = ET.SubElement(link, 'visual', name=f"visual_{i}")
                
                geometry_collision = ET.SubElement(collision, 'geometry')
                geometry_visual = ET.SubElement(visual, 'geometry')
                
                box_collision = ET.SubElement(geometry_collision, 'box')
                box_visual = ET.SubElement(geometry_visual, 'box')
                
                size_collision = ET.SubElement(box_collision, 'size')
                size_collision.text = f"{width} {length} {height}"
                
                size_visual = ET.SubElement(box_visual, 'size')
                size_visual.text = f"{width} {length} {height}"


                
        elif object_type == 'Pot' or object_type == 'Pot-Thick':
            # Extracting and concatenating the x and y values from the 'steps' dictionary
            x_values = [item for step in sklop_content_inner['steps'].values() for item in step['x']]
            y_values = [item for step in sklop_content_inner['steps'].values() for item in step['y']]
        
            if object_type == 'Pot':
                initial_buffer = 0.05
            # elif object_type == 'Pot-Thick':
            #     initial_buffer = 3
        
            for i in range(len(x_values) - 1):
                
                x1, y1 = x_values[i], y_values[i]
                x2, y2 = x_values[i+1], y_values[i+1]
                
                # Create a shapely line from the start and end points
                line = LineString([(x1, y1), (x2, y2)])
                # Dilate the line to create the thickness (for instance, 0.1 units in this case)
                path = line.buffer(initial_buffer, cap_style=2, join_style=2)  # using butt cap for straight paths
                
                # Using the bounding box of the dilated path to represent it
                minx, miny, maxx, maxy = path.bounds
                
                width = maxx - minx
                length = maxy - miny
                height = 0.1  # As you've defined
                
                # Midpoint of the bounding box
                midpoint_x = (minx + maxx) / 2
                midpoint_y = (miny + maxy) / 2
                
                link = ET.SubElement(model, 'link', name=f"segment_{i}")
                
                pose = ET.SubElement(link, 'pose')
                pose.text = f"{midpoint_x} {midpoint_y} {height/2} 0 0 0"
                
                collision = ET.SubElement(link, 'collision', name=f"collision_{i}")
                visual = ET.SubElement(link, 'visual', name=f"visual_{i}")
                
                geometry_collision = ET.SubElement(collision, 'geometry')
                geometry_visual = ET.SubElement(visual, 'geometry')
                
                box_collision = ET.SubElement(geometry_collision, 'box')
                box_visual = ET.SubElement(geometry_visual, 'box')
                
                size_collision = ET.SubElement(box_collision, 'size')
                size_collision.text = f"{width} {length} {height}"
                
                size_visual = ET.SubElement(box_visual, 'size')
                size_visual.text = f"{width} {length} {height}"
                
                # Optional: Set a Gainsboro color for the path
                material = ET.SubElement(visual, 'material')
                ambient = ET.SubElement(material, 'ambient')
                # ambient.text = "0.1627, 0.1627, 0.8627, 1.0" # RGBA for Gainsboro
                ambient.text = "1.0, 1.0, 0.3, 1.0"  # Yellow

        else:
            pass


    # Convert the XML to string
    tree = ET.ElementTree(root)
    sdf_str = ET.tostring(root, encoding='unicode')
    
    return sdf_str


sdf_output = plotly_to_gazebo(plotly_sklop_content_inner_instances)
with open("Livarna_LJ_worldSDF_v2.sdf", "w") as f:
    f.write(sdf_output)

# print(sdf_output)
