import subprocess
import os

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# Change directory
os.chdir('pycefr')

# Run dict.py
print("Running dict.py...")
run_command("python3 dict.py")

# Run pycerfl.py
print("Running pycerfl.py...")
run_command("python3 pycerfl.py directory ../PythonFiles/pydriller")

print("Script execution completed.")