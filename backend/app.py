#!/usr/bin/env python3
"""
Flask backend for trajectory optimization
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the current directory to the path to import rocket_optimizer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from rocket_optimizer import RocketLanding2D
    print("Successfully imported RocketLanding2D from rocket_optimizer.py")
except ImportError as e:
    print(f"Error importing from rocket_optimizer.py: {e}")
    print("Make sure rocket_optimizer.py is in the current directory")
    RocketLanding2D = None

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Trajectory optimization API is running'
    })

@app.route('/api/parameters/defaults', methods=['GET'])
def get_default_parameters():
    """Get default simulation parameters"""
    return jsonify({
        'initial_conditions': {
            'vertical_position': 1000.0,
            'horizontal_position': 0.0,
            'vertical_speed': 0.0,
            'horizontal_speed': 0.0
        },
        'constraints': {
            'vertical_position': {'min': 0, 'max': 2000},
            'horizontal_position': {'min': -1500, 'max': 1500},
            'vertical_speed': {'min': -50, 'max': 50},
            'horizontal_speed': {'min': -50, 'max': 50}
        }
    })

@app.route('/api/optimize', methods=['POST'])
def optimize_trajectory():
    """
    Optimize rocket trajectory from initial conditions to target (0, 0)
    
    Expected JSON format:
    {
        "initial_conditions": {
            "vertical_position": 1000.0,
            "horizontal_position": 0.0,
            "vertical_speed": 0.0,
            "horizontal_speed": 0.0
        }
    }
    """
    try:
        # Parse JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract initial conditions
        initial_conditions = data.get('initial_conditions', {})
        
        # Validate required fields
        required_fields = ['vertical_position', 'horizontal_position', 'vertical_speed', 'horizontal_speed']
        for field in required_fields:
            if field not in initial_conditions:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract values
        x0 = float(initial_conditions['horizontal_position'])  # Initial horizontal position
        y0 = float(initial_conditions['vertical_position'])    # Initial vertical position
        vx0 = float(initial_conditions['horizontal_speed'])    # Initial horizontal velocity
        vy0 = float(initial_conditions['vertical_speed'])      # Initial vertical velocity
        
        # Validate constraints
        if y0 < 0 or y0 > 2000:
            return jsonify({'error': 'Vertical position must be between 0 and 2000 m'}), 400
        if abs(x0) > 1500:
            return jsonify({'error': 'Horizontal position must be between -1500 and 1500 m'}), 400
        if abs(vx0) > 50 or abs(vy0) > 50:
            return jsonify({'error': 'Velocity components must be between -50 and 50 m/s'}), 400
        
        # Create and configure the optimization problem
        if RocketLanding2D is None:
            return jsonify({'error': 'Optimization engine not available'}), 500
        
        # Create rocket landing problem with custom initial conditions
        custom_conditions = {
            'horizontal_position': x0,
            'vertical_position': y0,
            'horizontal_speed': vx0,
            'vertical_speed': vy0
        }
        rocket = RocketLanding2D(custom_initial_conditions=custom_conditions)
        
        # Override initial conditions in the optimization problem
        # This would require modifying the RocketLanding2D class to accept initial conditions
        # For now, we'll create a mock trajectory
        
        # Run optimization
        try:
            x_opt, u_opt = rocket.solve()
            
            # Extract trajectory data
            trajectory = extract_trajectory_data(x_opt, u_opt, rocket)
            
            # Calculate optimization metrics
            metrics = calculate_metrics(x_opt, u_opt, rocket, x0, y0, vx0, vy0)
            
            return jsonify({
                'success': True,
                'trajectory': trajectory,
                'metrics': metrics,
                'initial_conditions': {
                    'horizontal_position': x0,
                    'vertical_position': y0,
                    'horizontal_speed': vx0,
                    'vertical_speed': vy0
                }
            })
            
        except Exception as opt_error:
            return jsonify({
                'error': f'Optimization failed: {str(opt_error)}',
                'details': 'The optimization problem could not be solved with the given initial conditions'
            }), 500
        
    except ValueError as e:
        return jsonify({'error': f'Invalid number format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

def extract_trajectory_data(x_opt, u_opt, rocket):
    """Extract trajectory data from optimization results"""
    import numpy as np
    
    # Time vector
    time = np.linspace(0, rocket.T, rocket.N + 1)
    
    # Extract states (position, velocity)
    trajectory = {
        'time': time.tolist(),
        'horizontal_position': x_opt[0, :].tolist(),
        'vertical_position': x_opt[1, :].tolist(),
        'horizontal_velocity': x_opt[2, :].tolist(),
        'vertical_velocity': x_opt[3, :].tolist(),
        'thrust_horizontal': u_opt[0, :].tolist(),
        'thrust_vertical': u_opt[1, :].tolist()
    }
    
    return trajectory

def calculate_metrics(x_opt, u_opt, rocket, x0, y0, vx0, vy0):
    """Calculate optimization metrics"""
    import numpy as np
    
    # Final position
    final_x = float(x_opt[0, -1])
    final_y = float(x_opt[1, -1])
    
    # Final velocity
    final_vx = float(x_opt[2, -1])
    final_vy = float(x_opt[3, -1])
    
    # Landing accuracy
    landing_error = np.sqrt(final_x**2 + final_y**2)
    
    # Fuel consumption (approximate)
    fuel_consumption = float(np.sum(np.sqrt(u_opt[0, :]**2 + u_opt[1, :]**2)))
    
    # Flight time
    flight_time = float(rocket.T)
    
    # Maximum velocity
    velocities = np.sqrt(x_opt[2, :]**2 + x_opt[3, :]**2)
    max_velocity = float(np.max(velocities))
    
    # Maximum thrust
    thrusts = np.sqrt(u_opt[0, :]**2 + u_opt[1, :]**2)
    max_thrust = float(np.max(thrusts))
    
    metrics = {
        'landing_error': landing_error,
        'fuel_consumption': fuel_consumption,
        'flight_time': flight_time,
        'max_velocity': max_velocity,
        'max_thrust': max_thrust,
        'final_position': {
            'x': final_x,
            'y': final_y
        },
        'final_velocity': {
            'vx': final_vx,
            'vy': final_vy
        },
        'success': landing_error < 1.0  # Landing within 1 meter is considered success
    }
    
    return metrics

if __name__ == '__main__':
    print("Starting Trajectory Optimization API...")
    print("Available endpoints:")
    print("  GET  /api/health - Health check")
    print("  GET  /api/parameters/defaults - Get default parameters")
    print("  POST /api/optimize - Optimize trajectory")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
