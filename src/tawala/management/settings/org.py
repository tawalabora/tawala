from .conf import Conf, ConfField


class OrgConf(Conf):
    """Organization-related configuration settings."""

    name = ConfField(
        env="ORG_NAME",
        toml="org.name",
        type=str,
    )
    short_name = ConfField(
        env="ORG_SHORT_NAME",
        toml="org.short-name",
        type=str,
    )
    description = ConfField(
        env="ORG_DESCRIPTION",
        toml="org.description",
        type=str,
    )


ORG = OrgConf()


__all__ = ["ORG"]
