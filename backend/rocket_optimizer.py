#!/usr/bin/env python3
"""
Enhanced Rocket Landing Optimization with Custom Initial Conditions
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import casadi as ca
from casadi import MX, Function, Opti, vertcat, sin, cos, sum2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.animation import FuncAnimation


class Rocket:
    def __init__(self):
        """
        Initialize the rocket parameters.
        """
        self.Isp_main = 282  # Main engine specific impulse [s]
        self.Isp_rcs = 200  # RCS specific impulse [s]
        self.dry_mass = 22000  # Dry mass [kg]
        self.propellant_mass = 6000  # Propellant mass [kg]
        self.wet_mass = self.dry_mass + self.propellant_mass  # Wet mass
        self.max_thrust_main = 845000  # Max main engine thrust [N]
        self.min_thrust_main = 0 * self.max_thrust_main # Min main engine thrust [N]
        self.max_thrust_rcs = 5000  # Max RCS thrust per thruster [N]
        self.max_gimbal_angle = 15 * np.pi / 180  # Max gimbal angle [rad]

class RocketLanding2D:
    def __init__(self, rocket, custom_initial_conditions=None):
        """
        Initialize the rocket landing optimization problem.
        
        Args:
            custom_initial_conditions: Dict with keys:
                - horizontal_position: Initial x position [m]
                - vertical_position: Initial y position [m] 
                - horizontal_speed: Initial x velocity [m/s]
                - vertical_speed: Initial y velocity [m/s]
        """
        self.rocket = rocket  # Rocket object containing parameters 
        self.f = Function()  # Placeholder for the dynamics funtion  
        self.x0 = None # Initialise initial conditions
        
        # Physical parameters
        self.g = 9.81  # Gravity [m/s^2]
    
        # Time parameters
        self.T = 20.0  # Total time [s]
        self.N = 100   # Number of discretization points
        self.dt = self.T / self.N  # Time step [s]

        self.setup_initial_conditions(custom_initial_conditions)

        # Set initial conditions

    def setup_initial_conditions(self, custom_initial_conditions={}):

        x0 = custom_initial_conditions.get('horizontal_position', 0.0)
        y0 = custom_initial_conditions.get('vertical_position', 1000.0)
        vx0 = custom_initial_conditions.get('horizontal_speed', 0.0)
        vy0 = custom_initial_conditions.get('vertical_speed', 0.0)
        theta0= custom_initial_conditions.get('theta', 0.0)
        omega0 = 0
        mass0 = self.rocket.wet_mass  # Initial mass (dry mass)

        self.x0 = vertcat(x0, y0, vx0, vy0, theta0, omega0, mass0)
        
    def setup_target_conditions(self):
        """
        Set the target conditions for the optimization problem.
        """
        self.xf = 0.0      # Final horizontal position [m]
        self.yf = 0.0      # Final vertical position [m]
        self.vxf = 0.0     # Final horizontal velocity [m/s]
        self.vyf = 0.0     # Final vertical velocity [m/s]

    def setup_dynamics(self):
        """Define the rocket dynamics as CasADi expressions"""
        # State variables
        x = MX.sym('x')   # Horizontal position [m] # type: ignore
        y = MX.sym('y')  # Vertical position [m] # type: ignore
        vx = MX.sym('vx')  # Horizontal velocity [m/s] # type: ignore
        vy = MX.sym('vy')  # Vertical velocity [m/s] # type: ignore
        theta = MX.sym('theta')  # Attitude angle [rad] (0 = vertical) # type: ignore
        omega = MX.sym('omega')  # Angular velocity [rad/s] # type: ignore
        m = MX.sym('m')  # Total mass [kg] # type: ignore

        state = vertcat(x, y, vx, vy, theta, omega, m)

        # Control variables
        T_main = MX.sym('T_main')  # Main engine thrust magnitude [N] # type: ignore
        delta = MX.sym('delta')  # Main engine gimbal angle [rad] # type: ignore
        T_rcs_left = MX.sym('T_rcs_l')  # Left RCS thrust [N]  # type: ignore
        T_rcs_right = MX.sym('T_rcs_r')  # Right RCS thrust [N] # type: ignore

        control = vertcat(T_main, delta, T_rcs_left, T_rcs_right)

        # Dynamics
        # Main engine thrust components (in body frame, then rotated)
        Fx_main = T_main * sin(delta)
        Fy_main = T_main * cos(delta)

        # Transform to inertial frame
        Fx_total = Fx_main * cos(theta) - Fy_main * sin(theta)
        Fy_total = Fx_main * sin(theta) + Fy_main * cos(theta)

        # RCS forces (assumed to be horizontal in body frame)
        Fx_rcs = (T_rcs_right - T_rcs_left) * cos(theta)
        Fy_rcs = (T_rcs_right - T_rcs_left) * sin(theta)

        # Total forces
        Fx_total += Fx_rcs
        Fy_total += Fy_rcs

        # Accelerations
        ax = Fx_total / m
        ay = Fy_total / m - self.g

        # Torque from RCS (assuming thrusters at distance L from center)
        L_rcs = 5.0  # Distance of RCS from center of mass [m]
        torque = (T_rcs_right + T_rcs_left) * L_rcs

        # Torque from gimbaled main engine
        L_gimbal = 10.0  # Distance from gimbal point to center of mass [m]
        torque += T_main * sin(delta) * L_gimbal

        # Moment of inertia (simplified as m*L^2)
        I = m * (15.0) ** 2
        alpha = torque / I  # Angular acceleration

        # Mass flow rate
        mdot = -(T_main / (self.rocket.Isp_main * self.g) +
                 (T_rcs_left + T_rcs_right) / (self.rocket.Isp_rcs * self.g))

        # State derivatives
        xdot = vx
        ydot = vy
        vxdot = ax
        vydot = ay
        thetadot = omega
        omegadot = alpha

        dynamics = vertcat(xdot, ydot, vxdot, vydot, thetadot, omegadot, mdot)

        # Create CasADi function
        self.f = Function('f', [state, control], [dynamics])

        return state, control, dynamics

    
    def setup_optimization(self):
        """Set up the optimization problem"""
        # Decision variables
        # State: [x, y, vx, vy]
        # Control: [Tx, Ty] (thrust components)

        self.setup_dynamics()
        
        # Create CasADi optimization problem
        opti = Opti()
        
        # Decision variables
        X = opti.variable(7, self.N + 1)  # States over time
        U = opti.variable(4, self.N)      # Controls over time

        opti.subject_to(X[:, 0] == self.x0)  # initial conditions

 # Dynamics constraints (RK4 integration)
        for k in range(self.N):
            k1 = self.f(X[:, k], U[:, k]) #type: ignore
            k2 = self.f(X[:, k] + self.dt / 2 * k1, U[:, k]) #type: ignore
            k3 = self.f(X[:, k] + self.dt / 2 * k2, U[:, k]) #type: ignore
            k4 = self.f(X[:, k] + self.dt * k3, U[:, k]) #type: ignore
            x_next = X[:, k] + self.dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4) #type: ignore
            opti.subject_to(X[:, k + 1] == x_next)

        # Control constraints
        opti.subject_to(U[0, :] >= self.rocket.min_thrust_main)  # Main thrust positive
        opti.subject_to(U[0, :] <= self.rocket.max_thrust_main)  # Main thrust limit
        opti.subject_to(U[1, :] >= -self.rocket.max_gimbal_angle)  # Gimbal angle limits
        opti.subject_to(U[1, :] <= self.rocket.max_gimbal_angle)
        opti.subject_to(U[2, :] >= 0)  # RCS thrust positive
        opti.subject_to(U[2, :] <= self.rocket.max_thrust_rcs)
        opti.subject_to(U[3, :] >= 0)
        opti.subject_to(U[3, :] <= self.rocket.max_thrust_rcs)

        # State constraints
        opti.subject_to(X[6, :] >= self.rocket.dry_mass)  # Mass above dry mass
        opti.subject_to(X[1, :] >= 0)  # Above ground

        # Landing constraints
        landing_tolerance = 10.0
        opti.subject_to(X[0, -1] ** 2 <= landing_tolerance ** 2)  # Land near x=0
        opti.subject_to(X[1, -1] <= 5.0)  # Low altitude
        opti.subject_to(X[2, -1] ** 2 + X[3, -1] ** 2 <= 1.0 ** 2)  # Low velocity
        opti.subject_to(X[4, -1] ** 2 <= (0.1 * np.pi / 180) ** 2)  # Upright
        opti.subject_to(X[5, -1] ** 2 <= 0.01 ** 2)  # Low angular velocity

        # Objective: Minimize fuel consumption and control effort
        fuel_cost = -X[6, -1]  # Maximize final mass = minimize fuel use
        control_effort = sum2(U[0, :] ** 2) * 1e-8 + sum2(U[1, :] ** 2) * 1e-3
        attitude_penalty = sum2(X[4, :] ** 2) * 10

        opti.minimize(fuel_cost + control_effort + attitude_penalty)

        # Solver options
        p_opts = {"expand": True}
        s_opts = {"max_iter": 2000, "print_level": 5}
        opti.solver('ipopt', p_opts, s_opts)

        return opti, X, U
    
    def solve(self):
        """Solve the optimization problem"""
        print("Setting up optimization problem...")
        self.setup_dynamics()
        opti, X, U = self.setup_optimization()


        for i in range(self.N + 1):
            opti.set_initial(X[0, i], 1000 * (1 - i / self.N))
            opti.set_initial(X[1, i], 2000 * (1 - i / self.N))
            opti.set_initial(X[6, i], 5000 - 1000 * i / self.N)

        opti.set_initial(U[0, :], self.rocket.max_thrust_main * 0.7)
        
        print("Solving optimization problem...")
        try:
            sol = opti.solve()
            
            # Extract solution
            x_opt = sol.value(X)
            u_opt = sol.value(U)
            
            # Print results
            print("Optimization successful!")
            print(f"Final position: ({x_opt[0, -1]:.3f}, {x_opt[1, -1]:.3f}) m")
            print(f"Final velocity: ({x_opt[2, -1]:.3f}, {x_opt[3, -1]:.3f}) m/s")
            print(f"Landing error: {np.sqrt(x_opt[0, -1]**2 + x_opt[1, -1]**2):.3f} m")
            
            return x_opt, u_opt
            
        except Exception as e:
            print(f"Optimization failed: {e}")
            x_opt = opti.debug.value(X)
            u_opt = opti.debug.value(U)
            return x_opt, u_opt
    
    def plot_results(self, x_opt, u_opt, save_figure=True):
        """Plot the optimization results"""
        time = np.linspace(0, self.T, self.N + 1)
        time_u = np.linspace(0, self.T, self.N)

        fig, axes = plt.subplots(3, 2, figsize=(12, 10))

        # Trajectory
        ax = axes[0, 0]
        ax.plot(x_opt[0, :], x_opt[1, :], 'b-', linewidth=2)
        ax.plot(x_opt[0, 0], x_opt[1, 0], 'go', markersize=10, label='Start')
        ax.plot(x_opt[0, -1], x_opt[1, -1], 'ro', markersize=10, label='End')
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax.set_xlabel('X Position [m]')
        ax.set_ylabel('Y Position [m]')
        ax.set_title('Trajectory')
        ax.grid(True)
        ax.legend()
        ax.set_ylim([-50, max(x_opt[1, :]) * 1.1])

        # Velocity
        ax = axes[0, 1]
        ax.plot(time, x_opt[2, :], 'b-', label='Vx')
        ax.plot(time, x_opt[3, :], 'r-', label='Vy')
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Velocity [m/s]')
        ax.set_title('Velocity Components')
        ax.grid(True)
        ax.legend()

        # Attitude
        ax = axes[1, 0]
        ax.plot(time, x_opt[4, :] * 180 / np.pi, 'b-', label='Theta')
        ax.plot(time, x_opt[5, :] * 180 / np.pi, 'r-', label='Omega')
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Angle [deg], Rate [deg/s]')
        ax.set_title('Attitude')
        ax.grid(True)
        ax.legend()

        # Mass
        ax = axes[1, 1]
        ax.plot(time, x_opt[6, :], 'g-')
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Mass [kg]')
        ax.set_title('Rocket Mass')
        ax.grid(True)

        # Main thrust and gimbal
        ax = axes[2, 0]
        ax.plot(time_u, u_opt[0, :] / 1000, 'b-', label='Main Thrust')
        ax2 = ax.twinx()
        ax2.plot(time_u, u_opt[1, :] * 180 / np.pi, 'r-', label='Gimbal Angle')
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Main Thrust [kN]', color='b')
        ax2.set_ylabel('Gimbal Angle [deg]', color='r')
        ax.set_title('Main Engine Control')
        ax.grid(True)

        # RCS thrust
        ax = axes[2, 1]
        ax.plot(time_u, u_opt[2, :], 'b-', label='Left RCS')
        ax.plot(time_u, u_opt[3, :], 'r-', label='Right RCS')
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('RCS Thrust [N]')
        ax.set_title('RCS Control')
        ax.grid(True)
        ax.legend()

        plt.tight_layout()
        plt.show()

        # Print landing statistics
        print("\nLanding Statistics:")
        print(f"Final position: ({x_opt[0, -1]:.2f}, {x_opt[1, -1]:.2f}) m")
        print(f"Final velocity: ({x_opt[2, -1]:.2f}, {x_opt[3, -1]:.2f}) m/s")
        print(f"Final attitude: {x_opt[4, -1] * 180 / np.pi:.2f} deg")
        print(f"Final angular rate: {x_opt[5, -1] * 180 / np.pi:.2f} deg/s")
        print(f"Fuel consumed: {x_opt[6, 0] - x_opt[6, -1]:.2f} kg")
        plt.tight_layout()
        
        if save_figure:
            plt.savefig('/workspace/trajectory_results.png', dpi=300, bbox_inches='tight')
            print("Results saved as 'trajectory_results.png'")
        
        plt.close()
        
        return fig

def main():
    """Main function for testing"""
    # Test with custom initial conditions
    custom_conditions = {
        'horizontal_position': 500.0,
        'vertical_position': 2000.0,
        'horizontal_speed': -20.0,
        'vertical_speed': -100,
        'theta': 0.1  # Initial angle [rad]
    }
    rocket = Rocket()
    landing = RocketLanding2D(rocket, custom_initial_conditions=custom_conditions)
    
    x_opt, u_opt = landing.solve()
    landing.plot_results(x_opt, u_opt)

    try:

        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    main()
