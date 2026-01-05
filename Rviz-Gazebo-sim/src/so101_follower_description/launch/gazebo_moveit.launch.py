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

def generate_launch_description():
    package_path = get_package_share_directory("so101_follower_description")
    print(f"✓ Package found at: {package_path}")
    meshes_path = os.path.join(package_path, "meshes")
    print(f"✓ Meshes directory exists")
    mesh_files = [f for f in os.listdir(meshes_path) if f.endswith('.stl')]
    print(f"✓ Found {len(mesh_files)} STL files")

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

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("ros_gz_sim"),
                "launch",
                "ros_gz_sim.launch.py"  # Combined server + client
            ])
        ]),
        launch_arguments={
            "gz_args": "-r empty.sdf",  # Gazebo finds this via its resource paths
            "use_sim_time": use_sim_time,
        }.items(),
    )

    # Spawn robot - delayed
    robot_urdf = PathJoinSubstitution([
        FindPackageShare("so101_follower_description"),
        "urdf",
        "so101_follower_new.urdf.tmp"
    ])

    spawn_entity = TimerAction(
        period=3.0,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="spawn_entity.py",
                arguments=[
                    "-entity", "so101_follower",
                    "-file", robot_urdf,
                    "-x", "0.0", "-y", "0.0", "-z", "0.1",
                ],
                output="screen",
            )
        ]
    )


    return LaunchDescription([
        *declared_arguments,
        gazebo,
        spawn_entity,
    ])

