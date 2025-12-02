"""UI management command: tailwind"""

import platform
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser


class Command(BaseCommand):
    help = "Build Tailwind CSS using the Tailwind CLI."

    def add_arguments(self, parser: CommandParser) -> None:
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "-b",
            "--build",
            dest="build",
            action="store_true",
            help="Build the Tailwind CSS file.",
        )
        group.add_argument(
            "-d",
            "--download",
            "--install",
            dest="install",
            action="store_true",
            help="Download and install the Tailwind CSS CLI executable.",
        )

        parser.add_argument(
            "-y",
            "--yes",
            dest="auto_confirm",
            action="store_true",
            help="Automatically confirm all prompts.",
        )

    def _get_platform_info(self) -> tuple[str, str]:
        """
        Determine the current platform and architecture.

        Returns:
            tuple[str, str]: (platform_name, architecture) e.g., ('linux', 'x64')

        Raises:
            CommandError: If platform or architecture is unsupported
        """
        system: str = platform.system().lower()
        machine: str = platform.machine().lower()

        # Map system names
        platform_map: dict[str, str] = {
            "darwin": "macos",
            "linux": "linux",
            "windows": "windows",
        }

        platform_name: str | None = platform_map.get(system)
        if not platform_name:
            raise CommandError(
                f"Unsupported operating system: {system}. "
                "Supported: Linux, macOS, Windows"
            )

        # Map architecture names
        # Reference: https://docs.python.org/3/library/platform.html#platform.machine
        arch_map: dict[str, str] = {
            # x86_64 variants
            "x86_64": "x64",
            "amd64": "x64",
            "x64": "x64",
            # ARM64 variants
            "arm64": "arm64",
            "aarch64": "arm64",
            "armv8": "arm64",
        }

        architecture: str | None = arch_map.get(machine)
        if not architecture:
            raise CommandError(
                f"Unsupported architecture: {machine}. Supported: x64, arm64"
            )

        return platform_name, architecture

    def _get_download_url(
        self, version: str, platform_name: str, architecture: str
    ) -> str:
        """
        Construct the download URL for the Tailwind CLI executable.

        Args:
            version: Version string (e.g., 'v4.1.17' or 'latest')
            platform_name: Platform name ('linux', 'macos', 'windows')
            architecture: Architecture ('x64', 'arm64')

        Returns:
            str: Complete download URL
        """
        base_url: str = "https://github.com/tailwindlabs/tailwindcss/releases"

        # Construct filename based on platform and architecture
        # Match exact filenames from GitHub releases
        if platform_name == "windows":
            # Windows only has x64 version
            filename: str = "tailwindcss-windows-x64.exe"
        elif platform_name == "linux":
            # Linux has both architectures (standard glibc versions)
            filename = f"tailwindcss-linux-{architecture}"
        elif platform_name == "macos":
            # macOS has both architectures
            filename = f"tailwindcss-macos-{architecture}"
        else:
            raise CommandError(f"Unsupported platform: {platform_name}")

        # Construct full download path
        download_path: str = f"{base_url}/download/{version}/{filename}"

        return download_path

    def _download_file(
        self, url: str, destination: Path, show_progress: bool = True
    ) -> None:
        """
        Download a file from a URL to a destination path.

        Args:
            url: URL to download from
            destination: Path to save the file
            show_progress: Whether to show download progress

        Raises:
            CommandError: If download fails
        """
        temp_destination: Path = destination.with_suffix(destination.suffix + ".tmp")

        try:
            self.stdout.write(f"Downloading from: {url}")

            # Create a custom progress callback
            def progress_callback(
                block_num: int, block_size: int, total_size: int
            ) -> None:
                if show_progress and total_size > 0:
                    downloaded: int = block_num * block_size
                    percent: float = min(100.0, (downloaded / total_size) * 100)
                    self.stdout.write(
                        f"\rProgress: {percent:.1f}% ({downloaded}/{total_size} bytes)",
                        ending="",
                    )
                    self.stdout.flush()

            # Download to temporary file first
            urlretrieve(url, temp_destination, progress_callback)

            if show_progress:
                self.stdout.write("")

            # Move temp file to final destination only if download completed
            temp_destination.rename(destination)

            self.stdout.write(self.style.SUCCESS(f"✓ Downloaded to: {destination}"))

        except KeyboardInterrupt:
            # Clean up partial download on keyboard interrupt
            if temp_destination.exists():
                temp_destination.unlink()
            self.stdout.write("\n")
            self.stdout.write(self.style.WARNING("Download cancelled by user."))
            raise CommandError("Installation aborted.")
        except HTTPError as e:
            # Clean up on error
            if temp_destination.exists():
                temp_destination.unlink()
            raise CommandError(
                f"Failed to download from {url}. HTTP Error {e.code}: {e.reason}"
            )
        except URLError as e:
            # Clean up on error
            if temp_destination.exists():
                temp_destination.unlink()
            raise CommandError(f"Failed to download: {e.reason}")
        except Exception as e:
            # Clean up on error
            if temp_destination.exists():
                temp_destination.unlink()
            raise CommandError(f"Download failed: {e}")

    def _make_executable(self, file_path: Path) -> None:
        """
        Make a file executable (Unix-like systems only).

        Args:
            file_path: Path to the file to make executable
        """
        if sys.platform != "win32":
            current_permissions: int = file_path.stat().st_mode
            new_permissions: int = (
                current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            )
            file_path.chmod(new_permissions)
            self.stdout.write(self.style.SUCCESS(f"✓ Made executable: {file_path}"))

    def handle_install(self, auto_confirm: bool = False) -> None:
        """
        Handle the installation/download of Tailwind CLI.

        Args:
            auto_confirm: Skip confirmation prompts if True

        Raises:
            CommandError: If installation fails
        """
        tailwind_config: dict[str, Any] = settings.TAILWIND_CLI

        # Get platform information automatically
        platform_name, architecture = self._get_platform_info()
        self.stdout.write(
            f"Detected platform: {self.style.SUCCESS(f'{platform_name}-{architecture}')}"
        )

        # Get version from settings
        version: str = tailwind_config["VERSION"]

        # Get download folder from CLI_DIR
        folder = Path(settings.CLI_DIR)
        folder.mkdir(parents=True, exist_ok=True)

        # Determine destination filename
        destination_name: str
        if platform_name == "windows":
            destination_name = "tailwindcss.exe"
        else:
            destination_name = "tailwindcss"

        destination: Path = folder / destination_name

        # Show download information
        download_url: str = self._get_download_url(version, platform_name, architecture)
        self.stdout.write("\nDownload Information:")
        self.stdout.write(f"  Version:     {version}")
        self.stdout.write(f"  Platform:    {platform_name}-{architecture}")
        self.stdout.write(f"  Destination: {destination}")
        self.stdout.write(f"  URL:         {download_url}\n")

        # Check if already exists
        if destination.exists():
            self.stdout.write(
                self.style.WARNING(f"⚠ Tailwind CLI already exists at: {destination}")
            )
            if not auto_confirm:
                overwrite: str = input("Overwrite? (y/N): ").strip().lower()
                if overwrite != "y":
                    self.stdout.write("Installation cancelled.")
                    return
            else:
                self.stdout.write("Auto-confirming overwrite...")
            destination.unlink()
        else:
            # Confirm download if not auto-confirmed
            if not auto_confirm:
                confirm: str = input("Proceed with download? (y/N): ").strip().lower()
                if confirm != "y":
                    self.stdout.write("Installation cancelled.")
                    return

        # Download the file
        self._download_file(download_url, destination)

        # Make executable (Unix-like systems)
        self._make_executable(destination)

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Tailwind CLI successfully installed at: {destination}\n"
                f"  Platform: {platform_name}-{architecture}\n"
                f"  Version: {version}"
            )
        )

    def handle_build(self) -> None:
        """
        Handle the build process for Tailwind CSS.

        Raises:
            CommandError: If build fails or configuration is incomplete
        """
        tailwind_config: dict[str, Any] = settings.TAILWIND_CLI
        tailwind_cli: str | Path | None = tailwind_config.get("PATH")
        css_config: dict[str, str] = tailwind_config.get("CSS", {})
        input_css: str | None = css_config.get("input")
        output_css: str | None = css_config.get("output")

        if not tailwind_cli or not input_css or not output_css:
            raise CommandError(
                "Tailwind CLI configuration is incomplete. "
                "Check TAILWIND_CLI settings in your Tawala settings."
            )

        command: list[str] = [
            str(tailwind_cli),
            "-i",
            str(input_css),
            "-o",
            str(output_css),
            "--minify",
        ]

        try:
            self.stdout.write("Building Tailwind CSS...")
            subprocess.run(command, check=True)
            self.stdout.write(self.style.SUCCESS("✓ Tailwind CSS built successfully!"))

        except FileNotFoundError:
            raise CommandError(
                f"Tailwind CSS CLI not found at '{tailwind_cli}'. "
                "Please run 'tawala tailwind --install' first."
            )
        except subprocess.CalledProcessError as e:
            raise CommandError(f"Tailwind CSS build failed: {e}")
        except Exception as e:
            raise CommandError(f"An unexpected error occurred: {e}")

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Main command handler.

        Args:
            *args: Positional arguments
            **options: Command options from argument parser
        """
        if options["install"]:
            self.handle_install(auto_confirm=options.get("auto_confirm", False))
        elif options["build"]:
            self.handle_build()
