# Nexus Node Automation Scripts

This repository contains a tool to solve the problem of automatically running multiple Nexus node commands from a text file, each in its own persistent terminal tab.

---

## Windows Python Runner

This tool uses a Python script to control the **Windows Terminal** directly, creating a new *visual, mouse-clickable tab* for each command.

### Features
*   Runs on Windows.
*   Automatically detects your installed WSL distributions (e.g., Ubuntu).
*   Automatically detects all "real" users in that WSL distro (`root`, `rm`, etc.).
*   Asks you to select the Distro and User from a menu.
*   Asks for a delay between launching nodes.
*   Creates a new, graphical Windows Terminal tab for each command.

### Setup
**1.** You must have [Python](https://www.python.org/) installed on Windows.
**2.** You must have the [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701) installed.
**3.** Place your commands in the `commands.txt` file in this folder (one per line).

### How to Run
**1.** Open PowerShell or Command Prompt.
**2.** Navigate to this folder: `cd windows-python-runner`
**3.** Run the script:
    ```powershell
    python run_commands.py
    ```
**4.** Follow the on-screen prompts.
