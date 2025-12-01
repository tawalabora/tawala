from . import base


class SecurityConfig(base.Config):
    """Security-related configuration settings."""

    secret_key = base.ConfField(
        env="SECRET_KEY",
        toml="secret-key",
    )
    debug = base.ConfField(
        env="DEBUG",
        toml="debug",
        default=True,
    )
    allowed_hosts = base.ConfField(
        env="ALLOWED_HOSTS",
        toml="allowed-hosts",
    )


class ApplicationConfig(base.Config):
    """Application and URL configuration settings."""

    configured_apps = base.ConfField(
        env="CONFIGURED_APPS",
        toml="configured-apps",
    )


class DatabaseConfig(base.Config):
    """Database configuration settings."""

    backend = base.ConfField(
        env="DB_BACKEND",
        toml="db.backend",
        default="sqlite3",
    )
    service = base.ConfField(
        env="DB_SERVICE",
        toml="db.service",
    )
    pool = base.ConfField(
        env="DB_POOL",
        toml="db.pool",
        default=False,
    )
    ssl_mode = base.ConfField(
        env="DB_SSL_MODE",
        toml="db.ssl-mode",
        default="prefer",
    )
    use_vars = base.ConfField(
        env="DB_USE_VARS",
        toml="db.use-vars",
        default=False,
    )

    user = base.ConfField(env="DB_USER", default="postgres")
    password = base.ConfField(env="DB_PASSWORD")
    name = base.ConfField(env="DB_NAME", default="postgres")
    host = base.ConfField(env="DB_HOST", default="localhost")
    port = base.ConfField(env="DB_PORT", default="5432")


class StorageConfig(base.Config):
    """Storage configuration settings."""

    backend = base.ConfField(
        env="STORAGE_BACKEND",
        toml="storage.backend",
        default="filesystem",
    )
    token = base.ConfField(
        env="STORAGE_TOKEN",
        toml="storage.token",
    )


class CommandsConfig(base.Config):
    """Install/Build Commands to be executed settings."""

    install = base.ConfField(
        env="COMMANDS_INSTALL",
        toml="commands.install",
    )
    build = base.ConfField(
        env="COMMANDS_BUILD",
        toml="commands.build",
    )


class TailwindCLIConfig(base.Config):
    """Tailwind CLI configuration settings."""

    path = base.ConfField(
        env="TAILWIND_CLI_PATH",
        toml="tailwind-cli.path",
    )

    version = base.ConfField(
        env="TAILWIND_CLI_VERSION",
        toml="tailwind-cli.version",
        default="v4.1.17",
    )
