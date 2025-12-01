"""Management command: dev

Tawala development server with an enhanced user experience. Extends Django's
runserver command with ASCII art, formatted output, local/network URLs,
timezone information, and optional clipboard integration.

Example:
    tawala dev
    tawala dev 8001
    tawala dev --no-clipboard
    tawala dev 0.0.0.0:9000 --no-clipboard
"""

from typing import Any

from django.contrib.staticfiles.management.commands.runserver import (
    Command as RunserverCommand,
)
from django.core.management.base import CommandParser

from ..arts import get_dev_art
from ..enums import TerminalSize


class Command(RunserverCommand):
    """Tawala development server with enhanced UX.

    Extends Django's runserver command with the following features:
    - Colorful ASCII art banner
    - Server address and version information
    - Current date and timezone display
    - Local network address detection
    - Optional clipboard integration for server URL
    - Terminal-responsive output (adapts to terminal width)

    Attributes:
        help: Command description.
        _raw_ipv6: Whether the address is raw IPv6 format.
        addr: Server address.
        port: Server port.
        protocol: HTTP protocol (http/https).
        use_ipv6: Whether to use IPv6.
        no_clipboard: Whether to disable clipboard copying.

    Examples:
        # Start development server on default address
        tawala dev

        # Start on specific port
        tawala dev 8001

        # Disable clipboard copying
        tawala dev --no-clipboard

        # Start on specific address and port
        tawala dev 0.0.0.0:9000 --no-clipboard
    """

    help = "Tawala development server"

    # Declare parent class attributes for type checking
    _raw_ipv6: bool
    addr: str
    port: str
    protocol: str
    use_ipv6: bool

    def add_arguments(self, parser: CommandParser) -> None:
        """Add custom arguments to the command.

        Extends the parent runserver arguments with Tawala-specific options.

        Args:
            parser: The argument parser to add arguments to.
        """
        super().add_arguments(parser)
        parser.add_argument(
            "--no-clipboard",
            action="store_true",
            help="Disable copying the server URL to clipboard",
        )

    def handle(self, *args: object, **options: Any) -> str | None:
        """Handle the dev command execution.

        Processes command options and invokes the parent runserver command.

        Args:
            *args: Positional arguments from the command.
            **options: Command options including:
                - no_clipboard (bool): If True, skip clipboard copying.

        Returns:
            Result from parent command or None.
        """
        self.no_clipboard = options.get("no_clipboard", False)
        return super().handle(*args, **options)

    def check_migrations(self) -> None:
        """Check for unapplied migrations and display a warning.

        Overrides Django's default check_migrations to use 'tawala migrate'
        instead of 'python manage.py migrate' in the warning message.

        Prints a notice if there are unapplied migrations that could affect
        the project's functionality.
        """
        from django.core.exceptions import ImproperlyConfigured
        from django.db import DEFAULT_DB_ALIAS, connections
        from django.db.migrations.executor import MigrationExecutor

        try:
            executor = MigrationExecutor(connections[DEFAULT_DB_ALIAS])
        except ImproperlyConfigured:
            return

        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            apps_waiting_migration = sorted(
                {migration.app_label for migration, backwards in plan}  # type: ignore[reportUnusedVariable]
            )
            self.stdout.write(
                self.style.NOTICE(
                    "\nYou have %(unapplied_migration_count)s unapplied migration(s). "
                    "Your project may not work properly until you apply the "
                    "migrations for app(s): %(apps_waiting_migration)s."
                    % {
                        "unapplied_migration_count": len(plan),
                        "apps_waiting_migration": ", ".join(apps_waiting_migration),
                    }
                )
            )
            # This is the only overridden part. Replaced 'python manage.py migrate' with 'tawala migrate'
            self.stdout.write(self.style.NOTICE("Run 'tawala migrate' to apply them."))

    def on_bind(self, server_port: int) -> None:
        """Custom server startup message and initialization.

        Overrides Django's default on_bind to provide a custom startup
        banner, server information, and clipboard functionality.
        Called when the development server binds to a port. Displays startup
        banner, server information, and optionally copies the URL to clipboard.

        Args:
            server_port: The port the server is bound to.
        """
        self._print_startup_banner()
        self._print_server_info(server_port)

        if not self.no_clipboard:
            self._copy_to_clipboard(server_port)

        self.stdout.write("")  # spacing

    def _print_startup_banner(self) -> None:
        """Print ASCII banner based on terminal width.

        Displays either a full ASCII art banner or a compact version depending
        on whether the terminal is wide enough. Includes warning messages and
        control instructions appropriate for the terminal size.
        """
        import shutil

        self.stdout.write(self.style.SUCCESS("\n✨ Starting dev server...") + "\n")

        terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns
        art_lines = get_dev_art(terminal_width)

        for line in art_lines:
            self.stdout.write(self.style.HTTP_INFO(line))

        if terminal_width >= TerminalSize.THRESHOLD:
            self.stdout.write(
                self.style.HTTP_INFO("         🔥  Development Server  🔥")
            )
            self.stdout.write(
                self.style.WARNING("       ⚠️  Not suitable for production!  ⚠️")
            )
            self.stdout.write(self.style.NOTICE("             Press Ctrl-C to quit"))
        else:
            self.stdout.write(self.style.HTTP_INFO("    🔥  Dev Server  🔥"))
            self.stdout.write(self.style.WARNING("  ⚠️   Not for production! ⚠️"))
            self.stdout.write(self.style.NOTICE("       Ctrl-C to quit"))

        self.stdout.write("")

    def _print_server_info(self, server_port: int) -> None:
        """Print server and version information.

        Displays the current date/time with timezone, Tawala version,
        local server address, and network address (if applicable).

        Args:
            server_port: The port the server is bound to.
        """
        from django.conf import settings
        from django.utils import timezone

        tz = timezone.get_current_timezone()
        now = timezone.localtime(timezone.now(), timezone=tz)
        timestamp = now.strftime("%B %d, %Y - %X")
        tz_name = now.strftime("%Z")
        version = getattr(settings, "TAWALA_VERSION", "unknown")

        if tz_name:
            self.stdout.write(
                f"\n  📅 Date: {self.style.HTTP_NOT_MODIFIED(timestamp)} ({tz_name})"
            )
        else:
            self.stdout.write(f"\n  📅 Date: {self.style.HTTP_NOT_MODIFIED(timestamp)}")

        self.stdout.write(
            f"  🔧 Tawala version: {self.style.HTTP_NOT_MODIFIED(version)}"
        )

        addr = self._format_address()
        url = f"{self.protocol}://{addr}:{server_port}/"
        self.stdout.write(f"  🌐 Local address:   {self.style.SUCCESS(url)}")

        if self.addr == "0" or self.addr == "0.0.0.0":
            self._print_network_url(server_port)

    def _format_address(self) -> str:
        """Format address for display.

        Handles IPv6 addresses by wrapping them in brackets and formats
        0.0.0.0 for display.

        Returns:
            The formatted address string ready for display.
        """
        if self._raw_ipv6:
            return f"[{self.addr}]"
        elif self.addr == "0":
            return "0.0.0.0"
        else:
            return self.addr

    def _print_network_url(self, server_port: int) -> None:
        """Print LAN IP address if available.

        Attempts to determine the local network IP address and displays
        the network URL for accessing the dev server from other machines
        on the same network. Silently fails if the address cannot be determined.

        Args:
            server_port: The port the server is bound to.
        """
        import socket

        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            network_url = f"{self.protocol}://{local_ip}:{server_port}/"
            self.stdout.write(
                f"  🌍 Network address: {self.style.SUCCESS(network_url)}"
            )
        except socket.gaierror:
            pass

    def _copy_to_clipboard(self, server_port: int) -> None:
        """Copy server URL to clipboard.

        Attempts to copy the server URL to the system clipboard using pyperclip.
        Gracefully handles missing pyperclip or clipboard unavailability.

        Args:
            server_port: The port the server is bound to.
        """
        try:
            import pyperclip

            addr = self._format_address()
            url = f"{self.protocol}://{addr}:{server_port}/"

            pyperclip.copy(url)
            self.stdout.write(f"  📋 {self.style.SUCCESS('Copied to clipboard!')}")
        except ImportError:
            self.stdout.write(
                f"  📋 {self.style.WARNING('pyperclip not installed - skipping clipboard copy')}"
            )
        except Exception:
            pass
