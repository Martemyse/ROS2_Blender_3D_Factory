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

with open('ros_objekti_v1.txt') as f:
    lines = f.readlines()
traces_mapping_dict = json.loads(lines[0])
plotly_sklop_content_inner = traces_mapping_dict[1]
plotly_sklop_content_inner_instances = {k:v for k,v in plotly_sklop_content_inner.items() if not k in ['colors','number_of_traces','traces_list','legend_instances']}

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
        model = ET.SubElement(world, 'model', name=sklop_name)
        # model.set('name', sklop_name)
        
        # breakpoint()
        if object_type == 'Tlačni stroj':
            # Machines are represented with their respective dimensions in plotly
            for i, (x, y) in enumerate(zip(sklop_content_inner['x'][:-1], sklop_content_inner['y'][:-1])):  # exclude last point since it's a duplicate of the first
                link = ET.SubElement(model, 'link', name=f"machine_{i}")
            
                # Calculate machine dimensions from the provided data
                width = abs(sklop_content_inner['x'][i+1] - x) * scale
                length = abs(sklop_content_inner['y'][i+1] - y) * scale
                height = 1 # Assuming a fixed height for machines for now

                # Set the machine's position
                pose = ET.SubElement(link, 'pose')
                pose.text = f"{x + width/2} {y + length/2} {height/2} 0 0 0"  # Center the machine based on its dimensions

                # Generate the SDF for this machine
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


                # Optional: Set a blue color for the machine
                material = ET.SubElement(visual, 'material')
                ambient = ET.SubElement(material, 'ambient')
                ambient.text = "0.0 0.65098 1.0 1"  # RGBA for #00a6ff

        elif object_type == 'Topilna peč':
            # Machines are represented with their respective dimensions in plotly
            for i, (x, y) in enumerate(zip(sklop_content_inner['x'][:-1], sklop_content_inner['y'][:-1])):  # exclude last point since it's a duplicate of the first
                link = ET.SubElement(model, 'link', name=f"machine_{i}")

                # Calculate machine dimensions from the provided data
                width = abs(sklop_content_inner['x'][i+1] - x)
                length = abs(sklop_content_inner['y'][i+1] - y)
                height = 1  # Assuming a fixed height for machines for now

                # Set the machine's position
                pose = ET.SubElement(link, 'pose')
                pose.text = f"{x + width/2} {y + length/2} {height/2} 0 0 0"  # Center the machine based on its dimensions

                # Generate the SDF for this machine
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

                # Optional: Set a blue color for the machine
                material = ET.SubElement(visual, 'material')
                ambient = ET.SubElement(material, 'ambient')
                ambient.text = "1.0, 0.5098, 0.5098, 1.0" # RGBA for #00a6ff
                
        # Convert the plotly sklop_content_inner to relevant Gazebo SDF
        elif object_type == 'Zid':
            # Assuming walls are lines in plotly
            # For simplicity, we'll make a thin box for each wall segment
            # NOTE: This example assumes 2D walls.
            for i in range(len(sklop_content_inner['x']) - 1):
                link = ET.SubElement(model, 'link', name=f"segment_{i}")
            
                # Calculate geometry
                x1, y1 = sklop_content_inner['x'][i] * scale, sklop_content_inner['y'][i] * scale
                x2, y2 = sklop_content_inner['x'][i+1] * scale, sklop_content_inner['y'][i+1] * scale
            
                width = 0.1  # Assuming a fixed width for walls
                height = 2  # Assuming a fixed height for walls
                length = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5  # This computes the segment length and then it should be scaled
                
                # Calculate midpoint of the segment for positioning
                midpoint_x = (x1 + x2) / 2
                midpoint_y = (y1 + y2) / 2
                pose = ET.SubElement(link, 'pose')
                pose.text = f"{midpoint_x} {midpoint_y} {height/2} 0 0 0"
        
                # Generate the SDF for this segment
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
            line = LineString(list(zip([x * scale for x in sklop_content_inner['x']],[y * scale for y in sklop_content_inner['y']])))

            if object_type == 'Pot':
                initial_buffer = 0.05
            elif object_type == 'Pot-Thick':
                initial_buffer = 0.1
            
            path = line.buffer(initial_buffer, cap_style=3, join_style=1)
            
            # Now we create the outer and inner segments for coloring purposes.
            outer_path = path.buffer(0.02, cap_style=3, join_style=1)  # Dilating
            inner_path = outer_path.buffer(-0.02, cap_style=3, join_style=1)  # Erosion
        
            paths = {
                'outer': (outer_path.difference(inner_path), "0.502, 0.502, 0.502, 1.0"),  # grey color for outer segment
                'inner': (inner_path, "0.882, 0.882, 1.0, 1.0")  # AliceBlue for inner segment
            }
        
            for segment_type, (path_segment, color) in paths.items():
                exterior = path_segment.exterior
                for i, (x, y) in enumerate(exterior.coords[:-1]):
                    link = ET.SubElement(model, 'link', name=f"{segment_type}_segment_{i}")
                    x1, y1 = exterior.coords[i][0] * scale, exterior.coords[i][1] * scale
                    x2, y2 = exterior.coords[i+1][0] * scale, exterior.coords[i+1][1] * scale
                            
                    width = 0.1
                    height = 0.01
                    length = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5  # This computes the segment length and it is already scaled because x1,x2,y1,y2 are scaled
                    
                    midpoint_x = (x1 + x2) / 2
                    midpoint_y = (y1 + y2) / 2
                    pose = ET.SubElement(link, 'pose')
                    pose.text = f"{midpoint_x} {midpoint_y} {height/2} 0 0 0"
            
                    collision = ET.SubElement(link, 'collision', name=f"{segment_type}_collision_{i}")
                    visual = ET.SubElement(link, 'visual', name=f"{segment_type}_visual_{i}")
            
                    geometry_collision = ET.SubElement(collision, 'geometry')
                    geometry_visual = ET.SubElement(visual, 'geometry')
            
                    box_collision = ET.SubElement(geometry_collision, 'box')
                    box_visual = ET.SubElement(geometry_visual, 'box')
            
                    size_collision = ET.SubElement(box_collision, 'size')
                    size_collision.text = f"{width} {length} {height}"
                    
                    size_visual = ET.SubElement(box_visual, 'size')
                    size_visual.text = f"{width} {length} {height}"
                    
                    # Set color
                    material = ET.SubElement(visual, 'material')
                    ambient = ET.SubElement(material, 'ambient')
                    ambient.text = color
        else:
            pass


    # Convert the XML to string
    tree = ET.ElementTree(root)
    sdf_str = ET.tostring(root, encoding='unicode')
    
    return sdf_str


sdf_output = plotly_to_gazebo(plotly_sklop_content_inner_instances)
with open("Livarna_LJ_worldSDF_v1.sdf", "w") as f:
    f.write(sdf_output)

# print(sdf_output)
