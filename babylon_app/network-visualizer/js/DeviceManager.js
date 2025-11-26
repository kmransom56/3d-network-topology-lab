class DeviceManager {
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
}