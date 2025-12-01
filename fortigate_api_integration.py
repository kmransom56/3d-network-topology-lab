#!/usr/bin/env python3
"""
FortiGate API Integration
Pulls live network topology data from FortiGate environment
"""

import requests
import json
import ssl
import urllib3
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import asyncio
import aiohttp
import certifi

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FortiGateAPIClient:
    """Client for interacting with FortiGate REST API"""
    
    def __init__(self, host: str, username: str, password: str, port: int = 443, verify_ssl: bool = False, api_token: str = None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.api_token = api_token
        self.verify_ssl = verify_ssl
        self.base_url = f"https://{host}:{port}"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        
        if not verify_ssl:
            self.session.verify = False
        
        # If API token is provided, use it for authentication
        if api_token:
            self.session.headers.update({'Authorization': f'Bearer {api_token}'})
        
        self.csrf_token = None
        self.session_id = None
    
    def login(self) -> bool:
        """Authenticate using API token - no login needed for REST API"""
        try:
            # If API token is provided, test it directly
            if self.api_token:
                # Test API token with a simple API call
                test_url = f"{self.base_url}/api/v2/monitor/system/status?vdom=root"
                response = self.session.get(test_url)
                
                if response.status_code == 200 and response.headers.get('content-type', '').startswith('application/json'):
                    logger.info(f"Successfully authenticated with API token to FortiGate at {self.host}")
                    return True
                else:
                    logger.error(f"API token authentication failed: {response.status_code} - {response.text[:200]}")
                    return False
            else:
                logger.error("No API token provided")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def logout(self):
        """Logout from FortiGate session"""
        try:
            logout_url = f"{self.base_url}/logout"
            response = self.session.get(logout_url)
            logger.info("Logged out from FortiGate")
        except Exception as e:
            logger.error(f"Logout error: {e}")
    
    def test_connection(self) -> bool:
        """Test connection to FortiGate"""
        try:
            # First login
            if not self.login():
                return False
            
            # Test API access
            response = self.session.get(f"{self.base_url}/api/v2/monitor/system/status")
            if response.status_code == 200:
                logger.info(f"Successfully connected to FortiGate at {self.host}")
                return True
            else:
                logger.error(f"Failed to access API: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def get_system_status(self) -> Dict:
        """Get FortiGate system status"""
        try:
            url = f"{self.base_url}/api/v2/monitor/system/status?vdom=root"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                # Extract the actual status from results
                results = data.get('results', {})
                # Merge top-level fields with results for easier access
                status_data = {
                    **results,
                    'serial': data.get('serial', results.get('serial', 'Unknown')),
                    'version': data.get('version', results.get('version', 'Unknown')),
                    'hostname': results.get('hostname', data.get('hostname', 'FortiGate')),
                    'status': data.get('status', 'unknown')
                }
                return status_data
            else:
                logger.error(f"Failed to get system status: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {}
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        try:
            url = f"{self.base_url}/api/v2/cmdb/system/global?vdom=root"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                logger.error(f"Failed to get system info: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {}
    
    def get_interfaces(self) -> List[Dict]:
        """Get network interface information"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/cmdb/system/interface")
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Failed to get interfaces: {e}")
            return []
    
    def get_firewall_policies(self) -> List[Dict]:
        """Get firewall policies"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/cmdb/firewall/policy")
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Failed to get firewall policies: {e}")
    
    def get_addresses(self) -> List[Dict]:
        """Get firewall address objects"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/cmdb/firewall/address")
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Failed to get addresses: {e}")
            return []
    
    def get_firewall_policies(self) -> List[Dict]:
        """Get firewall policies"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/cmdb/firewall/policy")
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Failed to get firewall policies: {e}")
            return []
    
    def get_vips(self) -> List[Dict]:
        """Get VIP (Virtual IP) objects"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/cmdb/firewall/vip")
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Failed to get VIPs: {e}")
            return []
    
    def get_dhcp_servers(self) -> List[Dict]:
        """Get DHCP server information"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/cmdb/system/dhcp/server")
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Failed to get DHCP servers: {e}")
            return []
    
    def get_wifi_settings(self) -> Dict:
        """Get WiFi controller settings"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/cmdb/wifi")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get WiFi settings: {e}")
            return {}
    
    def get_wifi_ap_list(self) -> List[Dict]:
        """Get managed access points"""
        try:
            url = f"{self.base_url}/api/v2/monitor/wifi/managed_ap/select?vdom=root"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Failed to get AP list: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Failed to get AP list: {e}")
            return []
    
    def get_switch_controller(self) -> Dict:
        """Get switch controller information"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/cmdb/switch-controller")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get switch controller: {e}")
            return {}
    
    def get_managed_switches(self) -> List[Dict]:
        """Get managed switches"""
        try:
            url = f"{self.base_url}/api/v2/cmdb/switch-controller/managed-switch?vdom=root"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Failed to get managed switches: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Failed to get managed switches: {e}")
            return []
    
    def get_user_devices(self) -> List[Dict]:
        """Get connected user devices (endpoints)"""
        try:
            url = f"{self.base_url}/api/v2/monitor/user/device/query?vdom=root"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Failed to get user devices: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Failed to get user devices: {e}")
            return []
    
    def get_dhcp_leases(self) -> List[Dict]:
        """Get DHCP lease information"""
        try:
            response = self.session.get(f"{self.base_url}/api/v2/monitor/system/dhcp/lease")
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Failed to get DHCP leases: {e}")
            return []


class NetworkTopologyBuilder:
    """Build network topology from FortiGate data"""
    
    def __init__(self, api_client: FortiGateAPIClient):
        self.api_client = api_client
        self.topology = {
            "devices": [],
            "connections": [],
            "metadata": {
                "last_updated": None,
                "fortigate_info": {}
            }
        }
    
    def build_topology(self) -> Dict:
        """Build complete network topology"""
        logger.info("Building network topology from FortiGate...")
        
        # Get FortiGate system info
        system_status = self.api_client.get_system_status()
        system_info = self.api_client.get_system_info()
        
        # Add FortiGate as central device
        results = system_info.get('results', {})
        first_result = results if isinstance(results, dict) else (results[0] if results and isinstance(results, list) else {})
        
        fortigate_device = {
            "id": "fortigate_main",
            "name": system_status.get('hostname', 'FortiGate'),
            "type": "firewall",
            "model": system_status.get('model', first_result.get('platform_str', 'Unknown')),
            "serial": system_status.get('serial', 'Unknown'),
            "version": system_status.get('version', 'Unknown'),
            "ip": self.api_client.host,
            "position": {"x": 0, "y": 0, "z": 0},
            "metadata": {
                "status": system_status.get('status', 'unknown'),
                "cpu_usage": system_status.get('cpu_usage', 0),
                "memory_usage": system_status.get('mem_usage', 0),
                "uptime": system_status.get('uptime', 0)
            }
        }
        self.topology["devices"].append(fortigate_device)
        self.topology["metadata"]["fortigate_info"] = fortigate_device
        
        # Get network interfaces
        interfaces = self.api_client.get_interfaces()
        for iface in interfaces:
            if iface.get('status') == 'up':
                interface_device = {
                    "id": f"interface_{iface.get('name', 'unknown')}",
                    "name": iface.get('name', 'Unknown Interface'),
                    "type": "interface",
                    "ip": iface.get('ip', ''),
                    "subnet": iface.get('subnet', ''),
                    "connected_to": "fortigate_main",
                    "position": {"x": 2, "y": 0, "z": 0},
                    "metadata": {
                        "mac": iface.get('macaddr', ''),
                        "mtu": iface.get('mtu', 1500),
                        "speed": iface.get('speed', 0)
                    }
                }
                self.topology["devices"].append(interface_device)
                
                # Create connection
                self.topology["connections"].append({
                    "source": "fortigate_main",
                    "target": interface_device["id"],
                    "type": "network",
                    "bandwidth": iface.get('speed', 0)
                })
        
        # Get managed switches
        switches = self.api_client.get_managed_switches()
        for i, switch in enumerate(switches[:10]):  # Limit to first 10 switches
            switch_device = {
                "id": f"switch_{switch.get('name', f'switch_{i}')}",
                "name": switch.get('name', f'Switch {i}'),
                "type": "switch",
                "model": switch.get('model', 'Unknown'),
                "serial": switch.get('serial', 'Unknown'),
                "ip": switch.get('ip', ''),
                "position": {"x": -3, "y": 0, "z": i * 2},
                "connected_to": "fortigate_main",
                "metadata": {
                    "status": switch.get('status', 'unknown'),
                    "ports": switch.get('num_ports', 0),
                    "firmware": switch.get('sw_version', 'Unknown')
                }
            }
            self.topology["devices"].append(switch_device)
            
            # Create connection to FortiGate
            self.topology["connections"].append({
                "source": "fortigate_main",
                "target": switch_device["id"],
                "type": "network",
                "bandwidth": 1000
            })
        
        # Get access points
        try:
            access_points = self.api_client.get_wifi_ap_list()
        except Exception as e:
            logger.warning(f"Failed to get access points: {e}")
            access_points = []
            
        for i, ap in enumerate(access_points[:20]):  # Limit to first 20 APs
            ap_device = {
                "id": f"ap_{ap.get('name', f'ap_{i}')}",
                "name": ap.get('name', f'AP {i}'),
                "type": "access_point",
                "model": ap.get('model', 'Unknown'),
                "serial": ap.get('serial', 'Unknown'),
                "ip": ap.get('ip', ''),
                "position": {"x": 3, "y": 0, "z": i * 1.5},
                "connected_to": "fortigate_main",
                "metadata": {
                    "status": ap.get('status', 'unknown'),
                    "wifi_clients": ap.get('wifi_clients', 0),
                    "radio_1": ap.get('radio_1', {}),
                    "radio_2": ap.get('radio_2', {})
                }
            }
            self.topology["devices"].append(ap_device)
            
            # Create connection to FortiGate
            self.topology["connections"].append({
                "source": "fortigate_main",
                "target": ap_device["id"],
                "type": "wifi",
                "bandwidth": ap.get('radio_1', {}).get('max_bandwidth', 0)
            })
        
        # Get user devices
        try:
            user_devices = self.api_client.get_user_devices()
        except Exception as e:
            logger.warning(f"Failed to get user devices: {e}")
            user_devices = []
            
        for i, device in enumerate(user_devices[:50]):  # Limit to first 50 devices
            user_device = {
                "id": f"device_{device.get('mac', f'device_{i}').replace(':', '_')}",
                "name": device.get('hostname', f'Device {i}'),
                "type": "endpoint",
                "ip": device.get('ip', ''),
                "mac": device.get('mac', ''),
                "position": {"x": 5, "y": 0, "z": i * 0.5},
                "connected_to": "fortigate_main",
                "metadata": {
                    "os": device.get('os_type', 'Unknown'),
                    "user": device.get('user', 'Unknown'),
                    "last_seen": device.get('last_seen', ''),
                    "device_type": device.get('devtype', 'Unknown')
                }
            }
            self.topology["devices"].append(user_device)
            
            # Create connection
            self.topology["connections"].append({
                "source": "fortigate_main",
                "target": user_device["id"],
                "type": "endpoint",
                "bandwidth": 100
            })
        
        # Update metadata
        self.topology["metadata"]["last_updated"] = datetime.now().isoformat()
        self.topology["metadata"]["device_counts"] = {
            "firewall": 1,
            "switch": len(switches),
            "access_point": len(access_points),
            "endpoint": len(user_devices),
            "interface": len([i for i in interfaces if i.get('status') == 'up'])
        }
        
        logger.info(f"Built topology with {len(self.topology['devices'])} devices and {len(self.topology['connections'])} connections")
        return self.topology
    
    def save_topology(self, output_path: Path):
        """Save topology to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.topology, f, indent=2)
        logger.info(f"Topology saved to {output_path}")
    
    def export_to_babylon_format(self) -> Dict:
        """Convert topology to Babylon.js compatible format"""
        babylon_data = {
            "version": "2.0",
            "models": [],
            "connections": [],
            "metadata": self.topology["metadata"]
        }
        
        for device in self.topology["devices"]:
            model = {
                "name": device["id"],
                "displayName": device["name"],
                "category": device["type"],
                "position": device["position"],
                "tags": [device["type"]],
                "metadata": device.get("metadata", {}),
                "properties": {
                    "ip": device.get("ip", ""),
                    "model": device.get("model", ""),
                    "serial": device.get("serial", "")
                }
            }
            babylon_data["models"].append(model)
        
        for conn in self.topology["connections"]:
            connection = {
                "source": conn["source"],
                "target": conn["target"],
                "type": conn["type"],
                "bandwidth": conn.get("bandwidth", 0)
            }
            babylon_data["connections"].append(connection)
        
        return babylon_data


async def main():
    """Main function to pull data from FortiGate and create visualization"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pull network topology from FortiGate')
    parser.add_argument('--host', required=True, help='FortiGate IP address or hostname')
    parser.add_argument('--username', required=True, help='FortiGate username')
    parser.add_argument('--password', required=True, help='FortiGate password')
    parser.add_argument('--port', type=int, default=443, help='FortiGate HTTPS port')
    parser.add_argument('--output', default='fortinet_topology.json', help='Output file for topology')
    parser.add_argument('--babylon-output', default='babylon_topology.json', help='Babylon.js format output')
    parser.add_argument('--no-ssl-verify', action='store_true', help='Disable SSL verification')
    
    args = parser.parse_args()
    
    # Create API client
    api_client = FortiGateAPIClient(
        host=args.host,
        username=args.username,
        password=args.password,
        port=args.port,
        verify_ssl=not args.no_ssl_verify
    )
    
    # Test connection
    if not api_client.test_connection():
        logger.error("Failed to connect to FortiGate. Please check credentials and network connectivity.")
        return
    
    # Build topology
    builder = NetworkTopologyBuilder(api_client)
    topology = builder.build_topology()
    
    # Logout when done
    api_client.logout()
    
    # Save topology
    builder.save_topology(Path(args.output))
    
    # Export to Babylon format
    babylon_data = builder.export_to_babylon_format()
    with open(args.babylon_output, 'w') as f:
        json.dump(babylon_data, f, indent=2)
    
    print("\n" + "="*60)
    print("FortiGate Topology Extraction Complete!")
    print("="*60)
    print(f"Devices discovered: {len(topology['devices'])}")
    print(f"Connections mapped: {len(topology['connections'])}")
    print(f"Topology saved to: {args.output}")
    print(f"Babylon.js format: {args.babylon_output}")
    
    # Print device summary
    counts = topology["metadata"]["device_counts"]
    print("\nDevice Summary:")
    print(f"  Firewall: {counts['firewall']}")
    print(f"  Switches: {counts['switch']}")
    print(f"  Access Points: {counts['access_point']}")
    print(f"  Endpoints: {counts['endpoint']}")
    print(f"  Interfaces: {counts['interface']}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
