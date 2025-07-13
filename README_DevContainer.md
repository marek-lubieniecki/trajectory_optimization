# Trajectory Optimization Dev Container

This project includes a Visual Studio Code dev container configuration for consistent development environment setup.

## Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code

## Getting Started

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <your-repository-url>
   cd trajectory_optimization
   ```

2. **Open in VS Code**:
   ```bash
   code .
   ```

3. **Reopen in Container**:
   - VS Code should automatically detect the dev container configuration
   - Click "Reopen in Container" when prompted, or
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) and select "Dev Containers: Reopen in Container"

4. **Wait for setup**: The container will build and install all dependencies automatically

## What's Included

### Development Environment
- **Python 3.11** with scientific computing libraries
- **CasADi** for optimization
- **NumPy, Matplotlib, SciPy** for numerical computing
- **Jupyter** for interactive development
- **IPOPT solver** for nonlinear optimization

### VS Code Extensions
- Python language support with IntelliSense
- Jupyter notebook support
- Code formatting (Black) and linting (Flake8, Pylint)
- Git integration
- Spell checker

### Pre-configured Tasks
Access via `Ctrl+Shift+P` → "Tasks: Run Task":
- **Run Trajectory Optimization**: Execute the main optimization script
- **Install Dependencies**: Install core requirements
- **Install Dev Dependencies**: Install development tools
- **Format Code with Black**: Auto-format Python code
- **Lint with Flake8**: Check code quality

### Debug Configurations
- **Debug Trajectory Optimization**: Debug the main.py file
- **Debug Current File**: Debug any Python file

## File Structure

```
.devcontainer/
├── devcontainer.json          # Main dev container configuration
.vscode/
├── tasks.json                 # VS Code tasks
├── launch.json                # Debug configurations
└── settings.json              # Workspace settings
docs/
├── devcontainer-explained.md  # Detailed devcontainer.json explanation
├── tasks-explained.md         # Detailed tasks.json explanation
├── launch-explained.md        # Detailed launch.json explanation
├── settings-explained.md      # Detailed settings.json explanation
└── why-docker-wsl-needed.md   # Why Docker + WSL is essential
requirements.txt               # Core dependencies
requirements-dev.txt           # Development dependencies
main.py                        # Main trajectory optimization script
```

## Usage

### Running the Optimization
- Press `F5` to debug the main script
- Use `Ctrl+Shift+P` → "Tasks: Run Task" → "Run Trajectory Optimization"
- Or run in terminal: `python main.py`

### Code Formatting
- Auto-formatting on save is enabled
- Manual formatting: `Ctrl+Shift+P` → "Format Document"
- Or use the task: "Format Code with Black"

### Interactive Development
- Create new Jupyter notebooks with `.ipynb` extension
- Use `#%%` in Python files to create interactive cells

## Troubleshooting

### Container Build Issues
- Ensure Docker Desktop is running
- Try rebuilding: `Ctrl+Shift+P` → "Dev Containers: Rebuild Container"

### Package Installation Issues
- Open terminal in container and run: `pip install -r requirements-dev.txt`
- For IPOPT issues, the container includes system dependencies

### Display Issues (for matplotlib)
- The container includes X11 forwarding setup
- Plots should display in separate windows or inline in Jupyter

## Customization

### Adding New Dependencies
1. Add packages to `requirements.txt` or `requirements-dev.txt`
2. Rebuild container or run "Install Dev Dependencies" task

### Modifying VS Code Settings
- Edit `.vscode/settings.json` for workspace-specific settings
- Edit `.devcontainer/devcontainer.json` for container-wide settings

### Adding System Packages
- Modify the `onCreateCommand` in `devcontainer.json`
- Add `apt-get install` commands as needed

## Detailed Documentation

For comprehensive explanations of each configuration file:

- **[DevContainer Explained](docs/devcontainer-explained.md)**: Line-by-line explanation of `.devcontainer/devcontainer.json`
- **[Tasks Explained](docs/tasks-explained.md)**: Complete guide to `.vscode/tasks.json`
- **[Launch Explained](docs/launch-explained.md)**: Debug configuration details for `.vscode/launch.json`
- **[Settings Explained](docs/settings-explained.md)**: VS Code settings breakdown for `.vscode/settings.json`
- **[Why Docker + WSL](docs/why-docker-wsl-needed.md)**: Technical explanation of Docker Desktop + WSL requirement
