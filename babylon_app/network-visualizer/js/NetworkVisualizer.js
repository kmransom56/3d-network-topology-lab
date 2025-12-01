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
            alpha: false // Disable alpha for solid background
        });

        this.scene = new BABYLON.Scene(this.engine);
        // Dark Grey Studio Background
        this.scene.clearColor = new BABYLON.Color4(0.2, 0.2, 0.2, 1);
        this.scene.ambientColor = new BABYLON.Color3(0.3, 0.3, 0.3);

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
        this.camera.applyGravity = false;

        // Setup studio lighting system
        this.setupLighting();

        // Setup clean environment
        this.setupEnvironment();

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
            firewall: { x: 0, z: 0, color: new BABYLON.Color3.FromHexString("#FF6B6B") }, // Soft Red
            switch: { x: 5, z: 0, color: new BABYLON.Color3.FromHexString("#4D96FF") }, // Soft Blue
            access_point: { x: -5, z: 0, color: new BABYLON.Color3.FromHexString("#9B59B6") }, // Soft Purple
            router: { x: 0, z: 5, color: new BABYLON.Color3.FromHexString("#F39C12") } // Soft Orange
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
        // Studio Lighting Setup (3-Point Lighting)

        // 1. Key Light (Main source, bright, casts shadows)
        const keyLight = new BABYLON.DirectionalLight('keyLight', new BABYLON.Vector3(-1, -2, -1), this.scene);
        keyLight.intensity = 1.2;
        keyLight.position = new BABYLON.Vector3(20, 40, 20);

        // Enable shadows for Key Light
        const shadowGenerator = new BABYLON.ShadowGenerator(2048, keyLight);
        shadowGenerator.useBlurExponentialShadowMap = true;
        shadowGenerator.blurKernel = 32;
        shadowGenerator.useKernelBlur = true;
        this.shadowGenerator = shadowGenerator;

        // 2. Fill Light (Softer, fills shadows, opposite to key)
        const fillLight = new BABYLON.HemisphericLight('fillLight', new BABYLON.Vector3(1, 1, 0), this.scene);
        fillLight.intensity = 0.6;
        fillLight.diffuse = new BABYLON.Color3(0.9, 0.9, 1.0); // Slightly cool
        fillLight.groundColor = new BABYLON.Color3(0.2, 0.2, 0.2);

        // 3. Rim Light (Backlight, separates objects from background)
        const rimLight = new BABYLON.DirectionalLight('rimLight', new BABYLON.Vector3(0, -1, 2), this.scene);
        rimLight.intensity = 0.5;
        rimLight.position = new BABYLON.Vector3(0, 20, -20);
        rimLight.diffuse = new BABYLON.Color3(1.0, 0.9, 0.8); // Slightly warm
    }

    setupEnvironment() {
        // Create seamless matte ground
        const ground = BABYLON.MeshBuilder.CreateGround('ground', {
            width: 100,
            height: 100,
            subdivisions: 2
        }, this.scene);

        const groundMaterial = new BABYLON.StandardMaterial('groundMat', this.scene);
        groundMaterial.diffuseColor = new BABYLON.Color3(0.2, 0.2, 0.2); // Match background
        groundMaterial.specularColor = new BABYLON.Color3(0, 0, 0); // Matte
        groundMaterial.receiveShadows = true;

        ground.material = groundMaterial;
        ground.receiveShadows = true;

        // No fog for clean studio look
        this.scene.fogMode = BABYLON.Scene.FOGMODE_NONE;
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
        pipeline.samples = 4; // MSAA

        // Subtle Bloom for "softness"
        pipeline.bloomEnabled = true;
        pipeline.bloomThreshold = 0.9;
        pipeline.bloomWeight = 0.1;
        pipeline.bloomKernel = 64;

        // Image Processing
        pipeline.imageProcessingEnabled = true;
        pipeline.imageProcessing.contrast = 1.1;
        pipeline.imageProcessing.exposure = 1.0;

        this.pipeline = pipeline;
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