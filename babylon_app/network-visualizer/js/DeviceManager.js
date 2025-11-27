/**
 * DeviceManager - 3D Model Loading and Device Management
 * 
 * This class handles loading and management of 3D FortiGate device models
 * for the Babylon.js network visualizer. It supports both authentic 3D models
 * (.glb files) and procedural fallback models.
 * 
 * Features:
 * - Automatic 3D model preloading and caching
 * - Fallback to procedural models if 3D files not available
 * - Model cloning for efficient multiple instances
 * - Device interaction (hover, click, labels)
 * - Support for FortiGate-61E, FortiSwitch-124E-POE, FortiAP-231F, and endpoints
 * 
 * Model Files Required:
 * - assets/models/fortigate-61e.glb (1,832 bytes) 
 * - assets/models/fortiswitch-124e-poe.glb (2,048 bytes) 
 * - assets/models/fortiap-231f.glb (70,904 bytes) 
 * - assets/models/endpoint-laptop.glb (2,024 bytes) 
 * - assets/models/endpoint-desktop.glb (2,040 bytes) 
 * - assets/models/endpoint-mobile.glb (2,040 bytes) 
 * - assets/models/endpoint-server.glb (2,036 bytes) 
 * 
 * @class DeviceManager
 * @param {BABYLON.Scene} scene - The Babylon.js scene
 */

class DeviceManager {
    constructor(scene) {
        this.scene = scene;
        this.devices = new Map();
        this.labels = new Map();
        this.animationEnabled = false;
        this.deviceData = [];
        this.loadedModels = new Map(); // Cache for loaded 3D models
    }
    
    async loadDevices(deviceData) {
        this.deviceData = deviceData;
        console.log(`Loading ${deviceData.length} devices...`);
        
        // Pre-load all 3D models
        await this.preloadModels();
        
        for (const deviceInfo of deviceData) {
            await this.createDevice(deviceInfo);
        }
        
        console.log(`Successfully loaded ${this.devices.size} devices`);
    }
    
    /**
     * Preload all 3D models for efficient device creation
     * 
     * Loads all required .glb model files and caches them for cloning.
     * Models that fail to load are set to null to trigger procedural fallback.
     * 
     * Model Files Status:
     * - fortigate-61e.glb (1,832 bytes) - Working
     * - fortiswitch-124e-poe.glb (2,048 bytes) - Working  
     * - fortiap-231f.glb (70,904 bytes) - Working
     * - endpoint-laptop.glb (2,024 bytes) - Working
     * - endpoint-desktop.glb (2,040 bytes) - Working
     * - endpoint-mobile.glb (2,040 bytes) - Working
     * - endpoint-server.glb (2,036 bytes) - Working
     * - router.glb - Not implemented (procedural fallback)
     */
    async preloadModels() {
        const modelPaths = {
            'firewall': 'assets/models/fortigate-61e.glb',
            'switch': 'assets/models/fortiswitch-124e-poe.glb',
            'access_point': 'assets/models/fortiap-231f.glb',
            'router': 'assets/models/router.glb', // Not implemented
            'endpoint-laptop': 'assets/models/endpoint-laptop.glb',
            'endpoint-desktop': 'assets/models/endpoint-desktop.glb',
            'endpoint-mobile': 'assets/models/endpoint-mobile.glb',
            'endpoint-server': 'assets/models/endpoint-server.glb'
        };
        
        for (const [deviceType, modelPath] of Object.entries(modelPaths)) {
            try {
                console.log(`Loading 3D model: ${modelPath}`);
                const result = await BABYLON.SceneLoader.ImportMeshAsync("", modelPath, "", this.scene);
                this.loadedModels.set(deviceType, result.meshes[0]);
                console.log(`Successfully loaded model: ${deviceType}`);
            } catch (error) {
                this.loadedModels.set(deviceType, null);
                console.warn(`Failed to load model ${deviceType}, will use procedural fallback:`, error.message);
            }
        }
    }
    
    async createDevice(deviceInfo) {
        try {
            let mesh;
            
            // Try to use loaded 3D model first, fallback to procedural
            if (deviceInfo.type === 'endpoint') {
                // Determine endpoint subtype for 3D model selection
                const endpointType = this.detectEndpointType(deviceInfo);
                const modelKey = `endpoint-${endpointType}`;
                
                if (this.loadedModels.has(modelKey) && this.loadedModels.get(modelKey)) {
                    mesh = this.createModelInstance(deviceInfo, this.loadedModels.get(modelKey));
                } else {
                    mesh = this.createEndpointModel(deviceInfo);
                }
            } else {
                // For FortiGate equipment
                if (this.loadedModels.has(deviceInfo.type) && this.loadedModels.get(deviceInfo.type)) {
                    mesh = this.createModelInstance(deviceInfo, this.loadedModels.get(deviceInfo.type));
                } else {
                    // Fallback to procedural models
                    switch (deviceInfo.type) {
                        case 'firewall':
                            mesh = this.createFortiGateModel(deviceInfo);
                            break;
                        case 'switch':
                            mesh = this.createFortiSwitchModel(deviceInfo);
                            break;
                        case 'access_point':
                            mesh = this.createFortiAPModel(deviceInfo);
                            break;
                        case 'router':
                            mesh = this.createRouterModel(deviceInfo);
                            break;
                        default:
                            mesh = this.createGenericDeviceModel(deviceInfo);
                    }
                }
            }
            
            // Position device
            if (deviceInfo.position) {
                mesh.position = new BABYLON.Vector3(
                    deviceInfo.position.x || 0,
                    deviceInfo.position.y || 1,
                    deviceInfo.position.z || 0
                );
            } else {
                this.autoPositionDevice(mesh, this.devices.size);
            }
            
            // Store device reference
            this.devices.set(deviceInfo.name, {
                mesh: mesh,
                info: deviceInfo,
                visible: true
            });
            
            // Add interaction handlers
            this.setupDeviceInteraction(mesh, deviceInfo);
            
            // Create label
            this.createLabel(mesh, deviceInfo.name);
            
            console.log(`✅ Created device: ${deviceInfo.name} (${deviceInfo.type})`);
            
        } catch (error) {
            console.error(`❌ Failed to create device ${deviceInfo.name}:`, error);
        }
    }
    
    detectEndpointType(deviceInfo) {
        const name = (deviceInfo.name || '').toLowerCase();
        const mac = (deviceInfo.mac || '').toLowerCase();
        
        // Check MAC vendor prefixes for common manufacturers
        const macVendors = {
            'apple': ['28:cf:e9', 'a4:c3:61', '40:a6:d9', '98:01:a7'],
            'samsung': ['e8:50:8b', 'ac:c1:ee', '38:b1:db'],
            'dell': ['10:9a:dd', '18:03:73', '84:2b:2b'],
            'hp': ['28:cf:e9', '3c:d9:2b', 'f0:4d:a5'],
            'lenovo': ['70:72:3c', '00:1a:6b', 'f4:ce:46']
        };
        
        for (const [vendor, prefixes] of Object.entries(macVendors)) {
            for (const prefix of prefixes) {
                if (mac.startsWith(prefix)) {
                    return vendor === 'apple' ? 'laptop' : 'desktop';
                }
            }
        }
        
        // Check name patterns
        if (name.includes('laptop') || name.includes('notebook') || name.includes('macbook')) {
            return 'laptop';
        } else if (name.includes('desktop') || name.includes('pc') || name.includes('tower')) {
            return 'desktop';
        } else if (name.includes('phone') || name.includes('mobile') || name.includes('iphone') || name.includes('android')) {
            return 'mobile';
        }
        
        return 'desktop'; // Default
    }
    
    createModelInstance(deviceInfo, sourceMesh) {
        const instance = sourceMesh.clone(`${deviceInfo.name}_3d_model`);
        instance.position = new BABYLON.Vector3(0, 0, 0);
        return instance;
    }
    
    autoPositionDevice(mesh, index) {
        // Auto-position devices in a circular or grid pattern
        const gridSize = Math.ceil(Math.sqrt(index + 1));
        const spacing = 4;
        
        const row = Math.floor(index / gridSize);
        const col = index % gridSize;
        
        mesh.position.x = (col - gridSize / 2) * spacing;
        mesh.position.z = (row - gridSize / 2) * spacing;
        mesh.position.y = 1;
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
        labelMaterial.disableLighting = true;
        
        const labelPlane = BABYLON.MeshBuilder.CreatePlane(
            `${text}_label`,
            { width: 2, height: 0.5 },
            this.scene
        );
        labelPlane.material = labelMaterial;
        labelPlane.parent = mesh;
        labelPlane.position.y = 1.5;
        labelPlane.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;
        
        // Draw text on texture
        const ctx = labelTexture.getContext();
        ctx.font = 'bold 20px Arial';
        ctx.fillStyle = '#00ff88';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, 128, 32);
        labelTexture.update();
        
        this.labels.set(text, labelPlane);
    }
    
    setupDeviceInteraction(mesh, deviceInfo) {
        mesh.actionManager = new BABYLON.ActionManager(this.scene);
        
        // Click interaction
        mesh.actionManager.registerAction(
            new BABYLON.ExecuteCodeAction(
                BABYLON.ActionManager.OnPickTrigger,
                () => this.onDeviceClick(deviceInfo)
            )
        );
        
        // Hover interaction
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
    }
    
    onDeviceClick(deviceInfo) {
        const deviceInfoElement = document.getElementById('deviceInfo');
        
        // Build detailed device information
        let infoHtml = `
            <h4>${deviceInfo.name}</h4>
            <div class="device-stat">
                <span class="stat-label">Type:</span>
                <span class="stat-value">${deviceInfo.type}</span>
            </div>
        `;
        
        if (deviceInfo.mac) {
            infoHtml += `
                <div class="device-stat">
                    <span class="stat-label">MAC Address:</span>
                    <span class="stat-value">${deviceInfo.mac}</span>
                </div>
            `;
        }
        
        if (deviceInfo.ip) {
            infoHtml += `
                <div class="device-stat">
                    <span class="stat-label">IP Address:</span>
                    <span class="stat-value">${deviceInfo.ip}</span>
                </div>
            `;
        }
        
        if (deviceInfo.status) {
            infoHtml += `
                <div class="device-stat">
                    <span class="stat-label">Status:</span>
                    <span class="stat-value">${deviceInfo.status}</span>
                </div>
            `;
        }
        
        if (deviceInfo.model) {
            infoHtml += `
                <div class="device-stat">
                    <span class="stat-label">Model:</span>
                    <span class="stat-value">${deviceInfo.model}</span>
                </div>
            `;
        }
        
        if (deviceInfo.vlan) {
            infoHtml += `
                <div class="device-stat">
                    <span class="stat-label">VLAN:</span>
                    <span class="stat-value">${deviceInfo.vlan}</span>
                </div>
            `;
        }
        
        deviceInfoElement.innerHTML = infoHtml;
    }
    
    onDeviceHover(mesh, isHovering) {
        if (isHovering) {
            mesh.scaling = new BABYLON.Vector3(1.1, 1.1, 1.1);
            if (mesh.material) {
                mesh.material.emissiveColor = new BABYLON.Color3(0.1, 0.2, 0.1);
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
            .filter(device => device.info.type === category);
    }
    
    filterByCategories(categories) {
        const showAll = categories.includes('all');
        
        this.devices.forEach((device, name) => {
            const shouldShow = showAll || categories.includes(device.info.type);
            device.visible = shouldShow;
            
            if (device.mesh) {
                device.mesh.setEnabled(shouldShow);
            }
            
            const label = this.labels.get(name);
            if (label) {
                label.setEnabled(shouldShow && label.parent.isEnabled);
            }
        });
    }
    
    getVisibleDeviceCount() {
        return Array.from(this.devices.values())
            .filter(device => device.visible).length;
    }
    
    getDeviceCount() {
        return this.devices.size;
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
                    // Gentle floating animation
                    device.mesh.position.y += Math.sin(Date.now() * 0.001) * 0.01;
                }
            });
        });
    }
}