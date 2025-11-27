#!/usr/bin/env python3
"""
Convert FortiGate .obj and .svg models to .glb format for Babylon.js
"""

import os
import subprocess
import sys
from pathlib import Path

# Model mappings - using the closest available models
MODEL_MAPPINGS = {
    # FortiGate models
    'fortigate-61e': {
        'obj': 'babylon_app/network-visualizer/models/models/FortiGate_Series_R22_2025Q2_generic.obj',
        'svg': 'babylon_app/network-visualizer/models/optimized_svgs/FortiGate_Series_R22_2025Q2_generic.svg',
        'output': 'babylon_app/network-visualizer/assets/models/fortigate-61e.glb'
    },
    # FortiSwitch models  
    'fortiswitch-124e-poe': {
        'obj': 'babylon_app/network-visualizer/models/models/FortiSwitch_Series_R14_2025Q2_generic.obj',
        'svg': 'babylon_app/network-visualizer/models/optimized_svgs/FortiSwitch_Series_R14_2025Q2_generic.svg',
        'output': 'babylon_app/network-visualizer/assets/models/fortiswitch-124e-poe.glb'
    },
    # FortiAP models
    'fortiap-231f': {
        'obj': 'babylon_app/network-visualizer/models/models/FortiAP Series_R8_2025Q2_generic.obj',
        'svg': 'babylon_app/network-visualizer/models/optimized_svgs/FortiAP Series_R8_2025Q2_generic.svg',
        'output': 'babylon_app/network-visualizer/assets/models/fortiap-231f.glb'
    }
}

def check_blender():
    """Check if Blender is available"""
    try:
        result = subprocess.run(['blender', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Blender found: {result.stdout.split()[1]}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Blender not found. Please install Blender from blender.org")
    return False

def convert_obj_to_glb(input_obj, output_glb):
    """Convert .obj to .glb using Blender"""
    blender_script = f'''
import bpy
import os

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import OBJ file
obj_file = r"{os.path.abspath(input_obj)}"
bpy.ops.wm.obj_import(filepath=obj_file)

# Select all imported objects
bpy.ops.object.select_all(action='SELECT')

# Set origin to center
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# Scale to appropriate size (1 unit = 1 meter in Babylon.js)
bpy.ops.transform.resize(value=(0.01, 0.01, 0.01))

# Center the objects
bpy.ops.object.location_clear()

# Export as GLB
glb_file = r"{os.path.abspath(output_glb)}"
bpy.ops.export_scene.gltf(
    filepath=glb_file,
    export_format='GLB',
    export_selected=True,
    export_materials='EXPORT',
    export_colors=True,
    export_cameras=False,
    export_lights=False
)

print(f"Converted {{obj_file}} to {{glb_file}}")
'''
    
    # Create temporary script file
    script_file = "temp_convert.py"
    with open(script_file, 'w') as f:
        f.write(blender_script)
    
    try:
        # Run Blender with the script
        cmd = [
            'blender', '--background', '--python', script_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Successfully converted {input_obj} to {output_glb}")
            return True
        else:
            print(f"❌ Blender conversion failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Blender conversion timed out")
        return False
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False
    finally:
        # Clean up temporary script
        if os.path.exists(script_file):
            os.remove(script_file)

def create_placeholder_models():
    """Create simple placeholder .glb files using basic geometry"""
    placeholder_script = '''
import bpy
import bmesh

def create_fortigate_placeholder():
    # Create main box
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    fortigate = bpy.context.active_object
    fortigate.name = "FortiGate-61E"
    
    # Add vent details
    bpy.ops.mesh.primitive_cube_add(size=(0.8, 0.05, 0.4), 
                                   location=(0, 0.2, 0.25))
    vent1 = bpy.context.active_object
    vent1.name = "Vent1"
    
    bpy.ops.mesh.primitive_cube_add(size=(0.8, 0.05, 0.4), 
                                   location=(0, 0.2, -0.25))
    vent2 = bpy.context.active_object
    vent2.name = "Vent2"
    
    return [fortigate, vent1, vent2]

def create_fortiswitch_placeholder():
    # Create switch box
    bpy.ops.mesh.primitive_cube_add(size=(2, 0.3, 0.8), location=(0, 0, 0))
    switch = bpy.context.active_object
    switch.name = "FortiSwitch-124E-POE"
    
    # Add port indicators
    for i in range(8):
        x = -0.7 + (i * 0.2)
        bpy.ops.mesh.primitive_cube_add(size=(0.1, 0.05, 0.1), 
                                       location=(x, -0.15, 0.4))
        port = bpy.context.active_object
        port.name = f"Port{i}"
    
    return [switch]

def create_fortiap_placeholder():
    # Create AP cylinder
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.2, 
                                        location=(0, 0, 0))
    ap = bpy.context.active_object
    ap.name = "FortiAP-231F"
    
    # Add antennas
    for i in range(6):
        angle = (i / 6) * 6.283  # 2 * PI
        x = 0.3 * (angle ** 0.5)  # Position antennas
        z = 0.3 * (angle ** 0.5)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.4, 
                                            location=(x, 0.2, z))
        antenna = bpy.context.active_object
        antenna.name = f"Antenna{i}"
    
    return [ap]

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create placeholders
models = []
models.extend(create_fortigate_placeholder())
models.extend(create_fortiswitch_placeholder())
models.extend(create_fortiap_placeholder())

# Select all models
for obj in models:
    obj.select_set(True)

# Scale down
bpy.ops.transform.resize(value=(0.01, 0.01, 0.01))

# Export individual models
for i, model in enumerate(models):
    bpy.ops.object.select_all(action='DESELECT')
    model.select_set(True)
    
    if "FortiGate" in model.name:
        bpy.ops.export_scene.gltf(
            filepath="babylon_app/network-visualizer/assets/models/fortigate-61e.glb",
            export_format='GLB',
            export_selected=True
        )
    elif "FortiSwitch" in model.name:
        bpy.ops.export_scene.gltf(
            filepath="babylon_app/network-visualizer/assets/models/fortiswitch-124e-poe.glb",
            export_format='GLB',
            export_selected=True
        )
    elif "FortiAP" in model.name:
        bpy.ops.export_scene.gltf(
            filepath="babylon_app/network-visualizer/assets/models/fortiap-231f.glb",
            export_format='GLB',
            export_selected=True
        )

print("Created placeholder models")
'''
    
    script_file = "create_placeholders.py"
    with open(script_file, 'w') as f:
        f.write(placeholder_script)
    
    try:
        cmd = ['blender', '--background', '--python', script_file]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Created placeholder models")
            return True
        else:
            print(f"❌ Placeholder creation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating placeholders: {e}")
        return False
    finally:
        if os.path.exists(script_file):
            os.remove(script_file)

def main():
    print("🚀 Starting FortiGate Model Conversion Workflow")
    print("=" * 50)
    
    # Ensure output directory exists
    output_dir = Path("babylon_app/network-visualizer/assets/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if Blender is available
    blender_available = check_blender()
    
    if blender_available:
        print("\n📦 Converting existing .obj models to .glb...")
        success_count = 0
        
        for model_name, files in MODEL_MAPPINGS.items():
            obj_file = files['obj']
            output_file = files['output']
            
            if os.path.exists(obj_file):
                if convert_obj_to_glb(obj_file, output_file):
                    success_count += 1
            else:
                print(f"⚠️  Source file not found: {obj_file}")
        
        if success_count == 0:
            print("\n🔧 Creating placeholder models...")
            create_placeholder_models()
    else:
        print("\n🔧 Blender not available, creating simple placeholder models...")
        # Create simple placeholder files without Blender
        create_simple_placeholders()
    
    print("\n✅ Model conversion workflow completed!")
    print("📁 Check babylon_app/network-visualizer/assets/models/ for .glb files")

def create_simple_placeholders():
    """Create very simple placeholder files when Blender is not available"""
    # Create empty .glb files (will trigger fallback to procedural models)
    placeholder_files = [
        'babylon_app/network-visualizer/assets/models/fortigate-61e.glb',
        'babylon_app/network-visualizer/assets/models/fortiswitch-124e-poe.glb', 
        'babylon_app/network-visualizer/assets/models/fortiap-231f.glb',
        'babylon_app/network-visualizer/assets/models/endpoint-laptop.glb',
        'babylon_app/network-visualizer/assets/models/endpoint-desktop.glb',
        'babylon_app/network-visualizer/assets/models/endpoint-mobile.glb',
        'babylon_app/network-visualizer/assets/models/endpoint-server.glb'
    ]
    
    for file_path in placeholder_files:
        Path(file_path).touch()
        print(f"📝 Created placeholder: {file_path}")

if __name__ == "__main__":
    main()
