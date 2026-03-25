#!/C:/Users/Avinash/cst_env/Scripts/python.exe
"""
CST External Scripting Example
Demonstrates how to create a patch antenna using the cst.interface API

This example shows:
1. Creating a DesignEnvironment
2. Building geometry with History List commands
3. Configuring simulation settings
4. Saving and running the simulation
"""
#py "C:\Users\Avinash\Documents\myProject_Stuff\cst_linker\example_script.py" --output "C:\Users\Avinash\Documents\myProject_Stuff\cst_linker\external"

import os
#import sys

# Import CST API
import cst.interface
# try:
#     import cst.interface
# except ImportError:
#     print("ERROR: CST Python API not found!")
#     print("Install with: pip install --no-index --find-links '<CST_PATH>/Library/Python/repo/simple' cst-studio-suite-link")
#     sys.exit(1)


def create_patch_antenna_external(
    #substrate_material: str,
    patch_length_mm: float,
    patch_width_mm: float,
    substrate_thickness_mm: float,
    port_type: str = "Waveguide",
    excitation_mode: str = "H01",
    output_path: str = ".",
) -> None:
    """
    Create a patch antenna using external scripting.

    This function demonstrates the CST interface methodology:
    - DesignEnvironment for connection
    - MWS project for project management
    - History List for geometry creation
    """
    print("=" * 60)
    print("CST External Scripting Example")
    print("=" * 60)
    print()

    # Step 1: Initialize DesignEnvironment
    design_env = cst.interface.DesignEnvironment()
    
    # Step 2: Create and save MWS project
    # Create new MWS (Microwave Studio) project
    project = design_env.new_mws()

    # Save project (must be absolute path)
    project_name = "example_patch_antenna.cstprj"
    if os.path.isabs(output_path):
        save_path = os.path.join(output_path, project_name)
    else:
        save_path = os.path.abspath(os.path.join(output_path, project_name))
    project.save(save_path, allow_overwrite=True)
    print(f"  Project saved to: {save_path}")
    print()

    # Set the units
    unit_history = f"""
    With Units
        .SetUnit "Length", "mm"
        .SetUnit "Frequency", "GHz"
        .SetUnit "Voltage", "V"
        .SetUnit "Resistance", "Ohm"
        .SetUnit "Inductance", "nH"
        .SetUnit "Temperature",  "degC"
        .SetUnit "Time", "ns"
        .SetUnit "Current", "A"
        .SetUnit "Conductance", "S"
        .SetUnit "Capacitance", "pF"
    End With
    """
    project.model3d.add_to_history("Set units", unit_history)
    
    # Step 3: Create substrate
    substrate_thickness = substrate_thickness_mm
    # Build history command for substrate
    substrate_history = f"""
    With Material
        .Reset
        .Name "FR-4 (lossy)"
        .Folder ""
        .FrqType "all"
        .Type "Normal"
        .SetMaterialUnit "GHz", "mm"
        .Epsilon "4.3"
        .Mu "1.0"
        .Kappa "0.0"
        .TanD "0.025"
        .TanDFreq "10.0"
        .TanDGiven "True"
        .TanDModel "ConstTanD"
        .KappaM "0.0"
        .TanDM "0.0"
        .TanDMFreq "0.0"
        .TanDMGiven "False"
        .TanDMModel "ConstKappa"
        .DispModelEps "None"
        .DispModelMu "None"
        .DispersiveFittingSchemeEps "General 1st"
        .DispersiveFittingSchemeMu "General 1st"
        .UseGeneralDispersionEps "False"
        .UseGeneralDispersionMu "False"
        .Rho "0.0"
        .ThermalType "Normal"
        .ThermalConductivity "0.3"
        .SetActiveMaterial "all"
        .Colour "0.94", "0.82", "0.76"
        .Wireframe "False"
        .Transparency "0"
        .Create
    End With
    """
    project.model3d.add_to_history("Create substrate material", substrate_history)

    substrate_material = "FR-4 (lossy)"
    substrate_width = 2 * patch_width_mm
    substrate_length = 2 * patch_length_mm

    substrate_history = f"""
    With Brick
        .Reset
        .Name "substrate"
        .Component "component1"
        .Material "{substrate_material}"
        .Xrange "- {substrate_width/2}", " {substrate_width/2}"
        .Yrange "- {substrate_length/2}", " {substrate_length/2}"
        .Zrange " {0.035}", " {0.035+substrate_thickness}"
        .Create
    End With
    """
    # Add to history list
    project.model3d.add_to_history("Create substrate", substrate_history)

    # Step 4: Create ground plane
    ground_thickness = 0.035

    ground_history = f"""
    With Brick
        .Reset
        .Name "ground_plane"
        .Component "component1"
        .Material "Copper (annealed)"
        .Xrange "- {substrate_width/2}", " {substrate_width/2}"
        .Yrange "- {substrate_length/2}", " {substrate_length/2}"
        .Zrange " {0}", " {ground_thickness}"
        .Create
    End With
    """
    project.model3d.add_to_history("Create ground plane", ground_history)

    # Step 5: Create dielectric patch
    patch_history = f"""
    With Brick
        .Reset
        .Name "patch"
        .Component "component1"
        .Material "Copper (annealed)"
        .Xrange "- {patch_width_mm/2}", " {patch_width_mm/2}"
        .Yrange "- {patch_length_mm/2}", " {patch_length_mm/2}"
        .Zrange " {0.035 + substrate_thickness}", " {0.035 + 0.035 + substrate_thickness}"
        .Create
    End With
    """
    project.model3d.add_to_history("Create patch", patch_history)

    # Step 6: Create Microstrip
    MW = 2.86
    microstrip_history = f"""
    With Brick
        .Reset 
        .Name "microstrip" 
        .Component "component1" 
        .Material "Copper (annealed)" 
        .Xrange "- {2.86/2}", " {2.86/2}"
        .Yrange "- {patch_length_mm/2}", "- {substrate_length/2}" 
        .Zrange " {0.035 + substrate_thickness}", " {0.035 + 0.035 + substrate_thickness}"
        .Create
    End With
    """
    
    project.model3d.add_to_history("Create microstrip", microstrip_history)

    # Step 7: Create Insets
    inset_history = f"""
    With Material
        .Reset
        .Name "Vacuum"
        .Folder ""
        .FrqType "all"
        .Type "Normal"
        .SetMaterialUnit "Hz", "mm"
        .Epsilon "1.0"
        .Mu "1.0"
        .Kappa "0"
        .TanD "0.0"
        .TanDFreq "0.0"
        .TanDGiven "False"
        .TanDModel "ConstKappa"
        .KappaM "0"
        .TanDM "0.0"
        .TanDMFreq "0.0"
        .TanDMGiven "False"
        .TanDMModel "ConstKappa"
        .DispModelEps "None"
        .DispModelMu "None"
        .DispersiveFittingSchemeEps "General 1st"
        .DispersiveFittingSchemeMu "General 1st"
        .UseGeneralDispersionEps "False"
        .UseGeneralDispersionMu "False"
        .Rho "0"
        .ThermalConductivity "0"
        .SetActiveMaterial "all"
        .Colour "0.5", "0.8", "1"
        .Wireframe "False"
        .Transparency "0"
        .Create
    End With
    """
    project.model3d.add_to_history("Create inset material", inset_history)

    InL = 9
    InW = 0.74
    inset_history = f"""
    With Brick
        .Reset 
        .Name "inset1"
        .Component "component1" 
        .Material "Vacuum" 
        .Xrange "- {MW/2}", "- {MW/2 + InW}" 
        .Yrange "- {patch_length_mm/2 - InL}", "- {patch_length_mm / 2}" 
        .Zrange " {0.035 + substrate_thickness}", " {0.035 + 0.035 + substrate_thickness}"
        .Create
    End With
    """
    project.model3d.add_to_history("Create inset1", inset_history)
    boolean_history = f""" Solid.Subtract "component1:patch", "component1:inset1" """
    project.model3d.add_to_history("Create subtract inset1", boolean_history)

    inset_history = f"""
    With Brick
        .Reset 
        .Name "inset2" 
        .Component "component1" 
        .Material "Vacuum" 
        .Xrange " {MW/2}", " {MW/2 + InW}" 
        .Yrange "- {patch_length_mm/2 - InL}", "- {patch_length_mm / 2}" 
        .Zrange " {0.035 + substrate_thickness}", " {0.035 + 0.035 + substrate_thickness}"
        .Create
    End With
    """
    project.model3d.add_to_history("Create inset2", inset_history)
    boolean_history = f""" Solid.Subtract "component1:patch", "component1:inset2" """
    project.model3d.add_to_history("Create subtract inset2", boolean_history)



    # Step 10: Add port
    print("Step 10: Adding port...")

    if port_type == "Waveguide":
        port_history = f"""
        With Port
            .Reset
            .Name "Port1"
            .Type "Waveguide"
            .Component "component1"
            .Position " -26, -26, 0"
            .Xrange "- 27", " 27"
            .Yrange "- 27", " 27"
            .Zrange "- {substrate_thickness/2}", " {substrate_thickness/2}"
            .Mode "{excitation_mode}"
            .Normal "Z"
        End With
        """
        print(f"  Port type: Waveguide")
        print(f"  Excitation mode: {excitation_mode}")
    else:
        port_history = f"""
        With Port
            .Reset
            .Name "Port1"
            .Type "Discrete"
            .Component "component1"
            .Position " -26, -26, 0"
            .Xrange "- 27", " 27"
            .Yrange "- 27", " 27"
            .Zrange "- {substrate_thickness/2}", " {substrate_thickness/2}"
            .Mode "Coaxial"
            .Normal "Z"
        End With
        """
        print(f"  Port type: Discrete")
        print(f"  Excitation mode: Coaxial")

    project.model3d.add_to_history(f"Add {port_type.lower()} port", port_history)
    print()

    # Step 11: Set simulation time
    print("Step 11: Setting simulation time...")

    time_history = f"""
    With Fdtd
        .Reset
        .Name "max_time"
        .MaxTime 400000
    End With
    """

    project.model3d.add_to_history("Set simulation time: 400000 ps", time_history)
    print("  Max simulation time: 400000 ps (0.4 ns)")
    print()

    # Step 12: Configure adaptivity
    print("Step 12: Setting adaptivity...")

    adaptivity_history = """
    With Fdtd
        .Reset
        .Name "adaptivity"
        .Type "Sweep"
    End With
    """

    project.model3d.add_to_history("Set adaptivity: Sweep", adaptivity_history)
    print("  Adaptivity: Sweep")
    print()

    # Summary
    print("=" * 60)
    print("Antenna Creation Complete!")
    print("=" * 60)
    print()
    print(f"Project file: {save_path}")
    print()
    print("Next steps:")
    print("  1. Open the .cstprj file in CST Studio")
    print("  2. Check geometry in 3D viewer")
    print("  3. Click 'Compute' to run simulation")
    print("  4. Or run: cst run '" + save_path + "'")
    print()


def main():
    """Main entry point for examples."""
    import argparse

    parser = argparse.ArgumentParser(
        description="CST External Scripting Examples"
    )
    parser.add_argument(
        "--output", "-o",
        default=".",
        help="Output path for CST project files"
    )
    # parser.add_argument(
    #     "--create-single", "-c",
    #     action="store_true",
    #     help="Create single antenna with default parameters"
    # )
    parser.add_argument(
        "--parametric", "-p",
        action="store_true",
        help="Run parametric study"
    )

    args = parser.parse_args()
    print("=" * 60)
    print("Enter parametric values")
    patch_length_mm = float(input("Enter patch length in mm:"))
    substrate_thickness_mm = float(input("Enter substrate height in mm:"))
    
    create_patch_antenna_external(
        output_path=args.output,
        patch_length_mm=patch_length_mm,
        patch_width_mm=38.0,
        substrate_thickness_mm=substrate_thickness_mm,
    )

    # if args.create_single:
        
    # else:
    #     # Default: create single antenna
    #     create_patch_antenna_external(
    #         #substrate_material="FR-4",
    #         output_path=args.output
    #     )


if __name__ == "__main__":
    main()
