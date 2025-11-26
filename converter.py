"""
Visio to SVG Converter - Core Module
Supports VSS to SVG conversion using olefile extraction
"""

import olefile
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List
import re
import shutil
from enum import Enum


class ConversionStrategy(str, Enum):
    VSS_EXTRACTOR = "vss_extractor"
    VSDX_LIBRARY = "vsdx"
    ASPOSE = "aspose"


class VisioConverter:
    """Convert Visio stencil files to SVG format"""

    def __init__(self):
        self.available_strategies = self._detect_available_strategies()

    def _detect_available_strategies(self) -> list[ConversionStrategy]:
        """Detect which conversion strategies are available"""
        strategies = []
        
        # Check VSS extractor (always available)
        strategies.append(ConversionStrategy.VSS_EXTRACTOR)

        # Check vsdx library
        try:
            import vsdx
            strategies.append(ConversionStrategy.VSDX_LIBRARY)
        except ImportError:
            pass

        return strategies

    async def convert_vss_extractor(
        self, input_path: Path, output_dir: Path
    ) -> list[Path]:
        """Convert VSS files using olefile extraction"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            ole = olefile.OleFileIO(input_path)
            
            # Read the VisioDocument stream
            visio_data = ole.openstream('VisioDocument').read()
            ole.close()
            
            # Look for shape data patterns
            text_pattern = rb'[\x20-\x7E]{3,}'  # ASCII strings of 3+ chars
            texts = re.findall(text_pattern, visio_data)
            
            # Create SVG files for each potential shape
            svg_files = []
            shape_count = 0
            
            # Simple approach: create placeholder SVGs for detected shapes
            for i, text in enumerate(texts[:50]):  # Limit to first 50 text strings
                try:
                    decoded_text = text.decode('utf-8', errors='ignore').strip()
                    if len(decoded_text) > 3 and not decoded_text.startswith('Visio'):
                        shape_count += 1
                        
                        # Create a simple SVG placeholder
                        svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="10" width="80" height="80" 
          fill="none" stroke="black" stroke-width="2"/>
    <text x="50" y="55" text-anchor="middle" 
          font-family="Arial" font-size="12">{decoded_text}</text>
</svg>"""
                        
                        # Clean filename
                        safe_name = re.sub(r'[^\w\-_.]', '_', decoded_text)[:50]
                        svg_path = output_dir / f"shape_{shape_count:03d}_{safe_name}.svg"
                        svg_path.write_text(svg_content, encoding='utf-8')
                        svg_files.append(svg_path)
                        
                except Exception:
                    continue
            
            # Also create a generic placeholder for the stencil
            generic_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="10" width="80" height="80" 
          fill="none" stroke="black" stroke-width="2"/>
    <text x="50" y="55" text-anchor="middle" 
          font-family="Arial" font-size="10">Shape</text>
</svg>"""
            
            generic_path = output_dir / f"{input_path.stem}_generic.svg"
            generic_path.write_text(generic_svg, encoding='utf-8')
            svg_files.append(generic_path)
            
            return svg_files
            
        except Exception as e:
            raise RuntimeError(f"VSS extraction failed: {str(e)}")

    async def convert_vsdx_library(
        self, input_path: Path, output_dir: Path
    ) -> list[Path]:
        """Convert using vsdx Python library (for .vsdx files only)"""
        if ConversionStrategy.VSDX_LIBRARY not in self.available_strategies:
            raise RuntimeError("vsdx library not available")

        if input_path.suffix.lower() != ".vsdx":
            raise ValueError(
                "vsdx library only supports .vsdx files, not .vss"
            )

        try:
            from vsdx import VisioFile

            output_dir.mkdir(parents=True, exist_ok=True)
            svg_files = []

            with VisioFile(str(input_path)) as vis:
                # Extract each page as SVG
                for page_index, page in enumerate(vis.pages):
                    svg_content = page.to_svg()
                    
                    svg_path = output_dir / f"{input_path.stem}_page_{page_index}.svg"
                    svg_path.write_text(svg_content)
                    svg_files.append(svg_path)

            return svg_files

        except Exception as e:
            raise RuntimeError(f"vsdx conversion failed: {str(e)}")

    async def convert(
        self,
        input_path: Path,
        output_dir: Path,
        strategy: Optional[ConversionStrategy] = None,
    ) -> dict:
        """
        Convert Visio file to SVG using best available strategy

        Args:
            input_path: Path to .vss or .vsdx file
            output_dir: Directory to save SVG files
            strategy: Specific strategy to use (auto-detect if None)

        Returns:
            Dict with success status and list of SVG files
        """
        # Auto-detect strategy if not specified
        if strategy is None:
            if input_path.suffix.lower() == ".vss":
                strategy = ConversionStrategy.VSS_EXTRACTOR
            elif input_path.suffix.lower() == ".vsdx":
                if ConversionStrategy.VSDX_LIBRARY in self.available_strategies:
                    strategy = ConversionStrategy.VSDX_LIBRARY
                else:
                    strategy = ConversionStrategy.VSS_EXTRACTOR
            else:
                raise ValueError(f"Unsupported file type: {input_path.suffix}")

        # Validate strategy
        if strategy not in self.available_strategies:
            raise RuntimeError(f"Strategy {strategy} not available")

        try:
            if strategy == ConversionStrategy.VSS_EXTRACTOR:
                svg_files = await self.convert_vss_extractor(input_path, output_dir)
            elif strategy == ConversionStrategy.VSDX_LIBRARY:
                svg_files = await self.convert_vsdx_library(input_path, output_dir)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            return {
                "success": True,
                "strategy": strategy,
                "input_file": str(input_path),
                "output_files": [str(f) for f in svg_files],
                "count": len(svg_files),
            }

        except Exception as e:
            return {
                "success": False,
                "strategy": strategy,
                "input_file": str(input_path),
                "error": str(e),
                "output_files": [],
                "count": 0,
            }

    def get_manual_instructions(self) -> dict:
        """Get instructions for manual conversion workflow"""
        return {
            "method": "Manual Conversion in Microsoft Visio",
            "steps": [
                "1. Open the .vss file in Microsoft Visio",
                "2. For each shape/stencil you want to convert:",
                "   - Right-click the shape and select 'Edit Master' > 'Edit Master Shape'",
                "   - Select all elements (Ctrl+A)",
                "   - Go to File > Save As",
                "   - Choose 'SVG (*.svg)' as the file type",
                "   - Save with a descriptive name",
                "3. Repeat for each device icon you need",
            ],
            "alternative": {
                "method": "Using Visio 2016+ Export Feature",
                "steps": [
                    "1. Open .vss file in Visio",
                    "2. File > Export > Change File Type",
                    "3. Select 'SVG Scalable Vector Graphics'",
                    "4. Click 'Save As' and choose output location",
                ],
            },
            "batch_conversion": {
                "tool": "Visio VBA Macro",
                "description": "Create a VBA macro to batch export all shapes in a stencil",
                "note": "This requires Visio and VBA programming",
            },
        }
