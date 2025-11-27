# Exporting FortiGate Icons from .vss Files

## Method 1: Visio Export (Recommended)
1. Open your FortiGate .vss stencil file in Microsoft Visio
2. Drag each icon you want to use onto a blank page
3. Select the icon(s) and go to File > Save As
4. Choose "PNG" or "SVG" format
5. Set transparent background
6. Save with descriptive names (e.g., "fortigate-61e.png", "fortiswitch-124e.png")

## Method 2: Screen Capture (Alternative)
1. Open the .vss file in Visio
2. Zoom in on each icon
3. Use Snipping Tool (Windows) to capture each icon
4. Save as PNG with transparent background
5. Use image editor to remove white background

## Required Icons:
- FortiGate-61E (firewall)
- FortiSwitch-124E-POE (switch)
- FortiAP-231F (access point)
- Generic endpoint devices (laptop, desktop, mobile, server)

## Naming Convention:
Use these exact filenames:
- `fortigate-61e.png`
- `fortiswitch-124e-poe.png`
- `fortiap-231f.png`
- `endpoint-laptop.png`
- `endpoint-desktop.png`
- `endpoint-mobile.png`
- `endpoint-server.png`

## Size Requirements:
- Recommended: 128x128 pixels per icon
- Minimum: 64x64 pixels
- Maximum: 256x256 pixels
- Must be transparent PNG format

## Where to Place Icons:
Save the exported icons in this directory:
```
babylon_app/network-visualizer/assets/icons/
```
