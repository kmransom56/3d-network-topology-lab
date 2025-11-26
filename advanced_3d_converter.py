#!/usr/bin/env python3
"""
Advanced SVG to 3D Converter
Creates actual 3D models from SVG paths for Babylon.js
"""

import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import List, Tuple, Dict, Optional
import numpy as np

# Try to import trimesh for 3D model creation
try:
    import trimesh
    import trimesh.creation
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    print("Warning: trimesh not available. Install with: pip install trimesh")


class Advanced3DConverter:
    """Convert SVG paths to actual 3D models"""
    
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "models").mkdir(exist_ok=True)
        (self.output_dir / "gltf").mkdir(exist_ok=True)
        (self.output_dir / "textures").mkdir(exist_ok=True)
    
    def parse_svg_path(self, path_data: str) -> List[Tuple[float, float]]:
        """Parse SVG path data into points"""
        points = []
        
        # Simple path parser (basic implementation)
        commands = {
            'M': self.parse_move_to,
            'L': self.parse_line_to,
            'C': self.parse_curve_to,
            'Z': self.parse_close_path
        }
        
        i = 0
        current_pos = (0, 0)
        
        while i < len(path_data):
            if path_data[i].upper() in commands:
                cmd = path_data[i].upper()
                i += 1
                
                # Skip whitespace
                while i < len(path_data) and path_data[i].isspace():
                    i += 1
                
                # Parse coordinates
                coords = []
                while i < len(path_data) and (path_data[i].isdigit() or path_data[i] in '-.eE'):
                    num_str = ''
                    while i < len(path_data) and (path_data[i].isdigit() or path_data[i] in '-.eE'):
                        num_str += path_data[i]
                        i += 1
                    if num_str:
                        coords.append(float(num_str))
                    
                    # Skip whitespace and commas
                    while i < len(path_data) and (path_data[i].isspace() or path_data[i] == ','):
                        i += 1
                
                # Process command
                if cmd in commands and coords:
                    new_points = commands[cmd](current_pos, coords)
                    points.extend(new_points)
                    if new_points:
                        current_pos = new_points[-1]
            else:
                i += 1
        
        return points
    
    def parse_move_to(self, current_pos: Tuple[float, float], coords: List[float]) -> List[Tuple[float, float]]:
        """Parse M command (move to)"""
        points = []
        for i in range(0, len(coords), 2):
            if i + 1 < len(coords):
                points.append((coords[i], coords[i+1]))
        return points
    
    def parse_line_to(self, current_pos: Tuple[float, float], coords: List[float]) -> List[Tuple[float, float]]:
        """Parse L command (line to)"""
        points = []
        for i in range(0, len(coords), 2):
            if i + 1 < len(coords):
                points.append((coords[i], coords[i+1]))
        return points
    
    def parse_curve_to(self, current_pos: Tuple[float, float], coords: List[float]) -> List[Tuple[float, float]]:
        """Parse C command (cubic bezier) - simplified"""
        # For simplicity, just use the end point
        points = []
        if len(coords) >= 6:
            points.append((coords[4], coords[5]))
        return points
    
    def parse_close_path(self, current_pos: Tuple[float, float], coords: List[float]) -> List[Tuple[float, float]]:
        """Parse Z command (close path)"""
        return []
    
    def svg_to_3d_mesh(self, svg_path: Path) -> Optional[Dict]:
        """Convert SVG to 3D mesh data"""
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            
            # Extract paths
            mesh_data = {
                "name": svg_path.stem,
                "vertices": [],
                "faces": [],
                "paths": []
            }
            
            for elem in root.iter():
                if elem.tag.endswith('path'):
                    path_data = elem.get('d', '')
                    if path_data:
                        points = self.parse_svg_path(path_data)
                        if points:
                            mesh_data["paths"].append(points)
            
            # Convert paths to 3D vertices and faces
            if mesh_data["paths"]:
                mesh_data = self.create_3d_from_paths(mesh_data)
            
            return mesh_data
            
        except Exception as e:
            print(f"Error processing {svg_path}: {e}")
            return None
    
    def create_3d_from_paths(self, mesh_data: Dict) -> Dict:
        """Convert 2D paths to 3D mesh"""
        vertices = []
        faces = []
        
        # Create a simple extrusion of the path
        for path in mesh_data["paths"]:
            if len(path) < 3:
                continue
            
            # Create vertices for front and back faces
            base_index = len(vertices)
            
            # Front face vertices
            for point in path:
                vertices.append([point[0], point[1], 0])
            
            # Back face vertices (extruded)
            extrusion_depth = 0.1
            for point in path:
                vertices.append([point[0], point[1], extrusion_depth])
            
            # Create faces
            n = len(path)
            
            # Front face
            if n >= 3:
                for i in range(1, n-1):
                    faces.append([base_index + i, base_index + i + 1, base_index])
            
            # Back face
            if n >= 3:
                back_start = base_index + n
                for i in range(1, n-1):
                    faces.append([back_start, back_start + i + 1, back_start + i])
            
            # Side faces
            for i in range(n):
                next_i = (i + 1) % n
                # Quad split into two triangles
                faces.append([base_index + i, base_index + next_i, base_index + n + i])
                faces.append([base_index + next_i, base_index + n + next_i, base_index + n + i])
        
        mesh_data["vertices"] = vertices
        mesh_data["faces"] = faces
        
        return mesh_data
    
    def create_obj_file(self, mesh_data: Dict, output_path: Path):
        """Create OBJ file from mesh data"""
        obj_content = [f"# Generated from {mesh_data['name']}"]
        obj_content.append(f"o {mesh_data['name']}")
        
        # Write vertices
        for vertex in mesh_data["vertices"]:
            obj_content.append(f"v {vertex[0]} {vertex[1]} {vertex[2]}")
        
        # Write faces (OBJ uses 1-based indexing)
        for face in mesh_data["faces"]:
            if len(face) == 3:
                obj_content.append(f"f {face[0]+1} {face[1]+1} {face[2]+1}")
            elif len(face) == 4:
                obj_content.append(f"f {face[0]+1} {face[1]+1} {face[2]+1} {face[3]+1}")
        
        output_path.write_text('\n'.join(obj_content))
    
    def create_gltf_file(self, mesh_data: Dict, output_path: Path):
        """Create GLTF file from mesh data (simplified)"""
        if not TRIMESH_AVAILABLE:
            # Create a simple GLTF structure
            gltf = {
                "asset": {"version": "2.0"},
                "scenes": [{"nodes": [0]}],
                "nodes": [{"mesh": 0}],
                "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
                "accessors": [
                    {"bufferView": 0, "componentType": 5126, "count": len(mesh_data["vertices"]), "type": "VEC3", "min": [0, 0, 0], "max": [100, 100, 0.1]},
                    {"bufferView": 1, "componentType": 5123, "count": len(mesh_data["faces"]) * 3, "type": "SCALAR"}
                ],
                "bufferViews": [
                    {"buffer": 0, "byteOffset": 0, "byteLength": len(mesh_data["vertices"]) * 12},
                    {"buffer": 0, "byteOffset": len(mesh_data["vertices"]) * 12, "byteLength": len(mesh_data["faces"]) * 6}
                ],
                "buffers": [{"byteLength": len(mesh_data["vertices"]) * 12 + len(mesh_data["faces"]) * 6}]
            }
            
            output_path.write_text(json.dumps(gltf, indent=2))
        else:
            # Use trimesh for proper GLTF export
            try:
                # Convert to trimesh
                vertices = np.array(mesh_data["vertices"])
                faces = np.array(mesh_data["faces"])
                
                mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
                
                # Export as GLTF
                mesh.export(str(output_path))
            except Exception as e:
                print(f"Error creating GLTF with trimesh: {e}")
                # Fallback to simple GLTF
                self.create_gltf_file(mesh_data, output_path)
    
    def process_svg_files(self) -> List[Dict]:
        """Process all SVG files"""
        svg_files = list(self.input_dir.rglob("*.svg"))
        processed_meshes = []
        
        print(f"Processing {len(svg_files)} SVG files...")
        
        for i, svg_file in enumerate(svg_files):
            if i % 50 == 0:
                print(f"Processed {i}/{len(svg_files)} files...")
            
            mesh_data = self.svg_to_3d_mesh(svg_file)
            if mesh_data and mesh_data["vertices"]:
                # Save OBJ file
                obj_path = self.output_dir / "models" / f"{mesh_data['name']}.obj"
                self.create_obj_file(mesh_data, obj_path)
                
                # Save GLTF file
                gltf_path = self.output_dir / "gltf" / f"{mesh_data['name']}.gltf"
                self.create_gltf_file(mesh_data, gltf_path)
                
                processed_meshes.append(mesh_data)
        
        return processed_meshes
    
    def create_babylon_manifest(self, meshes: List[Dict]) -> Path:
        """Create Babylon.js manifest"""
        manifest = {
            "version": "2.0",
            "models": []
        }
        
        for mesh in meshes:
            model_info = {
                "name": mesh["name"],
                "objPath": f"models/{mesh['name']}.obj",
                "gltfPath": f"gltf/{mesh['name']}.gltf",
                "vertexCount": len(mesh["vertices"]),
                "faceCount": len(mesh["faces"]),
                "category": self.categorize_device(mesh["name"]),
                "tags": self.extract_tags(mesh["name"])
            }
            manifest["models"].append(model_info)
        
        manifest_path = self.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        return manifest_path
    
    def categorize_device(self, filename: str) -> str:
        """Categorize device based on filename"""
        filename_lower = filename.lower()
        
        categories = {
            "firewall": ["fortigate", "firewall", "fg", "gate"],
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


def main():
    """Main conversion function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced SVG to 3D conversion')
    parser.add_argument('input_dir', help='Directory containing SVG files')
    parser.add_argument('output_dir', help='Output directory for 3D files')
    
    args = parser.parse_args()
    
    converter = Advanced3DConverter(args.input_dir, args.output_dir)
    meshes = converter.process_svg_files()
    
    # Create manifest
    manifest_path = converter.create_babylon_manifest(meshes)
    
    print("\n" + "="*60)
    print("Advanced 3D Conversion Complete!")
    print("="*60)
    print(f"Processed {len(meshes)} SVG files")
    print(f"Created OBJ files in: {converter.output_dir / 'models'}")
    print(f"Created GLTF files in: {converter.output_dir / 'gltf'}")
    print(f"Manifest: {manifest_path.name}")
    print("="*60)


if __name__ == "__main__":
    main()
