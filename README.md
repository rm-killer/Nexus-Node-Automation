# Nexus Node Multi-Launcher

This script automates the process of running multiple Nexus nodes, each in its own tab within the Windows Terminal. It is designed for Windows users who are running Nexus nodes in a WSL (Windows Subsystem for Linux) environment.

---

## Prerequisites

Before you begin, you will need to have the following installed and configured:

1.  **WSL and Ubuntu:** This script requires a WSL environment with Ubuntu installed.
    *   **Guide:** [Ubuntu and WSL instalation](https://github.com/rm-killer/WSL-Ubuntu-Installation-Guide)

2.  **Nexus Node:** You must have the Nexus node software installed and configured within your Ubuntu environment.
    *   **Guide:** `[Link to your Nexus Node installation guide]`

3.  **Python:** You will need Python installed on your Windows system to run the script.
    *   [Download Python](https://www.python.org/downloads/)
    *   **Important:** During installation, make sure to check the box that says **"Add Python to PATH"**.

4.  **Windows Terminal:** The script is designed to work with the Windows Terminal, which is usually pre-installed on modern versions of Windows. If you don't have it, you can get it here:
    *   [Install Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701)

## How to Download

1.  Go to the main page of this repository on GitHub.
2.  Click the green **<> Code** button.
3.  Click **Download ZIP**.
4.  Extract the ZIP file to a location of your choice on your computer.

## How to Use

1.  **Add your node commands to the `commands_list.txt` file.** Open the `commands_list.txt` file and add your `nexus-network start` commands. Each line in this file represents a new Nexus node that will be launched in its own terminal tab.

    For example:
    ```
    nexus-network start --node-id "YOUR_NODE_ID_1"
    nexus-network start --node-id "YOUR_NODE_ID_2"
    ```
    Replace `"YOUR_NODE_ID_1"`, `"YOUR_NODE_ID_2"`, etc., with your actual Nexus node IDs.

2.  **Open PowerShell or Command Prompt** in the folder where you extracted the files.

3.  **Run the script:**
    ```powershell
    python nexus_multinode_runner.py
    ```

4.  **Follow the on-screen prompts.** The script will ask you to select your WSL distribution and the user you want to run the commands as.
