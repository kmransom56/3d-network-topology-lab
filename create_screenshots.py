#!/usr/bin/env python3
"""
Automated Screenshot Creator for 3D Network Topology Lab
Creates professional screenshots for GitHub repository
"""

import asyncio
import os
import subprocess
import time
from pathlib import Path
from playwright.async_api import async_playwright

class ScreenshotCreator:
    def __init__(self):
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
    async def create_all_screenshots(self):
        """Create all required screenshots for the repository"""
        print("🚀 Starting automated screenshot creation...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            try:
                # 1. 3D Network Visualization
                await self.capture_3d_visualizer(page)
                
                # 2. Configuration Display
                await self.capture_configuration(page)
                
                # 3. VSS Converter Help
                await self.capture_vss_converter(page)
                
                # 4. Project Structure
                await self.capture_project_structure(page)
                
                # 5. README Documentation
                await self.capture_readme(page)
                
                print("✅ All screenshots created successfully!")
                
            except Exception as e:
                print(f"❌ Error creating screenshots: {e}")
            finally:
                await browser.close()
    
    async def capture_3d_visualizer(self, page):
        """Capture the 3D Network Visualizer interface"""
        print("📸 Capturing 3D Network Visualizer...")
        
        # Navigate to the 3D app
        await page.goto("http://localhost:3001")
        await page.wait_for_load_state('networkidle')
        
        # Wait for the app to load (with fallback)
        try:
            await page.wait_for_selector('#loadingScreen', state='hidden', timeout=15000)
        except:
            print("Loading screen still visible, proceeding anyway...")
            await page.wait_for_timeout(3000)  # Extra time for 3D rendering
        
        # Take full page screenshot
        await page.screenshot(
            path=self.screenshots_dir / "3d_main_interface.png",
            full_page=True,
            animations='disabled'
        )
        
        # Capture sidebar specifically
        await page.screenshot(
            path=self.screenshots_dir / "3d_sidebar_controls.png",
            clip={'x': 0, 'y': 100, 'width': 300, 'height': 600}
        )
        
        print("✅ 3D Visualizer screenshots captured")
    
    async def capture_configuration(self, page):
        """Capture FortiGate configuration display"""
        print("📸 Capturing configuration setup...")
        
        # Run the configuration command and capture output
        result = subprocess.run(
            ['python', 'run_fortigate_discovery.py', '--config'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        
        # Create a simple HTML page to display the configuration
        config_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>FortiGate Configuration</title>
            <style>
                body {{ font-family: 'Courier New', monospace; background: #1e1e1e; color: #d4d4d4; padding: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .header {{ color: #4fc3f7; font-size: 24px; margin-bottom: 20px; }}
                .config-line {{ margin: 5px 0; }}
                .highlight {{ color: #ffd700; }}
                .success {{ color: #4caf50; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">FortiGate Network Discovery Configuration</div>
                <pre>{result.stdout}</pre>
            </div>
        </body>
        </html>
        """
        
        # Write temporary HTML file
        temp_file = self.screenshots_dir / "temp_config.html"
        temp_file.write_text(config_html)
        
        # Navigate to and screenshot
        await page.goto(f"file://{temp_file.absolute()}")
        await page.wait_for_load_state('networkidle')
        
        await page.screenshot(
            path=self.screenshots_dir / "configuration_setup.png",
            full_page=True
        )
        
        # Clean up temp file
        temp_file.unlink()
        
        print("✅ Configuration screenshot captured")
    
    async def capture_vss_converter(self, page):
        """Capture VSS to SVG converter help"""
        print("📸 Capturing VSS converter help...")
        
        # Get help output
        result = subprocess.run(
            ['python', 'vss_to_svg.py', '--help'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        
        # Create HTML for help display
        help_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>VSS to SVG Converter</title>
            <style>
                body {{ font-family: 'Consolas', 'Monaco', monospace; background: #f8f9fa; color: #333; padding: 20px; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ color: #2196f3; font-size: 28px; margin-bottom: 20px; border-bottom: 2px solid #2196f3; padding-bottom: 10px; }}
                .usage {{ color: #4caf50; font-weight: bold; }}
                .options {{ margin: 20px 0; }}
                .option {{ margin: 8px 0; padding: 5px; background: #f5f5f5; border-radius: 4px; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">VSS to SVG Converter</div>
                <pre>{result.stdout}</pre>
            </div>
        </body>
        </html>
        """
        
        # Write and capture
        temp_file = self.screenshots_dir / "temp_help.html"
        temp_file.write_text(help_html)
        
        await page.goto(f"file://{temp_file.absolute()}")
        await page.wait_for_load_state('networkidle')
        
        await page.screenshot(
            path=self.screenshots_dir / "vss_converter_help.png",
            full_page=True
        )
        
        temp_file.unlink()
        
        print("✅ VSS converter help screenshot captured")
    
    async def capture_project_structure(self, page):
        """Capture project structure"""
        print("📸 Capturing project structure...")
        
        # Get directory listing
        result = subprocess.run(
            ['cmd', '/c', 'dir', '/b', '/o:gn'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        
        # Create HTML for project structure
        structure_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Project Structure</title>
            <style>
                body {{ font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace; background: #282c34; color: #abb2bf; padding: 20px; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
                .header {{ color: #61afef; font-size: 24px; margin-bottom: 20px; }}
                .structure {{ background: #21252b; padding: 20px; border-radius: 8px; border: 1px solid #3e4451; }}
                .line {{ margin: 2px 0; }}
                .directory {{ color: #e06c75; }}
                .file {{ color: #98c379; }}
                .executable {{ color: #d19a66; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">3D Network Topology Lab - Project Structure</div>
                <div class="structure">
                    <pre>{result.stdout}</pre>
                </div>
            </div>
        </body>
        </html>
        """
        
        temp_file = self.screenshots_dir / "temp_structure.html"
        temp_file.write_text(structure_html)
        
        await page.goto(f"file://{temp_file.absolute()}")
        await page.wait_for_load_state('networkidle')
        
        await page.screenshot(
            path=self.screenshots_dir / "project_structure.png",
            full_page=True
        )
        
        temp_file.unlink()
        
        print("✅ Project structure screenshot captured")
    
    async def capture_readme(self, page):
        """Capture README documentation"""
        print("📸 Capturing README documentation...")
        
        # Read README content
        readme_path = Path("README.md")
        if readme_path.exists():
            readme_content = readme_path.read_text(encoding='utf-8', errors='ignore')
            
            # Create HTML for README display
            readme_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>README.md</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #ffffff; color: #24292e; padding: 40px; max-width: 1200px; margin: 0 auto; }}
                    .container {{ background: #f6f8fa; padding: 30px; border-radius: 8px; border: 1px solid #d1d5da; }}
                    .header {{ color: #0366d6; font-size: 32px; margin-bottom: 20px; border-bottom: 1px solid #e1e4e8; padding-bottom: 16px; }}
                    .content {{ line-height: 1.6; }}
                    .code {{ background: #f6f8fa; padding: 16px; border-radius: 6px; font-family: 'SFMono-Regular', monospace; margin: 16px 0; }}
                    pre {{ white-space: pre-wrap; word-wrap: break-word; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">README.md</div>
                    <div class="content">
                        <pre>{readme_content[:2000]}...</pre>
                    </div>
                </div>
            </body>
            </html>
            """
            
            temp_file = self.screenshots_dir / "temp_readme.html"
            temp_file.write_text(readme_html)
            
            await page.goto(f"file://{temp_file.absolute()}")
            await page.wait_for_load_state('networkidle')
            
            await page.screenshot(
                path=self.screenshots_dir / "readme_preview.png",
                full_page=True
            )
            
            temp_file.unlink()
            
            print("✅ README screenshot captured")
        else:
            print("⚠️ README.md not found")

def main():
    """Main function to run screenshot creation"""
    print("🎬 3D Network Topology Lab - Automated Screenshot Creator")
    print("=" * 60)
    
    creator = ScreenshotCreator()
    
    # Check if 3D app is running
    try:
        import requests
        response = requests.get("http://localhost:3001", timeout=5)
        if response.status_code != 200:
            print("❌ 3D app not responding on port 3001")
            print("Please start the Babylon.js server first:")
            print("  cd babylon_app && node server.js")
            return
    except:
        print("❌ Cannot connect to 3D app on port 3001")
        print("Please start the Babylon.js server first:")
        print("  cd babylon_app && node server.js")
        return
    
    # Run screenshot creation
    asyncio.run(creator.create_all_screenshots())
    
    print("\n🎉 Screenshots created in 'screenshots/' directory:")
    print("  📸 3D Network Visualizer: 3d_main_interface.png")
    print("  📸 Configuration: configuration_setup.png")
    print("  📸 VSS Converter: vss_converter_help.png")
    print("  📸 Project Structure: project_structure.png")
    print("  📸 README Preview: readme_preview.png")
    print("\n🚀 Ready to add to your GitHub repository!")

if __name__ == "__main__":
    main()
