class SceneManager {
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
}