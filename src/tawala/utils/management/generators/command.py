"""Base command generator for Tawala management commands.

Provides a reusable framework for creating management commands that execute
a series of configured commands with consistent output formatting and error handling.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


@dataclass
class CommandResult:
    """Result of executing a single command.

    Attributes:
        command: The command that was executed.
        success: Whether the command executed successfully.
        error: Error message if the command failed, None otherwise.
    """

    command: str
    success: bool
    error: str | None = None


class CommandOutput(ABC):
    """Base class for command process output handling.

    Defines the interface for displaying command process information,
    progress, and results. Subclasses can implement different output strategies.
    """

    def __init__(self, command: BaseCommand) -> None:
        """Initialize the output handler with a command reference.

        Args:
            command: The parent Command instance for stdout/styling.
        """
        self.command = command

    @abstractmethod
    def print_header(self, command_count: int, dry_run: bool, mode: str) -> None:
        """Print the command process header.

        Args:
            command_count: Number of commands to execute.
            dry_run: Whether running in dry-run mode.
            mode: The mode of operation (e.g., 'BUILD', 'INSTALL').
        """
        pass

    @abstractmethod
    def print_no_commands_error(self, mode: str) -> None:
        """Print error message when no commands are configured.

        Args:
            mode: The mode of operation (e.g., 'build', 'install').
        """
        pass

    @abstractmethod
    def print_dry_run_preview(self, commands: list[str]) -> None:
        """Print the dry-run preview of all commands.

        Args:
            commands: List of commands to preview.
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
        """Print the command process summary.

        Args:
            total: The total number of commands.
            completed: Number of successfully completed commands.
            failed: Number of failed commands.
        """
        pass


class CommandExecutor:
    """Executor for running commands.

    Handles parsing and execution of individual commands,
    including error handling and result tracking.
    """

    def __init__(self, command: BaseCommand) -> None:
        """Initialize the command executor.

        Args:
            command: The parent Command instance.
        """
        self.command = command

    def execute(self, cmd: str) -> CommandResult:
        """Execute a single command.

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


class CommandProcess:
    """Orchestrator for the command execution process.

    Coordinates command execution, output handling, and process flow.
    Manages the overall workflow including dry-run and actual execution.

    Attributes:
        command: The parent Command instance.
        output: The output handler for displaying information.
        executor: The command executor for running commands.
        mode: The mode of operation (e.g., 'BUILD', 'INSTALL').
    """

    def __init__(
        self,
        command: BaseCommand,
        output: CommandOutput,
        executor: CommandExecutor,
        mode: str,
    ) -> None:
        """Initialize the command process.

        Args:
            command: The parent Command instance.
            output: The output handler for displaying information.
            executor: The command executor for running commands.
            mode: The mode of operation (e.g., 'BUILD', 'INSTALL').
        """
        self.command = command
        self.output = output
        self.executor = executor
        self.mode = mode

    def run(self, commands: list[str], dry_run: bool = False) -> None:
        """Run the command process.

        Args:
            commands: List of commands to execute.
            dry_run: If True, show commands without executing them.
        """
        self.output.print_header(len(commands), dry_run, self.mode)

        if dry_run:
            self.output.print_dry_run_preview(commands)
            return

        self._execute_commands(commands)

    def _execute_commands(self, commands: list[str]) -> None:
        """Execute all commands sequentially.

        Args:
            commands: List of commands to execute.
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


class CommandGenerator(ABC):
    """Base generator for creating command execution processes.

    Provides a template for building management commands that execute
    a series of configured commands with consistent behavior.
    """

    def __init__(self, django_command: BaseCommand) -> None:
        """Initialize the command generator.

        Args:
            django_command: The Django BaseCommand instance.
        """
        self.django_command = django_command

    @abstractmethod
    def get_commands_from_settings(self) -> list[str]:
        """Retrieve commands from Django settings.

        Returns:
            List of command strings to execute.
        """
        pass

    @abstractmethod
    def create_output_handler(self) -> CommandOutput:
        """Create the output handler for the command process.

        Returns:
            An instance of CommandOutput for handling display.
        """
        pass

    @abstractmethod
    def get_mode(self) -> str:
        """Get the mode identifier for this command process.

        Returns:
            A string identifier like 'BUILD' or 'INSTALL'.
        """
        pass

    def generate(self, dry_run: bool = False) -> None:
        """Generate and execute the command process.

        Args:
            dry_run: If True, show commands without executing them.
        """
        commands = self.get_commands_from_settings()

        if not commands:
            output = self.create_output_handler()
            output.print_no_commands_error(self.get_mode().lower())
            return

        # Initialize components
        output = self.create_output_handler()
        executor = CommandExecutor(self.django_command)
        process = CommandProcess(self.django_command, output, executor, self.get_mode())

        # Run the process
        process.run(commands, dry_run=dry_run)
