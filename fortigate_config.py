#!/usr/bin/env python3
"""
FortiGate Configuration Settings
Uses environment variables for secure credential management
"""

import os
from pathlib import Path
from typing import Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from the same directory as this script
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Using system environment variables only.")

# FortiGate Connection Settings from environment
FORTIGATE_CONFIG = {
    "host": os.getenv('FORTIGATE_HOST', '192.168.0.254'),
    "port": int(os.getenv('FORTIGATE_PORT', '10443')),
    "username": os.getenv('FORTIGATE_USERNAME', 'admin'),
    "password": os.getenv('FORTIGATE_PASSWORD', '!cg@RW%G@o'),
    "verify_ssl": os.getenv('FORTIGATE_VERIFY_SSL', 'false').lower() == 'true'
}

# Output Settings from environment
OUTPUT_CONFIG = {
    "topology_file": os.getenv('TOPOLOGY_FILE', 'fortinet_topology.json'),
    "babylon_file": os.getenv('BABYLON_FILE', 'babylon_topology.json'),
    "auto_refresh_interval": int(os.getenv('AUTO_REFRESH_INTERVAL', '300'))
}

# Visualization Settings from environment
VIZ_CONFIG = {
    "device_limits": {
        "switches": int(os.getenv('MAX_SWITCHES', '10')),
        "access_points": int(os.getenv('MAX_ACCESS_POINTS', '20')),
        "endpoints": int(os.getenv('MAX_ENDPOINTS', '50'))
    },
    "layout": {
        "fortigate_position": {"x": 0, "y": 0, "z": 0},
        "switch_spacing": {"x": -3, "z": 2},
        "ap_spacing": {"x": 3, "z": 1.5},
        "endpoint_spacing": {"x": 5, "z": 0.5}
    },
    "colors": {
        "firewall": "#ff4444",
        "switch": "#44ff44",
        "access_point": "#4444ff",
        "endpoint": "#ffaa44",
        "interface": "#aaaaaa"
    }
}

# Filter Settings
FILTER_CONFIG = {
    "include_offline_devices": False,
    "min_bandwidth_threshold": 1,
    "device_types": ["firewall", "switch", "access_point", "endpoint"]
}

# Complete configuration dictionary
CONFIG = {
    "fortigate": FORTIGATE_CONFIG,
    "output": OUTPUT_CONFIG,
    "visualization": VIZ_CONFIG,
    "filters": FILTER_CONFIG
}

def get_config() -> Dict[str, Any]:
    """Return the complete configuration"""
    return CONFIG

def get_fortigate_config() -> Dict[str, Any]:
    """Return FortiGate connection settings"""
    return FORTIGATE_CONFIG

def update_fortigate_config(host=None, port=None, username=None, password=None, verify_ssl=None):
    """Update FortiGate configuration (for command line overrides)"""
    if host is not None:
        FORTIGATE_CONFIG["host"] = host
    if port is not None:
        FORTIGATE_CONFIG["port"] = port
    if username is not None:
        FORTIGATE_CONFIG["username"] = username
    if password is not None:
        FORTIGATE_CONFIG["password"] = password
    if verify_ssl is not None:
        FORTIGATE_CONFIG["verify_ssl"] = verify_ssl

def validate_config() -> bool:
    """Validate that required configuration is present"""
    if not FORTIGATE_CONFIG["host"]:
        print("ERROR: FORTIGATE_HOST not configured")
        return False
    
    if not FORTIGATE_CONFIG["username"]:
        print("ERROR: FORTIGATE_USERNAME not configured")
        return False
    
    if FORTIGATE_CONFIG["password"] == 'YOUR_PASSWORD_HERE':
        print("ERROR: FORTIGATE_PASSWORD not configured")
        return False
    
    return True

def print_config_status():
    """Print current configuration status (without sensitive data)"""
    print("Current FortiGate Configuration:")
    print(f"  Host: {FORTIGATE_CONFIG['host']}")
    print(f"  Port: {FORTIGATE_CONFIG['port']}")
    print(f"  Username: {FORTIGATE_CONFIG['username']}")
    print(f"  Password: {'*' * len(FORTIGATE_CONFIG['password']) if FORTIGATE_CONFIG['password'] != 'YOUR_PASSWORD_HERE' else 'Not set'}")
    print(f"  SSL Verify: {FORTIGATE_CONFIG['verify_ssl']}")
    print(f"  Config File: {Path(__file__).parent / '.env' if Path(__file__).parent / '.env' else 'Not found'}")

def create_env_file():
    """Create a .env file from .env.example if it doesn't exist"""
    env_path = Path(__file__).parent / '.env'
    example_path = Path(__file__).parent / '.env.example'
    
    if not env_path.exists() and example_path.exists():
        import shutil
        shutil.copy(example_path, env_path)
        print(f"Created {env_path} from template")
        print("Please edit the .env file with your FortiGate credentials")
        return True
    
    return False
