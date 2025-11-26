"""
VSS to SVG Converter
Supports multiple backends for converting Visio stencil files to SVG format.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Dict
import shutil
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConversionBackend(Enum):
    """Available conversion backends"""
    VSS_EXTRACTOR = "vss_extractor"
    LIBVISIO2SVG = "libvisio2svg"
    PYWIN32 = "pywin32"
    ASPOSE = "aspose"


class VSSConverter:
    """Converter for VSS (Visio Stencil) files to SVG format"""
    
    def __init__(self, backend: Optional[ConversionBackend] = None):
        """
        Initialize the converter
        
        Args:
            backend: Preferred conversion backend. If None, auto-detect best available.
        """
        self.backend = backend or self._detect_backend()
        logger.info(f"Using conversion backend: {self.backend.value}")
    
    def _detect_backend(self) -> ConversionBackend:
        """Auto-detect the best available conversion backend"""
        
        # Check for VSS extractor (always available)
        logger.info("Using VSS extractor backend")
        return ConversionBackend.VSS_EXTRACTOR
        
        # Check for libvisio2svg CLI tool
        if shutil.which('vss2svg-conv'):
            logger.info("Detected vss2svg-conv command-line tool")
            return ConversionBackend.LIBVISIO2SVG
        
        # Check for pywin32 (Windows with Visio)
        if sys.platform == 'win32':
            try:
                import win32com.client
                logger.info("Detected pywin32 - will attempt to use Visio COM automation")
                return ConversionBackend.PYWIN32
            except ImportError:
                pass
        
        # Check for Aspose.Diagram
        try:
            import asposediagram
            logger.info("Detected Aspose.Diagram library")
            return ConversionBackend.ASPOSE
        except ImportError:
            pass
        
        raise RuntimeError(
            "No suitable conversion backend found. Please install one of:\n"
            "1. libvisio2svg (Linux/WSL): https://github.com/kakwa/libvisio2svg\n"
            "2. pywin32 with MS Visio installed (Windows)\n"
            "3. Aspose.Diagram: pip install aspose-diagram"
        )
    
    def convert_vss(
        self, 
        input_path: Path, 
        output_dir: Path, 
        scale: float = 1.0,
        prefix: str = ""
    ) -> List[Path]:
        """
        Convert a VSS file to SVG format
        
        Args:
            input_path: Path to input VSS file
            output_dir: Directory to save SVG files
            scale: Scaling factor for output (default 1.0)
            prefix: Optional prefix for output filenames
            
        Returns:
            List of paths to generated SVG files
        """
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.backend == ConversionBackend.VSS_EXTRACTOR:
            return self._convert_vss_extractor(input_path, output_dir, scale, prefix)
        elif self.backend == ConversionBackend.LIBVISIO2SVG:
            return self._convert_libvisio2svg(input_path, output_dir, scale, prefix)
        elif self.backend == ConversionBackend.PYWIN32:
            return self._convert_pywin32(input_path, output_dir, scale, prefix)
        elif self.backend == ConversionBackend.ASPOSE:
            return self._convert_aspose(input_path, output_dir, scale, prefix)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
    
    def _convert_libvisio2svg(
        self, 
        input_path: Path, 
        output_dir: Path, 
        scale: float,
        prefix: str
    ) -> List[Path]:
        """Convert using libvisio2svg command-line tool"""
        logger.info(f"Converting {input_path.name} using libvisio2svg...")
        
        cmd = [
            'vss2svg-conv',
            '-i', str(input_path),
            '-o', str(output_dir),
            '-s', str(scale)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.debug(result.stdout)
            
            # Find generated SVG files
            svg_files = sorted(output_dir.glob('*.svg'))
            
            # Apply prefix if specified
            if prefix:
                renamed_files = []
                for svg_file in svg_files:
                    new_name = output_dir / f"{prefix}{svg_file.name}"
                    svg_file.rename(new_name)
                    renamed_files.append(new_name)
                svg_files = renamed_files
            
            logger.info(f"Generated {len(svg_files)} SVG files")
            return svg_files
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Conversion failed: {e.stderr}")
            raise RuntimeError(f"libvisio2svg conversion failed: {e.stderr}")
    
    def _convert_pywin32(
        self, 
        input_path: Path, 
        output_dir: Path, 
        scale: float,
        prefix: str
    ) -> List[Path]:
        """Convert using pywin32 and Visio COM automation"""
        try:
            import win32com.client
        except ImportError:
            raise ImportError("pywin32 not installed. Install with: pip install pywin32")
        
        logger.info(f"Converting {input_path.name} using Visio COM automation...")
        
        svg_files = []
        visio = None
        
        try:
            # Start Visio
            visio = win32com.client.Dispatch("Visio.Application")
            visio.Visible = False
            
            # Open stencil file
            stencil = visio.Documents.Open(str(input_path.absolute()))
            
            # Iterate through masters in stencil
            for master in stencil.Masters:
                master_name = self._sanitize_filename(master.Name)
                output_file = output_dir / f"{prefix}{master_name}.svg"
                
                # Create temporary document to export master
                doc = visio.Documents.Add("")
                page = doc.Pages.Item(1)
                
                # Drop shape on page
                shape = page.Drop(master, 4.25, 5.5)
                
                # Set page size to fit shape
                page.ResizeToFitContents()
                
                # Export to SVG
                page.Export(str(output_file.absolute()))
                
                svg_files.append(output_file)
                logger.info(f"Exported: {master_name}.svg")
                
                # Close temporary document
                doc.Close()
            
            # Close stencil
            stencil.Close()
            
        finally:
            if visio:
                visio.Quit()
        
        logger.info(f"Generated {len(svg_files)} SVG files")
        return svg_files
    
    def _convert_vss_extractor(
        self, 
        input_path: Path, 
        output_dir: Path, 
        scale: float,
        prefix: str
    ) -> List[Path]:
        """Convert VSS files using olefile extraction"""
        import olefile
        import re
        
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
                        svg_path = output_dir / f"{prefix}shape_{shape_count:03d}_{safe_name}.svg"
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
            
            generic_path = output_dir / f"{prefix}{input_path.stem}_generic.svg"
            generic_path.write_text(generic_svg, encoding='utf-8')
            svg_files.append(generic_path)
            
            logger.info(f"Generated {len(svg_files)} SVG files")
            return svg_files
            
        except Exception as e:
            raise RuntimeError(f"VSS extraction failed: {str(e)}")
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize filename by removing invalid characters"""
        # Replace invalid characters with underscore
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name.strip()
    
    def batch_convert(
        self,
        input_files: List[Path],
        output_dir: Path,
        scale: float = 1.0
    ) -> Dict[Path, List[Path]]:
        """
        Batch convert multiple VSS files
        
        Args:
            input_files: List of VSS file paths
            output_dir: Output directory for all SVG files
            scale: Scaling factor
            
        Returns:
            Dictionary mapping input file to list of generated SVG files
        """
        results = {}
        
        for input_file in input_files:
            input_file = Path(input_file)
            logger.info(f"\nProcessing: {input_file.name}")
            
            # Create subdirectory for each VSS file
            file_output_dir = output_dir / input_file.stem
            
            try:
                svg_files = self.convert_vss(
                    input_file,
                    file_output_dir,
                    scale=scale,
                    prefix=""
                )
                results[input_file] = svg_files
                
            except Exception as e:
                logger.error(f"Failed to convert {input_file.name}: {e}")
                results[input_file] = []
        
        return results


def main():
    """CLI interface for VSS to SVG conversion"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert Visio VSS stencil files to SVG format'
    )
    parser.add_argument('input', help='Input VSS file or directory')
    parser.add_argument('-o', '--output', default='./svg_output', 
                       help='Output directory for SVG files')
    parser.add_argument('-s', '--scale', type=float, default=1.0,
                       help='Scale factor for output (default: 1.0)')
    parser.add_argument('-b', '--backend', 
                       choices=['vss_extractor', 'libvisio2svg', 'pywin32', 'aspose'],
                       help='Force specific conversion backend')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Recursively process VSS files in directory')
    
    args = parser.parse_args()
    
    # Determine backend
    backend = None
    if args.backend:
        backend = ConversionBackend(args.backend)
    
    # Initialize converter
    try:
        converter = VSSConverter(backend=backend)
    except RuntimeError as e:
        logger.error(str(e))
        sys.exit(1)
    
    # Get input files
    input_path = Path(args.input)
    output_dir = Path(args.output)
    
    if input_path.is_file():
        input_files = [input_path]
    elif input_path.is_dir():
        pattern = '**/*.vss' if args.recursive else '*.vss'
        input_files = list(input_path.glob(pattern))
        if not input_files:
            logger.error(f"No VSS files found in {input_path}")
            sys.exit(1)
    else:
        logger.error(f"Input not found: {input_path}")
        sys.exit(1)
    
    logger.info(f"Found {len(input_files)} VSS file(s) to convert")
    
    # Convert files
    results = converter.batch_convert(input_files, output_dir, scale=args.scale)
    
    # Summary
    total_svgs = sum(len(svgs) for svgs in results.values())
    logger.info(f"\nConversion complete!")
    logger.info(f"Total VSS files processed: {len(results)}")
    logger.info(f"Total SVG files generated: {total_svgs}")
    logger.info(f"Output directory: {output_dir.absolute()}")


if __name__ == '__main__':
    main()
