from .conf import Conf, ConfField


class RunCommandsConf(Conf):
    """Install/Build Commands to be executed settings."""

    install = ConfField(
        env="RUNCOMMANDS_INSTALL",
        toml="runcommands.install",
        default=["tailwind -i --use-cache"],
        type=list,
    )
    build = ConfField(
        env="RUNCOMMANDS_BUILD",
        toml="runcommands.build",
        default=[
            "makemigrations",
            "migrate",
            "tailwind -b",
            "collectstatic --noinput",
        ],
        type=list,
    )


RUNCOMMANDS = RunCommandsConf()


__all__ = ["RUNCOMMANDS"]
