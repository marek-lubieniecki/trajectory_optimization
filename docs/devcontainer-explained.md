# DevContainer Configuration Explained

This document provides a line-by-line explanation of the `.devcontainer/devcontainer.json` file.

## File: `.devcontainer/devcontainer.json`

### Basic Container Configuration

```json
{
    "name": "Trajectory Optimization",
```
**Explanation**: Sets the display name for the dev container. This name appears in VS Code's status bar and container selection dialogs.

```json
    "image": "mcr.microsoft.com/devcontainers/python:1-3.11-bullseye",
```
**Explanation**: Specifies the base Docker image to use. This is Microsoft's official Python 3.11 dev container image based on Debian Bullseye. It includes:
- Python 3.11 pre-installed
- Common development tools (git, curl, wget, etc.)
- Node.js for VS Code extensions
- The `vscode` user with sudo privileges

### Features Section

```json
    "features": {
        "ghcr.io/devcontainers/features/git:1": {},
```
**Explanation**: Installs the Git feature. The `{}` means using default settings. This ensures Git is properly configured with credential helpers and VS Code integration.

```json
        "ghcr.io/devcontainers/features/common-utils:2": {
            "installZsh": true,
            "configureZshAsDefaultShell": true,
            "installOhMyZsh": true,
            "upgradePackages": true
        }
```
**Explanation**: Installs common utilities feature with specific options:
- `"installZsh": true` - Installs Zsh shell (more features than bash)
- `"configureZshAsDefaultShell": true` - Makes Zsh the default shell for the `vscode` user
- `"installOhMyZsh": true` - Installs Oh My Zsh framework for better shell experience (themes, plugins, auto-completion)
- `"upgradePackages": true` - Updates all system packages to latest versions during container build

### VS Code Customizations

```json
    "customizations": {
        "vscode": {
            "settings": {
```
**Explanation**: Configures VS Code settings that will be applied when the container starts.

#### Python Settings

```json
                "python.defaultInterpreterPath": "/usr/local/bin/python",
```
**Explanation**: Sets the default Python interpreter path. This ensures VS Code uses the Python 3.11 installation in the container.

```json
                "python.linting.enabled": true,
                "python.linting.pylintEnabled": true,
```
**Explanation**: Enables Python linting (code quality checking) and specifically enables Pylint as a linter.

```json
                "python.formatting.autopep8Path": "/usr/local/py-utils/bin/autopep8",
                "python.formatting.blackPath": "/usr/local/py-utils/bin/black",
                "python.formatting.yapfPath": "/usr/local/py-utils/bin/yapf",
```
**Explanation**: Sets paths for various Python code formatters. These tools are pre-installed in the Microsoft Python image at `/usr/local/py-utils/bin/`.

```json
                "python.linting.banditPath": "/usr/local/py-utils/bin/bandit",
                "python.linting.flake8Path": "/usr/local/py-utils/bin/flake8",
                "python.linting.mypyPath": "/usr/local/py-utils/bin/mypy",
                "python.linting.pycodestylePath": "/usr/local/py-utils/bin/pycodestyle",
                "python.linting.pydocstylePath": "/usr/local/py-utils/bin/pydocstyle",
                "python.linting.pylintPath": "/usr/local/py-utils/bin/pylint",
```
**Explanation**: Sets paths for various Python linting tools:
- **bandit**: Security linter for Python
- **flake8**: Style guide enforcement
- **mypy**: Static type checker
- **pycodestyle**: PEP 8 style checker
- **pydocstyle**: Docstring style checker
- **pylint**: Comprehensive code analysis

```json
                "python.testing.pytestPath": "/usr/local/py-utils/bin/pytest",
```
**Explanation**: Sets the path for pytest testing framework.

#### General Editor Settings

```json
                "files.watcherExclude": {
                    "**/node_modules/**": true
                },
```
**Explanation**: Excludes `node_modules` directories from file watching to improve performance (even though this is a Python project, VS Code extensions may create node_modules).

```json
                "terminal.integrated.defaultProfile.linux": "zsh"
```
**Explanation**: Sets Zsh as the default terminal shell in VS Code's integrated terminal.

#### VS Code Extensions

```json
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-python.flake8",
                "ms-python.black-formatter",
```
**Explanation**: Core Python development extensions:
- **ms-python.python**: Main Python extension (IntelliSense, debugging, formatting)
- **ms-python.vscode-pylance**: Fast Python language server (better than Jedi)
- **ms-python.flake8**: Flake8 linting integration
- **ms-python.black-formatter**: Black code formatter integration

```json
                "ms-toolsai.jupyter",
                "ms-toolsai.jupyter-keymap",
                "ms-toolsai.jupyter-renderers",
```
**Explanation**: Jupyter notebook support:
- **ms-toolsai.jupyter**: Core Jupyter extension for .ipynb files
- **ms-toolsai.jupyter-keymap**: Jupyter-style keyboard shortcuts
- **ms-toolsai.jupyter-renderers**: Enhanced output rendering (plots, tables, etc.)

```json
                "ms-vscode.vscode-json",
                "redhat.vscode-yaml",
```
**Explanation**: Configuration file support:
- **ms-vscode.vscode-json**: JSON file editing with schema validation
- **redhat.vscode-yaml**: YAML file editing and validation

```json
                "ms-vscode.cmake-tools",
                "twxs.cmake",
```
**Explanation**: CMake support (useful if working with compiled dependencies):
- **ms-vscode.cmake-tools**: CMake project management
- **twxs.cmake**: CMake syntax highlighting

```json
                "formulahendry.code-runner",
```
**Explanation**: Allows running code snippets quickly with Ctrl+Alt+N.

```json
                "streetsidesoftware.code-spell-checker",
```
**Explanation**: Spell checker for code comments and documentation.

```json
                "ms-python.autopep8",
                "njpwerner.autodocstring",
                "ms-vscode.sublime-keybindings"
```
**Explanation**: Additional productivity extensions:
- **ms-python.autopep8**: PEP 8 auto-formatting
- **njpwerner.autodocstring**: Auto-generates Python docstrings
- **ms-vscode.sublime-keybindings**: Sublime Text keyboard shortcuts for VS Code

### Container Runtime Configuration

```json
    "forwardPorts": [8888, 8000],
```
**Explanation**: Automatically forwards these ports from container to host:
- **8888**: Default Jupyter notebook port
- **8000**: Common development server port

```json
    "postCreateCommand": "pip install --user -r requirements-dev.txt",
```
**Explanation**: Command executed after container is created. Installs Python packages from requirements-dev.txt to the user's home directory.

```json
    "remoteUser": "vscode",
```
**Explanation**: Sets the user account to use inside the container. The `vscode` user has sudo privileges and is pre-configured in Microsoft's base images.

```json
    "workspaceFolder": "/workspace",
    "workspaceMount": "source=${localWorkspaceFolder},target=/workspace,type=bind,consistency=cached",
```
**Explanation**: 
- **workspaceFolder**: Sets the working directory inside the container
- **workspaceMount**: Bind mounts your local project folder to `/workspace` in the container with cached consistency for better performance on macOS/Windows

### Container Arguments

```json
    "runArgs": [
        "--cap-add=SYS_PTRACE",
        "--security-opt",
        "seccomp=unconfined"
    ],
```
**Explanation**: Docker run arguments for debugging support:
- **--cap-add=SYS_PTRACE**: Allows debuggers to attach to processes
- **--security-opt seccomp=unconfined**: Relaxes security constraints for development

### Environment Variables

```json
    "containerEnv": {
        "DISPLAY": ":1"
    },
```
**Explanation**: Sets environment variables in the container. `DISPLAY=:1` enables X11 forwarding for GUI applications (matplotlib plots).

### Lifecycle Commands

```json
    "initializeCommand": "echo 'Initializing trajectory optimization dev container...'",
```
**Explanation**: Command run on the host before container starts. Used for logging/debugging.

```json
    "onCreateCommand": [
        "sudo apt-get update",
        "sudo apt-get install -y pkg-config build-essential gfortran libopenblas-dev liblapack-dev",
        "sudo apt-get install -y coinor-libipopt-dev",
        "sudo apt-get install -y libx11-dev xvfb"
    ],
```
**Explanation**: Commands run when container is created (cached for subsequent starts):
- **apt-get update**: Updates package lists
- **pkg-config build-essential gfortran**: Build tools for compiling packages
- **libopenblas-dev liblapack-dev**: Linear algebra libraries (required for NumPy/SciPy)
- **coinor-libipopt-dev**: IPOPT optimization solver (required for CasADi)
- **libx11-dev xvfb**: X11 display support for matplotlib

```json
    "updateContentCommand": "pip install --user -r requirements-dev.txt",
```
**Explanation**: Command run when container content is updated (e.g., when requirements change).

```json
    "postStartCommand": "echo 'Container ready for trajectory optimization development!'"
```
**Explanation**: Command run every time the container starts. Used for logging/confirmation.

## Summary

This dev container configuration creates a complete Python scientific computing environment with:
- Python 3.11 with all necessary system dependencies
- IPOPT solver for optimization
- Comprehensive VS Code extensions for Python development
- Jupyter notebook support
- Code quality tools (linting, formatting)
- GUI support for matplotlib plots
- Optimized performance settings
