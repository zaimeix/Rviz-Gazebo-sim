from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_move_group_launch
from launch_ros.parameter_descriptions import ParameterValue

import os
import sys
sys.path.append(os.path.dirname(__file__))
import common

def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(common.ROBOT_NAME, package_name=common.PKG_NAME).to_moveit_configs()
    # Force use_sim_time = true
    moveit_config.moveit_cpp.update({"use_sim_time": ParameterValue(True, value_type=bool)})
    moveit_config.robot_description_semantic["use_sim_time"] = True
    moveit_config.robot_description_kinematics["use_sim_time"] = True

    return generate_move_group_launch(moveit_config)
