import axios from 'axios';
import { useState } from 'react';

const App = () => {
    // State for rocket parameters
    const [params, setParams] = useState({
        verticalPosition: 1000,   // m (start high above ground)
        horizontalPosition: 0,    // m
        verticalSpeed: 0,         // m/s
        horizontalSpeed: 0        // m/s
    });

    // State for UI
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState('');

    // Parameter constraints
    const constraints = {
        verticalPosition: { min: 0, max: 2000 },
        horizontalPosition: { min: -1500, max: 1500 },
        verticalSpeed: { min: -50, max: 50 },
        horizontalSpeed: { min: -50, max: 50 }
    };

    // Labels for parameters
    const labels = {
        verticalPosition: 'Rocket Vertical Position [m]',
        horizontalPosition: 'Rocket Horizontal Position [m]',
        verticalSpeed: 'Rocket Initial Vertical Speed [m/s]',
        horizontalSpeed: 'Rocket Initial Horizontal Speed [m/s]'
    };

    // Handle slider changes
    const handleSliderChange = (param, value) => {
        setParams(prev => ({
            ...prev,
            [param]: parseFloat(value)
        }));
    };

    // Handle optimization request
    const handleOptimize = async () => {
        setIsLoading(true);
        setMessage('Running optimization...');
        setMessageType('loading');

        try {
            const response = await axios.post('/api/optimize', {
                initial_conditions: {
                    vertical_position: params.verticalPosition,
                    horizontal_position: params.horizontalPosition,
                    vertical_speed: params.verticalSpeed,
                    horizontal_speed: params.horizontalSpeed
                }
            });

            setMessage('Optimization completed successfully!');
            setMessageType('success');
            console.log('Optimization results:', response.data);
        } catch (error) {
            setMessage(`Error: ${error.response?.data?.error || error.message}`);
            setMessageType('error');
            console.error('Optimization error:', error);
        } finally {
            setIsLoading(false);
        }
    };    // Calculate rocket position on grid (pixels)
    const getRocketPosition = () => {
        const gridWidth = 800;
        const gridHeight = 600;

        // Grid represents -1500 to 1500 horizontally and 0 to 3000 vertically
        const x = ((params.horizontalPosition + 1500) / 3000) * gridWidth;
        const y = gridHeight - ((params.verticalPosition / 3000) * gridHeight);

        return { x, y };
    };

    // Calculate ground line position (y=0)
    const getGroundLinePosition = () => {
        const gridHeight = 600;
        // Ground line at y=0 in world coordinates
        const y = gridHeight - ((0 / 3000) * gridHeight);
        return y;
    };

    // Calculate target position (0,0)
    const getTargetPosition = () => {
        const gridWidth = 800;
        const gridHeight = 600;
        // Target at (0,0) in world coordinates
        const x = ((0 + 1500) / 3000) * gridWidth;
        const y = gridHeight - ((0 / 3000) * gridHeight);
        return { x, y };
    };

    // Calculate velocity vector
    const getVelocityVector = () => {
        const scale = 3; // Scale factor for velocity vector
        const length = Math.sqrt(params.horizontalSpeed ** 2 + params.verticalSpeed ** 2) * scale;
        const angle = Math.atan2(-params.verticalSpeed, params.horizontalSpeed) * (180 / Math.PI);

        return { length, angle };
    };

    const rocketPos = getRocketPosition();
    const velocityVector = getVelocityVector();
    const groundLineY = getGroundLinePosition();
    const targetPos = getTargetPosition();

    return (
        <div className="app">
            {/* Controls Panel */}
            <div className="controls-panel">
                <h2>Rocket Parameters</h2>

                {Object.entries(constraints).map(([param, constraint]) => (
                    <div key={param} className="slider-group">
                        <label>{labels[param]}</label>
                        <div className="slider-container">
                            <input
                                type="range"
                                min={constraint.min}
                                max={constraint.max}
                                step="0.1"
                                value={params[param]}
                                onChange={(e) => handleSliderChange(param, e.target.value)}
                                className="slider"
                            />
                            <div className="value-display">
                                {params[param].toFixed(1)}
                            </div>
                        </div>
                    </div>
                ))}

                <button
                    className="optimize-button"
                    onClick={handleOptimize}
                    disabled={isLoading}
                >
                    {isLoading ? 'Optimizing...' : 'Run Optimization'}
                </button>

                {message && (
                    <div className={`status-message ${messageType}`}>
                        {message}
                    </div>
                )}
            </div>

            {/* Visualization Panel */}
            <div className="visualization-panel">
                <h2>Rocket Visualization</h2>

                <div className="grid-container">
                    {/* Ground Line (y=0) */}
                    <div
                        className="ground-line"
                        style={{
                            top: `${groundLineY}px`
                        }}
                    />

                    {/* Target at (0,0) */}
                    <div
                        className="target"
                        style={{
                            left: `${targetPos.x}px`,
                            top: `${targetPos.y}px`
                        }}
                    />

                    {/* Rocket */}
                    <div
                        className="rocket"
                        style={{
                            left: `${rocketPos.x}px`,
                            top: `${rocketPos.y}px`,
                            transform: `translate(-50%, -50%) rotate(${velocityVector.angle}deg)`
                        }}
                    />

                    {/* Velocity Vector */}
                    {velocityVector.length > 0 && (
                        <div
                            className="velocity-vector"
                            style={{
                                left: `${rocketPos.x}px`,
                                top: `${rocketPos.y}px`,
                                width: `${velocityVector.length}px`,
                                transform: `rotate(${velocityVector.angle}deg)`
                            }}
                        />
                    )}

                    {/* Axis Labels */}
                    <div className="axis-labels x-axis">X (horizontal) [m]</div>
                    <div className="axis-labels y-axis">Y (vertical) [m]</div>

                    {/* Grid Info */}
                    <div className="grid-info">
                        <div>Position: ({params.horizontalPosition.toFixed(1)}, {params.verticalPosition.toFixed(1)}) m</div>
                        <div>Velocity: ({params.horizontalSpeed.toFixed(1)}, {params.verticalSpeed.toFixed(1)}) m/s</div>
                        <div>Speed: {Math.sqrt(params.horizontalSpeed ** 2 + params.verticalSpeed ** 2).toFixed(1)} m/s</div>
                        <div>Distance to target: {Math.sqrt(params.horizontalPosition ** 2 + params.verticalPosition ** 2).toFixed(1)} m</div>
                        <div>Grid: X(-1500 to 1500m), Y(0 to 3000m)</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default App;
