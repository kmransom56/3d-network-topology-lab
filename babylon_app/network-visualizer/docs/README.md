# 3D Network Visualizer

A complete Babylon.js application for visualizing network infrastructure in 3D.

## Features

- **3D Device Models**: Import and display 3D models of network devices
- **Interactive Visualization**: Click, hover, and interact with devices
- **Category Filtering**: Filter devices by type (firewall, switch, access point, etc.)
- **Connection Visualization**: See network connections between devices
- **Responsive Design**: Works on desktop and mobile devices
- **Performance Optimized**: Efficient rendering for large networks

## Quick Start

1. Open `index.html` in your web browser
2. The application will automatically load all available 3D models
3. Use mouse to navigate:
   - Left click + drag: Rotate view
   - Right click + drag: Pan view
   - Scroll: Zoom in/out
4. Click on devices to see detailed information

## Customization

### Adding New Models

1. Place your 3D model files (.obj, .gltf) in the `models/` directory
2. Update `manifest.json` with model information
3. The application will automatically load new models

### Modifying Device Categories

Edit the `manifest.json` file to categorize your devices:

```json
{
  "name": "FortiGate-60F",
  "category": "firewall",
  "tags": ["firewall", "security", "utm"]
}
```

### Custom Colors

Device colors are defined in `js/DeviceManager.js`. Modify the `categoryColors` object to change device appearance.

## API Reference

### DeviceManager

Manages 3D device models and their interactions.

- `loadDevice(modelInfo)`: Load a 3D device model
- `getDevicesByCategory(category)`: Get all devices of a specific category
- `filterByCategories(categories)`: Filter visible devices by category
- `toggleLabels(show)`: Show/hide device labels

### ConnectionManager

Manages network connections between devices.

- `createConnection(mesh1, mesh2)`: Create a visual connection
- `toggleVisibility(show)`: Show/hide all connections

### SceneManager

Manages the 3D scene environment.

- `setupEnvironment()`: Configure skybox and lighting

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Performance Tips

- Use GLTF models for better performance
- Limit the number of visible devices
- Disable animations for large networks
- Use category filters to reduce render load

## Troubleshooting

### Models Not Loading
- Check that model files are in the correct directory
- Verify `manifest.json` format is correct
- Check browser console for error messages

### Poor Performance
- Reduce the number of visible devices
- Use simpler 3D models
- Close other browser tabs
- Update graphics drivers

## License

This project is provided as-is for educational and demonstration purposes.
