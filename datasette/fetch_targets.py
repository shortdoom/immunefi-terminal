import subprocess
import os

def execute_git_pull(projects_directory):
    os.chdir(projects_directory)

    result = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)

    if "Already up to date." not in result.stdout:
        print("Updates found.")
        print(result.stdout)
        execute_load_targets()
    else:
        print("No updates found.")

def execute_load_targets():
    os.chdir(datasette_directory)
    subprocess.run(['python3', 'load_targets.py'])

# Specify the directory
# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory of the current directory
parent_directory = os.path.dirname(current_directory)

# Define the datasette and projects directories
datasette_directory = current_directory
projects_directory = os.path.join(parent_directory, 'targets')

# Execute the git pull command in the specified directory
execute_git_pull(projects_directory)