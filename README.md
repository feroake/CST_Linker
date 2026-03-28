# CST_Linker
Python script to automate the process of making antennas. Using CST Studio Suite 2025. Done with the help of claude qwen 3.5 local instance.

>[!important]
> - Needs CST Studio Suite 2025, I am working with this version not sure if it is compatible with other versions
> - **Python 3.11 required** the cst studio suite python library packages require python *<3.12,>=3.7*


### Steps to Run
- *Create python virtual environment by downloading python 3.11 and assigning it a name (cst_env)*
- `py install 3.11`
- `py -3.11 -m venv cst_env`
- *Set it may be required to enable the Activate.ps1 script by setting the execution policy for the user*
- `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- `cst_env\Scripts\activate`
- *Install CST library*
- `pip install --no-index --find-links "C:/Program Files (x86)/CST Studio Suite 2025/Library/Python/repo/simple" cst-studio-suite-link`
- *run the external script*
- `py "*<Path\to\external\script>*"`

## Table of parameters
<img width="1007" height="811" alt="image" src="https://github.com/user-attachments/assets/2b30d953-5fea-455f-bbd6-71aebc469dbc" />


## Overview

This script uses CST's external Python scripting model to:
- Initialize a DesignEnvironment
- Create a new MWS (Microwave Studio) project
- Build geometries using the History List mechanism
- Configure simulation settings (FDTD solver, ports, frequency range)
- Save the project to disk

**Reference Methodology:** https://blog.technia.com/en/simulation/cst-studio-suite-python-scripting

## Usage
- Refer to *cst_patch_antenna.py* to see fully automated workflow
- *example_script.py* asks the user for patch length in mm and substrate height in mm. This is done in accordance with our ML automated flow where given a frequency the algorithm will output the patch length and substrate height which then further will be inputted into the cst linker to automate the process of antenna generation. As of now the linker part is a separate module from the ML module.
- *FirstExternalPythonScript.py* can be used as a debugging script to check and verify if CST api is correctly installed and the module is properly working. If done correctly, running the script should open CST and automatically generate a solid block of PEC.

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
