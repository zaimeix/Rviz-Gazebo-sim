#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory

# File to fix
sdf_file = "so101_follower.urdf.tmp"
package_name = "so101_follower_description"
sdf_file_new = "so101_follower_new.urdf.tmp"

# Read file
with open(sdf_file, 'r') as f:
    content = f.read()

# Get package path and replace
package_path = get_package_share_directory(package_name)
content = content.replace(f'model://{package_name}/', f'file://{package_path}/')

# Write back
with open(sdf_file_new, 'w') as f:
    f.write(content)

print(f"Fixed paths in {sdf_file_new}")
