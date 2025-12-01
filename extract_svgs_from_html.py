import os
import re

def extract_svgs(html_path, output_dir):
    print(f"Processing {html_path}...")
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {html_path}: {e}")
        return

    # Regex to find SVG blocks
    # This is a simple regex and might need adjustment if the HTML is complex
    # It looks for <svg ... </svg> across multiple lines
    svg_pattern = re.compile(r'(<svg[^>]*>.*?</svg>)', re.DOTALL | re.IGNORECASE)
    
    svgs = svg_pattern.findall(content)
    
    print(f"Found {len(svgs)} SVG elements.")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for i, svg_content in enumerate(svgs):
        # Try to find a title for the filename
        title_match = re.search(r'<title[^>]*>(.*?)</title>', svg_content, re.IGNORECASE)
        if title_match:
            name = title_match.group(1).strip()
            safe_name = "".join([c if c.isalnum() else "_" for c in name])
            filename = f"{i}_{safe_name}.svg"
        else:
            filename = f"icon_{i}.svg"
            
        output_path = os.path.join(output_dir, filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
        except Exception as e:
            print(f"Error writing {output_path}: {e}")
            
    print(f"Extracted {len(svgs)} SVGs to {output_dir}")

if __name__ == "__main__":
    base_dir = "babylon_3d/babylon_app/network-visualizer/assets/extracted_icons_docker"
    
    # Walk through directories to find index.html files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == "index.html":
                html_path = os.path.join(root, file)
                # Output to a 'svgs' subdirectory
                output_dir = os.path.join(root, "svgs")
                extract_svgs(html_path, output_dir)
