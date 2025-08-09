# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 21:41:22 2023

@author: Martin-PC
"""

import xml.etree.ElementTree as ET

def plotly_to_gazebo(plotly_fig, output_filename="output.sdf"):
    # Create the root SDF element
    root = ET.Element('sdf', version="1.6")
    world = ET.SubElement(root, 'world', name='default')
    
    # # Add global ambient light to the world
    # ambient = ET.SubElement(world, 'ambient')
    # ambient.text = '0.5 0.5 0.5 1'  # This value represents a mid-gray ambient light; adjust as needed.

    # Add Directional Light
    light = ET.SubElement(world, 'light', type='directional', name='sun')
    pose = ET.SubElement(light, 'pose')
    pose.text = '0 0 10 0 0 0'  # Adjust as needed
    diffuse = ET.SubElement(light, 'diffuse')
    diffuse.text = '0.8 0.8 0.8 1'  # White light, you can adjust the RGB values as needed
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
    ground_plane_visual_size.text = '100 100'


    
    # 1. Extract Data from Plotly:
    # For simplicity, let's say we are only interested in scatter plots and their points
    scatter_data = plotly_fig['data'][0]  # assuming first trace is scatter
    x_data = scatter_data['x']
    y_data = scatter_data['y']
    
    # 2. Convert Data to SDF:
    for i, (x, y) in enumerate(zip(x_data, y_data)):
        model = ET.SubElement(world, 'model', name=f"point_{i}")
        pose = ET.SubElement(model, 'pose')
        pose.text = f"{x} {y} 0 0 0 0"
        
        link = ET.SubElement(model, 'link', name='link')
        
        # Add a simple box for visualization of the point
        collision = ET.SubElement(link, 'collision', name='collision')
        geometry = ET.SubElement(collision, 'geometry')
        box = ET.SubElement(geometry, 'box')
        size = ET.SubElement(box, 'size')
        size.text = "0.1 0.1 0.1"  # fixed size for simplicity

        visual = ET.SubElement(link, 'visual', name='visual')
        geometry_visual = ET.SubElement(visual, 'geometry')
        box_visual = ET.SubElement(geometry_visual, 'box')
        size_visual = ET.SubElement(box_visual, 'size')
        size_visual.text = "0.1 0.1 0.1"

        # Adding a bright color for better visibility
        material = ET.SubElement(visual, 'material')
        ambient = ET.SubElement(material, 'ambient')
        ambient.text = "0 1 0 1"  # Bright green color

    # 3. Output & Save as SDF File:
    tree = ET.ElementTree(root)
    tree.write(output_filename, encoding='utf-8', xml_declaration=True)

# Test with a sample plotly figure
plotly_fig = {
    'data': [
        {
            'type': 'scatter',
            'x': [1, 2, 3],
            'y': [1, 2, 3]
        }
    ]
}
plotly_to_gazebo(plotly_fig)
