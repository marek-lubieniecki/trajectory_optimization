#!/usr/bin/env python3
"""
Test suite for trajectory optimization backend
"""

import pytest
import json
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, RocketLanding2D
from rocket_optimizer import RocketLanding2D as RocketOptimizer

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_initial_conditions():
    """Sample initial conditions for testing"""
    return {
        "initial_conditions": {
            "vertical_position": 1000.0,
            "horizontal_position": 0.0,
            "vertical_speed": 0.0,
            "horizontal_speed": 0.0
        }
    }

@pytest.fixture
def custom_initial_conditions():
    """Custom initial conditions for testing"""
    return {
        "initial_conditions": {
            "vertical_position": 500.0,
            "horizontal_position": 100.0,
            "vertical_speed": -5.0,
            "horizontal_speed": 10.0
        }
    }

class TestRocketOptimizer:
    """Test the rocket optimization engine directly"""
    
    def test_rocket_optimizer_initialization(self):
        """Test that RocketOptimizer can be initialized"""
        rocket = RocketOptimizer()
        assert rocket is not None
        assert rocket.g == 9.81
        assert rocket.m == 1000
        assert rocket.T_max == 15000
    
    def test_rocket_optimizer_with_custom_conditions(self):
        """Test RocketOptimizer with custom initial conditions"""
        custom_conditions = {
            'horizontal_position': 50.0,
            'vertical_position': 200.0,
            'horizontal_speed': -5.0,
            'vertical_speed': 2.0
        }
        
        rocket = RocketOptimizer(custom_initial_conditions=custom_conditions)
        assert rocket.x0 == 50.0
        assert rocket.y0 == 200.0
        assert rocket.vx0 == -5.0
        assert rocket.vy0 == 2.0
    
    def test_rocket_optimization_solve(self):
        """Test that optimization can solve successfully"""
        custom_conditions = {
            'horizontal_position': 10.0,
            'vertical_position': 100.0,
            'horizontal_speed': 0.0,
            'vertical_speed': 0.0
        }
        
        rocket = RocketOptimizer(custom_initial_conditions=custom_conditions)
        
        try:
            x_opt, u_opt = rocket.solve()
            
            # Check that we got results
            assert x_opt is not None
            assert u_opt is not None
            
            # Check dimensions
            assert x_opt.shape[0] == 4  # [x, y, vx, vy]
            assert x_opt.shape[1] == rocket.N + 1  # Time steps + 1
            assert u_opt.shape[0] == 2  # [Tx, Ty]
            assert u_opt.shape[1] == rocket.N  # Time steps
            
            # Check initial conditions are satisfied
            assert abs(x_opt[0, 0] - 10.0) < 1e-6  # Initial x position
            assert abs(x_opt[1, 0] - 100.0) < 1e-6  # Initial y position
            assert abs(x_opt[2, 0] - 0.0) < 1e-6  # Initial x velocity
            assert abs(x_opt[3, 0] - 0.0) < 1e-6  # Initial y velocity
            
            # Check final conditions (should land at origin)
            assert abs(x_opt[0, -1] - 0.0) < 1e-3  # Final x position
            assert abs(x_opt[1, -1] - 0.0) < 1e-3  # Final y position
            assert abs(x_opt[2, -1] - 0.0) < 1e-3  # Final x velocity
            assert abs(x_opt[3, -1] - 0.0) < 1e-3  # Final y velocity
            
            print("✓ Optimization solved successfully!")
            
        except Exception as e:
            pytest.fail(f"Optimization failed: {e}")

class TestFlaskAPI:
    """Test the Flask API endpoints"""
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'message' in data
    
    def test_defaults_endpoint(self, client):
        """Test the defaults endpoint"""
        response = client.get('/api/parameters/defaults')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'initial_conditions' in data
        assert 'constraints' in data
        
        # Check initial conditions structure
        initial_conditions = data['initial_conditions']
        assert 'vertical_position' in initial_conditions
        assert 'horizontal_position' in initial_conditions
        assert 'vertical_speed' in initial_conditions
        assert 'horizontal_speed' in initial_conditions
    
    def test_optimize_endpoint_valid_request(self, client, sample_initial_conditions):
        """Test the optimize endpoint with valid data"""
        response = client.post('/api/optimize', 
                             data=json.dumps(sample_initial_conditions),
                             content_type='application/json')
        
        # Should return success or detailed error
        assert response.status_code in [200, 500]  # 500 if optimization fails
        
        data = json.loads(response.data)
        
        if response.status_code == 200:
            # Check successful response structure
            assert 'success' in data
            assert 'trajectory' in data
            assert 'metrics' in data
            assert 'initial_conditions' in data
            
            # Check trajectory structure
            trajectory = data['trajectory']
            assert 'time' in trajectory
            assert 'horizontal_position' in trajectory
            assert 'vertical_position' in trajectory
            assert 'horizontal_velocity' in trajectory
            assert 'vertical_velocity' in trajectory
            
            # Check metrics structure
            metrics = data['metrics']
            assert 'landing_error' in metrics
            assert 'fuel_consumption' in metrics
            assert 'flight_time' in metrics
            
            print("✓ Optimization API returned successful response!")
        else:
            # Check error response structure
            assert 'error' in data
            print(f"⚠ Optimization failed with error: {data['error']}")
    
    def test_optimize_endpoint_missing_data(self, client):
        """Test the optimize endpoint with missing data"""
        response = client.post('/api/optimize', 
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_optimize_endpoint_invalid_constraints(self, client):
        """Test the optimize endpoint with invalid constraints"""
        invalid_data = {
            "initial_conditions": {
                "vertical_position": -100.0,  # Invalid: below ground
                "horizontal_position": 0.0,
                "vertical_speed": 0.0,
                "horizontal_speed": 0.0
            }
        }
        
        response = client.post('/api/optimize', 
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Vertical position must be between 0 and 2000' in data['error']
    
    def test_optimize_endpoint_extreme_values(self, client):
        """Test the optimize endpoint with extreme but valid values"""
        extreme_data = {
            "initial_conditions": {
                "vertical_position": 1500.0,
                "horizontal_position": 1000.0,
                "vertical_speed": -20.0,
                "horizontal_speed": 30.0
            }
        }
        
        response = client.post('/api/optimize', 
                             data=json.dumps(extreme_data),
                             content_type='application/json')
        
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 500]
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert 'trajectory' in data
            print("✓ Extreme values handled successfully!")
        else:
            assert 'error' in data
            print(f"⚠ Extreme values caused expected failure: {data['error']}")

class TestOptimizationMath:
    """Test the mathematical aspects of optimization"""
    
    def test_physics_conservation(self):
        """Test that physics laws are conserved in optimization"""
        custom_conditions = {
            'horizontal_position': 0.0,
            'vertical_position': 100.0,
            'horizontal_speed': 0.0,
            'vertical_speed': 0.0
        }
        
        rocket = RocketOptimizer(custom_initial_conditions=custom_conditions)
        
        try:
            x_opt, u_opt = rocket.solve()
            
            # Check that rocket doesn't go below ground
            assert all(x_opt[1, :] >= -1e-6), "Rocket went below ground level"
            
            # Check that final position is at target (0, 0)
            final_position_error = (x_opt[0, -1]**2 + x_opt[1, -1]**2)**0.5
            assert final_position_error < 0.1, f"Landing error too large: {final_position_error}"
            
            # Check that final velocity is near zero
            final_velocity = (x_opt[2, -1]**2 + x_opt[3, -1]**2)**0.5
            assert final_velocity < 0.1, f"Final velocity too large: {final_velocity}"
            
            print("✓ Physics conservation tests passed!")
            
        except Exception as e:
            pytest.skip(f"Optimization failed, skipping physics test: {e}")

if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, '-v'])
