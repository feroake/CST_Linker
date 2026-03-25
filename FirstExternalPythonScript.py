# cst.interface gives us access to CST's Python methods for controlling a project
import cst.interface

# Initiate a DesignEnvironment class object that provides a connection/interface to the CST
# Studio Suite GUI/Frontend
cst_de = cst.interface.DesignEnvironment()

# Create a new High Frequency 3D project using Microwave Studio 
mws_prj = cst_de.new_mws()

#Save the simulation project to specified directory
my_path = r"C:\Users\Avinash\Documents\CST_Stuff\external"
mws_prj.save(my_path, allow_overwrite=True)

# Define the Brick using the commands from CST's History List
history_list = f"""
With Brick
     .Reset 
     .Name "solid1" 
     .Component "component1" 
     .Material "PEC" 
     .Xrange "-5", "5" 
     .Yrange "-5", "5" 
     .Zrange "-5", "5" 
     .Create
End With 
"""

#Write the Brick command to the History List of the active simulation project
mws_prj.model3d.add_to_history(f"Python: My First Brick Command", history_list)

#Save the simulation project
mws_prj.save(my_path, allow_overwrite=True)