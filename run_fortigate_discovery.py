#!/usr/bin/env python3
"""
FortiGate Network Discovery Runner
Easy script to discover and visualize your FortiGate network
"""

import sys
import argparse
from pathlib import Path
from fortigate_config import get_fortigate_config, update_fortigate_config, validate_config, print_config_status, create_env_file
from fortigate_api_integration import FortiGateAPIClient, NetworkTopologyBuilder


def main():
    """Main discovery runner"""
    parser = argparse.ArgumentParser(description='Discover FortiGate Network Topology')
    parser.add_argument('--host', help='FortiGate IP address (overrides config)')
    parser.add_argument('--username', help='FortiGate username (overrides config)')
    parser.add_argument('--password', help='FortiGate password (overrides config)')
    parser.add_argument('--port', type=int, help='FortiGate HTTPS port (overrides config)')
    parser.add_argument('--no-ssl-verify', action='store_true', help='Disable SSL verification')
    parser.add_argument('--output', help='Output topology file (overrides config)')
    parser.add_argument('--babylon-output', help='Babylon.js format output (overrides config)')
    parser.add_argument('--config', action='store_true', help='Show current configuration')
    parser.add_argument('--create-env', action='store_true', help='Create .env file from template')
    
    args = parser.parse_args()
    
    # Create .env file if requested
    if args.create_env:
        if create_env_file():
            print("✓ .env file created. Please edit it with your credentials.")
        else:
            print("✗ .env file already exists or template not found.")
        return
    
    # Show configuration if requested
    if args.config:
        print_config_status()
        print("\nConfiguration Sources:")
        print("  1. .env file (highest priority)")
        print("  2. System environment variables")
        print("  3. Default values")
        print("  4. Command line arguments (override all)")
        print("\nTo update configuration:")
        print("  1. Edit .env file (recommended)")
        print("  2. Set environment variables")
        print("  3. Use command line arguments")
        return
    
    # Update configuration with command line arguments
    update_fortigate_config(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        verify_ssl=not args.no_ssl_verify
    )
    
    # Get final configuration
    config = get_fortigate_config()
    
    # Validate configuration
    if not validate_config():
        print("\nTo fix configuration:")
        print("  1. Run: python run_fortigate_discovery.py --create-env")
        print("  2. Edit the created .env file")
        print("  3. Or use command line arguments")
        sys.exit(1)
    
    print("="*60)
    print("FortiGate Network Discovery")
    print("="*60)
    print(f"Target: {config['host']}:{config['port']}")
    print(f"Username: {config['username']}")
    print(f"SSL Verification: {config['verify_ssl']}")
    print()
    
    # Create API client
    api_client = FortiGateAPIClient(
        host=config['host'],
        username=config['username'],
        password=config['password'],
        port=config['port'],
        verify_ssl=config['verify_ssl']
    )
    
    # Test connection
    print("Testing connection to FortiGate...")
    if not api_client.test_connection():
        print("ERROR: Failed to connect to FortiGate!")
        print("Please check:")
        print("  - FortiGate IP address and port")
        print("  - Username and password are valid")
        print("  - Network connectivity")
        print("  - Admin access is enabled on FortiGate")
        print("  - Trusted hosts configuration")
        sys.exit(1)
    
    print("✓ Connection successful!")
    
    # Build topology
    print("\nDiscovering network topology...")
    builder = NetworkTopologyBuilder(api_client)
    topology = builder.build_topology()
    
    # Logout when done
    api_client.logout()
    
    # Get output file names
    output_config = config.get('output', {})
    topology_file = args.output or output_config.get('topology_file', 'fortinet_topology.json')
    babylon_file = args.babylon_output or output_config.get('babylon_file', 'babylon_topology.json')
    
    # Save topology
    print(f"\nSaving topology to {topology_file}...")
    builder.save_topology(Path(topology_file))
    
    # Export to Babylon format
    print(f"Exporting to Babylon.js format: {babylon_file}...")
    babylon_data = builder.export_to_babylon_format()
    with open(babylon_file, 'w') as f:
        import json
        json.dump(babylon_data, f, indent=2)
    
    # Display results
    print("\n" + "="*60)
    print("Discovery Complete!")
    print("="*60)
    print(f"Devices discovered: {len(topology['devices'])}")
    print(f"Connections mapped: {len(topology['connections'])}")
    print(f"Topology file: {topology_file}")
    print(f"Babylon.js file: {babylon_file}")
    
    # Device summary
    counts = topology["metadata"]["device_counts"]
    print("\nDevice Summary:")
    print(f"  FortiGate: {counts['firewall']}")
    print(f"  Switches: {counts['switch']}")
    print(f"  Access Points: {counts['access_point']}")
    print(f"  Endpoints: {counts['endpoint']}")
    print(f"  Active Interfaces: {counts['interface']}")
    
    print("\nNext Steps:")
    print(f"1. Copy {babylon_file} to babylon_app/network-visualizer/models/")
    print("2. Open babylon_app/network-visualizer/index.html in your browser")
    print("3. View your live 3D network topology!")
    print("="*60)


if __name__ == "__main__":
    main()
