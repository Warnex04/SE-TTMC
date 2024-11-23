import os
import xml.etree.ElementTree as ET
import json
from collections import defaultdict

def parse_sbc_files(directory, block_data):
    """
    Recursively parses all .sbc files in the given directory and extracts block names, grid sizes, and component costs.
    
    Args:
        directory (str): Path to the directory containing .sbc files.
        block_data (dict): Dictionary to store block data.
    """
    # Walk through the directory
    for root_dir, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".sbc"):
                file_path = os.path.join(root_dir, file)
                try:
                    # Parse the XML file
                    tree = ET.parse(file_path)
                    root = tree.getroot()

                    # Extract blocks and components
                    for block in root.findall(".//Definition"):
                        block_name = block.find("DisplayName").text if block.find("DisplayName") is not None else "Unknown"
                        cube_size = block.find("CubeSize").text if block.find("CubeSize") is not None else "Unknown"
                        components = block.find("Components")

                        # Skip if no components are found
                        if components is not None:
                            # Store components as a list of dictionaries
                            component_list = []
                            for component in components.findall("Component"):
                                component_name = component.get("Subtype")
                                component_count = component.get("Count")
                                component_list.append({
                                    "Component Name": component_name,
                                    "Component Count": int(component_count) if component_count else 0
                                })

                            # Organize data by block name and grid size
                            if block_name not in block_data:
                                block_data[block_name] = {}
                            block_data[block_name][cube_size] = component_list

                except Exception as e:
                    print(f"Error parsing file {file_path}: {e}")

# Initialize a dictionary to store block data
block_data = {}

# Directories to parse
modded_directory = "data/modded/rebels-games-modded-blocks"
vanilla_directory = "data/vanilla"

# Parse modded and vanilla directories
parse_sbc_files(modded_directory, block_data)
parse_sbc_files(vanilla_directory, block_data)

# Save the data to a JSON file
output_json = "parsed_block_data.json"
with open(output_json, "w") as f:
    json.dump(block_data, f, indent=4)

print(f"Data successfully saved to {output_json}")
