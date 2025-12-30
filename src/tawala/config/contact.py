from typing import TypedDict

from .conf import Conf, ConfField


class _ContactAddressConf(Conf):
    """Contact Address configuration settings."""

    country = ConfField(env="CONTACT_ADDRESS_COUNTRY", toml="contact.address.country", type=str)
    state = ConfField(env="CONTACT_ADDRESS_STATE", toml="contact.address.state", type=str)
    city = ConfField(env="CONTACT_ADDRESS_CITY", toml="contact.address.city", type=str)
    street = ConfField(env="CONTACT_ADDRESS_STREET", toml="contact.address.street", type=str)


class _ContactEmailConf(Conf):
    """Contact Email configuration settings."""

    primary = ConfField(env="CONTACT_EMAIL_PRIMARY", toml="contact.email.primary", type="email")
    additional = ConfField(
        env="CONTACT_EMAIL_ADDITIONAL",
        toml="contact.email.additional",
        type="list[email]",
    )


class _ContactNumberConf(Conf):
    """Contact Phone Number configuration settings."""

    primary = ConfField(env="CONTACT_NUMBER_PRIMARY", toml="contact.number.primary", type=str)
    additional = ConfField(
        env="CONTACT_NUMBER_ADDITIONAL",
        toml="contact.number.additional",
        type="list[str]",
    )


class ContactAddressDict(TypedDict):
    COUNTRY: str
    STATE: str
    CITY: str
    STREET: str


class ContactEmailDict(TypedDict):
    PRIMARY: str
    ADDITIONAL: list[str] | str


class ContactNumberDict(TypedDict):
    PRIMARY: str
    ADDITIONAL: list[str] | str


class ContactDict(TypedDict):
    address: ContactAddressDict
    email: ContactEmailDict
    phone: ContactNumberDict


_contact_address = _ContactAddressConf()
_contact_email = _ContactEmailConf()
_contact_number = _ContactNumberConf()


CONTACT: ContactDict = {
    "address": {
        "COUNTRY": _contact_address.country,
        "STATE": _contact_address.state,
        "CITY": _contact_address.city,
        "STREET": _contact_address.street,
    },
    "email": {
        "PRIMARY": _contact_email.primary,
        "ADDITIONAL": _contact_email.additional,
    },
    "phone": {
        "PRIMARY": _contact_number.primary,
        "ADDITIONAL": _contact_number.additional,
    },
}

__all__ = ["CONTACT"]
