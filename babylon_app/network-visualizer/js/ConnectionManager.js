class ConnectionManager {
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

        // Calculate path
        const path = [
            mesh1.position,
            new BABYLON.Vector3(
                (mesh1.position.x + mesh2.position.x) / 2,
                0.5, // Lift slightly
                (mesh1.position.z + mesh2.position.z) / 2
            ),
            mesh2.position
        ];

        // Create tube between meshes
        const line = BABYLON.MeshBuilder.CreateTube(
            `connection_${mesh1.name}_${mesh2.name}`,
            {
                path: path,
                radius: 0.15, // Thicker tube
                sideOrientation: BABYLON.Mesh.DOUBLESIDE,
                updatable: true
            },
            this.scene
        );

        // Create matte material
        const material = new BABYLON.StandardMaterial("connectionMat", this.scene);
        material.diffuseColor = new BABYLON.Color3(0.8, 0.8, 0.8); // Light Grey
        material.specularColor = new BABYLON.Color3(0.1, 0.1, 0.1); // Low specularity
        line.material = material;

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
}