#!/usr/bin/env python3
"""
SVG to 3D Converter Pipeline
Converts SVG icons to 3D models suitable for Babylon.js
"""

import os
import subprocess
import json
from pathlib import Path
import logging
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SVGTo3DConverter:
    """Convert SVG files to 3D models for Babylon.js"""
    
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def optimize_svg_for_3d(self, svg_path: Path) -> Path:
        """Optimize SVG file for 3D conversion"""
        optimized_path = self.output_dir / "optimized_svgs" / svg_path.name
        optimized_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Parse SVG
            tree = ET.parse(svg_path)
            root = tree.getroot()
            
            # Remove unnecessary attributes
            for elem in root.iter():
                # Remove attributes that aren't needed for 3D
                attrs_to_remove = ['style', 'fill-opacity', 'stroke-opacity', 'opacity']
                for attr in attrs_to_remove:
                    if attr in elem.attrib:
                        del elem.attrib[attr]
                
                # Convert text elements to paths if possible
                if elem.tag.endswith('text'):
                    # For now, we'll keep text as is, but in a real implementation,
                    # you'd want to convert text to paths using a library like svg.path
                    pass
            
            # Set standard dimensions
            root.set('width', '100')
            root.set('height', '100')
            root.set('viewBox', '0 0 100 100')
            
            # Save optimized SVG
            tree.write(optimized_path, encoding='utf-8', xml_declaration=True)
            logger.info(f"Optimized SVG: {svg_path.name}")
            return optimized_path
            
        except Exception as e:
            logger.error(f"Failed to optimize {svg_path}: {e}")
            return svg_path
    
    def svg_to_obj(self, svg_path: Path) -> Optional[Path]:
        """Convert SVG to OBJ file using Blender (if available)"""
        obj_path = self.output_dir / "models" / f"{svg_path.stem}.obj"
        obj_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a simple OBJ representation (rectangular prism for each shape)
        # In a real implementation, you'd use Blender or another 3D converter
        obj_content = f"""# Generated from {svg_path.name}
# Simple rectangular prism representation

o {svg_path.stem}
v 0 0 0
v 1 0 0
v 1 1 0
v 0 1 0
v 0 0 0.1
v 1 0 0.1
v 1 1 0.1
v 0 1 0.1

f 1 2 3 4
f 5 8 7 6
f 1 5 6 2
f 2 6 7 3
f 3 7 8 4
f 4 8 5 1
"""
        
        obj_path.write_text(obj_content)
        logger.info(f"Created OBJ: {obj_path.name}")
        return obj_path
    
    def create_babylon_js_manifest(self, svg_files: List[Path]) -> Path:
        """Create a manifest file for Babylon.js"""
        manifest = {
            "version": "1.0",
            "models": []
        }
        
        for svg_file in svg_files:
            model_info = {
                "name": svg_file.stem,
                "svgPath": f"optimized_svgs/{svg_file.name}",
                "objPath": f"models/{svg_file.stem}.obj" if (self.output_dir / "models" / f"{svg_file.stem}.obj").exists() else None,
                "category": self.categorize_device(svg_file.stem),
                "tags": self.extract_tags(svg_file.stem)
            }
            manifest["models"].append(model_info)
        
        manifest_path = self.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        logger.info(f"Created manifest: {manifest_path.name}")
        return manifest_path
    
    def categorize_device(self, filename: str) -> str:
        """Categorize device based on filename"""
        filename_lower = filename.lower()
        
        categories = {
            "firewall": ["fortigate", "firewall", "fg"],
            "switch": ["switch", "fortiswitch", "fs"],
            "access_point": ["ap", "fortiap", "wifi", "wireless"],
            "router": ["router", "fortinet"],
            "security": ["fortinet", "security", "utm"],
            "other": ["accessories", "other"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in filename_lower for keyword in keywords):
                return category
        
        return "unknown"
    
    def extract_tags(self, filename: str) -> List[str]:
        """Extract tags from filename"""
        tags = []
        filename_lower = filename.lower()
        
        # Common Fortinet product tags
        if "fortigate" in filename_lower:
            tags.append("firewall")
        if "switch" in filename_lower:
            tags.append("switch")
        if "ap" in filename_lower:
            tags.append("access_point")
        if "fibre" in filename_lower or "fiber" in filename_lower:
            tags.append("fiber")
        if "wifi" in filename_lower or "wireless" in filename_lower:
            tags.append("wireless")
        
        return tags
    
    def create_babylon_loader_script(self, manifest_path: Path) -> Path:
        """Create a Babylon.js loader script"""
        script_content = f"""// Auto-generated Babylon.js 3D Icon Loader
// Generated from VSS to SVG conversion

class Icon3DLoader {{
    constructor(scene) {{
        this.scene = scene;
        this.models = new Map();
        this.loadManifest();
    }}
    
    async loadManifest() {{
        try {{
            const response = await fetch('{manifest_path.name}');
            const manifest = await response.json();
            
            for (const modelInfo of manifest.models) {{
                await this.loadModel(modelInfo);
            }}
        }} catch (error) {{
            console.error('Failed to load manifest:', error);
        }}
    }}
    
    async loadModel(modelInfo) {{
        try {{
            // For now, create a simple box mesh for each icon
            // In a real implementation, you'd load the actual 3D model
            const mesh = BABYLON.MeshBuilder.CreateBox(modelInfo.name, 
                {{width: 1, height: 1, depth: 0.1}}, this.scene);
            
            // Add metadata
            mesh.metadata = {{
                name: modelInfo.name,
                category: modelInfo.category,
                tags: modelInfo.tags,
                svgPath: modelInfo.svgPath
            }};
            
            // Create a simple material
            const material = new BABYLON.StandardMaterial(`${{modelInfo.name}}_mat`, this.scene);
            material.diffuseColor = new BABYLON.Color3(0.2, 0.4, 0.8);
            mesh.material = material;
            
            this.models.set(modelInfo.name, mesh);
            console.log(`Loaded model: ${{modelInfo.name}}`);
        }} catch (error) {{
            console.error(`Failed to load model ${{modelInfo.name}}:`, error);
        }}
    }}
    
    getModel(name) {{
        return this.models.get(name);
    }}
    
    getModelsByCategory(category) {{
        const results = [];
        for (const [name, mesh] of this.models) {{
            if (mesh.metadata.category === category) {{
                results.push(mesh);
            }}
        }}
        return results;
    }}
    
    getModelsByTag(tag) {{
        const results = [];
        for (const [name, mesh] of this.models) {{
            if (mesh.metadata.tags && mesh.metadata.tags.includes(tag)) {{
                results.push(mesh);
            }}
        }}
        return results;
    }}
}}

// Usage in your Babylon.js application:
// const iconLoader = new Icon3DLoader(scene);
// const fortigate = iconLoader.getModel('FortiGate_60F');
// if (fortigate) {{
//     fortigate.position = new BABYLON.Vector3(0, 1, 0);
// }}
"""
        
        script_path = self.output_dir / "babylon-icon-loader.js"
        script_path.write_text(script_content)
        logger.info(f"Created Babylon.js loader: {script_path.name}")
        return script_path
    
    def process_all_svgs(self) -> Dict[str, List[Path]]:
        """Process all SVG files in the input directory"""
        results = {
            "optimized": [],
            "models": [],
            "manifest": None,
            "loader_script": None
        }
        
        # Find all SVG files
        svg_files = list(self.input_dir.rglob("*.svg"))
        logger.info(f"Found {len(svg_files)} SVG files to process")
        
        # Process each SVG
        optimized_svgs = []
        for svg_file in svg_files:
            optimized_svg = self.optimize_svg_for_3d(svg_file)
            optimized_svgs.append(optimized_svg)
            
            # Create OBJ file
            obj_file = self.svg_to_obj(optimized_svg)
            if obj_file:
                results["models"].append(obj_file)
        
        results["optimized"] = optimized_svgs
        
        # Create manifest
        manifest_path = self.create_babylon_js_manifest(optimized_svgs)
        results["manifest"] = manifest_path
        
        # Create Babylon.js loader
        loader_path = self.create_babylon_loader_script(manifest_path)
        results["loader_script"] = loader_path
        
        return results
    
    def create_html_demo(self) -> Path:
        """Create an HTML demo page"""
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>3D Icons Demo - Babylon.js</title>
    <style>
        body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
        #renderCanvas { width: 100%; height: 100%; touch-action: none; }
        #controls { position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 5px; }
        .control-group { margin: 10px 0; }
        select { width: 200px; }
    </style>
    <script src="https://cdn.babylonjs.com/babylon.js"></script>
</head>
<body>
    <canvas id="renderCanvas"></canvas>
    <div id="controls">
        <h3>3D Network Icons</h3>
        <div class="control-group">
            <label>Category:</label>
            <select id="categorySelect">
                <option value="all">All</option>
                <option value="firewall">Firewall</option>
                <option value="switch">Switch</option>
                <option value="access_point">Access Point</option>
            </select>
        </div>
        <div class="control-group">
            <button onclick="loadSelected()">Load Selected</button>
            <button onclick="clearScene()">Clear Scene</button>
        </div>
        <div id="info"></div>
    </div>
    
    <script src="babylon-icon-loader.js"></script>
    <script>
        const canvas = document.getElementById('renderCanvas');
        const engine = new BABYLON.Engine(canvas, true);
        const scene = new BABYLON.Scene(engine);
        
        // Camera
        const camera = new BABYLON.ArcRotateCamera('camera', 0, Math.PI/3, 10, BABYLON.Vector3.Zero(), scene);
        camera.attachControl(canvas, true);
        
        // Light
        const light = new BABYLON.HemisphericLight('light', new BABYLON.Vector3(0, 1, 0), scene);
        
        // Ground
        const ground = BABYLON.MeshBuilder.CreateGround('ground', {width: 10, height: 10}, scene);
        const groundMaterial = new BABYLON.StandardMaterial('groundMat', scene);
        groundMaterial.diffuseColor = new BABYLON.Color3(0.2, 0.2, 0.2);
        ground.material = groundMaterial;
        
        // Icon loader
        const iconLoader = new Icon3DLoader(scene);
        
        // UI functions
        function loadSelected() {{
            const category = document.getElementById('categorySelect').value;
            clearScene();
            
            let models = [];
            if (category === 'all') {{
                // Load a sample of each category
                models = iconLoader.getModelsByCategory('firewall').slice(0, 3);
                models = models.concat(iconLoader.getModelsByCategory('switch').slice(0, 3));
                models = models.concat(iconLoader.getModelsByCategory('access_point').slice(0, 3));
            }} else {{
                models = iconLoader.getModelsByCategory(category);
            }}
            
            // Position models in a grid
            models.forEach((mesh, index) => {{
                const row = Math.floor(index / 3);
                const col = index % 3;
                mesh.position = new BABYLON.Vector3(col * 2 - 2, 0.5, row * 2 - 2);
            }});
            
            document.getElementById('info').textContent = `Loaded ${{models.length}} models`;
        }}
        
        function clearScene() {{
            // Remove all dynamically created meshes
            scene.meshes.forEach(mesh => {{
                if (mesh.name !== 'ground' && mesh.name !== 'camera') {{
                    mesh.dispose();
                }}
            }});
        }}
        
        // Run render loop
        engine.runRenderLoop(() => {{
            scene.render();
        }});
        
        // Handle window resize
        window.addEventListener('resize', () => {{
            engine.resize();
        }});
    </script>
</body>
</html>
"""
        
        demo_path = self.output_dir / "demo.html"
        demo_path.write_text(html_content)
        logger.info(f"Created HTML demo: {demo_path.name}")
        return demo_path


def main():
    """Main conversion function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert SVG files to 3D models for Babylon.js')
    parser.add_argument('input_dir', help='Directory containing SVG files')
    parser.add_argument('output_dir', help='Output directory for 3D files')
    
    args = parser.parse_args()
    
    converter = SVGTo3DConverter(args.input_dir, args.output_dir)
    results = converter.process_all_svgs()
    
    # Create demo
    demo_path = converter.create_html_demo()
    
    print("\n" + "="*60)
    print("SVG to 3D Conversion Complete!")
    print("="*60)
    print(f"Processed {len(results['optimized'])} SVG files")
    print(f"Created {len(results['models'])} 3D models")
    print(f"Manifest: {results['manifest'].name}")
    print(f"Babylon.js Loader: {results['loader_script'].name}")
    print(f"HTML Demo: {demo_path.name}")
    print(f"\nOpen {demo_path} in your browser to see the 3D icons!")
    print("="*60)


if __name__ == "__main__":
    main()
