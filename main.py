# This is a python script which is gonna be used to spin up multiple containers for ROS Simulations.
# The invoking of the script is going to be done with the following syntax "python3 main.py -w <world_name> -n <number of robots> -p <array of N tuples for the positions>

import datetime
import os
import subprocess

def configure_containers(containers, world, number, positions):
    """
    Configure the containers for the simulation.
    
    Args:
        containers (list): List to store container configurations.
        world (str): Name of the world to simulate.
        number (int): Number of robots to simulate.
        positions (list): List of positions for the robots.
    """
    gz_container = {
        'service_name': 'gazebo_node',
        'name': 'gz_server',
        'image': 'thdhyan/gz_server:latest',
        'command': f"""
            source /opt/ros/humble/setup.bash && 
            source /ros2_ws/install/setup.bash && 
            ros2 launch gazebo_node gazebo.launch.py {world} && 
            tail -f /dev/null
        """,
    }
    containers.append(gz_container)
    
def run_containers(containers):
    """
    Run the containers using Docker Compose.
    
    Args:
        containers (list): List of container configurations.
    """
    docker_compose_file = "docker-compose.yml"
    base_file = "base_docker_compose.yml"
    
    # Read current runnig index from runs.txt
    with open('runs/runs.txt', 'rw') as f:
        lines = f.readlines()
        # Set the date and time to be run id  and write it to the file
        run_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        f.write(run_id)
        # also write the world name, number of robots and poses to file
        world_name = containers[0]['command'].split(' ')[-1]
        number_of_robots = len(containers) - 1
        f.write(world_name)
        f.write(str(number_of_robots))      
            
    
    with open(docker_compose_file, 'w') as f:
        f.write("version: '3.8'\n")
        
        # Write the base docker compose file
        with open(base_file, 'r') as base_f:
            f.write(base_f.read())
        
        f.write("services:\n")

        # Write the container configurations
        for container in containers:
            f.write(f"  {container['service_name']}:\n")
            f.write(f"    container_name: {container['name']}\n")
            f.write(f"    image: {container['image']}\n")
            f.write(f"    command: {container['command']}\n")
    command = ["docker-compose", "-f", docker_compose_file, "up"]
    
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

    args = parser.parse_args()

    # Validate positions
    if len(args.positions) != args.number * 3:
        raise ValueError("Number of positions must be twice the number of robots (x, y pairs).")

    # Gazebo container    
    docker_compose_dir = "runs/"
    
    containers = []
    
    configure_containers(containers, args.world, args.number, args.positions)

    #  Create the docker compose file
    
    docker_compose_file = f"{docker_compose_dir}docker-compose.yml"
    
    
    
    # Execute the command
    subprocess.run(command)

if __name__ == "__main__":
    main()