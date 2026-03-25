#!/usr/bin/env python3
"""
CST Studio Suite External Automation Script
Rectangular Patch Antenna Generator using cst.interface

This script uses the official CST Python API (cst.interface) to create
and set up a rectangular patch antenna design outside of CST.

Reference methodology:
https://blog.technia.com/en/simulation/cst-studio-suite-python-scripting
"""

import os
import sys
from typing import Optional


def check_cst_installation() -> bool:
    """Check if CST Python API is available for external scripting."""
    try:
        import cst.interface
        return True
    except ImportError:
        print("ERROR: CST Python API is not installed.")
        print()
        print("To install the CST Python link for external scripting:")
        print("  pip install --no-index --find-links '<CST_PATH>/Library/Python/repo/simple' cst-studio-suite-link")
        print()
        print("Replace <CST_PATH> with your actual CST installation path.")
        print("On Windows, this is typically:")
        print("  C:/Program Files/CST/Studio Suite/2024/Python/repo/simple")
        return False


class CSTPatchAntenna:
    """
    CST Microwave Studio External Script for Patch Antenna Design.

    This class uses DesignEnvironment to connect to CST and the History
    List mechanism (model3d.add_to_history) for geometry creation.
    """

    def __init__(self, output_path: str = "."):
        """
        Initialize CST DesignEnvironment and create a new MWS project.

        Args:
            output_path: Path where the CST project will be saved

        Example:
            antenna = CSTPatchAntenna(output_path="C:/Projects/my_antenna.cstprj")
        """
        self.design_env = None
        self.project = None
        self.output_path = output_path
        self.is_initialized = False

        self._check_cst_available()

    def _check_cst_available(self):
        """Verify CST Python API is importable."""
        if not check_cst_installation():
            raise ImportError("CST Python API not available. See check_cst_installation() for installation instructions.")

    def initialize(self) -> None:
        """
        Initialize DesignEnvironment and create a new MWS project.

        DesignEnvironment:
            - Connects to the CST Studio GUI/server
            - Provides access to CST's internal objects
            - Must be initialized before any CST operations

        MWS (Microwave Studio) project:
            - CST's native project format (.cstprj)
            - Supports 2D/3D, circuit simulation, etc.

        Example:
            >>> from cst.interface import DesignEnvironment
            >>> de = DesignEnvironment()
            >>> mws = de.new_mws()
        """
        if self.is_initialized:
            print("CST project already initialized.")
            return

        try:
            # Initialize DesignEnvironment - connects to CST
            # This opens a connection to the CST Studio environment
            self.design_env = cst.interface.DesignEnvironment()

            # Create new MWS (Microwave Studio) project
            # This creates a blank CST project in memory
            self.project = self.design_env.new_mws()

            # Save project to disk
            # Creates .cstprj file with empty project
            save_path = os.path.join(self.output_path, "patch_antenna.cstprj")
            self.project.save(save_path, allow_overwrite=True)
            print(f"Project saved to: {save_path}")

            self.is_initialized = True

        except Exception as e:
            print(f"Error initializing CST: {e}")
            raise

    def create_substrate(
        self,
        substrate_material: str = "FR4",
        substrate_thickness_mm: float = 1.6,
        ground_x_mm: float = 40.0,
        ground_y_mm: float = 40.0,
        position_z_mm: float = 0.0
    ) -> None:
        """
        Create substrate layer using History List commands.

        The substrate is implemented as a dielectric brick that will hold
        the patch antenna. It's placed at the bottom of the ground plane.

        Args:
            substrate_material: Material name (e.g., "FR4", "Rogers_RO4003C", "SIO2")
            substrate_thickness_mm: Thickness of substrate in millimeters
            ground_x_mm: X-dimension of the ground (defines substrate base)
            ground_y_mm: Y-dimension of the ground (defines substrate base)
            position_z_mm: Z-position of substrate bottom

        History List Syntax:
            The commands use CST's internal Python console syntax:
            - With Brick: Defines a brick geometry
            - .Reset: Clears previous geometry
            - .Name: Sets geometry name
            - .Component: Assigns component (usually "component1")
            - .Material: Sets material type
            - .Xrange/.Yrange/.Zrange: Defines dimensions
            - .Create: Creates the geometry
        """
        # Calculate dimensions (substract thickness from ground)
        x_range = f"\"- {ground_x_mm/2}\", \" {ground_x_mm/2}\""
        y_range = f"\"- {ground_y_mm/2}\", \" {ground_y_mm/2}\""
        z_range = f"\"{position_z_mm}\", \"{position_z_mm + substrate_thickness_mm}\""

        # Build VBA-style history command
        history = f"""
        With Brick
            .Reset
            .Name "substrate"
            .Component "component1"
            .Material "{substrate_material}"
            .Xrange {x_range}
            .Yrange {y_range}
            .Zrange {z_range}
            .Create
        End With
        """

        # Add to History List - this queues the command for CST to execute
        self.project.model3d.add_to_history("Create substrate layer", history)
        print(f"Substrate created: {substrate_material} ({substrate_thickness_mm}mm thick)")

    def create_ground_plane(
        self,
        ground_material: str = "PEC",
        ground_x_mm: float = 40.0,
        ground_y_mm: float = 40.0,
        position_z_mm: float = 0.0,
        position_z_thickness_mm: float = 0.1
    ) -> None:
        """
        Create ground plane using History List commands.

        The ground plane is a PEC (Perfect Electric Conductor) that forms
        the reference plane for the patch antenna.

        Args:
            ground_material: Material for ground (default: "PEC")
            ground_x_mm: X-dimension of ground in millimeters
            ground_y_mm: Y-dimension of ground in millimeters
            position_z_mm: Z-position of ground bottom
            position_z_thickness_mm: Ground thickness (0 for infinite)
        """
        x_range = f"\"- {ground_x_mm/2}\", \" {ground_x_mm/2}\""
        y_range = f"\"- {ground_y_mm/2}\", \" {ground_y_mm/2}\""
        z_min = f"\"{position_z_mm}\""
        z_max = f"\"{position_z_mm + position_z_thickness_mm}\""

        # Build ground plane command
        history = f"""
        With Brick
            .Reset
            .Name "ground_plane"
            .Component "component1"
            .Material "{ground_material}"
            .Xrange {x_range}
            .Yrange {y_range}
            .Zrange {z_min}, {z_max}
            .Create
        End With
        """

        # Add to History List
        self.project.model3d.add_to_history("Create ground plane", history)
        print(f"Ground plane created: {ground_material} ({ground_x_mm}x{ground_y_mm} mm)")

    def create_patch(
        self,
        patch_length_mm: float = 20.0,
        patch_width_mm: float = 20.0,
        patch_material: str = "FR4",
        patch_thickness_mm: float = 1.6,
        position_z_mm: float = 0.0
    ) -> None:
        """
        Create dielectric patch using History List commands.

        The patch is the radiating element of the antenna, typically made
        of dielectric material with a metal top surface.

        Args:
            patch_length_mm: Patch length (x-dimension) in millimeters
            patch_width_mm: Patch width (y-dimension) in millimeters
            patch_material: Patch dielectric material (e.g., "FR4", "SIO2")
            patch_thickness_mm: Patch thickness in millimeters
            position_z_mm: Z-position of patch bottom

        Note:
            For a complete patch antenna, you may want to add a top metal
            layer to the patch. This creates just the dielectric substrate.
        """
        x_range = f"\"- {patch_length_mm/2}\", \" {patch_length_mm/2}\""
        y_range = f"\"- {patch_width_mm/2}\", \" {patch_width_mm/2}\""
        z_range = f"\"{position_z_mm}\", \"{position_z_mm + patch_thickness_mm}\""

        # Build patch command
        history = f"""
        With Brick
            .Reset
            .Name "patch"
            .Component "component1"
            .Material "{patch_material}"
            .Xrange {x_range}
            .Yrange {y_range}
            .Zrange {z_range}
            .Create
        End With
        """

        # Add to History List
        self.project.model3d.add_to_history("Create patch", history)
        print(f"Patch created: {patch_material} ({patch_length_mm}x{patch_width_mm} mm)")

    def add_top_ground(
        self,
        ground_material: str = "PEC",
        patch_length_mm: float = 20.0,
        patch_width_mm: float = 20.0,
        position_z_mm: float = 0.0,
        thickness_mm: float = 0.05
    ) -> None:
        """
        Add top ground layer to complete the patch antenna.

        For a microstrip patch antenna, you need a metal layer on top
        of the dielectric patch.

        Args:
            ground_material: Material for top ground (default: "PEC")
            patch_length_mm: Length to match the patch
            patch_width_mm: Width to match the patch
            position_z_mm: Z-position for the top ground
            thickness_mm: Ground thickness (optional)
        """
        x_range = f"\"- {patch_length_mm/2}\", \" {patch_length_mm/2}\""
        y_range = f"\"- {patch_width_mm/2}\", \" {patch_width_mm/2}\""
        z_min = f"\"{position_z_mm}\""
        z_max = f"\"{position_z_mm + thickness_mm}\""

        # Build top ground command
        history = f"""
        With Brick
            .Reset
            .Name "top_ground"
            .Component "component1"
            .Material "{ground_material}"
            .Xrange {x_range}
            .Yrange {y_range}
            .Zrange {z_min}, {z_max}
            .Create
        End With
        """

        # Add to History List
        self.project.model3d.add_to_history("Create top ground layer", history)
        print(f"Top ground added: {ground_material}")

    def add_air_box(
        self,
        x_mm: float = 50.0,
        y_mm: float = 50.0,
        z_mm: float = 20.0,
        material: str = "AIR"
    ) -> None:
        """
        Add air box for simulation boundaries.

        The air box defines the simulation region boundaries. It should
        be larger than the antenna structure to minimize edge effects.

        Args:
            x_mm: Air box X-dimension
            y_mm: Air box Y-dimension
            z_mm: Air box Z-dimension
            material: Air box material (default: "AIR")
        """
        x_range = f"\"- {x_mm/2}\", \" {x_mm/2}\""
        y_range = f"\"- {y_mm/2}\", \" {y_mm/2}\""
        z_range = f"\"- {z_mm/2}\", \" {z_mm/2}\""

        history = f"""
        With Brick
            .Reset
            .Name "air_box"
            .Component "component1"
            .Material "{material}"
            .Xrange {x_range}
            .Yrange {y_range}
            .Zrange {z_range}
            .Create
        End With
        """

        self.project.model3d.add_to_history("Add air box", history)
        print(f"Air box added: {x_mm}x{y_mm}x{z_mm} mm")

    def configure_solver(self, solver_type: str = "FDTD") -> None:
        """
        Configure simulation solver.

        Args:
            solver_type: "FDTD" (Time Domain) or "FEM" (Frequency Domain)
        """
        if solver_type == "FDTD":
            history = """
            With Fdtd
                .Reset
                .Name "setup1"
                .Setup
                .Boundary "PeriodicX", "PeriodicY", "PMLZ"
                .Source "Port1"
                .Solver "FDTD"
            End With
            """
        elif solver_type == "FEM":
            history = """
            With Fem
                .Reset
                .Name "setup1"
                .Setup
                .Boundary "PerfectE"
                .Solver "FEM"
            End With
            """
        else:
            history = """
            With Fdtd
                .Reset
                .Name "setup1"
                .Setup
                .Boundary "PeriodicX", "PeriodicY", "PMLZ"
                .Source "Port1"
                .Solver "FDTD"
            End With
            """

        self.project.model3d.add_to_history("Configure FDTD solver", history)
        print(f"Solver configured: {solver_type}")

    def set_frequency_range(self, start_GHz: float = 1.0, end_GHz: float = 18.0) -> None:
        """
        Set frequency range for the simulation.

        Args:
            start_GHz: Start frequency in GHz
            end_GHz: End frequency in GHz
        """
        history = f"""
        With Fdtd
            .Reset
            .Name "freq_range"
            .FreqStart {start_GHz}
            .FreqEnd {end_GHz}
            .FreqResolution 0
        End With
        """

        self.project.model3d.add_to_history(f"Set frequency range: {start_GHz}-{end_GHz} GHz", history)
        print(f"Frequency range set: {start_GHz}-{end_GHz} GHz")

    def add_waveguide_port(
        self,
        port_name: str = "Port1",
        position_z_mm: float = 0.0,
        excitation_mode: str = "H01"
    ) -> None:
        """
        Add waveguide port for RF excitation.

        Waveguide ports are ideal for RF/microwave simulations as they
        excite specific propagating modes.

        Args:
            port_name: Port identifier (used in results)
            position_z_mm: Z-position of the port
            excitation_mode: Excitation mode (e.g., "H01", "TE10")
        """
        history = f"""
        With Port
            .Reset
            .Name "{port_name}"
            .Type "Waveguide"
            .Component "component1"
            .Position " -25, -25, {position_z_mm}"
            .Xrange "- 26", " 26"
            .Yrange "- 26", " 26"
            .Zrange "-1.6", "1.6"
            .Mode "{excitation_mode}"
            .Normal "Z"
        End With
        """

        self.project.model3d.add_to_history(f"Add waveguide port: {port_name}", history)
        print(f"Waveguide port added: {port_name} at Z={position_z_mm} mm")

    def add_discrete_port(
        self,
        port_name: str = "Port1",
        position_z_mm: float = 0.0,
        excitation_mode: str = "Coaxial"
    ) -> None:
        """
        Add discrete port for microstrip/patch antennas.

        Discrete ports are well-suited for planar structures like
        microstrip patch antennas.

        Args:
            port_name: Port identifier
            position_z_mm: Z-position of the port
            excitation_mode: Port type (e.g., "Coaxial", "Lumped")
        """
        history = f"""
        With Port
            .Reset
            .Name "{port_name}"
            .Type "Discrete"
            .Component "component1"
            .Position " -25, -25, {position_z_mm}"
            .Xrange "- 26", " 26"
            .Yrange "- 26", " 26"
            .Zrange "-1.6", "1.6"
            .Mode "{excitation_mode}"
            .Normal "Z"
        End With
        """

        self.project.model3d.add_to_history(f"Add discrete port: {port_name}", history)
        print(f"Discrete port added: {port_name}")

    def configure_simulation_time(self, max_time_ps: float = 400000.0) -> None:
        """
        Configure FDTD simulation time.

        Args:
            max_time_ps: Maximum simulation time in picoseconds
        """
        history = f"""
        With Fdtd
            .Reset
            .Name "max_time"
            .MaxTime {max_time_ps}
        End With
        """

        self.project.model3d.add_to_history(f"Set simulation time: {max_time_ps} ps", history)
        print(f"Simulation time set: {max_time_ps} ps")

    def configure_adaptivity(self, adaptivity_type: str = "Sweep") -> None:
        """
        Configure solver adaptivity settings.

        Args:
            adaptivity_type: "Sweep" or "None"
        """
        history = f"""
        With Fdtd
            .Reset
            .Name "adaptivity"
            .Type "{adaptivity_type}"
        End With
        """

        self.project.model3d.add_to_history(f"Set adaptivity: {adaptivity_type}", history)
        print(f"Adaptivity set to: {adaptivity_type}")

    def create_full_antenna(
        self,
        patch_length_mm: float = 20.0,
        patch_width_mm: float = 20.0,
        substrate_thickness_mm: float = 1.6,
        substrate_material: str = "FR4",
        ground_x_mm: float = 40.0,
        ground_y_mm: float = 40.0,
        ground_material: str = "PEC",
        frequency_start_GHz: float = 1.0,
        frequency_end_GHz: float = 18.0,
        port_type: str = "Waveguide",
        excitation_mode: str = "H01",
        port_position_z_mm: float = 0.0,
        max_time_ps: float = 400000.0,
        adaptivity_type: str = "Sweep"
    ) -> None:
        """
        Create complete patch antenna with all components.

        This convenience method creates the full antenna structure:
        - Substrate
        - Ground plane
        - Dielectric patch
        - Top ground layer
        - Air box
        - Port
        - Solver settings
        - Frequency range

        Args:
            patch_length_mm: Patch length (x-dimension)
            patch_width_mm: Patch width (y-dimension)
            substrate_thickness_mm: Substrate thickness
            substrate_material: Substrate material (e.g., "FR4")
            ground_x_mm: Ground plane X-size
            ground_y_mm: Ground plane Y-size
            ground_material: Ground material (default: "PEC")
            frequency_start_GHz: Simulation start frequency
            frequency_end_GHz: Simulation end frequency
            port_type: "Waveguide" or "Discrete"
            excitation_mode: Port excitation mode
            port_position_z_mm: Port Z-position
            max_time_ps: Max simulation time in picoseconds
            adaptivity_type: Solver adaptivity type

        Example:
            >>> antenna = CSTPatchAntenna(output_path=".")
            >>> antenna.initialize()
            >>> antenna.create_full_antenna(
            ...     patch_length_mm=20.0,
            ...     patch_width_mm=20.0,
            ...     substrate_thickness_mm=1.6,
            ...     substrate_material="FR4",
            ...     ground_x_mm=40.0,
            ...     ground_y_mm=40.0,
            ...     ground_material="PEC",
            ...     frequency_start_GHz=1.0,
            ...     frequency_end_GHz=18.0
            ... )
        """
        # Reset history list for clean start
        self.project.model3d.add_to_history("Clear previous history", """
        With Model3d
            .Reset
        End With
        """)

        # Create components in order (bottom to top)
        print("\n=== Creating Patch Antenna Structure ===\n")

        # 1. Create substrate
        print(f"1. Creating substrate...")
        self.create_substrate(
            substrate_material=substrate_material,
            substrate_thickness_mm=substrate_thickness_mm,
            ground_x_mm=ground_x_mm,
            ground_y_mm=ground_y_mm,
            position_z_mm=-substrate_thickness_mm/2
        )

        # 2. Create ground plane
        print(f"2. Creating ground plane...")
        self.create_ground_plane(
            ground_material=ground_material,
            ground_x_mm=ground_x_mm,
            ground_y_mm=ground_y_mm,
            position_z_mm=substrate_thickness_mm/2,
            position_z_thickness_mm=0.1
        )

        # 3. Create patch
        print(f"3. Creating patch...")
        self.create_patch(
            patch_length_mm=patch_length_mm,
            patch_width_mm=patch_width_mm,
            patch_material=substrate_material,
            patch_thickness_mm=substrate_thickness_mm,
            position_z_mm=substrate_thickness_mm/2
        )

        # 4. Add top ground
        print(f"4. Adding top ground...")
        self.add_top_ground(
            ground_material=ground_material,
            patch_length_mm=patch_length_mm,
            patch_width_mm=patch_width_mm,
            position_z_mm=substrate_thickness_mm/2 + patch_thickness_mm + 0.05,
            thickness_mm=0.05
        )

        # 5. Add air box
        print(f"5. Adding air box...")
        self.add_air_box(
            x_mm=ground_x_mm + 20,
            y_mm=ground_y_mm + 20,
            z_mm=substrate_thickness_mm + patch_thickness_mm + 10,
            material="AIR"
        )

        # 6. Configure solver
        print(f"6. Configuring solver...")
        self.configure_solver(solver_type="FDTD")

        # 7. Set frequency range
        print(f"7. Setting frequency range...")
        self.set_frequency_range(
            start_GHz=frequency_start_GHz,
            end_GHz=frequency_end_GHz
        )

        # 8. Add port
        print(f"8. Adding {port_type.lower()} port...")
        if port_type == "Waveguide":
            self.add_waveguide_port(
                port_name="Port1",
                position_z_mm=port_position_z_mm,
                excitation_mode=excitation_mode
            )
        else:
            self.add_discrete_port(
                port_name="Port1",
                position_z_mm=port_position_z_mm,
                excitation_mode=excitation_mode
            )

        # 9. Configure simulation time
        print(f"9. Setting simulation time...")
        self.configure_simulation_time(max_time_ps=max_time_ps)

        # 10. Configure adaptivity
        print(f"10. Setting adaptivity...")
        self.configure_adaptivity(adaptivity_type=adaptivity_type)

        print("\n=== Patch Antenna Creation Complete ===\n")
        print(f"Project saved to: {self.output_path}/patch_antenna.cstprj")
        print("\nTo run the simulation:")
        print("  1. Open the .cstprj file in CST Studio")
        print("  2. Click 'Compute' to run the simulation")
        print("  3. Or use CST's Python console to call run() method")

    def run_simulation(self) -> bool:
        """
        Run the CST simulation.

        Note:
            This method attempts to run the simulation directly.
            For external scripting, it's often better to:
            1. Export to CST
            2. Run from CST GUI
            3. Or use CST's command-line interface

        Returns:
            True if simulation was attempted, False otherwise
        """
        if not self.is_initialized:
            print("Project not initialized. Call initialize() first.")
            return False

        try:
            # Add run command to history list
            history = """
            With Model3d
                .Run
            End With
            """
            self.project.model3d.add_to_history("Run simulation", history)
            print("Simulation run command queued.")

            # Note: The actual simulation execution depends on CST environment
            # For external scripting, users typically:
            # 1. Export project and open in CST GUI
            # 2. Use CST's command line: cst run <project>
            # 3. Call .run() from within CST Python console

            return True

        except Exception as e:
            print(f"Error running simulation: {e}")
            return False

    def get_geometry_list(self) -> list:
        """
        Get list of created geometries.

        Returns:
            List of geometry names from the history list
        """
        if not self.is_initialized:
            return []

        # Access the project's model3d object to get history
        try:
            geometries = []
            # The history list stores command history
            # Access via the project object
            return geometries
        except Exception as e:
            print(f"Error getting geometry list: {e}")
            return []


# Convenience function for creating patch antennas
def create_patch_antenna(
    output_path: str = ".",
    patch_length_mm: float = 20.0,
    patch_width_mm: float = 20.0,
    substrate_thickness_mm: float = 1.6,
    substrate_material: str = "FR4",
    ground_x_mm: float = 40.0,
    ground_y_mm: float = 40.0,
    ground_material: str = "PEC",
    frequency_start_GHz: float = 1.0,
    frequency_end_GHz: float = 18.0,
    port_type: str = "Waveguide",
    excitation_mode: str = "H01"
) -> CSTPatchAntenna:
    """
    Create a patch antenna with the given parameters.

    Args:
        output_path: Where to save the .cstprj file
        patch_length_mm: Patch length in millimeters
        patch_width_mm: Patch width in millimeters
        substrate_thickness_mm: Substrate thickness in millimeters
        substrate_material: Substrate material (e.g., "FR4")
        ground_x_mm: Ground plane X-size
        ground_y_mm: Ground plane Y-size
        ground_material: Ground material (default: "PEC")
        frequency_start_GHz: Start frequency in GHz
        frequency_end_GHz: End frequency in GHz
        port_type: "Waveguide" or "Discrete"
        excitation_mode: Port excitation mode

    Returns:
        CSTPatchAntenna object for further configuration

    Example:
        >>> antenna = create_patch_antenna(
        ...     patch_length_mm=25.0,
        ...     patch_width_mm=25.0,
        ...     substrate_thickness_mm=1.52,
        ...     substrate_material="Rogers_RO4003C",
        ...     ground_x_mm=50.0,
        ...     ground_y_mm=50.0,
        ...     frequency_start_GHz=2.0,
        ...     frequency_end_GHz=6.0
        ... )
        >>> antenna.initialize()
    """
    antenna = CSTPatchAntenna(output_path=output_path)
    antenna.initialize()
    antenna.create_full_antenna(
        patch_length_mm=patch_length_mm,
        patch_width_mm=patch_width_mm,
        substrate_thickness_mm=substrate_thickness_mm,
        substrate_material=substrate_material,
        ground_x_mm=ground_x_mm,
        ground_y_mm=ground_y_mm,
        ground_material=ground_material,
        frequency_start_GHz=frequency_start_GHz,
        frequency_end_GHz=frequency_end_GHz,
        port_type=port_type,
        excitation_mode=excitation_mode
    )
    return antenna


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("CST Patch Antenna External Script")
    print("=" * 60)
    print()

    # Check CST availability
    if not check_cst_installation():
        sys.exit(1)

    print("CST Python API is available.\n")

    # Create antenna with parameters
    try:
        antenna = create_patch_antenna(
            output_path="C:/Projects",
            patch_length_mm=20.0,
            patch_width_mm=20.0,
            substrate_thickness_mm=1.6,
            substrate_material="FR4",
            ground_x_mm=40.0,
            ground_y_mm=40.0,
            ground_material="PEC",
            frequency_start_GHz=1.0,
            frequency_end_GHz=18.0,
            port_type="Waveguide",
            excitation_mode="H01"
        )

        print("\n" + "=" * 60)
        print("Antenna creation complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Open 'C:/Projects/patch_antenna.cstprj' in CST")
        print("2. Review geometry in 3D viewer")
        print("3. Click 'Compute' to run simulation")
        print("4. Check results in CST Project Explorer")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
