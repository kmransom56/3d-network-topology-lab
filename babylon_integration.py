#!/usr/bin/env python3
"""
Babylon.js Integration Package
Creates a complete 3D network visualization system for Babylon.js
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import zipfile


class BabylonIntegration:
    """Create Babylon.js integration package"""
    
    def __init__(self, models_dir: Path, output_dir: Path):
        self.models_dir = Path(models_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_network_visualizer(self) -> Path:
        """Create a complete network visualization system"""
        viz_dir = self.output_dir / "network-visualizer"
        viz_dir.mkdir(exist_ok=True)
        
        # Copy models
        models_dest = viz_dir / "models"
        if models_dest.exists():
            shutil.rmtree(models_dest)
        shutil.copytree(self.models_dir, models_dest)
        
        # Create main application
        self.create_main_app(viz_dir)
        
        # Create components
        self.create_components(viz_dir)
        
        # Create assets
        self.create_assets(viz_dir)
        
        # Create documentation
        self.create_docs(viz_dir)
        
        return viz_dir
    
    def create_main_app(self, viz_dir: Path):
        """Create main Babylon.js application"""
        app_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>3D Network Visualizer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="loadingScreen">
        <div class="loading-spinner"></div>
        <p>Loading 3D Network...</p>
    </div>
    
    <div id="header">
        <h1>3D Network Visualizer</h1>
        <div class="controls">
            <button id="btnReset">Reset View</button>
            <button id="btnFullscreen">Fullscreen</button>
            <button id="btnScreenshot">Screenshot</button>
        </div>
    </div>
    
    <div id="sidebar">
        <div class="panel">
            <h3>Device Categories</h3>
            <div id="categoryFilters">
                <label><input type="checkbox" value="all" checked> All Devices</label>
                <label><input type="checkbox" value="firewall"> Firewalls</label>
                <label><input type="checkbox" value="switch"> Switches</label>
                <label><input type="checkbox" value="access_point"> Access Points</label>
                <label><input type="checkbox" value="router"> Routers</label>
            </div>
        </div>
        
        <div class="panel">
            <h3>Display Options</h3>
            <label><input type="checkbox" id="showLabels" checked> Show Labels</label>
            <label><input type="checkbox" id="showConnections" checked> Show Connections</label>
            <label><input type="checkbox" id="animateDevices"> Animate Devices</label>
            <label><input type="range" id="zoomLevel" min="0.5" max="3" step="0.1" value="1"> Zoom</label>
        </div>
        
        <div class="panel">
            <h3>Device Info</h3>
            <div id="deviceInfo">
                <p>Click on a device to see details</p>
            </div>
        </div>
    </div>
    
    <div id="mainContent">
        <canvas id="renderCanvas"></canvas>
        <div id="stats">
            <span id="fps">FPS: 60</span>
            <span id="deviceCount">Devices: 0</span>
            <span id="connectionCount">Connections: 0</span>
        </div>
    </div>
    
    <!-- Babylon.js and dependencies -->
    <script src="https://cdn.babylonjs.com/babylon.js"></script>
    <script src="https://cdn.babylonjs.com/loaders/babylonjs.loaders.min.js"></script>
    <script src="https://cdn.babylonjs.com/gui/babylon.gui.min.js"></script>
    
    <!-- Application scripts -->
    <script src="js/NetworkVisualizer.js"></script>
    <script src="js/DeviceManager.js"></script>
    <script src="js/ConnectionManager.js"></script>
    <script src="js/UIManager.js"></script>
    <script src="js/SceneManager.js"></script>
    
    <script>
        // Initialize application
        window.addEventListener('DOMContentLoaded', () => {
            const app = new NetworkVisualizer('renderCanvas');
            app.init().then(() => {
                document.getElementById('loadingScreen').style.display = 'none';
            });
        });
    </script>
</body>
</html>"""
        
        (viz_dir / "index.html").write_text(app_content)
    
    def create_components(self, viz_dir: Path):
        """Create JavaScript components"""
        js_dir = viz_dir / "js"
        js_dir.mkdir(exist_ok=True)
        
        # Network Visualizer main class
        network_viz = """class NetworkVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.engine = null;
        this.scene = null;
        this.deviceManager = null;
        this.connectionManager = null;
        this.uiManager = null;
        this.sceneManager = null;
    }
    
    async init() {
        // Initialize Babylon.js
        this.engine = new BABYLON.Engine(this.canvas, true);
        this.scene = new BABYLON.Scene(this.engine);
        
        // Setup camera
        this.camera = new BABYLON.ArcRotateCamera(
            'camera', 
            Math.PI / 4, 
            Math.PI / 3, 
            20, 
            BABYLON.Vector3.Zero(), 
            this.scene
        );
        this.camera.attachControl(this.canvas, true);
        this.camera.lowerRadiusLimit = 5;
        this.camera.upperRadiusLimit = 50;
        
        // Setup lights
        const light1 = new BABYLON.HemisphericLight('light1', new BABYLON.Vector3(0, 1, 0), this.scene);
        light1.intensity = 0.7;
        
        const light2 = new BABYLON.DirectionalLight('light2', new BABYLON.Vector3(-1, -2, -1), this.scene);
        light2.intensity = 0.3;
        
        // Setup ground
        const ground = BABYLON.MeshBuilder.CreateGround('ground', {
            width: 30,
            height: 30
        }, this.scene);
        const groundMaterial = new BABYLON.StandardMaterial('groundMat', this.scene);
        groundMaterial.diffuseColor = new BABYLON.Color3(0.1, 0.1, 0.15);
        groundMaterial.specularColor = new BABYLON.Color3(0, 0, 0);
        ground.material = groundMaterial;
        
        // Initialize managers
        this.deviceManager = new DeviceManager(this.scene);
        this.connectionManager = new ConnectionManager(this.scene);
        this.uiManager = new UIManager();
        this.sceneManager = new SceneManager(this.scene);
        
        // Load models
        await this.loadModels();
        
        // Setup event handlers
        this.setupEventHandlers();
        
        // Start render loop
        this.startRenderLoop();
    }
    
    async loadModels() {
        try {
            const response = await fetch('models/manifest.json');
            const manifest = await response.json();
            
            for (const modelInfo of manifest.models) {
                await this.deviceManager.loadDevice(modelInfo);
            }
            
            // Create sample network topology
            this.createSampleTopology();
            
        } catch (error) {
            console.error('Failed to load models:', error);
        }
    }
    
    createSampleTopology() {
        // Create a sample network layout
        const devices = this.deviceManager.getAllDevices();
        
        if (devices.length === 0) return;
        
        // Position devices in a grid pattern
        const categories = {
            firewall: { x: 0, z: 0, color: new BABYLON.Color3(0.8, 0.2, 0.2) },
            switch: { x: 5, z: 0, color: new BABYLON.Color3(0.2, 0.8, 0.2) },
            access_point: { x: -5, z: 0, color: new BABYLON.Color3(0.2, 0.2, 0.8) },
            router: { x: 0, z: 5, color: new BABYLON.Color3(0.8, 0.8, 0.2) }
        };
        
        let deviceIndex = 0;
        for (const [category, config] of Object.entries(categories)) {
            const categoryDevices = this.deviceManager.getDevicesByCategory(category);
            const count = Math.min(categoryDevices.length, 3);
            
            for (let i = 0; i < count; i++) {
                const device = categoryDevices[i];
                if (device && device.mesh) {
                    device.mesh.position = new BABYLON.Vector3(
                        config.x + (i - 1) * 2,
                        0.5,
                        config.z
                    );
                    
                    // Apply category color
                    if (device.mesh.material) {
                        device.mesh.material.diffuseColor = config.color;
                    }
                    
                    deviceIndex++;
                }
            }
        }
        
        // Create connections between devices
        this.createConnections();
    }
    
    createConnections() {
        const firewalls = this.deviceManager.getDevicesByCategory('firewall');
        const switches = this.deviceManager.getDevicesByCategory('switch');
        const accessPoints = this.deviceManager.getDevicesByCategory('access_point');
        
        // Connect firewalls to switches
        firewalls.forEach(fw => {
            switches.forEach(sw => {
                if (fw.mesh && sw.mesh) {
                    this.connectionManager.createConnection(fw.mesh, sw.mesh);
                }
            });
        });
        
        // Connect switches to access points
        switches.forEach(sw => {
            accessPoints.forEach(ap => {
                if (sw.mesh && ap.mesh) {
                    this.connectionManager.createConnection(sw.mesh, ap.mesh);
                }
            });
        });
    }
    
    setupEventHandlers() {
        // Window resize
        window.addEventListener('resize', () => {
            this.engine.resize();
        });
        
        // UI controls
        document.getElementById('btnReset').addEventListener('click', () => {
            this.camera.position = new BABYLON.Vector3(0, 15, -20);
            this.camera.setTarget(BABYLON.Vector3.Zero());
        });
        
        document.getElementById('btnFullscreen').addEventListener('click', () => {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        });
        
        document.getElementById('btnScreenshot').addEventListener('click', () => {
            BABYLON.Tools.CreateScreenshot(this.engine, this.camera, 1920, 1080);
        });
        
        // Category filters
        document.querySelectorAll('#categoryFilters input').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateDeviceVisibility();
            });
        });
        
        // Display options
        document.getElementById('showLabels').addEventListener('change', (e) => {
            this.deviceManager.toggleLabels(e.target.checked);
        });
        
        document.getElementById('showConnections').addEventListener('change', (e) => {
            this.connectionManager.toggleVisibility(e.target.checked);
        });
        
        document.getElementById('animateDevices').addEventListener('change', (e) => {
            this.deviceManager.toggleAnimation(e.target.checked);
        });
        
        document.getElementById('zoomLevel').addEventListener('input', (e) => {
            this.camera.radius = 20 / parseFloat(e.target.value);
        });
    }
    
    updateDeviceVisibility() {
        const checkboxes = document.querySelectorAll('#categoryFilters input');
        const selectedCategories = [];
        
        checkboxes.forEach(cb => {
            if (cb.checked) {
                selectedCategories.push(cb.value);
            }
        });
        
        this.deviceManager.filterByCategories(selectedCategories);
    }
    
    startRenderLoop() {
        this.engine.runRenderLoop(() => {
            this.scene.render();
            
            // Update stats
            document.getElementById('fps').textContent = `FPS: ${Math.round(this.engine.getFps())}`;
            document.getElementById('deviceCount').textContent = 
                `Devices: ${this.deviceManager.getVisibleDeviceCount()}`;
            document.getElementById('connectionCount').textContent = 
                `Connections: ${this.connectionManager.getConnectionCount()}`;
        });
    }
}"""
        
        (js_dir / "NetworkVisualizer.js").write_text(network_viz)
        
        # Device Manager
        device_manager = """class DeviceManager {
    constructor(scene) {
        this.scene = scene;
        this.devices = new Map();
        this.labels = new Map();
        this.animationEnabled = false;
    }
    
    async loadDevice(modelInfo) {
        try {
            // Create a simple box mesh for demonstration
            // In production, you'd load the actual 3D model
            const mesh = BABYLON.MeshBuilder.CreateBox(
                modelInfo.name,
                { width: 1, height: 0.5, depth: 0.1 },
                this.scene
            );
            
            // Create material based on category
            const material = new BABYLON.StandardMaterial(`${modelInfo.name}_mat`, this.scene);
            const categoryColors = {
                firewall: new BABYLON.Color3(0.8, 0.2, 0.2),
                switch: new BABYLON.Color3(0.2, 0.8, 0.2),
                access_point: new BABYLON.Color3(0.2, 0.2, 0.8),
                router: new BABYLON.Color3(0.8, 0.8, 0.2),
                unknown: new BABYLON.Color3(0.5, 0.5, 0.5)
            };
            
            material.diffuseColor = categoryColors[modelInfo.category] || categoryColors.unknown;
            material.specularColor = new BABYLON.Color3(0.1, 0.1, 0.1);
            mesh.material = material;
            
            // Enable interactions
            mesh.isPickable = true;
            mesh.actionManager = new BABYLON.ActionManager(this.scene);
            
            // Add click action
            mesh.actionManager.registerAction(
                new BABYLON.ExecuteCodeAction(
                    BABYLON.ActionManager.OnPickTrigger,
                    () => this.onDeviceClick(modelInfo)
                )
            );
            
            // Add hover action
            mesh.actionManager.registerAction(
                new BABYLON.ExecuteCodeAction(
                    BABYLON.ActionManager.OnPointerOverTrigger,
                    () => this.onDeviceHover(mesh, true)
                )
            );
            
            mesh.actionManager.registerAction(
                new BABYLON.ExecuteCodeAction(
                    BABYLON.ActionManager.OnPointerOutTrigger,
                    () => this.onDeviceHover(mesh, false)
                )
            );
            
            // Store device info
            this.devices.set(modelInfo.name, {
                mesh: mesh,
                info: modelInfo,
                visible: true
            });
            
            // Create label
            this.createLabel(mesh, modelInfo.name);
            
            console.log(`Loaded device: ${modelInfo.name}`);
            
        } catch (error) {
            console.error(`Failed to load device ${modelInfo.name}:`, error);
        }
    }
    
    createLabel(mesh, text) {
        const labelTexture = new BABYLON.DynamicTexture(
            `${text}_label`,
            { width: 256, height: 64 },
            this.scene
        );
        
        const labelMaterial = new BABYLON.StandardMaterial(`${text}_label_mat`, this.scene);
        labelMaterial.diffuseTexture = labelTexture;
        labelMaterial.emissiveColor = new BABYLON.Color3(1, 1, 1);
        
        const labelPlane = BABYLON.MeshBuilder.CreatePlane(
            `${text}_label`,
            { width: 2, height: 0.5 },
            this.scene
        );
        labelPlane.material = labelMaterial;
        labelPlane.parent = mesh;
        labelPlane.position.y = 0.5;
        
        // Draw text on texture
        const ctx = labelTexture.getContext();
        ctx.font = '24px Arial';
        ctx.fillStyle = 'white';
        ctx.textAlign = 'center';
        ctx.fillText(text, 128, 40);
        labelTexture.update();
        
        this.labels.set(text, labelPlane);
    }
    
    onDeviceClick(modelInfo) {
        const deviceInfo = document.getElementById('deviceInfo');
        deviceInfo.innerHTML = `
            <h4>${modelInfo.name}</h4>
            <p><strong>Category:</strong> ${modelInfo.category}</p>
            <p><strong>Tags:</strong> ${modelInfo.tags.join(', ')}</p>
            <p><strong>Vertices:</strong> ${modelInfo.vertexCount}</p>
            <p><strong>Faces:</strong> ${modelInfo.faceCount}</p>
        `;
    }
    
    onDeviceHover(mesh, isHovering) {
        if (isHovering) {
            mesh.scaling = new BABYLON.Vector3(1.1, 1.1, 1.1);
            if (mesh.material) {
                mesh.material.emissiveColor = new BABYLON.Color3(0.2, 0.2, 0.2);
            }
        } else {
            mesh.scaling = new BABYLON.Vector3(1, 1, 1);
            if (mesh.material) {
                mesh.material.emissiveColor = new BABYLON.Color3(0, 0, 0);
            }
        }
    }
    
    getAllDevices() {
        return Array.from(this.devices.values());
    }
    
    getDevicesByCategory(category) {
        return Array.from(this.devices.values())
            .filter(device => device.info.category === category);
    }
    
    filterByCategories(categories) {
        const showAll = categories.includes('all');
        
        this.devices.forEach((device, name) => {
            const shouldShow = showAll || categories.includes(device.info.category);
            device.visible = shouldShow;
            
            if (device.mesh) {
                device.mesh.setEnabled(shouldShow);
            }
            
            const label = this.labels.get(name);
            if (label) {
                label.setEnabled(shouldShow);
            }
        });
    }
    
    getVisibleDeviceCount() {
        return Array.from(this.devices.values())
            .filter(device => device.visible).length;
    }
    
    toggleLabels(show) {
        this.labels.forEach(label => {
            label.setEnabled(show && label.parent.isEnabled);
        });
    }
    
    toggleAnimation(enabled) {
        this.animationEnabled = enabled;
        
        if (enabled) {
            this.startAnimation();
        }
    }
    
    startAnimation() {
        if (!this.animationEnabled) return;
        
        this.scene.registerBeforeRender(() => {
            if (!this.animationEnabled) return;
            
            this.devices.forEach(device => {
                if (device.mesh && device.visible) {
                    device.mesh.rotation.y += 0.01;
                }
            });
        });
    }
}"""
        
        (js_dir / "DeviceManager.js").write_text(device_manager)
        
        # Connection Manager
        connection_manager = """class ConnectionManager {
    constructor(scene) {
        this.scene = scene;
        this.connections = [];
        this.visible = true;
    }
    
    createConnection(mesh1, mesh2) {
        const connection = {
            mesh1: mesh1,
            mesh2: mesh2,
            line: null,
            visible: true
        };
        
        // Create line between meshes
        const line = BABYLON.MeshBuilder.CreateLines(
            `connection_${mesh1.name}_${mesh2.name}`,
            {
                points: [
                    mesh1.position,
                    new BABYLON.Vector3(
                        (mesh1.position.x + mesh2.position.x) / 2,
                        0.1,
                        (mesh1.position.z + mesh2.position.z) / 2
                    ),
                    mesh2.position
                ]
            },
            this.scene
        );
        
        line.color = new BABYLON.Color3(0.5, 0.5, 0.5);
        line.isPickable = false;
        
        connection.line = line;
        this.connections.push(connection);
    }
    
    toggleVisibility(show) {
        this.visible = show;
        this.connections.forEach(conn => {
            if (conn.line) {
                conn.line.setEnabled(show);
            }
        });
    }
    
    getConnectionCount() {
        return this.connections.length;
    }
}"""
        
        (js_dir / "ConnectionManager.js").write_text(connection_manager)
        
        # UI Manager
        ui_manager = """class UIManager {
    constructor() {
        this.setupUI();
    }
    
    setupUI() {
        // UI setup handled in HTML
    }
}"""
        
        (js_dir / "UIManager.js").write_text(ui_manager)
        
        # Scene Manager
        scene_manager = """class SceneManager {
    constructor(scene) {
        this.scene = scene;
        this.setupEnvironment();
    }
    
    setupEnvironment() {
        // Create skybox
        const skybox = BABYLON.MeshBuilder.CreateBox('skybox', { size: 100 }, this.scene);
        const skyboxMaterial = new BABYLON.StandardMaterial('skyboxMat', this.scene);
        skyboxMaterial.backFaceCulling = false;
        skyboxMaterial.disableLighting = true;
        skybox.material = skyboxMaterial;
        skybox.infiniteDistance = true;
        
        // Set skybox color (gradient effect)
        skyboxMaterial.diffuseColor = new BABYLON.Color3(0.1, 0.1, 0.2);
        skyboxMaterial.specularColor = new BABYLON.Color3(0, 0, 0);
    }
}"""
        
        (js_dir / "SceneManager.js").write_text(scene_manager)
    
    def create_assets(self, viz_dir: Path):
        """Create CSS and other assets"""
        css_dir = viz_dir / "styles"
        css_dir.mkdir(exist_ok=True)
        
        # Main CSS
        css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #1a1a1a;
    color: #ffffff;
    overflow: hidden;
}

#loadingScreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: #1a1a1a;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.loading-spinner {
    width: 50px;
    height: 50px;
    border: 3px solid #333;
    border-top: 3px solid #00ff88;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

#header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: #2a2a2a;
    border-bottom: 1px solid #444;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    z-index: 100;
}

#header h1 {
    font-size: 24px;
    color: #00ff88;
}

.controls button {
    background: #00ff88;
    color: #1a1a1a;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    margin-left: 10px;
    font-weight: bold;
    transition: background 0.3s;
}

.controls button:hover {
    background: #00cc6a;
}

#sidebar {
    position: fixed;
    left: 0;
    top: 60px;
    bottom: 0;
    width: 300px;
    background: #2a2a2a;
    border-right: 1px solid #444;
    padding: 20px;
    overflow-y: auto;
    z-index: 100;
}

.panel {
    margin-bottom: 30px;
}

.panel h3 {
    color: #00ff88;
    margin-bottom: 15px;
    font-size: 18px;
}

.panel label {
    display: block;
    margin-bottom: 10px;
    cursor: pointer;
}

.panel input[type="checkbox"] {
    margin-right: 10px;
}

.panel input[type="range"] {
    width: 100%;
    margin-top: 10px;
}

#deviceInfo {
    background: #1a1a1a;
    padding: 15px;
    border-radius: 4px;
    border: 1px solid #444;
}

#deviceInfo h4 {
    color: #00ff88;
    margin-bottom: 10px;
}

#deviceInfo p {
    margin-bottom: 8px;
    font-size: 14px;
}

#mainContent {
    margin-left: 300px;
    margin-top: 60px;
    height: calc(100vh - 60px);
    position: relative;
}

#renderCanvas {
    width: 100%;
    height: 100%;
    outline: none;
}

#stats {
    position: absolute;
    bottom: 20px;
    right: 20px;
    background: rgba(42, 42, 42, 0.9);
    padding: 10px 15px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 14px;
}

#stats span {
    margin-right: 20px;
}

@media (max-width: 768px) {
    #sidebar {
        width: 250px;
    }
    
    #mainContent {
        margin-left: 250px;
    }
    
    #header h1 {
        font-size: 20px;
    }
    
    .controls button {
        padding: 6px 12px;
        font-size: 14px;
    }
}"""
        
        (css_dir / "styles.css").write_text(css_content)
    
    def create_docs(self, viz_dir: Path):
        """Create documentation"""
        docs_dir = viz_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        readme_content = """# 3D Network Visualizer

A complete Babylon.js application for visualizing network infrastructure in 3D.

## Features

- **3D Device Models**: Import and display 3D models of network devices
- **Interactive Visualization**: Click, hover, and interact with devices
- **Category Filtering**: Filter devices by type (firewall, switch, access point, etc.)
- **Connection Visualization**: See network connections between devices
- **Responsive Design**: Works on desktop and mobile devices
- **Performance Optimized**: Efficient rendering for large networks

## Quick Start

1. Open `index.html` in your web browser
2. The application will automatically load all available 3D models
3. Use mouse to navigate:
   - Left click + drag: Rotate view
   - Right click + drag: Pan view
   - Scroll: Zoom in/out
4. Click on devices to see detailed information

## Customization

### Adding New Models

1. Place your 3D model files (.obj, .gltf) in the `models/` directory
2. Update `manifest.json` with model information
3. The application will automatically load new models

### Modifying Device Categories

Edit the `manifest.json` file to categorize your devices:

```json
{
  "name": "FortiGate-60F",
  "category": "firewall",
  "tags": ["firewall", "security", "utm"]
}
```

### Custom Colors

Device colors are defined in `js/DeviceManager.js`. Modify the `categoryColors` object to change device appearance.

## API Reference

### DeviceManager

Manages 3D device models and their interactions.

- `loadDevice(modelInfo)`: Load a 3D device model
- `getDevicesByCategory(category)`: Get all devices of a specific category
- `filterByCategories(categories)`: Filter visible devices by category
- `toggleLabels(show)`: Show/hide device labels

### ConnectionManager

Manages network connections between devices.

- `createConnection(mesh1, mesh2)`: Create a visual connection
- `toggleVisibility(show)`: Show/hide all connections

### SceneManager

Manages the 3D scene environment.

- `setupEnvironment()`: Configure skybox and lighting

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Performance Tips

- Use GLTF models for better performance
- Limit the number of visible devices
- Disable animations for large networks
- Use category filters to reduce render load

## Troubleshooting

### Models Not Loading
- Check that model files are in the correct directory
- Verify `manifest.json` format is correct
- Check browser console for error messages

### Poor Performance
- Reduce the number of visible devices
- Use simpler 3D models
- Close other browser tabs
- Update graphics drivers

## License

This project is provided as-is for educational and demonstration purposes.
"""
        
        (docs_dir / "README.md").write_text(readme_content)
    
    def create_deployment_package(self, viz_dir: Path) -> Path:
        """Create a zip package for deployment"""
        zip_path = self.output_dir / "network-visualizer.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in viz_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(viz_dir)
                    zipf.write(file_path, arcname)
        
        return zip_path


def main():
    """Main integration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create Babylon.js integration package')
    parser.add_argument('models_dir', help='Directory containing 3D models')
    parser.add_argument('output_dir', help='Output directory for integration package')
    
    args = parser.parse_args()
    
    integrator = BabylonIntegration(args.models_dir, args.output_dir)
    viz_dir = integrator.create_network_visualizer()
    zip_path = integrator.create_deployment_package(viz_dir)
    
    print("\n" + "="*60)
    print("Babylon.js Integration Complete!")
    print("="*60)
    print(f"Network visualizer created: {viz_dir}")
    print(f"Deployment package: {zip_path}")
    print(f"\nTo run:")
    print(f"1. Extract {zip_path.name}")
    print(f"2. Open index.html in your browser")
    print("="*60)


if __name__ == "__main__":
    main()
