/**
 * DeviceManager - 3D Model Loading and Device Management
 */

class DeviceManager {
    constructor(scene) {
        this.scene = scene;
        this.devices = new Map();
        this.labels = new Map();
        this.animationEnabled = false;
        this.deviceData = [];
        this.loadedModels = new Map(); // Cache for loaded 3D models
        this.iconTextures = new Map(); // Cache for icon textures
    }

    async loadDevices(deviceData) {
        this.deviceData = deviceData;
        console.log(`Loading ${deviceData.length} devices...`);

        // Pre-load all 3D models and icons
        await this.preloadAssets();

        for (const deviceInfo of deviceData) {

            // 1. Try to use Icon (Billboard) for Endpoints
            let iconType = deviceInfo.type;
            if (deviceInfo.type === 'endpoint') {
                iconType = `endpoint-${this.detectEndpointType(deviceInfo)}`;
                if (this.iconTextures.has(iconType)) {
                    mesh = this.createIconBillboard(deviceInfo, this.iconTextures.get(iconType));
                } else {
                    mesh = this.createClayModel(deviceInfo);
                }
            } else {
                // 2. Use Textured Clay Model for Network Devices
                mesh = this.createClayModel(deviceInfo);
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

    createIconBillboard(deviceInfo, texture) {
        const plane = BABYLON.MeshBuilder.CreatePlane(deviceInfo.name, { width: 3, height: 3 }, this.scene);
        const material = new BABYLON.StandardMaterial(`${deviceInfo.name}_mat`, this.scene);
        material.diffuseTexture = texture;
        material.specularColor = new BABYLON.Color3(0, 0, 0);
        material.emissiveColor = new BABYLON.Color3(1, 1, 1); // Self-illuminated
        material.useAlphaFromDiffuseTexture = true;
        plane.material = material;
        plane.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;
        return plane;
    }

    createClayModel(deviceInfo) {
        let mesh;
        let texture = null;
        let color = new BABYLON.Color3(1, 1, 1); // Default White

        // Define shapes and textures based on type
        switch (deviceInfo.type) {
            case 'firewall':
                mesh = BABYLON.MeshBuilder.CreateBox(deviceInfo.name, { width: 3, height: 1, depth: 2 }, this.scene);
                texture = this.iconTextures.get('firewall_texture');
                break;
            case 'switch':
                mesh = BABYLON.MeshBuilder.CreateBox(deviceInfo.name, { width: 3, height: 0.8, depth: 2 }, this.scene);
                texture = this.iconTextures.get('switch_texture');
                break;
            default: // Endpoint
                mesh = BABYLON.MeshBuilder.CreateBox(deviceInfo.name, { size: 1 }, this.scene);
                color = new BABYLON.Color3.FromHexString("#ECF0F1"); // White
        }

        // Apply Material
        const material = new BABYLON.StandardMaterial(`${deviceInfo.name}_clay`, this.scene);

        if (texture) {
            material.diffuseTexture = texture;
            material.diffuseColor = new BABYLON.Color3(1, 1, 1);

            // Fix for AP texture rotation/orientation if needed
            if (deviceInfo.type === 'access_point') {
                material.diffuseTexture.wAng = Math.PI; // Rotate 180 if needed
            }
        } else {
            material.diffuseColor = color;
        }

        material.specularColor = new BABYLON.Color3(0.2, 0.2, 0.2); // Slight gloss for plastic
        material.roughness = 0.5;
        mesh.material = material;

        return mesh;
    }

    createRoundedBox(name, options) {
        const width = options.width / 2;
        const depth = options.depth / 2;
        const radius = options.radius || 0.2;
        const height = options.height || 1;

        const shape = [];
        const segments = 16; // Smooth corners

        const addCorner = (offsetX, offsetZ, startAngle) => {
            for (let i = 0; i <= segments; i++) {
                const angle = startAngle + (Math.PI / 2 * (i / segments));
                shape.push(new BABYLON.Vector3(
                    offsetX + Math.cos(angle) * radius,
                    0,
                    offsetZ + Math.sin(angle) * radius
                ));
            }
        };

        // Generate rounded rectangle path (Counter-clockwise)
        addCorner(width - radius, depth - radius, 0); // Top Right
        addCorner(-width + radius, depth - radius, Math.PI / 2); // Top Left
        addCorner(-width + radius, -depth + radius, Math.PI); // Bottom Left
        addCorner(width - radius, -depth + radius, 3 * Math.PI / 2); // Bottom Right

        // Close shape
        shape.push(shape[0]);

        // Extrude
        const mesh = BABYLON.MeshBuilder.ExtrudePolygon(name, {
            shape: shape,
            depth: height,
            sideOrientation: BABYLON.Mesh.DOUBLESIDE,
            wrap: true
        }, this.scene);

        // Center vertically
        mesh.position.y = -height / 2;
        mesh.bakeCurrentTransformIntoVertices();

        return mesh;
    }

    detectEndpointType(deviceInfo) {
        const name = (deviceInfo.name || '').toLowerCase();
        if (name.includes('laptop') || name.includes('macbook')) return 'laptop';
        if (name.includes('mobile') || name.includes('phone')) return 'mobile';
        if (name.includes('server')) return 'server';
        return 'desktop';
    }

    autoPositionDevice(mesh, index) {
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
        labelMaterial.useAlphaFromDiffuseTexture = true;

        const labelPlane = BABYLON.MeshBuilder.CreatePlane(
            `${text}_label`,
            { width: 2, height: 0.5 },
            this.scene
        );
        labelPlane.material = labelMaterial;
        labelPlane.parent = mesh;
        labelPlane.position.y = 2; // Higher up
        labelPlane.billboardMode = BABYLON.Mesh.BILLBOARDMODE_ALL;

        const ctx = labelTexture.getContext();
        ctx.font = 'bold 20px Inter, Arial';
        ctx.fillStyle = 'white';
        // Add text shadow for readability
        ctx.shadowColor = "rgba(0,0,0,0.5)";
        ctx.shadowBlur = 4;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, 128, 32);
        labelTexture.update();

        this.labels.set(text, labelPlane);
    }

    setupDeviceInteraction(mesh, deviceInfo) {
        mesh.actionManager = new BABYLON.ActionManager(this.scene);

        mesh.actionManager.registerAction(
            new BABYLON.ExecuteCodeAction(
                BABYLON.ActionManager.OnPickTrigger,
                () => this.onDeviceClick(deviceInfo)
            )
        );

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
        let infoHtml = `<h4>${deviceInfo.name}</h4>`;
        infoHtml += `<div class="device-stat"><span class="stat-label">Type:</span><span class="stat-value">${deviceInfo.type}</span></div>`;
        if (deviceInfo.ip) infoHtml += `<div class="device-stat"><span class="stat-label">IP:</span><span class="stat-value">${deviceInfo.ip}</span></div>`;
        deviceInfoElement.innerHTML = infoHtml;
    }

    onDeviceHover(mesh, isHovering) {
        if (isHovering) {
            mesh.scaling = new BABYLON.Vector3(1.1, 1.1, 1.1);
        } else {
            mesh.scaling = new BABYLON.Vector3(1, 1, 1);
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
            if (device.mesh) device.mesh.setEnabled(shouldShow);
            const label = this.labels.get(name);
            if (label) label.setEnabled(shouldShow && label.parent.isEnabled);
        });
    }

    getVisibleDeviceCount() {
        return Array.from(this.devices.values()).filter(device => device.visible).length;
    }

    toggleLabels(show) {
        this.labels.forEach(label => label.setEnabled(show && label.parent.isEnabled));
    }

    toggleAnimation(enabled) {
        this.animationEnabled = enabled;
        if (enabled) this.startAnimation();
    }

    startAnimation() {
        if (!this.animationEnabled) return;
        this.scene.registerBeforeRender(() => {
            if (!this.animationEnabled) return;
            this.devices.forEach(device => {
                if (device.mesh && device.visible) {
                    device.mesh.position.y = 1 + Math.sin(Date.now() * 0.001) * 0.1;
                }
            });
        });
    }
}