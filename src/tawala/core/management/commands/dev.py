"""Management command: dev"""

from enum import IntEnum
from typing import Any

from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import (
    Command as RunserverCommand,
)
from django.core.management.base import CommandParser


class TerminalSize(IntEnum):
    """Terminal size threshold for ASCII art."""

    THRESHOLD = 60


class Command(RunserverCommand):
    """Tawala development server."""

    help = "Tawala development server"

    # Declare parent class attributes for type checking
    _raw_ipv6: bool
    addr: str
    port: str
    protocol: str
    use_ipv6: bool
    version: str = getattr(settings, "TAWALA_VERSION", "X.X.X")

    def add_arguments(self, parser: CommandParser):
        """Add custom arguments to the command."""
        super().add_arguments(parser)
        parser.add_argument(
            "--no-clipboard",
            action="store_true",
            help="Disable copying the server URL to clipboard",
        )

    def handle(self, *args: object, **options: Any) -> str | None:
        """Handle the dev command."""
        self.no_clipboard = options.get("no_clipboard", False)
        return super().handle(*args, **options)

    def check_migrations(self):
        """
        * OVERRIDDEN - django.core.management.base.BaseCommand.check_migrations
        Print a warning if the set of migrations on disk don't match the
        migrations in the database.
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
        """Custom server startup message."""
        self._print_startup_banner()
        self._print_server_info(server_port)

        if not self.no_clipboard:
            self._copy_to_clipboard(server_port)

        self.stdout.write("")  # spacing

    def _print_startup_banner(self) -> None:
        """Print ASCII banner based on terminal width."""
        import shutil

        self.stdout.write(self.style.SUCCESS("\n✨ Starting dev server...") + "\n")

        terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns

        if terminal_width >= TerminalSize.THRESHOLD:
            art_lines = [
                "",
                "  ████████╗ █████╗ ██╗    ██╗ █████╗ ██╗      █████╗ ",
                "  ╚══██╔══╝██╔══██╗██║    ██║██╔══██╗██║     ██╔══██╗",
                "     ██║   ███████║██║ █╗ ██║███████║██║     ███████║",
                "     ██║   ██╔══██║██║███╗██║██╔══██║██║     ██╔══██║",
                "     ██║   ██║  ██║╚███╔███╔╝██║  ██║███████╗██║  ██║",
                "     ╚═╝   ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝",
                "",
                "        ██████╗ ███████╗██╗   ██╗",
                "        ██╔══██╗██╔════╝██║   ██║",
                "        ██║  ██║█████╗  ██║   ██║",
                "        ██║  ██║██╔══╝  ╚██╗ ██╔╝",
                "        ██████╔╝███████╗ ╚████╔╝ ",
                "        ╚═════╝ ╚══════╝  ╚═══╝  ",
                "",
            ]
        else:
            art_lines = [
                "",
                "  ▀█▀ ▄▀█ █░█░█ ▄▀█ █░░ ▄▀█",
                "  ░█░ █▀█ ▀▄▀▄▀ █▀█ █▄▄ █▀█",
                "",
                "       █▀▄ █▀▀ █░█",
                "       █▄▀ ██▄ ▀▄▀",
                "",
            ]

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
        """Print server and version info."""
        from django.utils import timezone

        tz = timezone.get_current_timezone()
        now = timezone.localtime(timezone.now(), timezone=tz)
        timestamp = now.strftime("%B %d, %Y - %X")
        tz_name = now.strftime("%Z")

        if tz_name:
            self.stdout.write(
                f"\n  📅 Date: {self.style.HTTP_NOT_MODIFIED(timestamp)} ({tz_name})"
            )
        else:
            self.stdout.write(f"\n  📅 Date: {self.style.HTTP_NOT_MODIFIED(timestamp)}")

        self.stdout.write(
            f"  🔧 Tawala version: {self.style.HTTP_NOT_MODIFIED(self.version)}"
        )

        addr = self._format_address()
        url = f"{self.protocol}://{addr}:{server_port}/"
        self.stdout.write(f"  🌐 Local address:   {self.style.SUCCESS(url)}")

        if self.addr == "0" or self.addr == "0.0.0.0":
            self._print_network_url(server_port)

    def _format_address(self) -> str:
        """Format address display."""
        if self._raw_ipv6:
            return f"[{self.addr}]"
        elif self.addr == "0":
            return "0.0.0.0"
        else:
            return self.addr

    def _print_network_url(self, server_port: int) -> None:
        """Print LAN IP if possible."""
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
        """Copy URL to clipboard."""
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
