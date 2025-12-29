"""
Management command for TailwindCSS CLI installation and build management.

This module provides a clean, OOP-based interface for:
- Installing the TailwindCSS CLI binary
- Building TailwindCSS output files
- Cleaning generated CSS files
"""

from pathlib import Path
from platform import machine, system
from stat import S_IXGRP, S_IXOTH, S_IXUSR
from subprocess import DEVNULL, CalledProcessError, run
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser


class PlatformInfo:
    """Encapsulates platform and architecture information."""

    PLATFORM_MAP = {
        "darwin": "macos",
        "linux": "linux",
        "windows": "windows",
    }

    ARCH_MAP = {
        "x86_64": "x64",
        "amd64": "x64",
        "x64": "x64",
        "arm64": "arm64",
        "aarch64": "arm64",
        "armv8": "arm64",
    }

    def __init__(self):
        self.os_name = self._detect_os()
        self.architecture = self._detect_architecture()

    def _detect_os(self) -> str:
        """Detect and validate the operating system."""
        system_platform = system().lower()
        platform_name = self.PLATFORM_MAP.get(system_platform)

        if not platform_name:
            raise CommandError(
                f"Unsupported operating system: {system_platform}. "
                f"Supported: {', '.join(self.PLATFORM_MAP.values())}"
            )

        return platform_name

    def _detect_architecture(self) -> str:
        """Detect and validate the system architecture."""
        machine_platform = machine().lower()
        architecture = self.ARCH_MAP.get(machine_platform)

        if not architecture:
            raise CommandError(
                f"Unsupported architecture: {machine_platform}. "
                f"Supported: {', '.join(set(self.ARCH_MAP.values()))}"
            )

        return architecture

    def __str__(self) -> str:
        return f"{self.os_name}-{self.architecture}"


class TailwindCSSDownloader:
    """Handles downloading and installation of TailwindCSS CLI."""

    BASE_URL = "https://github.com/tailwindlabs/tailwindcss/releases"

    def __init__(self, stdout_writer: Callable[[str], None], verbose: bool = True):
        self.write = stdout_writer
        self.verbose = verbose

    def get_download_url(self, version: str, platform: PlatformInfo) -> str:
        """Generate the download URL for the TailwindCSS CLI binary."""
        filename = self._get_filename(platform)
        return f"{self.BASE_URL}/download/{version}/{filename}"

    def _get_filename(self, platform: PlatformInfo) -> str:
        """Determine the appropriate filename based on platform."""
        if platform.os_name == "windows":
            return "tailwindcss-windows-x64.exe"
        elif platform.os_name == "linux":
            return f"tailwindcss-linux-{platform.architecture}"
        elif platform.os_name == "macos":
            return f"tailwindcss-macos-{platform.architecture}"
        else:
            raise CommandError(f"Unsupported platform: {platform.os_name}")

    def download(self, url: str, destination: Path, show_progress: bool = True) -> None:
        """Download a file from URL to destination with progress tracking."""
        temp_destination = destination.with_suffix(destination.suffix + ".tmp")

        try:
            if self.verbose:
                self.write(f"Downloading from: {url}")

            def progress_callback(block_num: int, block_size: int, total_size: int) -> None:
                if self.verbose and show_progress and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(100.0, (downloaded / total_size) * 100)
                    self.write(f"\rProgress: {percent:.1f}% ({downloaded}/{total_size} bytes)")

            urlretrieve(url, temp_destination, progress_callback)

            if self.verbose and show_progress:
                self.write("")

            temp_destination.rename(destination)
            if self.verbose:
                self.write(f"✓ Downloaded to: {destination}")

        except KeyboardInterrupt:
            self._cleanup_temp_file(temp_destination)
            if self.verbose:
                self.write("\nDownload cancelled by user.")
            raise CommandError("Installation aborted.")
        except HTTPError as e:
            self._cleanup_temp_file(temp_destination)
            raise CommandError(f"Failed to download from {url}. HTTP Error {e.code}: {e.reason}")
        except URLError as e:
            self._cleanup_temp_file(temp_destination)
            raise CommandError(f"Failed to download: {e.reason}")
        except Exception as e:
            self._cleanup_temp_file(temp_destination)
            raise CommandError(f"Download failed: {e}")

    @staticmethod
    def _cleanup_temp_file(temp_file: Path) -> None:
        """Remove temporary file if it exists."""
        if temp_file.exists():
            temp_file.unlink()

    @staticmethod
    def make_executable(file_path: Path) -> None:
        """Make the file executable on Unix-like systems."""
        if system().lower() != "windows":
            current_permissions = file_path.stat().st_mode
            file_path.chmod(current_permissions | S_IXUSR | S_IXGRP | S_IXOTH)


class InstallHandler:
    """Handles the installation of TailwindCSS CLI."""

    def __init__(
        self,
        config: dict[str, Any],
        stdout_writer: Callable[[str], None],
        style: Any,
        verbose: bool = True,
    ):
        self.config = config
        self.write = stdout_writer
        self.style = style
        self.verbose = verbose
        self.downloader = TailwindCSSDownloader(stdout_writer, verbose)

    def install(self, auto_confirm: bool = False, use_cache: bool = False) -> None:
        """Install the TailwindCSS CLI binary."""
        platform = PlatformInfo()
        if self.verbose:
            self._display_platform_info(platform)

        cli_path = self.config["CLI"]
        self._ensure_directory_exists(cli_path.parent)

        version = self.config["VERSION"]
        download_url = self.downloader.get_download_url(version, platform)

        if self.verbose:
            self._display_download_info(version, platform, cli_path, download_url)

        if self._should_use_cache(cli_path, use_cache):
            return

        if not self._handle_existing_file(cli_path, auto_confirm):
            return

        if not self._confirm_download(auto_confirm):
            return

        self._perform_installation(download_url, cli_path, version, platform)

    def _display_platform_info(self, platform: PlatformInfo) -> None:
        """Display detected platform information."""
        self.write(f"Detected platform: {self.style.SUCCESS(str(platform))}")

    def _ensure_directory_exists(self, directory: Path) -> None:
        """Ensure the target directory exists."""
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise CommandError(
                f"Permission denied: Cannot create directory at {directory}. "
                f"Ensure the path is writable."
            )

    def _display_download_info(
        self,
        version: str,
        platform: PlatformInfo,
        cli_path: Path,
        download_url: str,
    ) -> None:
        """Display download information to the user."""
        self.write("\nDownload Information:")
        self.write(f"  Version:     {version}")
        self.write(f"  Platform:    {platform}")
        self.write(f"  Destination: {cli_path}")
        self.write(f"  URL:         {download_url}\n")

    def _should_use_cache(self, cli_path: Path, use_cache: bool) -> bool:
        """Check if cached CLI should be used."""
        if cli_path.exists() and use_cache:
            if self.verbose:
                self.write(
                    self.style.HTTP_NOT_MODIFIED(
                        "\nUsing cached TailwindCSS CLI. Skipping download.\n"
                    )
                )
            return True
        return False

    def _handle_existing_file(self, cli_path: Path, auto_confirm: bool) -> bool:
        """Handle existing CLI file. Returns True if installation should continue."""
        if not cli_path.exists():
            return True

        if auto_confirm:
            cli_path.unlink()
            return True

        if self.verbose:
            self.write(self.style.WARNING(f"\n⚠ TailwindCSS CLI already exists at: {cli_path}"))
        overwrite = input("Overwrite? (y/N): ").strip().lower()

        if overwrite == "y":
            cli_path.unlink()
            return True

        if self.verbose:
            self.write("Installation cancelled.")
        return False

    def _confirm_download(self, auto_confirm: bool) -> bool:
        """Confirm download with user unless auto-confirmed."""
        if auto_confirm:
            return True

        confirm = input("\nProceed with download? (y/N): ").strip().lower()
        if confirm != "y":
            if self.verbose:
                self.write("Installation cancelled.")
            return False

        return True

    def _perform_installation(
        self,
        download_url: str,
        cli_path: Path,
        version: str,
        platform: PlatformInfo,
    ) -> None:
        """Download and install the TailwindCSS CLI."""
        self.downloader.download(download_url, cli_path)
        self.downloader.make_executable(cli_path)

        if self.verbose:
            self.write(
                self.style.SUCCESS(
                    f"\n✓ TailwindCSS CLI successfully installed at: {cli_path}\n"
                    f"  Platform: {platform}\n"
                    f"  Version: {version}"
                )
            )


class BuildHandler:
    """Handles building TailwindCSS output files."""

    def __init__(
        self,
        config: dict[str, Any],
        stdout_writer: Callable[[str], None],
        style: Any,
        verbose: bool = True,
    ):
        self.config = config
        self.write = stdout_writer
        self.style = style
        self.verbose = verbose

    def build(self) -> None:
        """Build the TailwindCSS output file."""
        cli_path = self.config["CLI"]
        source_css = self.config["SOURCE"]
        output_css = self.config["OUTPUT"]

        self._validate_source_file(source_css)
        self._ensure_output_directory(output_css.parent)

        command = self._build_command(cli_path, source_css, output_css)
        self._execute_build(command, cli_path)

    def _validate_source_file(self, source_css: Path) -> None:
        """Validate that the source CSS file exists."""
        if not (source_css.exists() and source_css.is_file()):
            raise CommandError(f"TailwindCSS source file not found: {source_css}")

    def _ensure_output_directory(self, output_dir: Path) -> None:
        """Ensure the output directory exists."""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise CommandError(
                f"Permission denied: Cannot create directory at {output_dir}. "
                f"Ensure the path is writable."
            )

    @staticmethod
    def _build_command(cli_path: Path, source_css: Path, output_css: Path) -> list[str]:
        """Build the TailwindCSS CLI command."""
        return [
            str(cli_path),
            "-i",
            str(source_css),
            "-o",
            str(output_css),
            "--minify",
        ]

    def _execute_build(self, command: list[str], cli_path: Path) -> None:
        """Execute the TailwindCSS build command."""
        try:
            if self.verbose:
                self.write("Building TailwindCSS output file...")
                run(command, check=True)
                self.write(self.style.SUCCESS("✓ TailwindCSS output file built successfully!"))
            else:
                # Suppress all output from TailwindCSS CLI
                run(command, check=True, stdout=DEVNULL, stderr=DEVNULL)
        except FileNotFoundError:
            raise CommandError(
                f"TailwindCSS CLI not found at '{cli_path}'. "
                f"Run '{settings.PKG_NAME} tailwindcss install' first."
            )
        except CalledProcessError as e:
            raise CommandError(f"TailwindCSS build failed: {e}")
        except Exception as e:
            raise CommandError(f"Unexpected error: {e}")


class CleanHandler:
    """Handles cleaning of TailwindCSS output files."""

    def __init__(
        self,
        config: dict[str, Any],
        stdout_writer: Callable[[str], None],
        style: Any,
        verbose: bool = True,
    ):
        self.config = config
        self.write = stdout_writer
        self.style = style
        self.verbose = verbose

    def clean(self) -> None:
        """Delete the built TailwindCSS output file."""
        output_css = self.config["OUTPUT"]

        if not output_css.exists():
            return

        self._delete_output_file(output_css)

    def _delete_output_file(self, output_css: Path) -> None:
        """Delete the output CSS file."""
        try:
            output_css.unlink()
        except PermissionError:
            raise CommandError(
                f"Permission denied: Cannot delete file at {output_css}. "
                f"Ensure the file is not in use and the path is writable."
            )
        except Exception as e:
            raise CommandError(f"Failed to delete file: {e}")


class Command(BaseCommand):
    """Django management command for TailwindCSS CLI operations."""

    help = "TailwindCSS CLI management: install, build, and clean operations."

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command-line arguments."""
        self._add_command_argument(parser)
        self._add_flag_arguments(parser)
        self._add_option_arguments(parser)

    def _add_command_argument(self, parser: CommandParser) -> None:
        """Add the main command positional argument."""
        parser.add_argument(
            "command",
            nargs="?",
            choices=["install", "build", "clean"],
            help="Command to execute: install, build, or clean",
        )

    def _add_flag_arguments(self, parser: CommandParser) -> None:
        """Add flag-based command options (for backward compatibility)."""
        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument(
            "-i",
            "--install",
            dest="install",
            action="store_true",
            help="Download and install the TailwindCSS CLI executable.",
        )
        group.add_argument(
            "-b",
            "--build",
            dest="build",
            action="store_true",
            help="Build the TailwindCSS file.",
        )
        group.add_argument(
            "-cl",
            "--clean",
            dest="clean",
            action="store_true",
            help="Delete the built TailwindCSS output file.",
        )

    def _add_option_arguments(self, parser: CommandParser) -> None:
        """Add additional option arguments."""
        parser.add_argument(
            "-y",
            "--yes",
            dest="auto_confirm",
            action="store_true",
            help="Automatically confirm all prompts.",
        )
        parser.add_argument(
            "--use-cache",
            dest="use_cache",
            action="store_true",
            help="Skip download if CLI already exists.",
        )
        parser.add_argument(
            "--no-verbose",
            dest="no_verbose",
            action="store_true",
            help="Suppress output messages.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Main command handler."""
        config = settings.TAILWINDCSS
        command_type = self._determine_command(options)
        self._validate_options(command_type, options)
        verbose = not options.get("no_verbose", False)
        self._execute_command(command_type, config, options, verbose)

    def _determine_command(self, options: dict[str, Any]) -> str:
        """Determine which command to execute."""
        command = options.get("command")
        is_install = command == "install" or options.get("install", False)
        is_build = command == "build" or options.get("build", False)
        is_clean = command == "clean" or options.get("clean", False)

        command_count = sum([is_install, is_build, is_clean])

        if command_count == 0:
            raise CommandError(
                "You must specify a command: install, build, or clean. "
                "Use 'tailwindcss --help' for usage information."
            )
        elif command_count > 1:
            raise CommandError("Only one command can be specified at a time.")

        if is_install:
            return "install"
        elif is_build:
            return "build"
        else:
            return "clean"

    def _validate_options(self, command_type: str, options: dict[str, Any]) -> None:
        """Validate command options."""
        if command_type != "install" and options.get("use_cache", False):
            raise CommandError("The --use-cache option can only be used with install.")

    def _execute_command(
        self,
        command_type: str,
        config: dict[str, Any],
        options: dict[str, Any],
        verbose: bool,
    ) -> None:
        """Execute the specified command."""
        if command_type == "install":
            handler = InstallHandler(config, self.stdout.write, self.style, verbose)
            handler.install(
                auto_confirm=options.get("auto_confirm", False),
                use_cache=options.get("use_cache", False),
            )
        elif command_type == "build":
            handler = BuildHandler(config, self.stdout.write, self.style, verbose)
            handler.build()
        elif command_type == "clean":
            handler = CleanHandler(config, self.stdout.write, self.style, verbose)
            handler.clean()
