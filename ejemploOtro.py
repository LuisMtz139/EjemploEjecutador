import os
import xml.etree.ElementTree as ET

# Parse the XML file
tree = ET.parse('config.xml')
root = tree.getroot()

# Get the path from the XML file
ruta = root.find('Ruta').text

# Create three folders in the specified path
for i in range(1, 4):
    # Construct the folder name
    folder_name = f"Folder{i}"
    # Construct the full folder path
    folder_path = os.path.join(ruta, folder_name)
    # Create the folder
    os.makedirs(folder_path, exist_ok=True)

print("Folders created successfully.")