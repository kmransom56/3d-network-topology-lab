import os
import re
import base64

def extract_emfs(html_path, output_dir):
    print(f"Processing {html_path}...")
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {html_path}: {e}")
        return

    # Regex to find base64 EMF data
    # Looks for xlink:href="data:image/emf;base64,..."
    emf_pattern = re.compile(r'data:image/emf;base64,([A-Za-z0-9+/=\s]+)', re.IGNORECASE)
    
    matches = emf_pattern.findall(content)
    
    print(f"Found {len(matches)} EMF images.")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for i, b64_data in enumerate(matches):
        # Clean up whitespace/newlines from base64 string
        b64_data = re.sub(r'\s+', '', b64_data)
        
        try:
            emf_bytes = base64.b64decode(b64_data)
            
            # Try to find a name from the surrounding context if possible
            # (This is hard with just regex on the whole file, so we'll just use index for now)
            filename = f"icon_{i}.emf"
            output_path = os.path.join(output_dir, filename)
            
            with open(output_path, 'wb') as f:
                f.write(emf_bytes)
                
        except Exception as e:
            print(f"Error decoding/writing EMF {i}: {e}")
            
    print(f"Extracted {len(matches)} EMFs to {output_dir}")

if __name__ == "__main__":
    base_dir = "babylon_3d/babylon_app/network-visualizer/assets/extracted_icons_docker"
    
    # Walk through directories to find index.html files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == "index.html":
                html_path = os.path.join(root, file)
                # Output to a 'emfs' subdirectory
                output_dir = os.path.join(root, "emfs")
                extract_emfs(html_path, output_dir)
