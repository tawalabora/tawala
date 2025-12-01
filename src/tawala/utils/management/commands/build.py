"""Management command: build

Executes build commands defined in Tawala settings.
Supports dry-run mode for previewing commands before execution
and continues running remaining commands even if one fails.

Example:
    tawala build
    tawala build --dry-run
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError, CommandParser

from ..arts import get_build_art
from ..enums import TerminalSize


@dataclass
class CommandResult:
    """Result of executing a single build command.

    Attributes:
        command: The command that was executed.
        success: Whether the command executed successfully.
        error: Error message if the command failed, None otherwise.
    """

    command: str
    success: bool
    error: str | None = None


class BuildOutput(ABC):
    """Base class for build process output handling.

    Defines the interface for displaying build process information,
    progress, and results. Subclasses can implement different output strategies.
    """

    def __init__(self, command: "Command") -> None:
        """Initialize the output handler with a command reference.

        Args:
            command: The parent Command instance for stdout/styling.
        """
        self.command = command

    @abstractmethod
    def print_header(self, command_count: int, dry_run: bool) -> None:
        """Print the build process header.

        Args:
            command_count: Number of build commands to execute.
            dry_run: Whether running in dry-run mode.
        """
        pass

    @abstractmethod
    def print_no_commands_error(self) -> None:
        """Print error message when no build commands are configured."""
        pass

    @abstractmethod
    def print_dry_run_preview(self, commands: list[str]) -> None:
        """Print the dry-run preview of all build commands.

        Args:
            commands: List of build commands to preview.
        """
        pass

    @abstractmethod
    def print_command_header(self) -> None:
        """Print the command header before execution."""
        pass

    @abstractmethod
    def print_command_success(self, cmd: str, index: int, total: int) -> None:
        """Print successful command completion with progress bar.

        Args:
            cmd: The command that completed successfully.
            index: The current command index (1-based).
            total: The total number of commands.
        """
        pass

    @abstractmethod
    def print_command_failure(
        self, cmd: str, error: str, index: int, total: int
    ) -> None:
        """Print command failure information with progress bar.

        Args:
            cmd: The command that failed.
            error: The error message.
            index: The current command index (1-based).
            total: The total number of commands.
        """
        pass

    @abstractmethod
    def print_summary(self, total: int, completed: int, failed: int) -> None:
        """Print the build process summary.

        Args:
            total: The total number of commands.
            completed: Number of successfully completed commands.
            failed: Number of failed commands.
        """
        pass


class TawalaOutput(BuildOutput):
    """Tawala-themed build process output with ASCII art and emojis.

    Provides colorful, visually appealing output with progress bars,
    ASCII art, and strategic use of emojis and colors.
    """

    def print_header(self, command_count: int, dry_run: bool) -> None:
        """Print the build process header with ASCII art.

        Args:
            command_count: Number of build commands to execute.
            dry_run: Whether running in dry-run mode.
        """
        import shutil

        mode = "DRY RUN" if dry_run else "BUILD"
        self.command.stdout.write(
            self.command.style.SUCCESS(f"\n✨ Starting {mode.lower()} process...\n")
        )

        terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns
        art_lines = get_build_art(terminal_width)

        for line in art_lines:
            self.command.stdout.write(self.command.style.HTTP_INFO(line))

        if terminal_width >= TerminalSize.THRESHOLD:
            self.command.stdout.write(
                self.command.style.HTTP_INFO(f"              🔨  {mode} Process  🔨")
            )
            self.command.stdout.write(
                self.command.style.NOTICE(
                    f"           {command_count} command(s) to execute"
                )
            )
        else:
            self.command.stdout.write(
                self.command.style.HTTP_INFO(f"      🔨  {mode}  🔨")
            )
            self.command.stdout.write(
                self.command.style.NOTICE(f"    {command_count} command(s)")
            )

        self.command.stdout.write("")

    def print_no_commands_error(self) -> None:
        """Print error message when no build commands are configured."""
        self.command.stdout.write(
            self.command.style.ERROR("\n❌ No build commands configured!")
        )
        self.command.stdout.write(
            self.command.style.WARNING(
                "   Define build commands in your '.env' file or in pyproject.toml [tool.tawala] section:\n"
            )
        )
        self.command.stdout.write("")

    def print_dry_run_preview(self, commands: list[str]) -> None:
        """Print the dry-run preview of all build commands.

        Args:
            commands: List of build commands to preview.
        """
        self.command.stdout.write(
            self.command.style.NOTICE("Commands to be executed:\n")
        )

        for i, cmd in enumerate(commands, 1):
            self.command.stdout.write(
                f"  {self.command.style.NOTICE(f'[{i}]')} {self.command.style.HTTP_INFO(cmd)}"
            )

        self.command.stdout.write("")
        self.command.stdout.write(
            self.command.style.HTTP_NOT_MODIFIED(
                "✨ Use 'tawala build' to execute these commands"
            )
        )
        self.command.stdout.write("")

    def print_command_header(self) -> None:
        """Print the command header before execution.

        Args:
            cmd: The command being executed.
        """
        self.command.stdout.write(self.command.style.HTTP_NOT_MODIFIED("=" * 60 + "\n"))

    def print_command_success(self, cmd: str, index: int, total: int) -> None:
        """Print successful command completion with progress bar.

        Args:
            cmd: The command that completed successfully.
            index: The current command index (1-based).
            total: The total number of commands.
        """
        progress_bar = self._create_progress_bar(index, total)
        self.command.stdout.write(f"{progress_bar}")
        self.command.stdout.write(self.command.style.SUCCESS(f"✓ Completed: {cmd}"))
        self.command.stdout.write("")  # Add blank line after command output

    def print_command_failure(
        self, cmd: str, error: str, index: int, total: int
    ) -> None:
        """Print command failure information with progress bar.

        Args:
            cmd: The command that failed.
            error: The error message.
            index: The current command index (1-based).
            total: The total number of commands.
        """
        progress_bar = self._create_progress_bar(index, total)
        self.command.stdout.write(f"{progress_bar}")
        self.command.stdout.write(self.command.style.ERROR(f"✗ Failed: {cmd}"))
        self.command.stdout.write(self.command.style.ERROR(f"   Error: {error}"))
        self.command.stdout.write("")  # Add blank line after command output

    def print_summary(self, total: int, completed: int, failed: int) -> None:
        """Print the build process summary.

        Args:
            total: The total number of commands.
            completed: Number of successfully completed commands.
            failed: Number of failed commands.
        """
        self.command.stdout.write(self.command.style.HTTP_NOT_MODIFIED("=" * 60 + "\n"))
        if failed == 0:
            self.command.stdout.write(
                self.command.style.SUCCESS(
                    f"🎉 All {completed} command(s) completed successfully!"
                )
            )
        else:
            self.command.stdout.write(
                self.command.style.SUCCESS(
                    f"✓ {completed}/{total} command(s) completed"
                )
            )
            self.command.stdout.write(
                self.command.style.ERROR(f"✗ {failed}/{total} command(s) failed")
            )

        self.command.stdout.write("")

    def _create_progress_bar(self, current: int, total: int) -> str:
        """Create a visual progress bar for the build commands.

        Args:
            current: The current command index (1-based).
            total: The total number of commands.

        Returns:
            A formatted progress bar string.
        """
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        percentage = (current / total) * 100

        return (
            f"  [{bar}] "
            f"{self.command.style.HTTP_INFO(f'{current}/{total}')} "
            f"({self.command.style.NOTICE(f'{percentage:.0f}%')})"
        )


class CommandExecutor:
    """Executor for running build commands.

    Handles parsing and execution of individual build commands,
    including error handling and result tracking.
    """

    def __init__(self, command: "Command") -> None:
        """Initialize the command executor.

        Args:
            command: The parent Command instance.
        """
        self.command = command

    def execute(self, cmd: str) -> CommandResult:
        """Execute a single build command.

        Parses the command string, invokes the management command via call_command,
        and returns the result with any error information.

        Args:
            cmd: The command string to execute (e.g., 'collectstatic --noinput').

        Returns:
            CommandResult containing execution status and any error details.
        """
        try:
            # Validate and parse command
            parts: list[str] = cmd.strip().split()
            if not parts:
                return CommandResult(
                    command=cmd,
                    success=False,
                    error="Empty command string",
                )

            command_name: str = parts[0]
            command_args: list[str] = parts[1:]

            # Execute the management command
            call_command(command_name, *command_args)

            return CommandResult(command=cmd, success=True)
        except CommandError as e:
            return CommandResult(command=cmd, success=False, error=str(e))
        except (ValueError, OSError) as e:
            return CommandResult(command=cmd, success=False, error=str(e))


class BuildProcess:
    """Orchestrator for the build process.

    Coordinates command execution, output handling, and process flow.
    Manages the overall build workflow including dry-run and actual execution.

    Attributes:
        command: The parent Command instance.
        output: The output handler for displaying build information.
        executor: The command executor for running build commands.
    """

    def __init__(
        self,
        command: "Command",
        output: BuildOutput,
        executor: CommandExecutor,
    ) -> None:
        """Initialize the build process.

        Args:
            command: The parent Command instance.
            output: The output handler for displaying build information.
            executor: The command executor for running build commands.
        """
        self.command = command
        self.output = output
        self.executor = executor

    def run(self, commands: list[str], dry_run: bool = False) -> None:
        """Run the build process.

        Args:
            commands: List of build commands to execute.
            dry_run: If True, show commands without executing them.
        """
        self.output.print_header(len(commands), dry_run)

        if dry_run:
            self.output.print_dry_run_preview(commands)
            return

        self._execute_commands(commands)

    def _execute_commands(self, commands: list[str]) -> None:
        """Execute all build commands sequentially.

        Args:
            commands: List of build commands to execute.
        """
        total = len(commands)
        completed = 0
        failed = 0
        results: list[CommandResult] = []

        for i, cmd in enumerate(commands, 1):
            self.output.print_command_header()
            result = self.executor.execute(cmd)
            results.append(result)

            if result.success:
                self.output.print_command_success(cmd, i, total)
                completed += 1
            else:
                self.output.print_command_failure(
                    cmd, result.error or "Unknown error", i, total
                )
                failed += 1

        self.output.print_summary(total, completed, failed)


class Command(BaseCommand):
    """Tawala build command executor.

    Executes a series of build commands defined in Tawala settings or configuration.
    This command is useful for automating build processes such as collecting static
    files, compiling assets, running migrations, or any other build-related tasks.

    Features:
    - Execute multiple build commands in sequence
    - Dry-run mode to preview commands without execution
    - Error handling with continuation (remaining commands still run if one fails)
    - Colorful output with progress tracking
    - Creative ASCII art and progress visualization
    - Object-oriented architecture for extensibility

    Build commands should be defined in Tawala settings:

    Examples:
        # Execute all configured build commands
        tawala build

        # Preview commands without executing them
        tawala build --dry-run

        # Use from other management commands
        from django.core.management import call_command
        call_command('build')
        call_command('build', dry_run=True)
    """

    help = "Execute build commands"

    def add_arguments(self, parser: CommandParser) -> None:
        """Define command-line arguments.

        Args:
            parser: The argument parser to add arguments to.
        """
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show commands that would be executed without running them",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the build command execution.

        Retrieves build commands from Tawala settings, validates them, and either
        displays them (dry-run) or executes them sequentially. Continues execution
        even if individual commands fail.

        Args:
            *args: Unused positional arguments.
            **options: Command options including:
                - dry_run (bool): If True, show commands without executing.
        """
        dry_run: bool = options.get("dry_run", False)
        build_commands = getattr(settings, "COMMANDS_BUILD", [])

        if not build_commands:
            output = TawalaOutput(self)
            output.print_no_commands_error()
            return

        # Initialize components
        output = TawalaOutput(self)
        executor = CommandExecutor(self)
        process = BuildProcess(self, output, executor)

        # Run the build process
        process.run(build_commands, dry_run=dry_run)
