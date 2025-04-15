# This is a python script which is gonna be used to spin up multiple containers for ROS Simulations.
# The invoking of the script is going to be done with the following syntax "python3 main.py -w <world_name> -n <number of robots> -p <array of N tuples for the positions>

import datetime
import os
import subprocess
# Read kwargs in the function

def configure_containers(containers, world, number, positions, **kwargs):
    """
    Configure the containers for the simulation.
    
    Args:
        containers (list): List to store container configurations.
        world (str): Name of the world to simulate.
        number (int): Number of robots to simulate.
        positions (list): List of positions for the robots.
        **kwargs: Additional arguments for configuration.
    """
    # Get rviz args
    rviz = kwargs.get('rviz', 'false')
    gz_container = {
        'service_name': 'gazebo_node',
        'name': 'gz_server',
        'image': 'thdhyan/gazebo:latest',
        'command': f"""
            source /opt/ros/humble/setup.bash && 
            source /ros2_ws/install/setup.bash && 
            ros2 launch gazebo_node gazebo.launch.py world_name:={world} && 
            tail -f /dev/null
        """,
    }
    
    containers.append(gz_container)
    for i in range(number):
        container = {
            'service_name': f'robot_{i}',
            'name': f'robot_{i}',
            'image': 'thdhyan/robot_node:latest',
            'command': f"""
                source /opt/ros/humble/setup.bash && 
                source /ros2_ws/install/setup.bash && 
                ros2 launch robot_node spawn_robot.launch.py x_pose:={positions[i*3]} y:={positions[i*3+1]} z:={positions[i*3+2]}  use_rviz:={bool(rviz)}&& 
                tail -f /dev/null
            """,
        }
        containers.append(container)
    yolo_container = {
        'service_name': 'yolo_node',
        'name': 'yolo_node',
        'image': 'thdhyan/vision_ros:latest',
        'command': f"""
              source install/setup.bash &&
              ros2 launch yolo_bringup yolov8.launch.py input_image_topic:=/camera/image_raw &&
              tail -f /dev/null
        """,
        # 'entrypoint': ["/bin/bash", "-c", ""],
    }
    containers.append(yolo_container)
    
    explore_container = {
        'service_name': 'explore_node',
        'name': 'explore_node',
        'image': 'thdhyan/explore_node:latest',
        'command': f"""
            source /opt/ros/humble/setup.bash && 
            source /ros2_ws/install/setup.bash && 
            ros2 launch explore_node explore.launch.py explore_strategy:={kwargs.get('explore', 'random')}&& 
            tail -f /dev/null
        """,
    }
    
def run_containers(containers):
    """
    Run the containers using Docker Compose.
    
    Args:
        containers (list): List of container configurations.
    """
    base_file = "base-docker-compose.yaml"
    
    # Read current runnig index from runs.txt
    if not os.path.exists(base_file):
        with open(base_file, 'w') as f:
            f.write("\n")
    if os.path.exists('runs.txt'):
        with open('runs.txt', 'r') as f:
            lines = f.readlines()
            # Set the date and time to be run id  and write it to the file
            run_id = lines[0].strip()
    else:
        # If the file doesn't exist, create it and set the date and time to be run id
        # and write it to the file
        with open('runs.txt', 'w') as f:
            f.write("\n")
        
        run_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
    with open('runs.txt', 'r+') as f:
        lines = f.readlines()
        # Set the date and time to be run id  and write it to the file
        run_id = "current"
        # also write the world name, number of robots and poses to file
        world_name = containers[0]['command'].split(' ')[-1]
        number_of_robots = len(containers) - 1
        f.write(world_name)
        f.write(str(number_of_robots))      
            
    
    docker_compose_file = run_id+".docker-compose.yaml"

    
    with open(docker_compose_file, 'w') as f:
        f.write("version: '3.8'\n")
        # Write the base docker compose file
        with open(base_file, 'r') as base_f:
            f.write(base_f.read())
            
        
        f.write("\nservices:\n")

        # Write the container configurations
        for container in containers:
            f.write(f"  {container['service_name']}:\n")
            f.write(f"    <<: *common-config \n")
            f.write(f"    container_name: {container['name']}\n")
            f.write(f"    image: {container['image']}\n")
            f.write(f"    command: > \n")
            f.write(f"      bash -c '{container['command']}'\n")
            if 'entrypoint' in container:
                f.write(f"    entrypoint: {container['entrypoint']}\n")
        
        # print(container['command'])
            
    command = ["docker","compose", "-f", docker_compose_file, "up", "-d",]
    
    # Execute the command
    subprocess.run(command)
    


def main():
    
    import argparse
    import subprocess

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Spin up multiple containers for ROS Simulations.")
    parser.add_argument("-w", "--world", required=True, help="Name of the world to simulate.")
    parser.add_argument("-n", "--number", type=int, required=True, help="Number of robots to simulate.")
    parser.add_argument("-p", "--positions", nargs='+', required=True, help="List of positions for the robots.")
    parser.add_argument("-r", "--rviz", required=True, help="USE Rviz or not.")
    parser.add_argument("-e", "--explore", required=True, help="Exploration strategy to use.")

    args = parser.parse_args()

    # Validate positions
    if len(args.positions) != args.number * 3:
        raise ValueError("Number of positions must be twice the number of robots (x, y pairs).")

    # Gazebo container    
    docker_compose_dir = "runs/"
    
    containers = []
    
    configure_containers(containers, args.world, args.number, args.positions, rviz = args.rviz, explore = args.explore)
        
    run_containers(containers)
    
    
    
    # Execute the command
    # subprocess.run(command)

if __name__ == "__main__":
    main()