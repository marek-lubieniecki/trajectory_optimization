# VS Code Launch Configuration Explained

This document provides a line-by-line explanation of the `.vscode/launch.json` file.

## File: `.vscode/launch.json`

### File Structure Overview

```json
{
    "version": "0.2.0",
```
**Explanation**: Specifies the launch.json schema version. Version 0.2.0 is the current format for VS Code debug configurations.

```json
    "configurations": [
```
**Explanation**: Array containing all debug configuration definitions. Each configuration defines how to launch and debug your application.

## Configuration 1: Debug Trajectory Optimization

```json
        {
            "name": "Debug Trajectory Optimization",
```
**Explanation**: Human-readable name for the debug configuration. This appears in the debug dropdown menu and Run and Debug panel.

```json
            "type": "debugpy",
```
**Explanation**: Specifies the debugger type to use. `debugpy` is the modern Python debugger (replaces the deprecated `python` type). It provides:
- Better performance than the legacy Python debugger
- Support for Python 3.5+
- Advanced debugging features like conditional breakpoints
- Better integration with Jupyter notebooks

```json
            "request": "launch",
```
**Explanation**: Defines how to start the debug session:
- **"launch"**: Start a new process and debug it from the beginning
- **"attach"**: Attach to an already running process (alternative option)

```json
            "program": "${workspaceFolder}/main.py",
```
**Explanation**: Specifies the Python file to debug. Uses VS Code variable substitution:
- **${workspaceFolder}**: Resolves to the root folder of the workspace
- In the dev container, this becomes `/workspace/main.py`
- This ensures the configuration works regardless of the absolute path

```json
            "console": "integratedTerminal",
```
**Explanation**: Controls where the program output appears:
- **"integratedTerminal"**: Uses VS Code's integrated terminal (recommended)
- **"internalConsole"**: Uses VS Code's debug console (limited input support)
- **"externalTerminal"**: Uses system terminal (separate window)

For scientific computing, integrated terminal is preferred because:
- Supports interactive input (if needed)
- Better handling of matplotlib plots
- Consistent with development workflow

```json
            "justMyCode": false,
```
**Explanation**: Controls which code the debugger will step into:
- **false**: Can debug into library code (NumPy, CasADi, matplotlib, etc.)
- **true**: Only steps through your own code

For trajectory optimization, `false` is useful because:
- You might need to debug CasADi optimization issues
- Can step into NumPy/SciPy for understanding numerical problems
- Helpful for learning how libraries work

```json
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
```
**Explanation**: Sets environment variables for the debug session:
- **PYTHONPATH**: Tells Python where to look for modules
- **${workspaceFolder}**: Adds the project root to Python's module search path
- This allows importing custom modules from subdirectories without installation

## Configuration 2: Debug Current File

```json
        {
            "name": "Debug Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
```
**Explanation**: Similar to the first configuration, but uses `${file}` instead of a specific file:
- **${file}**: Resolves to the currently active file in the editor
- Allows debugging any Python file without changing configuration
- Useful for testing individual modules or scripts

```json
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```
**Explanation**: Same console and debugging scope settings as the first configuration.

## VS Code Variable Substitution

### Available Variables
- **${workspaceFolder}**: Root folder of the workspace (`/workspace` in container)
- **${file}**: Full path of currently active file
- **${fileBasename}**: Filename without path (`main.py`)
- **${fileDirname}**: Directory containing the current file
- **${fileExtname}**: File extension (`.py`)
- **${cwd}**: Current working directory

### Example Expansions (in dev container)
```json
// Input variables
"${workspaceFolder}/main.py"  // → /workspace/main.py
"${file}"                     // → /workspace/src/utils.py (if that's open)
"${fileBasename}"             // → utils.py
"${workspaceFolder}/data"     // → /workspace/data
```

## Debug Session Features

### When you press F5 or click "Start Debugging":

1. **VS Code reads launch.json** and shows available configurations
2. **Debugpy starts** the Python interpreter with debugging enabled
3. **Breakpoints are set** at any red dots you've clicked in the editor
4. **Program executes** until it hits a breakpoint or exception
5. **Debug controls become available**:
   - **Continue (F5)**: Resume execution
   - **Step Over (F10)**: Execute next line, don't enter functions
   - **Step Into (F11)**: Execute next line, enter function calls
   - **Step Out (Shift+F11)**: Finish current function and return
   - **Restart (Ctrl+Shift+F5)**: Stop and start again
   - **Stop (Shift+F5)**: Terminate debugging

### Debug Features Specific to Scientific Computing

#### Variable Inspection
```python
# When debugging trajectory optimization, you can inspect:
X = opti.variable(7, self.N + 1)  # View matrix dimensions and values
U = opti.variable(4, self.N)      # View control inputs
state_history = []                # View optimization history
```

#### Watch Expressions
You can add watch expressions to monitor values:
```python
X[0, -1]      # Final x position
X[1, -1]      # Final y position  
X[6, -1]      # Final mass (fuel consumption)
opti.debug.value(X[:, -1])  # Final state values
```

#### Call Stack
When debugging CasADi optimization, the call stack shows:
```
main.py:solve() line 150
casadi.nlpsol() line ???
ipopt.solve() line ???
```

## Advanced Configuration Options

### Conditional Breakpoints
```json
// Not in launch.json, but useful to know:
// Right-click on breakpoint → Edit Breakpoint → Add condition
// Example: k > 50  (only break when loop variable k exceeds 50)
```

### Launch with Arguments
```json
{
    "name": "Debug with Arguments",
    "type": "debugpy",
    "request": "launch",
    "program": "${workspaceFolder}/main.py",
    "args": ["--max-iterations", "1000", "--verbose"],
    "console": "integratedTerminal"
}
```

### Pre/Post Launch Tasks
```json
{
    "name": "Debug with Setup",
    "type": "debugpy",
    "request": "launch",
    "program": "${workspaceFolder}/main.py",
    "preLaunchTask": "Install Dependencies",
    "postDebugTask": "cleanup",
    "console": "integratedTerminal"
}
```

### Debugging with Different Python Interpreters
```json
{
    "name": "Debug with Conda Env",
    "type": "debugpy",
    "request": "launch",
    "python": "/opt/conda/envs/trajectory/bin/python",
    "program": "${workspaceFolder}/main.py",
    "console": "integratedTerminal"
}
```

## Debugging Scientific Code Best Practices

### 1. Strategic Breakpoint Placement
```python
# Good breakpoint locations for trajectory optimization:
def solve(self):
    # Breakpoint here to inspect initial setup
    opti, X, U = self.setup_optimization()
    
    # Breakpoint here to check optimization problem
    try:
        sol = opti.solve()  # Breakpoint before solve
        # Breakpoint here to inspect solution
        return sol
    except Exception as e:
        # Breakpoint here for optimization failures
        print(f"Optimization failed: {e}")
```

### 2. Useful Debug Console Commands
```python
# In debug console (when paused at breakpoint):
opti.debug.show_infeasibilities()  # Show constraint violations
opti.debug.value(X[:, -1])         # Evaluate expressions
len(X)                             # Check variable dimensions
type(sol)                          # Inspect object types
```

### 3. Debugging Matplotlib Issues
```json
{
    "name": "Debug with Display",
    "type": "debugpy",
    "request": "launch",
    "program": "${workspaceFolder}/main.py",
    "console": "integratedTerminal",
    "env": {
        "DISPLAY": ":1",
        "MPLBACKEND": "TkAgg"
    }
}
```

## Integration with Dev Container

### Why This Configuration Works in Container

1. **Python Path Resolution**: `${workspaceFolder}` correctly resolves to `/workspace`
2. **Debugpy Availability**: Installed via requirements-dev.txt
3. **Terminal Integration**: Works with container's integrated terminal
4. **File Mounting**: Source files are properly mounted and accessible

### Container-Specific Considerations

```json
// These settings work well in the dev container:
"console": "integratedTerminal"  // ✓ Works with container terminal
"justMyCode": false             // ✓ Can debug into pre-installed libraries
"env": {"PYTHONPATH": "..."}    // ✓ Container filesystem paths work
```

## Troubleshooting Debug Issues

### "Module not found" Errors
```json
// Add to env section:
"env": {
    "PYTHONPATH": "${workspaceFolder}:${workspaceFolder}/src"
}
```

### Debugger Not Stopping at Breakpoints
- Ensure file is saved (Ctrl+S)
- Check that debugpy is installed: `pip list | grep debugpy`
- Verify Python interpreter is correct: Check bottom-left of VS Code

### Slow Debugging Performance
```json
// Add to configuration:
"subProcess": false,           // Don't debug subprocesses
"django": false,              // Disable Django support
"justMyCode": true            // Only debug your code
```

## Summary

The launch.json configuration provides:

1. **Two debug configurations**:
   - Specific for main.py (trajectory optimization)
   - Generic for any current file

2. **Optimized for scientific computing**:
   - Can debug into library code (CasADi, NumPy)
   - Uses integrated terminal for better matplotlib support
   - Proper Python path configuration

3. **Container compatibility**:
   - Uses workspace-relative paths
   - Works with mounted filesystems
   - Integrates with dev container Python environment

4. **Development efficiency**:
   - Quick F5 debugging
   - Easy breakpoint management
   - Variable inspection for optimization problems
