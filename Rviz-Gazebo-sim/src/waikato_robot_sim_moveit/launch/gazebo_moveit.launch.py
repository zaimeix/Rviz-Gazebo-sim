from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from launch.actions import LogInfo
from launch.actions import ExecuteProcess
from launch.actions import SetEnvironmentVariable
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import FindExecutable
from launch import LaunchContext
import xacro

import os
import sys
sys.path.append(os.path.dirname(__file__))
import common

'''
since gazebo controller conflicts with controlle_manager,
the original controller_manager should be removed when starting gazebo controller.
and, due to gazebo uses different hardware interface, a set of seperate controller 
interface description is used.
'''

def generate_launch_description():
    robot_name = common.ROBOT_NAME

    robot_description_pkg_name = common.ROBOT_DSCRPT_PKG_NAME
    robot_description_file_name = common.ROBOT_DSCRPT_FILE_NAME

    robot_cfg_path = common.ROBOT_CONFIG_FOLDER_NAME
    robot_cfg_main_xacro_name = common.ROBOT_CONFIG_MAIN_XACRO_NAME
    robot_cfg_ros2_ctl_xacro_name = common.ROBOT_CONFIG_CONTROL_XACRO_NAME
    robot_cfg_controller_yaml_name = common.ROBOT_CONFIG_CONTROL_YAML_NAME
    robot_cfg_control_macro_name = common.ROBOT_CONFIG_CONTROL_MACRO_NAME

    pkg_name = common.PKG_NAME

    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation clock",
        )
    )
    
    use_sim_time = LaunchConfiguration("use_sim_time")
    pkg_share = FindPackageShare(pkg_name)
    
    initial_positions_file = PathJoinSubstitution([
        pkg_share,
        robot_cfg_path,
        "initial_positions.yaml"
    ])
    
    robot_description_file = PathJoinSubstitution([
        FindPackageShare(robot_description_pkg_name), 
        "urdf",
        robot_description_file_name
    ])
    
    xacro_file = PathJoinSubstitution([
        pkg_share,
        robot_cfg_path, 
        robot_cfg_main_xacro_name
    ])

    control_xacro_file = PathJoinSubstitution([
        pkg_share,
        robot_cfg_path, 
        robot_cfg_ros2_ctl_xacro_name
    ])

    control_yaml_file = PathJoinSubstitution([
        pkg_share,
        robot_cfg_path, 
        robot_cfg_controller_yaml_name
    ])

    launch_moveit_file = PathJoinSubstitution([
        pkg_share,
        "launch", 
        "move_group.launch.py"
    ])

    
    robot_description_content = ParameterValue(Command([
        'xacro ',
        xacro_file,
        ' robot_name:=', robot_name,
        ' robot_urdf_file:=', robot_description_file,
        ' robot_control_xacro_file:=', control_xacro_file,
        ' robot_control_yaml_file:=', control_yaml_file,
        ' control_macro_name:=', robot_cfg_control_macro_name,
        ' initial_positions_file:=', initial_positions_file,
    ]),value_type=str)
    
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': use_sim_time,
            'publish_frequency': 50.0
        }]
    )
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("gazebo_ros"), 
                "launch", 
                "gazebo.launch.py"  # Combined server + client
            ])
        ]),
        launch_arguments={
            "world": PathJoinSubstitution([
                FindPackageShare("gazebo_ros"), 
                "worlds", 
                "empty.world"
            ]),
            "verbose": "true",
            "use_sim_time": use_sim_time,
        }.items(),
    )

    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=["0", "0", "0", "0", "0", "0", "world", "base_link"],
        parameters=[{"use_sim_time": use_sim_time}],
    )

    gazebo_spawn_entity = TimerAction(
        period=4.0,
        actions=[
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=[
                    "-entity", robot_name,
                    "-topic", "robot_description",
                    "-x", "0.0", "-y", "0.0", "-z", "0.1",
                ],
                output="screen",
            )
        ]
    )

    spawn_joint_state_broadcaster = TimerAction(
        period=6.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=["joint_state_broadcaster", "-c", "/controller_manager"],
                output="screen",
            )
        ]
    )

    spawn_manipulator_controller = TimerAction(
        period=8.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=["manipulator_controller", "-c", "/controller_manager"],
                output="screen",
            )
        ]
    )

    move_group = TimerAction(
        period=10.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    launch_moveit_file
                ]),
                launch_arguments={
                    "use_sim_time": use_sim_time,
                }.items(),
            )
        ]
    )
    
    rviz_node = TimerAction(
        period=12.0,
        actions=[
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                output="log",
                arguments=["-d", PathJoinSubstitution([
                    FindPackageShare(pkg_name), robot_cfg_path, "moveit.rviz"
                ])],
                parameters=[{"use_sim_time": use_sim_time}],
            )
        ]
    )

    return LaunchDescription([
        *declared_arguments,
        robot_state_publisher,
        gazebo,
        static_tf,
        gazebo_spawn_entity,
        spawn_joint_state_broadcaster,
        spawn_manipulator_controller,
        move_group,
        rviz_node,
    ])