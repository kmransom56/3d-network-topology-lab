# 3D Network Topology Lab

A comprehensive laboratory for discovering, visualizing, and managing network infrastructure in interactive 3D. This tool connects to live FortiGate environments and generates real-time 3D network topology diagrams using Babylon.js, plus supports VSS to SVG conversion for custom network diagrams.

## 🚀 Features

### 🔍 **Live Network Discovery**
- **Session-based authentication** (works around FortiOS API token bugs)
- **Multi-device support**: FortiGate, FortiSwitch, FortiAP, endpoints
- **Real-time topology** with device metadata and connections
- **Secure credential management** with environment variables

### 🎨 **3D Visualization**
- **Interactive 3D diagrams** using Babylon.js
- **Authentic FortiGate 3D models** (FortiGate-61E, FortiSwitch-124E-POE, FortiAP-231F)
- **Realistic device models** with proper materials and scaling
- **Network connections** with bandwidth visualization
- **Web-based interface** for easy sharing

### 📊 **VSS to SVG Conversion**
- **Microsoft Visio support** for network diagrams
- **3D model generation** from SVG icons
- **Babylon.js integration** with optimized assets
- **Batch processing** capabilities

## 🏗️ Architecture

```
FortiGate Network → API Integration → Blender 3D Models → Babylon.js Visualization
     ↓                    ↓              ↓                    ↓
Live Discovery    Session Auth    Realistic Models    Interactive 3D
Device Metadata    Environment     FortiGate Equipment Web Interface
Network Links     Secure Config   .glb Files         Real-time Updates
```

## 📦 Installation

### Prerequisites
- Python 3.7+
- FortiGate with admin access
- Modern web browser
- Blender 5.0+ (for 3D model creation)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/kmransom56/3d-network-topology-lab.git
cd 3d-network-topology-lab

# Install dependencies
pip install -r requirements.txt

# Create environment configuration
python run_fortigate_discovery.py --create-env

# Edit .env with your FortiGate credentials
# FORTIGATE_HOST=192.168.1.1
# FORTIGATE_USERNAME=admin
# FORTIGATE_PASSWORD=your_password
```

## 🎯 Quick Start

### 1. Discover Your Network
```bash
# Test configuration
python run_fortigate_discovery.py --config

# Run discovery
python run_fortigate_discovery.py
```

### 2. Generate 3D Models (First Time Setup)
```bash
# Create authentic FortiGate 3D models
python create_fixed_endpoints.py

# Verify models are created
ls babylon_app/network-visualizer/assets/models/*.glb
```

### 3. Launch 3D Visualization
```bash
# Copy topology to 3D app
cp babylon_topology.json babylon_app/network-visualizer/models/manifest.json

# Start web server
cd babylon_app
node server.js

# Open browser to http://localhost:3001
```

### 4. Convert Visio Diagrams (Optional)
```bash
# Convert VSS to SVG
python vss_to_svg.py input.vss --backend vss_extractor

# Convert SVG to 3D models
python svg_to_3d.py extracted_svgs/ --output 3d_models/

# Generate Babylon.js integration
python babylon_integration.py --input 3d_models/ --output web_app/
```

## 📁 Project Structure

```
3d-network-topology-lab/
├── 🔧 Core Components
│   ├── fortigate_api_integration.py    # FortiGate API client
│   ├── run_fortigate_discovery.py     # Discovery runner
│   ├── fortigate_config.py            # Environment configuration
│   └── .env.example                   # Credential template
├── 🎨 3D Visualization
│   ├── babylon_app/                   # Babylon.js web application
│   │   ├── network-visualizer/       # Main 3D visualizer
│   │   ├── assets/models/             # 3D model files (.glb)
│   │   └── js/DeviceManager.js       # Model loading logic
│   ├── create_fixed_endpoints.py      # 3D model generator
│   ├── svg_to_3d.py                  # SVG to 3D converter
│   └── babylon_integration.py         # Web app generator
├── 📊 VSS Conversion
│   ├── converter.py                   # VSS extraction backend
│   └── vss_to_svg.py                  # VSS to SVG converter
├── 📚 Documentation
│   ├── FORTIGATE_SETUP.md             # Detailed setup guide
│   ├── QUICKSTART.md                  # Quick reference
│   ├── vss_to_3d_workflow.md          # 3D model workflow
│   └── .gitignore                     # Security protections
└── 📋 Configuration
    ├── requirements.txt               # Python dependencies
    └── .env                          # Your credentials (gitignored)
```

## 🔐 Security Features

- **Environment-based configuration** - No hardcoded credentials
- **Session authentication** - Secure login without API tokens
- **Git protection** - `.env` files excluded from version control
- **Trusted hosts** support for restricted access
- **SSL verification** options for secure connections

## 🌟 Use Cases

### **Network Operations**
- **Live topology monitoring** for network teams
- **Change visualization** before/after network updates
- **Capacity planning** with device inventory
- **Troubleshooting** with visual network maps

### **Documentation & Compliance**
- **Automated network diagrams** for documentation
- **Compliance reporting** with device inventories
- **Audit trails** with timestamped topology data
- **Network asset management**

### **Integration & Automation**
- **CI/CD pipelines** for network monitoring
- **API integration** with existing tools
- **Custom dashboards** using exported data
- **Scheduled topology updates**

## 🛠️ Advanced Configuration

### Environment Variables
```bash
# FortiGate Connection
FORTIGATE_HOST=192.168.1.1
FORTIGATE_PORT=443
FORTIGATE_USERNAME=admin
FORTIGATE_PASSWORD=secure_password
FORTIGATE_VERIFY_SSL=false

# Discovery Limits
MAX_SWITCHES=50
MAX_ACCESS_POINTS=100
MAX_ENDPOINTS=500

# Output Configuration
TOPOLOGY_FILE=network_topology.json
BABYLON_FILE=babylon_network.json
```

### Custom Device Positioning
```python
# In fortigate_config.py
VIZ_CONFIG = {
    "layout": {
        "fortigate_position": {"x": 0, "y": 0, "z": 0},
        "switch_spacing": {"x": -5, "z": 3},
        "ap_spacing": {"x": 5, "z": 2},
        "endpoint_spacing": {"x": 8, "z": 1}
    }
}
```

## 📊 Supported Devices

| Device Type | Discovery Method | 3D Model | File Size | Metadata |
|-------------|------------------|-----------|-----------|----------|
| **FortiGate-61E** | System API | Firewall (1,832 bytes) | ✅ Working | CPU, memory, uptime |
| **FortiSwitch-124E-POE** | Switch Controller | Switch (2,048 bytes) | ✅ Working | Port status, VLANs |
| **FortiAP-231F** | WiFi Controller | Access Point (70,904 bytes) | ✅ Working | Client count, radio info |
| **Laptop** | User Devices | Computer (2,024 bytes) | ✅ Working | IP, MAC, OS type |
| **Desktop** | User Devices | PC Tower (2,040 bytes) | ✅ Working | IP, MAC, OS type |
| **Mobile** | User Devices | Phone (2,040 bytes) | ✅ Working | IP, MAC, OS type |
| **Server** | User Devices | Rack Server (2,036 bytes) | ✅ Working | IP, MAC, OS type |
| **Interfaces** | System Interface | Network Port | N/A | Speed, status, MTU |

## 🚀 Deployment Options

### **Local Development**
```bash
python run_fortigate_discovery.py
cd babylon_app && node server.js
```

### **Docker Container**
```bash
docker build -t fortigate-visualizer .
docker run -p 8080:8080 --env-file .env fortigate-visualizer
```

### **Production Web Server**
```bash
# Behind nginx/Apache with SSL
# Environment variables for credentials
# Scheduled discovery via cron/systemd
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
git clone https://github.com/kmransom56/3d-network-topology-lab.git
cd 3d-network-topology-lab
pip install -r requirements.txt
python run_fortigate_discovery.py --config
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### **Troubleshooting**
- Check `FORTIGATE_SETUP.md` for detailed setup instructions
- Use `--config` flag to debug configuration issues
- Review FortiGate admin account permissions
- Verify network connectivity to FortiGate

### **Common Issues**
- **Connection failed**: Check IP, credentials, trusted hosts
- **No devices found**: Verify admin permissions, controller status
- **SSL errors**: Use `--no-ssl-verify` or install certificates
- **Session timeout**: Increase device limits in configuration

### **Getting Help**
- 📖 [Documentation](FORTIGATE_SETUP.md)
- 🚀 [Quick Start](QUICKSTART.md)
- 🐛 [Issue Tracker](https://github.com/kmransom56/3d-network-topology-lab/issues)
- 💬 [Discussions](https://github.com/kmransom56/3d-network-topology-lab/discussions)

## 🎉 Acknowledgments

- **Fortinet** for FortiGate network security products
- **Babylon.js** for 3D web visualization
- **Python** community for excellent libraries
- **Contributors** who help improve this project

## 📸 Screenshots

### 🎨 3D Network Visualization
![3D Network Visualizer](screenshots/3d_main_interface.png)

### ⚙️ Configuration Setup
![Configuration Setup](screenshots/configuration_setup.png)

### 🔄 VSS to SVG Conversion
![VSS Converter](screenshots/vss_converter_help.png)

### 📁 Project Structure
![Project Structure](screenshots/project_structure.png)

### 📖 Documentation
![README Preview](screenshots/readme_preview.png)

---

**Transform your FortiGate network from static diagrams to interactive 3D visualizations! 🌐✨**
