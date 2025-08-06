import sys
import os
import importlib.util

# Define the path to the target main.py file
target_main_path = os.path.join(
    os.path.dirname(__file__), 
    'research-analysis', 
    'vehical_analysis_by_state', 
    'main.py'
)

# Load the module from the specific file path
spec = importlib.util.spec_from_file_location("vehical_analysis_main", target_main_path)
vehical_analysis_module = importlib.util.module_from_spec(spec) # type: ignore
spec.loader.exec_module(vehical_analysis_module) # type: ignore

def app():
    vehical_analysis_module.main()
    
if __name__ == "__main__":
    app()