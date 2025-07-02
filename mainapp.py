import psutil
import asyncio
import platform
import os
import datetime
import subprocess

from textual.app import App, ComposeResult, on
from textual.widgets import Header, Footer, Static, Button, Input, RichLog
from textual.containers import VerticalScroll, Horizontal, Container
from textual.reactive import reactive


class Dashboard(App):
    """A Textual app for monitoring and quick access to a secure VM."""

    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("q", "quit", "Quit app"),
        ("s", "suspend", "Suspend to shell"),
    ]

    cpu_percent = reactive(0.0)
    mem_percent = reactive(0.0)
    disk_percent = reactive(0.0)
    top_dirs_info = reactive("")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app's UI."""
        yield Header()
        with Horizontal():
            with VerticalScroll(id="left-panel"):
                yield Container(
                    Static("[bold blue]VM Status[/bold blue]", classes="panel-title"),
                    Static(f"CPU: [green]{self.cpu_percent:.1f}%[/green]", id="cpu-info"),
                    Static(f"Memory: [green]{self.mem_percent:.1f}%[/green] used", id="mem-info"),
                    Static(f"Disk (Root): [green]{self.disk_percent:.1f}%[/green] used", id="disk-info"),
                    id="system-metrics-container",
                    classes="functional-panel"
                )

                self.aide_output = RichLog(wrap=True, auto_scroll=True, id="aide-log", markup=True)
                yield Container(
                    Static("[bold blue]AIDE Actions[/bold blue]", classes="panel-title"),
                    Button("Run AIDE Check", id="aide-check", variant="primary"),
                    self.aide_output,
                    id="aide-operations-container",
                    classes="functional-panel"
                )

            with VerticalScroll(id="right-panel"):
                yield Container(
                    Static("[bold blue]File System Info[/bold blue]", classes="panel-title"),
                    Static("Loading file system info...", id="top-dirs-display"),
                    id="disk-overview-container",
                    classes="functional-panel"
                )

                self.terminal_log = RichLog(wrap=True, auto_scroll=True, id="terminal-log", markup=True)
                yield Container(
                    Static("[bold blue]Command Runner[/bold blue]", classes="panel-title"),
                    Input(placeholder="Enter non-interactive command (e.g., ls, df, whoami)", id="terminal-input"),
                    self.terminal_log,
                    id="command-runner-container",
                    classes="functional-panel"
                )

        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted and ready."""
        self.set_interval(2, self.update_system_info)
        self.set_interval(10, self.update_file_system_info)

        self.update_system_info()
        self.update_file_system_info()
        self.terminal_log.write("[green]Welcome to the Secure VM Dashboard![/green]")
        self.terminal_log.write("[dim]Type a non-interactive command and press Enter.[/dim]")
        self.terminal_log.write("[dim]For interactive commands (e.g., nano, top), press 's' to suspend this app (then 'fg' to return).[/dim]")
        self.terminal_log.write("[dim]Alternatively, open a new SSH session to the VM for a separate terminal.[/dim]")
        self.aide_output.write("[dim]AIDE status and results will appear here.[/dim]")

    def update_system_info(self) -> None:
        """Updates the system information display using psutil."""
        self.cpu_percent = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        self.mem_percent = mem.percent
        disk = psutil.disk_usage('/')
        self.disk_percent = disk.percent

        self.query_one("#cpu-info", Static).update(f"CPU: [green]{self.cpu_percent:.1f}%[/green]")
        self.query_one("#mem-info", Static).update(
            f"Memory: [green]{self.mem_percent:.1f}%[/green] used "
            f"({mem.used / (1024**3):.1f}GB / {mem.total / (1024**3):.1f}GB)"
        )
        self.query_one("#disk-info", Static).update(
            f"Disk (Root): [green]{self.disk_percent:.1f}%[/green] used "
            f"({disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB)"
        )

    def update_file_system_info(self) -> None:
        """Collects and displays info about top-level directories."""
        path = "/"
        try:
            proc = subprocess.run(
                ["sudo", "du", "-sh", *[os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))][:10]],
                capture_output=True, text=True, check=False
            )
            output = proc.stdout
            if proc.stderr:
                output += f"\n[red]Error collecting sizes: {proc.stderr.strip()}[/red]"

            lines = output.splitlines()
            display_lines = [line for line in lines if not "Permission denied" in line]

            if not display_lines:
                display_lines = ["[dim]No accessible directories or data or permission denied for all.[/dim]"]

            self.query_one("#top-dirs-display", Static).update(
                f"[bold cyan]Top Directories in {path}:[/bold cyan]\n" + "\n".join(display_lines)
            )
        except Exception as e:
            self.query_one("#top-dirs-display", Static).update(f"[red]Error getting directory info: {e}[/red]")


    @on(Button.Pressed)
    async def handle_button_pressed(self, event: Button.Pressed) -> None:
        """Handles button presses for AIDE actions."""
        if event.button.id == "aide-check":
            self.aide_output.write(f"[yellow]Triggering AIDE check at {datetime.datetime.now().strftime('%H:%M:%S')}...[/yellow]")
            await self._run_aide_command("sudo aide --check")

    async def _run_aide_command(self, command: str) -> None:
        """Internal helper to run AIDE commands and display output, with improved exit code handling."""
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            self.aide_output.write(stdout.decode('utf-8'))
        if stderr:
            self.aide_output.write(f"[red]{stderr.decode('utf-8')}[/red]")

        if process.returncode == 0:
            self.aide_output.write(f"[green]AIDE command completed successfully (Exit Code 0).[/green]")
        elif process.returncode == 5:
            self.aide_output.write(f"[bold yellow]AIDE command completed with warnings/changes detected (Exit Code 5).[/bold yellow]")
            self.aide_output.write("[dim]This usually means AIDE found integrity violations or legitimate changes.[/dim]")
        else:
            self.aide_output.write(f"[bold red]AIDE command failed with unexpected exit code {process.returncode}.[/bold red]")
            self.aide_output.write("[dim]Please check the output above for more details.[/dim]")
        self.aide_output.scroll_end()

    @on(Input.Submitted, "#terminal-input")
    async def handle_command_input(self, event: Input.Submitted) -> None:
        """Handles commands submitted in the interactive terminal."""
        command = event.value.strip()
        if not command:
            return

        self.query_one("#terminal-input", Input).value = ""

        self.terminal_log.write(f"[bold magenta]@[/bold magenta] [green]$ {command}[/green]")

        await self._run_command_in_terminal(command)

    async def _run_command_in_terminal(self, command: str) -> None:
        """Internal helper to run a generic command in the terminal log."""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if stdout:
                self.terminal_log.write(stdout.decode('utf-8'))
            if stderr:
                self.terminal_log.write(f"[red]{stderr.decode('utf-8')}[/red]")

            if process.returncode != 0:
                self.terminal_log.write(f"[red]Command exited with code {process.returncode}[/red]")

        except FileNotFoundError:
            self.terminal_log.write(f"[red]Error: Command not found: '{command}'[/red]")
        except Exception as e:
            self.terminal_log.write(f"[red]Error executing command: {e}[/red]")

        self.terminal_log.scroll_end()

    def action_quit(self) -> None:
        """An action to quit the application."""
        self.exit()

    def action_suspend(self) -> None:
        """Suspend the application and return to the shell."""
        self.console.log("[bold yellow]App suspended. Type 'fg' and press Enter to return.[/bold yellow]")
        self.bell()
        self.suspend()


if __name__ == "__main__":
    app = Dashboard()
    app.run()
