import sys
import os
import pathlib
# Add user site-packages to path
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python313\site-packages")
if user_site not in sys.path:
    sys.path.append(user_site)

# Try importing pyvisio, handle if it fails
try:
    from pyvisio import open as open_vss
except ImportError as e:
    print(f"Error: pyvisio not installed. {e}")
    print(f"Sys Path: {sys.path}")
    sys.exit(1)

def extract_icons(vss_path, output_dir):
    print(f"Processing {vss_path}...")
    try:
        doc = open_vss(pathlib.Path(vss_path))
        
        vss_name = pathlib.Path(vss_path).stem
        target_dir = os.path.join(output_dir, vss_name)
        os.makedirs(target_dir, exist_ok=True)
        
        # Check if doc has shapes attribute directly or if we need to iterate differently
        shapes = getattr(doc, 'shapes', [])
        
        for i, shape in enumerate(shapes):
            try:
                # Sanitize name
                name = getattr(shape, 'name', f"shape_{i}")
                safe_name = "".join([c if c.isalnum() else "_" for c in name])
                
                svg_path = os.path.join(target_dir, f"{i}_{safe_name}.svg")
                
                # pyvisio to_svg
                if hasattr(shape, 'to_svg'):
                    shape.to_svg(svg_path)
                    print(f"Extracted: {svg_path}")
                else:
                    print(f"Shape {i} has no to_svg method")
            except Exception as e:
                print(f"Error extracting shape {i}: {e}")
                
    except Exception as e:
        print(f"Failed to open {vss_path}: {e}")

if __name__ == "__main__":
    vss_dir = "shared/fortinet"
    out_dir = "babylon_3d/babylon_app/network-visualizer/assets/extracted_icons_pyvisio"
    
    if not os.path.exists(vss_dir):
        print(f"Directory not found: {vss_dir}")
        sys.exit(1)
        
    for file in os.listdir(vss_dir):
        if file.lower().endswith(".vss"):
            extract_icons(os.path.join(vss_dir, file), out_dir)
