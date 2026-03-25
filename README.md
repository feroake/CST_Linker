# CST Studio Suite External Automation Script

A Python script for external automation of CST Studio Suite using the official `cst.interface` API. This script creates parameterized patch antenna designs without requiring win32com or internal CST execution.

## Overview

This script uses CST's external Python scripting model to:
- Initialize a DesignEnvironment
- Create a new MWS (Microwave Studio) project
- Build geometries using the History List mechanism
- Configure simulation settings (FDTD solver, ports, frequency range)
- Save the project to disk

**Reference Methodology:** https://blog.technia.com/en/simulation/cst-studio-suite-python-scripting

## Installation

### 1. Install CST Python Link

```bash
pip install --no-index --find-links "<CST_PATH>/Library/Python/repo/simple" cst-studio-suite-link
```

Replace `<CST_PATH>` with your CST installation path. On Windows, typically:
```
C:/Program Files/CST/Studio Suite/2024/Python/repo/simple
```

### 2. Verify Installation

```bash
python -c "import cst.interface; print('CST Python API installed successfully!')"
```

## Usage

### Basic Usage

```python
from cst_patch_antenna import create_patch_antenna

# Create antenna with default parameters
antenna = create_patch_antenna(
    output_path="C:/Projects",
    patch_length_mm=20.0,
    patch_width_mm=20.0,
    substrate_thickness_mm=1.6,
    substrate_material="FR4",
    ground_x_mm=40.0,
    ground_y_mm=40.0,
    frequency_start_GHz=1.0,
    frequency_end_GHz=18.0,
    port_type="Waveguide",
    excitation_mode="H01"
)
```

### Using CSTStudioSuiteLink Package

```python
from cst.studio_suite_link import CSTStudioSuiteLink

# Alternative using CSTStudioSuiteLink
with CSTStudioSuiteLink() as cst:
    cst.design_environment()
    # ... use CST API
```

### Custom Antenna Design

```python
antenna = CSTPatchAntenna(output_path=".")
antenna.initialize()
antenna.create_substrate(
    substrate_material="Rogers_RO4003C",
    substrate_thickness_mm=0.787,
    ground_x_mm=50.0,
    ground_y_mm=50.0
)
antenna.create_ground_plane(
    ground_material="PEC",
    ground_x_mm=50.0,
    ground_y_mm=50.0
)
antenna.create_patch(
    patch_length_mm=25.0,
    patch_width_mm=25.0,
    patch_material="Rogers_RO4003C",
    patch_thickness_mm=0.787
)
antenna.add_top_ground(
    ground_material="PEC",
    patch_length_mm=25.0,
    patch_width_mm=25.0
)
antenna.add_waveguide_port(
    port_name="Port1",
    position_z_mm=0.0,
    excitation_mode="H01"
)
antenna.set_frequency_range(
    start_GHz=2.0,
    end_GHz=6.0
)
```

## How It Works

### 1. DesignEnvironment

```python
design_env = cst.interface.DesignEnvironment()
```

- Connects to the CST Studio environment
- Provides access to CST's internal objects
- Must be initialized before any CST operations

### 2. MWS Project

```python
mws_project = design_env.new_mws()
mws_project.save("path/to/project.cstprj", allow_overwrite=True)
```

- Creates a new CST Microwave Studio project
- Saves to `.cstprj` file format

### 3. History List Mechanism

```python
history = """
With Brick
    .Reset
    .Name "substrate"
    .Component "component1"
    .Material "FR4"
    .Xrange "-10", "10"
    .Yrange "-10", "10"
    .Zrange "0", "1.6"
    .Create
End With
"""
mws_project.model3d.add_to_history("Create substrate", history)
```

**Command Structure:**
- `With Brick`: Defines a brick geometry
- `.Reset`: Clears previous geometry in the command
- `.Name`: Sets geometry identifier
- `.Component`: Assigns component (default: "component1")
- `.Material`: Sets material type (PEC, FR4, AIR, etc.)
- `.Xrange/.Yrange/.Zrange`: Defines dimensions
- `.Create`: Executes the geometry creation
- `End With`: Closes the brick definition

The `add_to_history()` method queues commands for CST to execute when the project is opened.

### 4. Geometry Creation Order

1. **Substrate**: Bottom dielectric layer
2. **Ground Plane**: PEC bottom plane
3. **Patch**: Dielectric radiating element
4. **Top Ground**: PEC top plane (completes microstrip)
5. **Air Box**: Simulation boundaries
6. **Port**: Waveguide or discrete port

### 5. Port Types

**Waveguide Port:**
- Best for RF/microwave simulations
- Excites specific propagating modes (e.g., H01, TE10)
- Defined by X/Y range and Z thickness

**Discrete Port:**
- Suitable for microstrip/patch antennas
- Coaxial or lumped port options
- Simpler port definition

## Parametric Sweeps

To create parametric sweeps, modify antenna parameters in a loop:

```python
from itertools import product

# Parametric study of patch dimensions
patch_lengths = [15.0, 18.0, 20.0, 22.0, 25.0]
patch_widths = [15.0, 18.0, 20.0, 22.0, 25.0]

for length, width in product(patch_lengths, patch_widths):
    antenna = create_patch_antenna(
        output_path=f"C:/Projects/parametric/{length}_x_{width}mm",
        patch_length_mm=length,
        patch_width_mm=width,
        substrate_thickness_mm=1.6,
        substrate_material="FR4",
        ground_x_mm=40.0,
        ground_y_mm=40.0,
        frequency_start_GHz=1.0,
        frequency_end_GHz=18.0
    )
    # Save with descriptive name
    antenna.design_env.project.save(
        f"C:/Projects/parametric/patch_{length}x{width}mm.cstprj",
        allow_overwrite=True
    )
```

## Script Structure

```
cst_patch_antenna.py
├── CSTPatchAntenna class
│   ├── __init__()              : Initialize DesignEnvironment
│   ├── initialize()            : Create and save MWS project
│   ├── create_substrate()      : Create dielectric substrate
│   ├── create_ground_plane()   : Create PEC ground
│   ├── create_patch()          : Create dielectric patch
│   ├── add_top_ground()        : Add top metal layer
│   ├── add_air_box()           : Add simulation boundaries
│   ├── configure_solver()      : Set FDTD/FEM solver
│   ├── set_frequency_range()   : Define simulation band
│   ├── add_waveguide_port()    : Add waveguide port
│   ├── add_discrete_port()     : Add discrete port
│   ├── configure_simulation_time() : Set max time
│   ├── configure_adaptivity()  : Set solver adaptivity
│   ├── create_full_antenna()   : Create complete antenna
│   ├── run_simulation()        : Run simulation
│   └── get_geometry_list()     : Get geometry list
│
└── create_patch_antenna()      : Convenience function
```

## Material Definitions

| Material | Type | Description |
|----------|------|-------------|
| "PEC" | Perfect Electric Conductor | Ideal metal (ground, top plane) |
| "AIR" | Air | Simulation air region |
| "FR4" | Dielectric | Standard PCB material (εᵣ≈4.4) |
| "SIO2" | Silica | Quartz/silicon dioxide |
| "Rogers_RO4003C" | Dielectric | High-frequency substrate |

## Running the Simulation

### Option 1: GUI Execution

1. Open the generated `.cstprj` file in CST Studio
2. Review the geometry in the 3D viewer
3. Click "Compute" button in the toolbar

### Option 2: Command Line

```bash
cst run "C:/Projects/patch_antenna.cstprj"
```

### Option 3: CST Python Console

```python
import cst
de = cst.interface.DesignEnvironment()
project = de.new_mws()
# ... create geometry ...
project.run()
```

## Extending the Script

### Adding New Geometries

```python
antenna.create_disk(
    radius_mm=10.0,
    height_mm=0.1,
    material="PEC",
    x_mm=0.0,
    y_mm=0.0,
    z_mm=10.0
)
```

### Adding Sources

```python
antenna.add_source(
    source_name="monopulse",
    source_type="Gaussian",
    frequency_GHz=9.0,
    power_W=1.0
)
```

### Adding Boundaries

```python
antenna.set_pml_boundaries()
antenna.set_periodic_boundaries()
```

### Saving Progress

```python
def save_project_with_name(antenna, name: str) -> None:
    """Save project with custom name."""
    path = os.path.join(antenna.output_path, name + ".cstprj")
    antenna.design_env.project.save(path, allow_overwrite=True)
```

## Troubleshooting

### "CST Python API not installed"

Install via:
```bash
pip install --no-index --find-links "C:/Program Files/CST/Studio Suite/2024/Python/repo/simple" cst-studio-suite-link
```

### "DesignEnvironment failed"

Ensure CST Studio is running. The DesignEnvironment requires an active CST license.

### "Geometry not visible"

1. Open the `.cstprj` file in CST
2. Check the 3D viewer for geometries
3. Look in "Project Explorer" for component list

### "Simulation fails"

1. Verify geometry is valid (no intersecting objects)
2. Check port positioning
3. Ensure frequency range covers expected resonances

## Files Created

| File | Description |
|------|-------------|
| `patch_antenna.cstprj` | CST project with geometry |
| `README.md` | This documentation |

## License

This script is provided as-is for use with CST Studio Suite. Refer to CST's licensing terms for redistribution.

## Support

For issues:
1. Check CST documentation: https://support.cst.com
2. Review CST API documentation
3. Open GitHub issue for CST Studio Suite

## References

- CST Python API: https://support.cst.com/ss/cst2022/help/Python_External_Scripting.html
- External Scripting Methodology: https://blog.technia.com/en/simulation/cst-studio-suite-python-scripting
- CST Studio Suite: https://www.cst.com/products/cst-studio-suite
