#!/usr/bin/env python3
"""
Simple README screenshot capture
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

async def capture_readme():
    screenshots_dir = Path("screenshots")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
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
            
            temp_file = screenshots_dir / "temp_readme.html"
            temp_file.write_text(readme_html, encoding='utf-8')
            
            await page.goto(f"file://{temp_file.absolute()}")
            await page.wait_for_load_state('networkidle')
            
            await page.screenshot(
                path=screenshots_dir / "readme_preview.png",
                full_page=True
            )
            
            temp_file.unlink()
            print("✅ README screenshot captured!")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_readme())
