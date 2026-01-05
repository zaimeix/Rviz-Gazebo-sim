from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_rsp_launch

import os
import sys
sys.path.append(os.path.dirname(__file__))
import common

def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(common.ROBOT_NAME, package_name=common.PKG_NAME).to_moveit_configs()
    return generate_rsp_launch(moveit_config)
