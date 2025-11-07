import subprocess
import time
import sys
import tempfile
import os

def get_wsl_distros():
    """Gets the list of installed WSL distributions."""
    try:
        # Added encoding 'utf-16-le' which is what wsl -l -q often outputs.
        # Added .replace('\x00', '') to strip null characters which cause issues.
        result = subprocess.run(
            ["wsl", "-l", "-q"],
            capture_output=True,
            text=True,
            encoding='utf-16-le'
        )
        lines = result.stdout.strip().replace('\x00', '').split('\n')
        distros = [line.strip() for line in lines if line.strip() and '\x00' not in line]
        if not distros:
            # Fallback for other encodings
            result = subprocess.run(
                ["wsl", "-l", "-q"],
                capture_output=True,
                text=True
            )
            lines = result.stdout.strip().split('\n')
            distros = [line.strip() for line in lines if line.strip()]

        return distros
    except FileNotFoundError:
        print("Error: `wsl` command not found. Please ensure WSL is installed and in your PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"Error getting WSL distributions: {e}")
        print("Please ensure WSL is installed and `wsl -l -q` runs correctly in your terminal.")
        sys.exit(1)

def select_distro(distros):
    """Prompts user to select a WSL distribution."""
    print("\nAvailable WSL distributions:")
    for i, distro in enumerate(distros, 1):
        print(f"[{i}] {distro}")

    while True:
        try:
            selection_input = input(f"\nEnter the number of the distribution to use (1-{len(distros)}): ")
            selection = int(selection_input)
            if 1 <= selection <= len(distros):
                return distros[selection - 1]
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(distros)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(0)

def get_wsl_users(distro):
    """Gets the list of 'real' users (UID 0 or >= 1000) from the selected WSL distribution."""
    print(f"\nDetecting users in {distro}...")
    
    # FIX: We must escape the dollar signs ($) for bash by using \\$ in the Python string.
    # This prevents 'bash -c' from trying to expand $3 and $1 as shell variables.
    awk_command = "awk -F: '(\\$3 >= 1000 || \\$3 == 0) && \\$1 != \"nobody\" {print \\$1}' /etc/passwd"
    
    try:
        # We pass the awk_command directly to 'bash -c'
        result = subprocess.run(
            ["wsl", "-d", distro, "--", "bash", "-c", awk_command],
            capture_output=True,
            text=True,
            encoding='utf-8', # Standard output from bash should be utf-8
            timeout=10, # Add a 10-second timeout
            stdin=subprocess.DEVNULL # Don't wait for stdin
        )
        if result.stderr:
            # Don't treat it as a fatal error, but show the message.
            print(f"Warning detecting users: {result.stderr.strip()}")
            # Continue, as awk might still have outputted something
            
        lines = result.stdout.strip().split('\n')
        users = [line.strip() for line in lines if line.strip()]
        
        if not users and result.stderr:
             print(f"Could not detect users. Raw error: {result.stderr.strip()}")
             print("Please ensure awk is installed in your WSL distro.")
             return []

        return users
    except subprocess.TimeoutExpired:
        print(f"Error: The command to detect users in {distro} timed out (10s).")
        print("This may be an issue with WSL. Please try restarting your computer or WSL (`wsl --shutdown`).")
        sys.exit(1)
    except Exception as e:
        print(f"Error running WSL command to get users: {e}")
        sys.exit(1)

def select_user(users):
    """Prompts user to select a WSL user from a list."""
    print("\nAvailable users found:")
    for i, user in enumerate(users, 1):
        print(f"[{i}] {user}")

    while True:
        try:
            selection_input = input(f"\nEnter the number of the user to run as (1-{len(users)}): ")
            selection = int(selection_input)
            if 1 <= selection <= len(users):
                return users[selection - 1]
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(users)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(0)

def read_commands(filename):
    """Reads commands from a file."""
    try:
        with open(filename, 'r') as f:
            commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return commands
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        print("Please make sure the file exists in the same directory as the script.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def get_user_inputs():
    """Gets command file and delay from user."""
    command_file = input("\nEnter the name of the command file (default: commands.txt): ").strip()
    if not command_file:
        command_file = "commands.txt"

    while True:
        try:
            delay_input = input("Enter the delay in seconds between commands (default: 3): ").strip()
            delay = int(delay_input) if delay_input else 3
            if delay < 0:
                print("Delay must be non-negative.")
                continue
            return command_file, delay
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(0)

def execute_command_in_tab(distro, wsl_username, command, is_first=False):
    """
    Executes a command in a Windows Terminal tab as a specific user.
    Uses a temporary script file to avoid argument parsing issues and
    uses 'bash -i' to ensure the user's .bashrc is loaded.
    """

    # Create a temporary script file in Windows temp directory with Unix line endings
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False, dir=os.environ.get('TEMP'), newline='\n') as f:
            script_content = f"""#!/bin/bash
# The '-i' flag used to launch this script should load .bashrc
# Go to the user's home directory
cd ~

# Run the command
{command}

# Keep the shell open for interaction
echo ""
echo "-------------------------------------------------------------------"
echo "Command completed. Press Ctrl+D to close or continue using the shell."
echo "-------------------------------------------------------------------"
exec bash
"""
            f.write(script_content)
            temp_script_path = f.name

    except Exception as e:
        print(f"Error: Could not create temporary script file: {e}")
        return False

    # Convert Windows path (like 'C:\Users\...\temp.sh') to WSL path (like '/mnt/c/Users/.../temp.sh')
    wsl_script_path = temp_script_path.replace('\\', '/').replace(':', '', 1)
    wsl_script_path = f"/mnt/{wsl_script_path[0].lower()}{wsl_script_path[1:]}"

    # Build the Windows Terminal command
    # This now includes '-u {wsl_username}' to run as the correct user
    wt_cmd_base = ['wt']
    if is_first:
        # Create new window, new tab
        wt_cmd_args = ['-w', '-1', 'nt']
    else:
        # Use existing window, add new tab
        wt_cmd_args = ['-w', '0', 'nt']

    # Add the WSL command part
    # We use 'bash -i' (interactive) to force loading .bashrc and the PATH
    wsl_cmd = [
        'wsl', '-d', distro,
        '-u', wsl_username,
        'bash', '-i', wsl_script_path
    ]

    wt_cmd = wt_cmd_base + wt_cmd_args + wsl_cmd

    # DEBUG: Print the exact command being executed
    # print(f"DEBUG: Executing command (as list):")
    # print(f"  {' '.join(wt_cmd)}")
    # print(f"  Temp Script Path (Windows): {temp_script_path}")
    # print(f"  Temp Script Path (WSL):     {wsl_script_path}")
    # print()

    try:
        # Use Popen to launch the command in a new, detached process
        subprocess.Popen(
            wt_cmd,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except FileNotFoundError:
        print("Error: `wt` (Windows Terminal) command not found.")
        print("Please ensure Windows Terminal is installed and in your PATH.")
        return False
    except Exception as e:
        print(f"Error executing command: {e}")
        # Clean up the temp file on error
        try:
            os.unlink(temp_script_path)
        except:
            pass # Ignore cleanup errors
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("WSL Command Runner - Windows Terminal Edition")
    print("=" * 60)

    # Get WSL distributions
    distros = get_wsl_distros()
    if not distros:
        print("Error: No WSL distributions found.")
        print("Please ensure WSL is installed and you have at least one distro.")
        sys.exit(1)

    # Select distribution
    selected_distro = select_distro(distros)
    print(f"\nSelected distribution: {selected_distro}")

    # --- NEW SECTION: Get the WSL username ---
    users = get_wsl_users(selected_distro)
    if not users:
        print(f"Error: No valid users found in {selected_distro}.")
        print("A valid user (like 'root' or a user with UID >= 1000) must exist.")
        sys.exit(1)
    
    wsl_username = select_user(users)
    print(f"\nWill run commands as user: {wsl_username}")
    # --- END NEW SECTION ---

    # Get user inputs (file and delay)
    command_file, delay = get_user_inputs()

    # Read commands
    commands = read_commands(command_file)
    if not commands:
        print(f"No valid commands found in {command_file}.")
        sys.exit(1)

    print(f"\nFound {len(commands)} command(s) to execute.")
    print(f"Delay between commands: {delay} second(s)")
    print("\nStarting execution in 3 seconds...")
    time.sleep(3)

    # Execute commands
    for i, command in enumerate(commands, 1):
        is_first = (i == 1)
        print(f"[{i}/{len(commands)}] Launching command: {command}")

        # Pass the wsl_username to the function
        if execute_command_in_tab(selected_distro, wsl_username, command, is_first):
            if i < len(commands):
                # Wait before next command (but not after the last one)
                print(f"    ... waiting {delay} second(s)...")
                time.sleep(delay)
        else:
            print(f"Failed to launch command: {command}")
            response = input("Continue with remaining commands? (y/n): ").strip().lower()
            if response != 'y':
                print("Stopping execution.")
                break

    print("\n" + "=" * 60)
    print("Execution complete!")
    print("Note: Temporary script files are left in your Temp folder.")
    print(r"(Usually C:\Users\YourUser\AppData\Local\Temp)")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)

