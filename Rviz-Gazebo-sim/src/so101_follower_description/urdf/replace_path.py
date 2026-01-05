#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory

# File to fix
file_original = "so101_follower.urdf.xacro"
file_new = "so101_follower_new.urdf.xacro"
package_name = "so101_follower_description"

# Read file
with open(file_original, 'r') as f:
    content = f.read()

# Get package path and replace
package_path = get_package_share_directory(package_name)
content = content.replace(f'package://{package_name}/', f'file://{package_path}/')

# Write back
with open(file_new, 'w') as f:
    f.write(content)

print(f"Fixed paths in {file_new}")
