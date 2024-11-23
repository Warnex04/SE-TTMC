import xml.etree.ElementTree as ET
import json
from collections import defaultdict

# Refined normalization function
def normalize_block_name_advanced(name):
    """
    Normalize block names by:
    - Stripping LargeBlock/SmallBlock prefixes
    - Removing size descriptors (e.g., 'large', 'small')
    - Removing underscores ('_') and spaces for uniformity
    """
    if not name:
        return ""
    name = name.lower()
    name = name.replace("largeblock", "").replace("smallblock", "")  # Remove grid-specific prefixes
    name = name.replace("large", "").replace("small", "")  # Remove size descriptors
    name = name.replace(" ", "")  # Remove underscores and spaces
    return name

# Load the block data from JSON
with open('parsed_block_data.json', 'r') as json_file:
    block_data = json.load(json_file)

# Parse the blueprint XML file
blueprint_file_path = 'Blueprints_cloud_Warnex LGMiner_bp.sbc'
tree = ET.parse(blueprint_file_path)
root = tree.getroot()

# Prepare data structures
blueprint_blocks = defaultdict(int)
total_components = defaultdict(int)
unmatched_blocks = []

# Extract blocks from the blueprint
for block in root.findall(".//MyObjectBuilder_CubeBlock"):
    block_name = block.find("SubtypeName").text
    if block_name is not None:
        normalized_name = normalize_block_name_advanced(block_name)
        blueprint_blocks[normalized_name] += 1

# Match blocks and calculate components
for normalized_name, count in blueprint_blocks.items():
    matched = False
    for json_block_name, json_block_data in block_data.items():
        if normalize_block_name_advanced(json_block_name) == normalized_name:
            matched = True
            components = json_block_data.get("Large", [])  # Assume "Large" grid by default
            for component in components:
                comp_name = component["Component Name"]
                comp_count = component["Component Count"] * count
                total_components[comp_name] += comp_count
            break
    if not matched:
        unmatched_blocks.append(normalized_name)

# Prepare results
blueprint_summary = {
    "Total unique block types": len(blueprint_blocks),
    "Total matched block types": len([name for name in blueprint_blocks if name not in unmatched_blocks]),
    "Total unmatched block types": len(unmatched_blocks),
    "Total component count": sum(total_components.values()),
}

# Print results
print("Blueprint Summary:")
print(blueprint_summary)

print("\nUnmatched Blocks After Additional Normalization:")
for block in unmatched_blocks:
    print(block)

print("\nTotal Components:")
for comp_name, comp_count in total_components.items():
    print(f"{comp_name}: {comp_count}")
