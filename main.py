#!/usr/bin/env python3
"""
2D Rocket Landing Trajectory Optimization using CasADi
Features:
- Gimbaled main engine (thrust magnitude and angle)
- Side RCS thrusters for attitude control
- Fuel consumption modeling
- Landing constraints
"""

from casadi import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.animation import FuncAnimation


class RocketLanding2D:
    def __init__(self):
        # Physical parameters
        self.g = 9.81  # Gravity [m/s^2]
        self.Isp_main = 300  # Main engine specific impulse [s]
        self.Isp_rcs = 200  # RCS specific impulse [s]
        self.dry_mass = 1000  # Dry mass [kg]
        self.max_thrust_main = 100000  # Max main engine thrust [N]
        self.min_thrust_main = 0.4 * self.max_thrust_main # Min main engine thrust [N]
        self.max_thrust_rcs = 1000  # Max RCS thrust per thruster [N]
        self.max_gimbal_angle = 10 * np.pi / 180  # Max gimbal angle [rad]

        # Simulation parameters
        self.T = 20.0  # Total time [s]
        self.N = 100  # Number of control intervals
        self.dt = self.T / self.N  # Time step

    def setup_dynamics(self):
        """Define the rocket dynamics as CasADi expressions"""
        # State variables
        x = MX.sym('x')  # Horizontal position [m]
        y = MX.sym('y')  # Vertical position [m]
        vx = MX.sym('vx')  # Horizontal velocity [m/s]
        vy = MX.sym('vy')  # Vertical velocity [m/s]
        theta = MX.sym('theta')  # Attitude angle [rad] (0 = vertical)
        omega = MX.sym('omega')  # Angular velocity [rad/s]
        m = MX.sym('m')  # Total mass [kg]

        state = vertcat(x, y, vx, vy, theta, omega, m)

        # Control variables
        T_main = MX.sym('T_main')  # Main engine thrust magnitude [N]
        delta = MX.sym('delta')  # Main engine gimbal angle [rad]
        T_rcs_left = MX.sym('T_rcs_l')  # Left RCS thrust [N]
        T_rcs_right = MX.sym('T_rcs_r')  # Right RCS thrust [N]

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
        mdot = -(T_main / (self.Isp_main * self.g) +
                 (T_rcs_left + T_rcs_right) / (self.Isp_rcs * self.g))

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
        opti = Opti()

        # Decision variables
        X = opti.variable(7, self.N + 1)  # States
        U = opti.variable(4, self.N)  # Controls

        # Initial conditions
        x0 = [500,  # x position [m]
              2000,  # y position [m]
              -20,  # x velocity [m/s]
              -100,  # y velocity [m/s]
              0.1,  # attitude angle [rad]
              0.0,  # angular velocity [rad/s]
              5000]  # initial mass [kg]

        opti.subject_to(X[:, 0] == x0)

        # Dynamics constraints (RK4 integration)
        for k in range(self.N):
            k1 = self.f(X[:, k], U[:, k])
            k2 = self.f(X[:, k] + self.dt / 2 * k1, U[:, k])
            k3 = self.f(X[:, k] + self.dt / 2 * k2, U[:, k])
            k4 = self.f(X[:, k] + self.dt * k3, U[:, k])
            x_next = X[:, k] + self.dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            opti.subject_to(X[:, k + 1] == x_next)

        # Control constraints
        opti.subject_to(U[0, :] >= self.min_thrust_main)  # Main thrust positive
        opti.subject_to(U[0, :] <= self.max_thrust_main)  # Main thrust limit
        opti.subject_to(U[1, :] >= -self.max_gimbal_angle)  # Gimbal angle limits
        opti.subject_to(U[1, :] <= self.max_gimbal_angle)
        opti.subject_to(U[2, :] >= 0)  # RCS thrust positive
        opti.subject_to(U[2, :] <= self.max_thrust_rcs)
        opti.subject_to(U[3, :] >= 0)
        opti.subject_to(U[3, :] <= self.max_thrust_rcs)

        # State constraints
        opti.subject_to(X[6, :] >= self.dry_mass)  # Mass above dry mass
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
        s_opts = {"max_iter": 1000, "print_level": 5}
        opti.solver('ipopt', p_opts, s_opts)

        return opti, X, U

    def solve(self):
        """Solve the optimization problem"""
        state_sym, control_sym, dynamics = self.setup_dynamics()
        opti, X, U = self.setup_optimization()

        # Initial guess
        for i in range(self.N + 1):
            opti.set_initial(X[0, i], 1000 * (1 - i / self.N))
            opti.set_initial(X[1, i], 2000 * (1 - i / self.N))
            opti.set_initial(X[6, i], 5000 - 1000 * i / self.N)

        opti.set_initial(U[0, :], self.max_thrust_main * 0.7)

        # Solve
        try:
            sol = opti.solve()

            # Extract solution
            x_opt = sol.value(X)
            u_opt = sol.value(U)

            return x_opt, u_opt

        except Exception as e:
            print(f"Optimization failed: {e}")
            # Return the best iterate if available
            x_opt = opti.debug.value(X)
            u_opt = opti.debug.value(U)
            print("State variables at failure:", x_opt)
            print("Control variables at failure:", u_opt)
            return x_opt, u_opt

    def plot_results(self, x_opt, u_opt):
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

    def animate_trajectory(self, x_opt, u_opt):
        """Create an animation of the landing"""
        fig, ax = plt.subplots(figsize=(8, 10))

        # Set up the plot
        ax.set_xlim(-100, max(x_opt[0, :]) * 1.2)
        ax.set_ylim(-50, max(x_opt[1, :]) * 1.1)
        ax.set_aspect('equal')
        ax.grid(True)
        ax.set_xlabel('X Position [m]')
        ax.set_ylabel('Y Position [m]')
        ax.set_title('Rocket Landing Animation')

        # Ground
        ground = Rectangle((-200, -50), max(x_opt[0, :]) * 1.5, 50,
                           facecolor='brown', alpha=0.5)
        ax.add_patch(ground)

        # Landing pad
        pad = Rectangle((-20, 0), 40, 2, facecolor='gray')
        ax.add_patch(pad)

        # Rocket body
        rocket_length = 30
        rocket_width = 5
        rocket = Rectangle((0, 0), rocket_width, rocket_length,
                           facecolor='white', edgecolor='black')
        ax.add_patch(rocket)

        # Trajectory line
        traj_line, = ax.plot([], [], 'b--', alpha=0.5)

        # Thrust vectors
        main_thrust, = ax.plot([], [], 'r-', linewidth=3)
        rcs_left, = ax.plot([], [], 'orange', linewidth=2)
        rcs_right, = ax.plot([], [], 'orange', linewidth=2)

        def init():
            return rocket, traj_line, main_thrust, rcs_left, rcs_right

        def animate(frame):
            # Update rocket position and orientation
            x = x_opt[0, frame]
            y = x_opt[1, frame]
            theta = x_opt[4, frame]

            # Transform rocket rectangle
            rocket.set_xy((x - rocket_width / 2 * cos(theta) - rocket_length / 2 * sin(theta),
                           y - rocket_width / 2 * sin(theta) + rocket_length / 2 * cos(theta)))
            rocket.angle = -theta * 180 / np.pi

            # Update trajectory
            traj_line.set_data(x_opt[0, :frame + 1], x_opt[1, :frame + 1])

            # Update thrust vectors (if frame < N)
            if frame < self.N:
                # Main thrust
                thrust_scale = 0.001
                thrust_mag = u_opt[0, frame] * thrust_scale
                delta = u_opt[1, frame]
                thrust_angle = theta - delta

                thrust_x = [x, x - thrust_mag * sin(thrust_angle)]
                thrust_y = [y, y - thrust_mag * cos(thrust_angle)]
                main_thrust.set_data(thrust_x, thrust_y)

                # RCS thrusts
                rcs_scale = 0.01
                rcs_y_offset = rocket_length * 0.4

                # Left RCS
                rcs_left_mag = u_opt[2, frame] * rcs_scale
                left_x = x - rcs_y_offset * sin(theta)
                left_y = y + rcs_y_offset * cos(theta)
                rcs_left.set_data([left_x, left_x - rcs_left_mag * cos(theta)],
                                  [left_y, left_y - rcs_left_mag * sin(theta)])

                # Right RCS
                rcs_right_mag = u_opt[3, frame] * rcs_scale
                right_x = x - rcs_y_offset * sin(theta)
                right_y = y + rcs_y_offset * cos(theta)
                rcs_right.set_data([right_x, right_x + rcs_right_mag * cos(theta)],
                                   [right_y, right_y + rcs_right_mag * sin(theta)])

            return rocket, traj_line, main_thrust, rcs_left, rcs_right

        anim = FuncAnimation(fig, animate, init_func=init,
                             frames=self.N + 1, interval=50, blit=True)

        #anim.save('rocket_landing.gif', writer='pillow', fps=15)
        plt.show()

        # Save the animation

        return anim





if __name__ == "__main__":
    # Create and solve the rocket landing problem
    rocket = RocketLanding2D()
    print("Setting up optimization problem...")

    # Solve
    print("Solving...")
    x_opt, u_opt = rocket.solve()

    # Plot results
    print("Plotting results...")
    rocket.plot_results(x_opt, u_opt)

    # Animate (optional - comment out if you don't want animation)
    print("Creating animation...")
    anim = rocket.animate_trajectory(x_opt, u_opt)