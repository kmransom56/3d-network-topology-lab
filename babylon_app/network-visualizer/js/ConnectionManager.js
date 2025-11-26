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
}