from .conf import Conf, ConfField


class ContactInfoAddressConf(Conf):
    """ContactInfo Address configuration settings."""

    country = ConfField(
        env="CONTACTINFO_ADDRESS_COUNTRY",
        toml="contactinfo.address.country",
        type=str,
    )
    state = ConfField(env="CONTACTINFO_ADDRESS_STATE", toml="contactinfo.address.state", type=str)
    city = ConfField(env="CONTACTINFO_ADDRESS_CITY", toml="contactinfo.address.city", type=str)
    street = ConfField(env="CONTACTINFO_ADDRESS_STREET", toml="contactinfo.address.street", type=str)


class ContactInfoEmailConf(Conf):
    """ContactInfo Email configuration settings."""

    primary = ConfField(env="CONTACTINFO_EMAIL_PRIMARY", toml="contactinfo.email.primary", type=str)
    additional = ConfField(
        env="CONTACTINFO_EMAIL_ADDITIONAL",
        toml="contactinfo.email.additional",
        type=list,
    )


class ContactInfoPhoneConf(Conf):
    """ContactInfo Phone Number configuration settings."""

    primary = ConfField(
        env="CONTACTINFO_NUMBER_PRIMARY", toml="contactinfo.number.primary", type=str
    )
    additional = ConfField(
        env="CONTACTINFO_NUMBER_ADDITIONAL",
        toml="contactinfo.number.additional",
        type=list,
    )


CONTACTINFO_ADDRESS = ContactInfoAddressConf()
CONTACTINFO_EMAIL = ContactInfoEmailConf()
CONTACTINFO_PHONE = ContactInfoPhoneConf()


__all__ = ["CONTACTINFO_ADDRESS", "CONTACTINFO_EMAIL", "CONTACTINFO_PHONE"]
