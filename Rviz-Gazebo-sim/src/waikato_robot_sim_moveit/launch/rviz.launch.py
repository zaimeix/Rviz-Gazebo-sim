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

import os
import sys
sys.path.append(os.path.dirname(__file__))
import common

'''
joints_state_publisher will publish all joints' state.
if joints controller is split into 2, such as manipulator and gripper controller, 
moveit cannot descide which controller group the action should be directed.
So remove the gripper controller.
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
    kkkk

    robot_description_content = Command([
        FindExecutable(name='xacro'),
        ' ',
        PathJoinSubstitution([
            FindPackageShare(common.PKG_NAME),
            robot_cfg_name,
            "so101_follower.urdf.xacro"
        ]),
        ' initial_positions_file:=',
        PathJoinSubstitution([
            FindPackageShare(common.PKG_NAME),
            robot_cfg_name,
            "initial_positions.yaml"
        ])
    ])

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
    pkg_my_so101_moveit = FindPackageShare(common.PKG_NAME)

    # Robot State Publisher
    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                pkg_my_so101_moveit,
                "launch",
                "rsp.launch.py"
            ])
        ]),
        launch_arguments={
            "use_sim_time": use_sim_time,
        }.items(),
    )
    
    # Spawn robot - delayed
    robot_urdf = PathJoinSubstitution([
        FindPackageShare("so101_follower_description"),
        "urdf",
        "so101_follower_new.urdf.tmp"
    ])

    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", "so101_follower",
            #"-topic", "robot_description_content",
            "-file", robot_urdf,
            "-x", "0.0", "-y", "0.0", "-z", "0.1",
        ],
        output="screen",
    )

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            {"robot_description": ParameterValue(robot_description_content, value_type=str)},
            PathJoinSubstitution([
                    FindPackageShare("my_so101_moveit"),
                    "config",
                    "ros2_controllers.yaml"
            ])
        ],
        output="screen"
    )
    
    '''
    # Controller manager - delayed
    controller_manager = TimerAction(
        period=6.0,
        actions=[
            Node(
                package="controller_manager",
                executable="ros2_control_node",
                parameters=[
                    PathJoinSubstitution([
                        pkg_my_so101_moveit,
                        "config",
                        "ros2_controllers.yaml"
                    ]),
                    {"use_sim_time": use_sim_time}
                ],
                output="screen",
            )
        ]
    )
    '''
    # Spawn controllers with proper timing - DUAL CONTROLLER APPROACH
    spawn_joint_state_broadcaster = TimerAction(
        period=9.0,
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
        period=11.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=["manipulator_controller", "-c", "/controller_manager"],
                output="screen",
            )
        ]
    )
    
    spawn_gripper_controller = TimerAction(
        period=13.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=["gripper_controller", "-c", "/controller_manager"],
                output="screen",
            )
        ]
    )
    
    # MoveGroup - delayed to ensure controllers are ready
    move_group = TimerAction(
        period=15.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        pkg_my_so101_moveit,
                        "launch", 
                        "move_group.launch.py"
                    ])
                ]),
                launch_arguments={
                    "use_sim_time": use_sim_time,
                }.items(),
            )
        ]
    )
    
    # RViz2 - delayed
    rviz_node = TimerAction(
        period=17.0,
        actions=[
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                output="log",
                arguments=["-d", PathJoinSubstitution([
                    pkg_my_so101_moveit, "config", "moveit.rviz"
                ])],
                parameters=[{"use_sim_time": use_sim_time}],
            )
        ]
    )
    
    # Static TF
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=["0", "0", "0", "0", "0", "0", "world", "base_link"],
        parameters=[{"use_sim_time": use_sim_time}],
    )

    return LaunchDescription([
        *declared_arguments,
        robot_state_publisher,
        static_tf,
        spawn_entity,
        controller_manager,
        spawn_joint_state_broadcaster,
        spawn_manipulator_controller,
        #spawn_gripper_controller,
        move_group,
        rviz_node,
    ])
    
