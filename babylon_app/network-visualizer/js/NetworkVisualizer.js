class NetworkVisualizer {
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
}