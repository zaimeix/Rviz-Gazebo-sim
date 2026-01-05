from ament_index_python.packages import get_package_share_directory

PKG_NAME = 'waikato_robot_sim_moveit'
PKG_SHARE = get_package_share_directory(PKG_NAME)


# for different robot, here are description related setup
# this is the name in the robot description
ROBOT_NAME = 'so101_follower'
ROBOT_DSCRPT_PKG_NAME = 'so101_follower_description'
ROBOT_DSCRPT_FILE_NAME = 'so101_follower_gz.urdf.xacro'

# following config setup is generated from the above robot description
# configuration folder name must be "config"
# MoveitConfigsBuilder hardcodes the configuration path as .../config/
ROBOT_CONFIG_FOLDER_NAME = 'config'
# the main xacro needs to bechanged by following the example file
ROBOT_CONFIG_MAIN_XACRO_NAME = 'so101_follower_gz.urdf.xacro'
ROBOT_CONFIG_CONTROL_XACRO_NAME = 'so101_follower_gz.ros2_control.xacro'
ROBOT_CONFIG_CONTROL_YAML_NAME = 'ros2_controllers_gz.yaml'
# you need to change the name in xxx.ros2_control.xacro file as following name
ROBOT_CONFIG_CONTROL_MACRO_NAME = 'waikato_robot_control'