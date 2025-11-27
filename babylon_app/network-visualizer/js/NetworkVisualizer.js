class NetworkVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.engine = null;
        this.scene = null;
        this.deviceManager = null;
        this.connectionManager = null;
        this.uiManager = null;
        this.sceneManager = null;
        this.particleSystem = null;
        this.skybox = null;
    }
    
    async init() {
        // Initialize Babylon.js with antialiasing
        this.engine = new BABYLON.Engine(this.canvas, true, {
            preserveDrawingBuffer: true,
            stencil: true,
            antialias: true,
            alpha: true
        });
        
        this.scene = new BABYLON.Scene(this.engine);
        this.scene.clearColor = new BABYLON.Color4(0.06, 0.06, 0.14, 1);
        
        // Setup advanced camera with smooth controls
        this.camera = new BABYLON.ArcRotateCamera(
            'camera', 
            Math.PI / 4, 
            Math.PI / 3, 
            25, 
            BABYLON.Vector3.Zero(), 
            this.scene
        );
        this.camera.attachControl(this.canvas, true);
        this.camera.lowerRadiusLimit = 8;
        this.camera.upperRadiusLimit = 60;
        this.camera.wheelPrecision = 50;
        this.camera.pinchPrecision = 50;
        this.camera.panningSensibility = 50;
        
        // Enable camera collisions with ground
        this.camera.checkCollisions = true;
        this.camera.applyGravity = true;
        
        // Setup advanced lighting system
        this.setupLighting();
        
        // Setup enhanced environment
        this.setupEnvironment();
        
        // Setup particle effects
        this.setupParticles();
        
        // Initialize managers
        this.deviceManager = new DeviceManager(this.scene);
        this.connectionManager = new ConnectionManager(this.scene);
        this.uiManager = new UIManager();
        this.sceneManager = new SceneManager(this.scene);
        
        // Setup post-processing effects
        this.setupPostProcessing();
        this.setupEventHandlers();
        
        // Start render loop
        this.startRenderLoop();
        
        // Load network data
        await this.loadNetworkData();
    }
    
    async loadNetworkData() {
        try {
            console.log('Loading network topology data...');
            // Try to load from live FortiGate data
            const response = await fetch('babylon_topology.json');
            if (response.ok) {
                const data = await response.json();
                console.log('Topology data loaded:', data);
                await this.loadTopologyData(data);
            } else {
                console.log('No topology file found, loading sample data...');
                // Load sample data if no live data available
                await this.loadSampleData();
            }
        } catch (error) {
            console.error('Error loading network data:', error);
            console.log('Loading sample data...');
            await this.loadSampleData();
        }
    }
    
    async loadTopologyData(data) {
        if (this.deviceManager && this.connectionManager) {
            await this.deviceManager.loadDevices(data.models || []);
            await this.connectionManager.loadConnections(data.connections || []);
        }
    }
    
    async loadSampleData() {
        // Create sample network topology
        const sampleDevices = [
            { id: 'fw1', name: 'FortiGate-100F', type: 'firewall', position: new BABYLON.Vector3(0, 2, 0) },
            { id: 'sw1', name: 'FortiSwitch-148F', type: 'switch', position: new BABYLON.Vector3(-8, 1, 0) },
            { id: 'sw2', name: 'FortiSwitch-148F', type: 'switch', position: new BABYLON.Vector3(8, 1, 0) },
            { id: 'ap1', name: 'FortiAP-431F', type: 'access_point', position: new BABYLON.Vector3(-12, 3, 5) },
            { id: 'ap2', name: 'FortiAP-431F', type: 'access_point', position: new BABYLON.Vector3(12, 3, 5) },
        ];
        
        const sampleConnections = [
            { from: 'fw1', to: 'sw1', bandwidth: 1000 },
            { from: 'fw1', to: 'sw2', bandwidth: 1000 },
            { from: 'sw1', to: 'ap1', bandwidth: 100 },
            { from: 'sw2', to: 'ap2', bandwidth: 100 },
        ];
        
        if (this.deviceManager && this.connectionManager) {
            await this.deviceManager.loadDevices(sampleDevices);
            await this.connectionManager.loadConnections(sampleConnections);
        }
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
            this.resetView();
        });
        
        document.getElementById('btnFullscreen').addEventListener('click', () => {
            this.toggleFullscreen();
        });
        
        document.getElementById('btnScreenshot').addEventListener('click', () => {
            this.takeScreenshot();
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
            // Update dynamic lights
            this.updateDynamicLights();
            
            // Update stats
            document.getElementById('fps').textContent = `FPS: ${Math.round(this.engine.getFps())}`;
            document.getElementById('deviceCount').textContent = 
                `Devices: ${this.deviceManager.getVisibleDeviceCount()}`;
            document.getElementById('connectionCount').textContent = 
                `Connections: ${this.connectionManager.getConnectionCount()}`;
            
            // Render scene
            this.scene.render();
        });
    }
    
    setupLighting() {
        // Main hemispheric light with soft shadows
        const hemisphericLight = new BABYLON.HemisphericLight('hemisphericLight', new BABYLON.Vector3(0, 1, 0), this.scene);
        hemisphericLight.intensity = 0.6;
        hemisphericLight.groundColor = new BABYLON.Color3(0.1, 0.2, 0.3);
        hemisphericLight.specular = new BABYLON.Color3(0.1, 0.1, 0.1);
        
        // Key light for dramatic effect
        const keyLight = new BABYLON.DirectionalLight('keyLight', new BABYLON.Vector3(-1, -2, -1), this.scene);
        keyLight.intensity = 0.4;
        keyLight.position = new BABYLON.Vector3(20, 40, 20);
        
        // Fill light to reduce harsh shadows
        const fillLight = new BABYLON.DirectionalLight('fillLight', new BABYLON.Vector3(1, -1, 1), this.scene);
        fillLight.intensity = 0.2;
        fillLight.position = new BABYLON.Vector3(-20, 30, -20);
        
        // Rim light for edge highlighting
        const rimLight = new BABYLON.DirectionalLight('rimLight', new BABYLON.Vector3(0, 0, -1), this.scene);
        rimLight.intensity = 0.15;
        rimLight.position = new BABYLON.Vector3(0, 50, 30);
        
        // Point lights for dynamic effects
        this.dynamicLights = [];
        for (let i = 0; i < 3; i++) {
            const pointLight = new BABYLON.PointLight(`pointLight${i}`, new BABYLON.Vector3(0, 10, 0), this.scene);
            pointLight.intensity = 0;
            pointLight.radius = 15;
            pointLight.diffuse = new BABYLON.Color3(0, 1, 0.5);
            this.dynamicLights.push(pointLight);
        }
    }
    
    setupEnvironment() {
        // Create enhanced ground with grid pattern
        const ground = BABYLON.MeshBuilder.CreateGround('ground', {
            width: 50,
            height: 50,
            subdivisions: 32
        }, this.scene);
        
        const groundMaterial = new BABYLON.StandardMaterial('groundMat', this.scene);
        groundMaterial.diffuseColor = new BABYLON.Color3(0.05, 0.08, 0.12);
        groundMaterial.specularColor = new BABYLON.Color3(0, 0, 0);
        groundMaterial.emissiveColor = new BABYLON.Color3(0, 0.1, 0.05);
        groundMaterial.backFaceCulling = false;
        
        // Add grid texture
        const groundTexture = new BABYLON.DynamicTexture('groundTexture', {width: 512, height: 512}, this.scene);
        const context = groundTexture.getContext();
        context.fillStyle = '#001122';
        context.fillRect(0, 0, 512, 512);
        
        // Draw grid lines
        context.strokeStyle = '#00ff88';
        context.lineWidth = 1;
        context.globalAlpha = 0.3;
        
        for (let i = 0; i <= 32; i++) {
            const pos = (i / 32) * 512;
            context.beginPath();
            context.moveTo(pos, 0);
            context.lineTo(pos, 512);
            context.stroke();
            
            context.beginPath();
            context.moveTo(0, pos);
            context.lineTo(512, pos);
            context.stroke();
        }
        
        groundTexture.update();
        groundMaterial.diffuseTexture = groundTexture;
        groundMaterial.diffuseTexture.uScale = 1;
        groundMaterial.diffuseTexture.vScale = 1;
        
        ground.material = groundMaterial;
        ground.receiveShadows = true;
        
        // Create subtle fog effect
        this.scene.fogMode = BABYLON.Scene.FOGMODE_EXP2;
        this.scene.fogDensity = 0.002;
        this.scene.fogColor = new BABYLON.Color3(0.06, 0.06, 0.14);
    }
    
    setupParticles() {
        // Create ambient particle system
        this.particleSystem = new BABYLON.ParticleSystem('particles', 2000, this.scene);
        this.particleSystem.particleTexture = new BABYLON.Texture('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==', this.scene);
        
        this.particleSystem.emitter = BABYLON.Vector3.Zero();
        this.particleSystem.minEmitBox = new BABYLON.Vector3(-25, 0, -25);
        this.particleSystem.maxEmitBox = new BABYLON.Vector3(25, 0, 25);
        
        this.particleSystem.color1 = new BABYLON.Color4(0, 1, 0.5, 0.1);
        this.particleSystem.color2 = new BABYLON.Color4(0, 0.5, 1, 0.1);
        this.particleSystem.colorDead = new BABYLON.Color4(0, 0, 0, 0);
        
        this.particleSystem.minSize = 0.1;
        this.particleSystem.maxSize = 0.3;
        
        this.particleSystem.minLifeTime = 2;
        this.particleSystem.maxLifeTime = 4;
        
        this.particleSystem.emitRate = 50;
        this.particleSystem.blendMode = BABYLON.ParticleSystem.BLENDMODE_ADD;
        this.particleSystem.gravity = new BABYLON.Vector3(0, -0.1, 0);
        
        this.particleSystem.direction1 = new BABYLON.Vector3(-1, 1, -1);
        this.particleSystem.direction2 = new BABYLON.Vector3(1, 1, 1);
        
        this.particleSystem.angularSpeed1 = 0;
        this.particleSystem.angularSpeed2 = 0;
        
        this.particleSystem.minEmitPower = 0.1;
        this.particleSystem.maxEmitPower = 0.3;
        this.particleSystem.updateSpeed = 0.01;
        
        this.particleSystem.start();
    }
    
    setupPostProcessing() {
        // Create default pipeline for post-processing effects
        const pipeline = new BABYLON.DefaultRenderingPipeline(
            'defaultPipeline', 
            true, 
            this.scene, 
            [this.camera]
        );
        
        // Enable effects
        pipeline.fxaaEnabled = true; // Anti-aliasing
        pipeline.bloomEnabled = true; // Bloom effect
        pipeline.bloomThreshold = 0.8;
        pipeline.bloomWeight = 0.3;
        pipeline.bloomKernel = 64;
        
        // Sharpening
        pipeline.sharpenEnabled = true;
        pipeline.sharpenAmount = 0.3;
        
        // Chromatic aberration for subtle sci-fi effect
        pipeline.chromaticAberrationEnabled = true;
        pipeline.chromaticAberration.aberrationAmount = 1.0;
        
        // Vignette
        pipeline.vignetteEnabled = true;
        pipeline.vignetteWeight = 0.5;
        pipeline.vignetteColor = new BABYLON.Color4(0, 0.5, 0.2, 1);
        
        // Grain for cinematic feel
        pipeline.grainEnabled = true;
        pipeline.grainAmount = 0.02;
        pipeline.grainIntensity = 0.5;
        
        this.pipeline = pipeline;
    }
    
    updateDynamicLights() {
        if (this.dynamicLights && this.deviceManager) {
            const time = Date.now() * 0.001;
            const devices = this.deviceManager.getAllDevices();
            
            this.dynamicLights.forEach((light, index) => {
                if (devices[index]) {
                    const device = devices[index];
                    light.position = device.position.clone();
                    light.position.y += 5;
                    
                    // Pulsing effect
                    const pulse = Math.sin(time * 2 + index) * 0.5 + 0.5;
                    light.intensity = pulse * 0.3;
                }
            });
        }
    }
    
    // Public methods for UI interaction
    resetView() {
        this.camera.alpha = Math.PI / 4;
        this.camera.beta = Math.PI / 3;
        this.camera.radius = 25;
        this.camera.target = BABYLON.Vector3.Zero();
    }
    
    takeScreenshot() {
        BABYLON.Tools.CreateScreenshot(this.engine, this.camera, { width: 1920, height: 1080 });
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.canvas.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
    
    dispose() {
        this.scene.dispose();
        this.engine.dispose();
    }
}