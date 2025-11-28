#!/usr/bin/env python3
"""
Python API Service for Shared Gateway
Provides discovery and 3D model services
"""

import json
import sys
import os
from pathlib import Path
import asyncio
from aiohttp import web, ClientSession
from aiohttp.web import Application, Request, Response
import aiohttp_cors

# Add babylon_3d to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from fortigate_api_integration import FortiGateAPIClient
    from fortigate_config import get_config, validate_config
except ImportError:
    print("Warning: FortiGate modules not available, using mock data")
    FortiGateAPIClient = None

class PythonAPIService:
    def __init__(self):
        self.config = self.get_mock_config()
        self.forti_client = None
        self.cache = {}
        
    def get_mock_config(self):
        return {
            'fortigate': {
                'host': os.environ.get('FORTIGATE_HOST', '192.168.1.1'),
                'username': os.environ.get('FORTIGATE_USERNAME', 'admin'),
                'password': os.environ.get('FORTIGATE_PASSWORD', ''),
                'port': int(os.environ.get('FORTIGATE_PORT', 443)),
                'verify_ssl': os.environ.get('VERIFY_SSL', 'false').lower() == 'true'
            }
        }
    
    async def start(self):
        """Initialize the service"""
        print("Python API Service starting...")
        
    async def get_topology(self, request):
        """Get network topology data"""
        # Return mock topology data
        topology_data = {
            'fortigate': {
                'name': 'FortiGate-61E',
                'serial': 'FG61E3X16800123',
                'version': 'v6.4.5',
                'ip': self.config['fortigate']['host']
            },
            'switches': [],
            'access_points': [],
            'endpoints': []
        }
        return web.json_response(topology_data)
    
    async def get_fortiaps(self, request):
        """Get FortiAP data"""
        return web.json_response([])
    
    async def get_fortiswitches(self, request):
        """Get FortiSwitch data"""
        return web.json_response([])
    
    async def get_historical(self, request):
        """Get historical data"""
        return web.json_response([])
    
    async def discover_devices(self, request):
        """Run device discovery"""
        try:
            data = await request.json()
            return web.json_response({'status': 'discovery_started', 'parameters': data})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def convert_vss(self, request):
        """Convert VSS to SVG"""
        try:
            data = await request.json()
            vss_path = data.get('vss_file_path')
            if not vss_path:
                return web.json_response({'error': 'VSS file path required'}, status=400)
            
            return web.json_response({'status': 'conversion_started', 'file': vss_path})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

async def main():
    service = PythonAPIService()
    await service.start()
    
    app = web.Application()
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    
    # Add routes
    app.router.add_get('/topology', service.get_topology)
    app.router.add_get('/fortiaps', service.get_fortiaps)
    app.router.add_get('/fortiswitches', service.get_fortiswitches)
    app.router.add_get('/historical', service.get_historical)
    app.router.add_post('/discover', service.discover_devices)
    app.router.add_post('/convert_vss', service.convert_vss)
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    port = int(os.environ.get('PYTHON_API_PORT', 13002))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', port)
    await site.start()
    
    print(f"Python API Service running on port {port}")
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    asyncio.run(main())
