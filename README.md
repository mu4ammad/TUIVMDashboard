Secure Enclave Dashboard (TUI VM Dashboard)

![image](https://github.com/user-attachments/assets/88bd2613-0640-4af6-9046-1ae243ea9a5e)


The Secure Enclave Dashboard is a Textual User Interface (TUI) application designed to provide quick access and monitoring capabilities for secure Linux Virtual Machines (VMs), particularly useful in High-Performance Computing (HPC) research environments like REU programs. It consolidates critical system information and security checks into a user-friendly, interactive terminal interface.
Features

    Real-time System Metrics: Displays live CPU, Memory, and Disk (root partition) utilization.

    AIDE File Integrity Monitoring: Provides a quick button to trigger aide --check (Advanced Intrusion Detection Environment) scans and displays the detailed output, including clear indicators for changes detected.

    Non-Interactive Command Runner: Allows users to execute common shell commands (e.g., ls, df, whoami) directly within the dashboard and view their output.

    Interactive Shell Access: Supports suspending the dashboard to access a full, interactive shell for complex tasks (e.g., nano, top), with easy resumption.

    Clean & Responsive Design: Utilizes Textual's powerful TUI capabilities for a modern, high-contrast, and organized interface within any standard terminal.

    System-Wide Deployment: Designed to be installed once on the VM and accessible to multiple authorized users.

Motivation

Traditional SSH command-line interfaces can be daunting for quick status checks or routine security verifications. This dashboard aims to enhance the user experience by providing an intuitive, centralized "single pane of glass" for essential VM monitoring and security operations, aligning with best practices for secure computing environments.
Deployment & Installation

For a comprehensive, step-by-step guide on how to deploy this dashboard on a Linux VM, please refer to the Secure Enclave Dashboard - General Deployment Playbook.

Key steps covered in the playbook include:

    System preparation (installing Python, pip, build tools).

    Deploying the application code and assets to a shared system location (/opt/dashboard_app).

    Setting up a dedicated Python virtual environment for dependencies.

    Configuring sudoers to allow passwordless execution of aide --check for specific users (essential for preventing dashboard hangs).

    Creating a system-wide wrapper script (dashboard) for easy launch.

Important Security Note: This dashboard is intended for monitoring and specific, controlled actions. It is crucial to follow the sudoers configuration precisely as outlined in the playbook to maintain system security and adhere to the principle of least privilege. Specifically, aide --update functionality is intentionally excluded from the dashboard due to its security implications.
Basic Usage

Once deployed, any authorized user can launch the dashboard from their SSH terminal.

    Launch the Dashboard:

    dashboard

    The TUI will launch in full screen.

    Navigate:

        Use Tab and Shift+Tab to move between interactive elements (buttons, input fields).

        Use Up/Down arrow keys within logs or input fields.

    Run AIDE Check:

        Navigate to the "Run AIDE Check" button and press Enter.

        Output will appear in the "AIDE Operations" log.

    Execute Commands:

        Navigate to the "Command Runner" input field.

        Type a non-interactive command (e.g., ls -l, df -h, whoami).

        Press Enter. Output will display in the "Command Runner" log.

    Suspend to Shell (for interactive commands like nano or top):

        Press the s key.

        The dashboard will suspend, and you'll return to your regular shell prompt.

        Run your interactive command.

        When finished, type fg (for foreground) and press Enter to return to the dashboard.

    Quit the Dashboard:

        Press the q key.

        The dashboard will exit, and your SSH session will close.

Security Considerations

This dashboard is designed with security in mind for a secure enclave environment:

    Least Privilege: Only aide --check is allowed passwordless via sudo, not aide --update or ALL commands.

    Non-Interactive Commands: The built-in command runner is limited to non-interactive commands to prevent terminal conflicts and reduce the attack surface.

    Centralized Deployment: The application code and virtual environment are stored in a root-owned, read-only accessible system directory (/opt/dashboard_app) to prevent unauthorized modification.

    SSH Gated: Access to the dashboard is inherently protected by the VM's SSH authentication.

Credits

    Developed as part of an REU program for HPC research.

    Built using the Textual TUI framework and psutil.

License

This project is open-source and available under the MIT License.
