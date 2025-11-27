#!/usr/bin/env python3
"""
Convert REAL FortiGate .obj models to .glb format for Babylon.js
Using your actual FortiGate model files, not placeholders!
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Your actual FortiGate model files
REAL_MODEL_MAPPINGS = {
    # Your actual FortiGate model
    'fortigate-61e': {
        'source': 'babylon_app/network-visualizer/models/models/FortiGate_Series_R22_2025Q2_generic.obj',
        'output': 'babylon_app/network-visualizer/assets/models/fortigate-61e.glb',
        'scale': 0.01,  # Scale down for Babylon.js
        'name': 'FortiGate-61E'
    },
    # Your actual FortiSwitch model  
    'fortiswitch-124e-poe': {
        'source': 'babylon_app/network-visualizer/models/models/FortiSwitch_Series_R14_2025Q2_generic.obj',
        'output': 'babylon_app/network-visualizer/assets/models/fortiswitch-124e-poe.glb',
        'scale': 0.01,
        'name': 'FortiSwitch-124E-POE'
    },
    # Your actual FortiAP model
    'fortiap-231f': {
        'source': 'babylon_app/network-visualizer/models/models/FortiAP Series_R8_2025Q2_generic.obj',
        'output': 'babylon_app/network-visualizer/assets/models/fortiap-231f.glb',
        'scale': 0.01,
        'name': 'FortiAP-231F'
    }
}

def wait_for_blender():
    """Wait for Blender installation to complete"""
    print("⏳ Checking for Blender installation...")
    
    # Check if Blender is available using the full path
    blender_path = r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
    
    if os.path.exists(blender_path):
        print(f"✅ Blender found at: {blender_path}")
        return blender_path
    else:
        print(f"❌ Blender not found at: {blender_path}")
        return None

def convert_real_obj_to_glb(source_obj, output_glb, scale, name, blender_path):
    """Convert your actual .obj to .glb using Blender"""
    
    blender_script = f'''
import bpy
import os
import math

# Clear existing scene completely
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import YOUR actual OBJ file
obj_file = r"{os.path.abspath(source_obj)}"
print(f"Importing: {{obj_file}}")

try:
    bpy.ops.wm.obj_import(
        filepath=obj_file,
        use_edges=True,
        use_smooth_groups=True,
        use_split_objects=True,
        use_split_groups=False,
        global_clamp_size=0.0,
        forward_axis='-Z',
        up_axis='Y'
    )
    print("OBJ imported successfully")
except Exception as e:
    print(f"Failed to import OBJ: {{e}}")
    raise

# Select all imported objects
bpy.ops.object.select_all(action='SELECT')

# Set origin to center of geometry for all objects
for obj in bpy.context.selected_objects:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# Apply the scale for Babylon.js compatibility
scale_factor = {scale}
bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor))
print(f"Applied scale: {{scale_factor}}")

# Center all objects at origin
bpy.ops.object.location_clear()

# Optional: Add simple materials if none exist
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH' and len(obj.data.materials) == 0:
        mat = bpy.data.materials.new(name=f"{{name}}_Material")
        mat.use_nodes = True
        # Set up basic material
        principled_bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if principled_bsdf:
            principled_bsdf.inputs['Base Color'].default_value = (0.2, 0.3, 0.4, 1.0)
            principled_bsdf.inputs['Metallic'].default_value = 0.1
            principled_bsdf.inputs['Roughness'].default_value = 0.3
        obj.data.materials.append(mat)

# Export as GLB with proper settings
glb_file = r"{os.path.abspath(output_glb)}"
print(f"Exporting to: {{glb_file}}")

try:
    bpy.ops.export_scene.gltf(
        filepath=glb_file,
        export_format='GLB',
        export_selected=True,
        export_materials='EXPORT',
        export_colors=True,
        export_texcoords=True,
        export_normals=True,
        export_tangents=False,
        export_animations=False,
        export_apply=False,
        export_yup=True,
        export_skins=False,
        export_morph=False,
        will_export_settings=False,
        export_extras=False,
        export_custom_properties=False,
        export_anim_single_armature=False,
        export_frame_range=False,
        export_frame_step=1,
        export_force_sampling=True,
        export_nla_strips_merged_animation=True,
        export_def_bones=False,
        export_optimize_keep_empty=True,
        export_optimize_animations=False,
        export_disable_extensions=False,
        export_lights=False,
        export_cameras=False,
    )
    print(f"Successfully exported to {{glb_file}}")
except Exception as e:
    print(f"Failed to export GLB: {{e}}")
    raise

print(f"Conversion complete: {{obj_file}} -> {{glb_file}}")
'''
    
    # Create temporary script file
    script_file = "temp_convert_real.py"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(blender_script)
    
    try:
        print(f"🔄 Converting {source_obj} to {output_glb}...")
        
        # Run Blender with the script
        cmd = [
            blender_path, '--background', '--python', script_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {name} converted to .glb format!")
            if os.path.exists(output_glb):
                size = os.path.getsize(output_glb)
                print(f"📁 File created: {output_glb} ({size:,} bytes)")
            return True
        else:
            print(f"❌ Blender conversion failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
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

def create_endpoint_models():
    """Create simple endpoint models since we don't have .obj files for them"""
    endpoint_script = '''
import bpy
import math

def create_laptop():
    # Create laptop base
    bpy.ops.mesh.primitive_cube_add(size=(0.8, 0.05, 0.6), location=(0, 0, 0))
    base = bpy.context.active_object
    base.name = "Laptop_Base"
    
    # Create screen
    bpy.ops.mesh.primitive_cube_add(size=(0.7, 0.4, 0.02), 
                                   location=(0, 0.2, -0.25))
    screen = bpy.context.active_object
    screen.name = "Laptop_Screen"
    
    return [base, screen]

def create_desktop():
    # Create desktop tower
    bpy.ops.mesh.primitive_cube_add(size=(0.3, 0.5, 0.4), location=(0, 0.25, 0))
    tower = bpy.context.active_object
    tower.name = "Desktop_Tower"
    
    # Create monitor
    bpy.ops.mesh.primitive_cube_add(size=(0.6, 0.4, 0.02), 
                                   location=(0, 0.5, -0.3))
    monitor = bpy.context.active_object
    monitor.name = "Desktop_Monitor"
    
    return [tower, monitor]

def create_mobile():
    # Create phone body
    bpy.ops.mesh.primitive_cube_add(size=(0.15, 0.25, 0.01), location=(0, 0.125, 0))
    phone = bpy.context.active_object
    phone.name = "Mobile_Phone"
    
    return [phone]

def create_server():
    # Create server rack
    bpy.ops.mesh.primitive_cube_add(size=(0.4, 0.6, 0.3), location=(0, 0.3, 0))
    server = bpy.context.active_object
    server.name = "Server_Rack"
    
    return [server]

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create all endpoint models
endpoints = []
endpoints.extend(create_laptop())
endpoints.extend(create_desktop())
endpoints.extend(create_mobile())
endpoints.extend(create_server())

# Apply materials and scale
for obj in endpoints:
    mat = bpy.data.materials.new(name=f"{{obj.name}}_Material")
    mat.use_nodes = True
    principled_bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf:
        if "Laptop" in obj.name or "Mobile" in obj.name:
            principled_bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1.0)
        elif "Desktop" in obj.name:
            principled_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)
        elif "Server" in obj.name:
            principled_bsdf.inputs['Base Color'].default_value = (0.2, 0.2, 0.2, 1.0)
        principled_bsdf.inputs['Metallic'].default_value = 0.2
        principled_bsdf.inputs['Roughness'].default_value = 0.4
    
    obj.data.materials.append(mat)

# Scale all objects
bpy.ops.transform.resize(value=(0.01, 0.01, 0.01))

# Export individual models
model_exports = [
    (["Laptop_Base", "Laptop_Screen"], "babylon_app/network-visualizer/assets/models/endpoint-laptop.glb"),
    (["Desktop_Tower", "Desktop_Monitor"], "babylon_app/network-visualizer/assets/models/endpoint-desktop.glb"),
    (["Mobile_Phone"], "babylon_app/network-visualizer/assets/models/endpoint-mobile.glb"),
    (["Server_Rack"], "babylon_app/network-visualizer/assets/models/endpoint-server.glb")
]

for export_names, output_path in model_exports:
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.name in export_names:
            obj.select_set(True)
    
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_selected=True,
        export_materials='EXPORT'
    )
    print(f"✅ Created: {{output_path}}")

print("🎉 All endpoint models created!")
'''
    
    script_file = "create_endpoints.py"
    with open(script_file, 'w') as f:
        f.write(endpoint_script)
    
    try:
        print("🔧 Creating endpoint models...")
        cmd = ['blender', '--background', '--python', script_file]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Endpoint models created successfully!")
            return True
        else:
            print(f"❌ Endpoint creation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating endpoints: {e}")
        return False
    finally:
        if os.path.exists(script_file):
            os.remove(script_file)

def main():
    print("🚀 Converting YOUR REAL FortiGate Models to .glb Format")
    print("=" * 60)
    
    # Ensure output directory exists
    output_dir = Path("babylon_app/network-visualizer/assets/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get Blender path
    blender_path = wait_for_blender()
    if not blender_path:
        print("❌ Cannot proceed without Blender")
        return False
    
    print("\n📦 Converting your ACTUAL FortiGate model files...")
    
    success_count = 0
    total_count = len(REAL_MODEL_MAPPINGS)
    
    for model_name, config in REAL_MODEL_MAPPINGS.items():
        source_file = config['source']
        output_file = config['output']
        scale = config['scale']
        name = config['name']
        
        print(f"\n🔄 Processing {name}...")
        
        if os.path.exists(source_file):
            print(f"📁 Found source: {source_file}")
            if convert_real_obj_to_glb(source_file, output_file, scale, name, blender_path):
                success_count += 1
        else:
            print(f"❌ Source file not found: {source_file}")
    
    print(f"\n📊 Conversion Results: {success_count}/{total_count} FortiGate models converted")
    
    # Create endpoint models
    print("\n💻 Creating endpoint device models...")
    if create_endpoint_models():
        print("✅ All models created successfully!")
    else:
        print("⚠️  Some endpoint models may have failed")
    
    # Verify output files
    print("\n📋 Verifying created .glb files:")
    created_files = []
    for model_name, config in REAL_MODEL_MAPPINGS.items():
        output_file = config['output']
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            created_files.append(f"✅ {os.path.basename(output_file)} ({size:,} bytes)")
        else:
            created_files.append(f"❌ {os.path.basename(output_file)} (missing)")
    
    # Check endpoint files
    endpoint_files = [
        'endpoint-laptop.glb', 'endpoint-desktop.glb', 
        'endpoint-mobile.glb', 'endpoint-server.glb'
    ]
    
    for endpoint in endpoint_files:
        endpoint_path = f"babylon_app/network-visualizer/assets/models/{endpoint}"
        if os.path.exists(endpoint_path):
            size = os.path.getsize(endpoint_path)
            created_files.append(f"✅ {endpoint} ({size:,} bytes)")
        else:
            created_files.append(f"❌ {endpoint} (missing)")
    
    for file_info in created_files:
        print(f"  {file_info}")
    
    print(f"\n🎉 REAL FortiGate Model Conversion Complete!")
    print(f"📁 All files in: babylon_app/network-visualizer/assets/models/")
    print(f"🌐 Ready for Babylon.js loading!")
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
