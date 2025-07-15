# Trajectory Optimization React Frontend

This React frontend provides an interactive interface for the trajectory optimization system with parameter controls and real-time visualization.

## Features

- **Interactive Controls**: Sliders for adjusting rocket parameters
  - Vertical position (0-200 m)
  - Horizontal position (-100-100 m)
  - Initial vertical speed (-50-50 m/s)
  - Initial horizontal speed (-50-50 m/s)

- **Real-time Visualization**: 
  - XY grid showing rocket position
  - Velocity vector visualization
  - Real-time parameter feedback

- **Optimization Integration**: 
  - Send parameters to backend API
  - Status feedback and error handling

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn package manager

## Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

## Running the Application

### Development Mode

1. **Start the development server**:
   ```bash
   npm start
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:3000
   ```

The application will automatically reload when you make changes to the code.

### Production Build

1. **Create a production build**:
   ```bash
   npm run build
   ```

2. **Serve the built files** (optional):
   ```bash
   npm install -g serve
   serve -s build
   ```

## Usage

### Parameter Controls

1. **Adjust rocket parameters** using the sliders on the left panel:
   - **Vertical Position**: Starting height of the rocket
   - **Horizontal Position**: Starting horizontal offset
   - **Vertical Speed**: Initial upward/downward velocity
   - **Horizontal Speed**: Initial left/right velocity

2. **Real-time feedback**: The visualization updates immediately as you adjust parameters

### Visualization

- **Red circle**: Represents the rocket position
- **Blue arrow**: Shows velocity vector (direction and magnitude)
- **Grid background**: Provides spatial reference
- **Info panel**: Displays current position, velocity, and speed values

### Running Optimization

1. **Set desired parameters** using the sliders
2. **Click "Run Optimization"** to send parameters to the backend
3. **Monitor status** in the message area below the button

## API Integration

The frontend expects a Flask backend running on `http://localhost:5000` with the following endpoint:

```
POST /api/optimize
Content-Type: application/json

{
  "initial_conditions": {
    "vertical_position": 100.0,
    "horizontal_position": 0.0,
    "vertical_speed": 0.0,
    "horizontal_speed": 0.0
  }
}
```

## Development Notes

### File Structure

```
frontend/
├── public/
│   └── index.html          # Main HTML template
├── src/
│   ├── App.js              # Main application component
│   ├── index.js            # React entry point
│   └── index.css           # Global styles
├── package.json            # Dependencies and scripts
└── README.md              # This file
```

### Customization

- **Parameter ranges**: Modify the `constraints` object in `App.js`
- **Styling**: Update `index.css` for visual customization
- **Grid dimensions**: Adjust grid scaling in `getRocketPosition()` function
- **Velocity vector**: Modify scale factor in `getVelocityVector()` function

### Adding New Parameters

1. **Add to state**:
   ```javascript
   const [params, setParams] = useState({
     // existing parameters...
     newParameter: defaultValue
   });
   ```

2. **Define constraints**:
   ```javascript
   const constraints = {
     // existing constraints...
     newParameter: { min: minValue, max: maxValue }
   };
   ```

3. **Add label**:
   ```javascript
   const labels = {
     // existing labels...
     newParameter: 'New Parameter [units]'
   };
   ```

## Troubleshooting

### Common Issues

1. **App won't start**:
   - Ensure Node.js is installed (`node --version`)
   - Try deleting `node_modules` and running `npm install` again

2. **API connection errors**:
   - Verify backend is running on port 5000
   - Check browser console for CORS errors
   - Ensure `"proxy": "http://localhost:5000"` is in `package.json`

3. **Styling issues**:
   - Clear browser cache
   - Check for CSS conflicts in developer tools

### Development Tips

- **Hot reload**: Changes to React components will automatically refresh
- **Browser tools**: Use React Developer Tools extension for debugging
- **Console logging**: Check browser console for errors and API responses

## Next Steps

To extend this frontend:

1. **Add result visualization** for optimization output
2. **Implement trajectory animation** from optimization results
3. **Add parameter presets** for common scenarios
4. **Include optimization metrics** display
5. **Add export functionality** for results

## Backend Integration

This frontend is designed to work with the Flask backend from the main project. Make sure to:

1. **Start the backend server** before using the frontend
2. **Configure CORS** in the Flask app for cross-origin requests
3. **Match API endpoints** between frontend and backend
