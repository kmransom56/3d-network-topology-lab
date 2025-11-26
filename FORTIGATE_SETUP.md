# FortiGate Live Network Discovery Setup

## Overview
This system connects to your live FortiGate environment to discover and visualize your network topology in 3D using Babylon.js. **Note: Uses session-based authentication instead of API tokens due to FortiOS bugs.**

## Prerequisites
- FortiGate with web management access
- Administrator account credentials (username/password)
- Python 3.7+ with required packages
- Network connectivity to FortiGate management interface

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Credentials

### Create Environment File (Recommended)
```bash
python run_fortigate_discovery.py --create-env
```

This creates a `.env` file from the template. Edit it with your credentials:

```bash
# FortiGate Connection Settings
FORTIGATE_HOST=192.168.1.1
FORTIGATE_PORT=443
FORTIGATE_USERNAME=admin
FORTIGATE_PASSWORD=your_actual_password
FORTIGATE_VERIFY_SSL=false

# Optional: Customize output files and limits
TOPOLOGY_FILE=my_network_topology.json
BABYLON_FILE=my_babylon_topology.json
MAX_SWITCHES=20
MAX_ACCESS_POINTS=50
MAX_ENDPOINTS=100
```

### Environment Variables (Alternative)
Set system environment variables instead of using .env file:

```bash
# Windows (Command Prompt)
set FORTIGATE_HOST=192.168.1.1
set FORTIGATE_USERNAME=admin
set FORTIGATE_PASSWORD=your_password

# Windows (PowerShell)
$env:FORTIGATE_HOST="192.168.1.1"
$env:FORTIGATE_USERNAME="admin"
$env:FORTIGATE_PASSWORD="your_password"

# Linux/Mac
export FORTIGATE_HOST=192.168.1.1
export FORTIGATE_USERNAME=admin
export FORTIGATE_PASSWORD=your_password
```

### Security Best Practices
- **Never commit .env files to version control** (included in .gitignore)
- Use strong, unique passwords for admin accounts
- Consider dedicated read-only admin account for discovery
- Configure **Trusted Hosts** on FortiGate to restrict management access
- Use **HTTPS** (port 443)
- Regularly rotate admin passwords

## Step 3: Configure FortiGate Access

### Create Administrator Account
1. Log into your FortiGate web interface
2. Go to **System > Administrators**
3. Create new administrator with type **Local** or **LDAP**
4. Set appropriate permissions (read-only is sufficient for discovery)
5. **Important**: Use a strong password and store it securely

### Optional: Configure Trusted Hosts
1. In FortiGate, go to **System > Administrators**
2. Edit your admin account
3. Set **Trusted Hosts** to your IP address/subnet
4. This restricts management access to trusted sources

## Step 4: Test Configuration

### Check Current Configuration
```bash
python run_fortigate_discovery.py --config
```

This shows your current configuration without revealing sensitive data.

### Validate Setup
```bash
python run_fortigate_discovery.py --host 192.168.1.1 --username admin --password your_password --config
```

## Step 5: Run Network Discovery

### Using Environment Configuration
```bash
python run_fortigate_discovery.py
```

### With Command Line Overrides
```bash
python run_fortigate_discovery.py --host 192.168.1.1 --username admin --password your_password --no-ssl-verify
```

### Custom Output Files
```bash
python run_fortigate_discovery.py --output my_topology.json --babylon-output my_babylon.json
```

## Step 6: View 3D Visualization

### Copy to Babylon App
```bash
cp babylon_topology.json babylon_app/network-visualizer/models/manifest.json
```

### Open Visualization
Open `babylon_app/network-visualizer/index.html` in your web browser

## Configuration Priority

The system uses this priority order (highest to lowest):
1. **Command line arguments** (override everything)
2. **.env file** (highest priority file-based)
3. **System environment variables**
4. **Default values** (fallback)

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `FORTIGATE_HOST` | `192.168.1.1` | FortiGate IP address |
| `FORTIGATE_PORT` | `443` | HTTPS port |
| `FORTIGATE_USERNAME` | `admin` | Admin username |
| `FORTIGATE_PASSWORD` | `YOUR_PASSWORD_HERE` | Admin password |
| `FORTIGATE_VERIFY_SSL` | `false` | SSL verification |
| `TOPOLOGY_FILE` | `fortinet_topology.json` | Topology output file |
| `BABYLON_FILE` | `babylon_topology.json` | Babylon.js output |
| `MAX_SWITCHES` | `10` | Maximum switches to discover |
| `MAX_ACCESS_POINTS` | `20` | Maximum APs to discover |
| `MAX_ENDPOINTS` | `50` | Maximum endpoints to discover |

## What Gets Discovered

### Devices
- **FortiGate**: Main firewall with system info
- **Managed Switches**: FortiSwitch devices with port status
- **Access Points**: FortiAPs with client counts
- **Endpoints**: Connected user devices
- **Interfaces**: Active network interfaces

### Connections
- Network links between devices
- WiFi connections to access points
- Bandwidth information where available

### Device Metadata
- IP addresses and MAC addresses
- Model and serial numbers
- System status and performance
- Firmware versions
- Connected clients

## Example Output

```
============================================================
FortiGate Network Discovery
============================================================
Target: 192.168.1.1:443
Username: admin
SSL Verification: False

Testing connection to FortiGate...
✓ Connection successful!

Discovering network topology...

============================================================
Discovery Complete!
============================================================
Devices discovered: 47
Connections mapped: 46
Topology file: fortinet_topology.json
Babylon.js file: babylon_topology.json

Device Summary:
  FortiGate: 1
  Switches: 3
  Access Points: 8
  Endpoints: 35
  Active Interfaces: 5
```

## Troubleshooting

### Configuration Issues
```bash
# Check if .env file exists and is readable
python run_fortigate_discovery.py --config

# Create .env if missing
python run_fortigate_discovery.py --create-env

# Test with command line to bypass .env
python run_fortigate_discovery.py --host 192.168.1.1 --username admin --password test
```

### Connection Failed
- Check FortiGate IP and port
- Verify username and password are valid
- Ensure admin access is enabled
- Check network connectivity
- Verify trusted hosts configuration

### Login Failed
- Check if admin account is locked
- Verify password hasn't expired
- Check if two-factor authentication is required
- Ensure account has sufficient permissions

### SSL Certificate Errors
- Use `--no-ssl-verify` for self-signed certificates
- Or set `FORTIGATE_VERIFY_SSL=true` in .env
- Install FortiGate certificate in trust store

### No Devices Found
- Check admin permissions
- Verify switch controller is enabled
- Check WiFi controller status
- Ensure devices are online

### Session Timeout
- Discovery may timeout on very large networks
- Increase device limits in .env file
- Use filters to reduce scope

## Security Considerations

### Credential Protection
- `.env` files are automatically excluded from git via `.gitignore`
- Never share or commit credential files
- Use read-only admin accounts when possible
- Regularly rotate admin passwords
- Monitor admin access logs on FortiGate

### Network Security
- Configure trusted hosts on FortiGate
- Use HTTPS for all management connections
- Consider VPN access for remote management
- Disable unused management interfaces

## Advanced Usage

### Custom Device Limits
Edit `.env` file:
```bash
MAX_SWITCHES=50
MAX_ACCESS_POINTS=100
MAX_ENDPOINTS=500
```

### Multiple FortiGates
Create multiple .env files:
```bash
# .env.production (production FortiGate)
FORTIGATE_HOST=10.1.1.1
FORTIGATE_USERNAME=prod_admin

# .env.staging (staging FortiGate)  
FORTIGATE_HOST=10.2.1.1
FORTIGATE_USERNAME=staging_admin

# Use specific environment
cp .env.production .env
python run_fortigate_discovery.py
```

### Automation Scripts
```bash
#!/bin/bash
# daily_discovery.sh

# Set credentials securely
export FORTIGATE_HOST=192.168.1.1
export FORTIGATE_USERNAME=admin
export FORTIGATE_PASSWORD=$SECURE_PASSWORD_VAR

# Run discovery
python run_fortigate_discovery.py --output "topology_$(date +%Y%m%d).json"

# Copy to web server
cp babylon_topology.json /var/www/html/network/
```

## Integration with Existing Tools

The generated topology files can be:
- Imported into network monitoring systems
- Used for capacity planning
- Integrated with documentation tools
- Customized for specific use cases

## Support

For issues with:
- **FortiGate Access**: Check FortiOS documentation
- **Session Authentication**: Review admin account settings
- **Environment Configuration**: Use `--config` flag to debug
- **This Tool**: Check logs and configuration
- **Babylon.js**: Check browser console for errors
