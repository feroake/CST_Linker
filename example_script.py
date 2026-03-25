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
    output_path: str = ".",
    patch_length_mm: float = 25.0,
    patch_width_mm: float = 25.0,
    substrate_thickness_mm: float = 1.52,
    ground_x_mm: float = 50.0,
    ground_y_mm: float = 50.0,
    frequency_start_GHz: float = 2.0,
    frequency_end_GHz: float = 6.0,
    port_type: str = "Waveguide",
    excitation_mode: str = "H01"
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
    print("Step 1: Initializing DesignEnvironment...")
    print("  This connects to the CST Studio environment.")
    design_env = cst.interface.DesignEnvironment()
    print("  DesignEnvironment initialized successfully.")
    print()

    # Step 2: Create and save MWS project
    print("Step 2: Creating MWS project...")

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

    # 


    # Step 3: Create substrate
    print("Step 3: Creating substrate layer...")
    substrate_thickness = substrate_thickness_mm

    # Calculate dimensions (centered)
    substrate_x = ground_x_mm / 2
    substrate_y = ground_y_mm / 2

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

    substrate_history = f"""
    With Brick
        .Reset
        .Name "substrate"
        .Component "component1"
        .Material "{substrate_material}"
        .Xrange "- {substrate_x}", " {substrate_x}"
        .Yrange "- {substrate_y}", " {substrate_y}"
        .Zrange "- {substrate_thickness/2}", " {substrate_thickness/2}"
        .Create
    End With
    """

    # Add to history list
    project.model3d.add_to_history("Create substrate", substrate_history)
    print(f"  Substrate: {substrate_material} ({substrate_thickness} mm thick)")
    print()

    # Step 4: Create ground plane
    print("Step 4: Creating ground plane...")

    # Ground plane (PEC, slightly larger than substrate)
    ground_thickness = 0.1

    ground_history = f"""
    With Brick
        .Reset
        .Name "ground_plane"
        .Component "component1"
        .Material "Copper (annealed)"
        .Xrange "- {ground_x_mm/2}", " {ground_x_mm/2}"
        .Yrange "- {ground_y_mm/2}", " {ground_y_mm/2}"
        .Zrange "- {ground_thickness/2}", " {ground_thickness/2}"
        .Create
    End With
    """

    project.model3d.add_to_history("Create ground plane", ground_history)
    print(f"  Ground: PEC ({ground_x_mm} x {ground_y_mm} mm)")
    print()

    # Step 5: Create dielectric patch
    print("Step 5: Creating dielectric patch...")

    # Patch is the radiating element
    patch_history = f"""
    With Brick
        .Reset
        .Name "patch"
        .Component "component1"
        .Material "Copper (annealed)"
        .Xrange "- {patch_length_mm/2}", " {patch_length_mm/2}"
        .Yrange "- {patch_width_mm/2}", " {patch_width_mm/2}"
        .Zrange "- {patch_length_mm/4}", " {patch_length_mm/4}"
        .Create
    End With
    """

    project.model3d.add_to_history("Create patch", patch_history)
    print(f"  Patch: {substrate_material} ({patch_length_mm} x {patch_width_mm} mm)")
    print()

    
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


def parametric_patch_studies(output_path: str = ".") -> None:
    """
    Create multiple patch antennas with different parameters.

    Demonstrates how to create parametric studies externally.
    """
    print("=" * 60)
    print("Parametric Patch Antenna Studies")
    print("=" * 60)
    print()

    # Define parametric ranges
    patch_lengths = [20.0, 25.0, 30.0]
    patch_widths = [20.0, 25.0, 30.0]
    substrate_thicknesses = [1.52, 0.787]
    substrate_materials = ["FR4", "Rogers_RO4003C"]

    # Create parametric study
    for length in patch_lengths:
        for width in patch_widths:
            for thickness in substrate_thicknesses:
                for material in substrate_materials:
                    # Create unique output path
                    folder = os.path.join(output_path, f"parametric_{material}")
                    os.makedirs(folder, exist_ok=True)

                    project_name = f"patch_{length}x{width}mm_{thickness}mm_{material}.cstprj"
                    save_path = os.path.join(folder, project_name)

                    try:
                        create_patch_antenna_external(
                            output_path=folder,
                            patch_length_mm=length,
                            patch_width_mm=width,
                            substrate_thickness_mm=thickness,
                            substrate_material=material,
                            ground_x_mm=40.0,
                            ground_y_mm=40.0,
                            frequency_start_GHz=1.0,
                            frequency_end_GHz=18.0,
                            port_type="Waveguide",
                            excitation_mode="H01"
                        )

                    except Exception as e:
                        print(f"  ERROR creating {project_name}: {e}")
                        continue


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
    parser.add_argument(
        "--create-single", "-c",
        action="store_true",
        help="Create single antenna with default parameters"
    )
    parser.add_argument(
        "--parametric", "-p",
        action="store_true",
        help="Run parametric study"
    )

    args = parser.parse_args()

    if args.create_single:
        create_patch_antenna_external(
            output_path=args.output,
            patch_length_mm=25.0,
            patch_width_mm=25.0,
            substrate_thickness_mm=1.52,
            #substrate_material="FR-4"
        )
    #elif args.parametric:
        #parametric_patch_studies(output_path=args.output)
    else:
        # Default: create single antenna
        create_patch_antenna_external(
            #substrate_material="FR-4",
            output_path=args.output
        )


if __name__ == "__main__":
    main()
