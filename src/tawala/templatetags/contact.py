from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def contact_address() -> dict[str, str]:
    """
    Returns the complete contact address dictionary.

    Usage in template:
        {% contact_address as address %}
        {{ address.COUNTRY }}, {{ address.CITY }}
    """
    return settings.CONTACT["address"]


@register.simple_tag
def get_contact_address_country() -> str:
    """Returns the contact address country."""
    return settings.CONTACT["address"]["COUNTRY"]


@register.simple_tag
def get_contact_address_state() -> str:
    """Returns the contact address state."""
    return settings.CONTACT["address"]["STATE"]


@register.simple_tag
def get_contact_address_city() -> str:
    """Returns the contact address city."""
    return settings.CONTACT["address"]["CITY"]


@register.simple_tag
def get_contact_address_street() -> str:
    """Returns the contact address street."""
    return settings.CONTACT["address"]["STREET"]


@register.simple_tag
def contact_email() -> dict[str, str | list[str]]:
    """
    Returns the complete contact email dictionary.

    Usage in template:
        {% contact_email as emails %}
        {{ emails.PRIMARY }}
        {% for email in emails.ADDITIONAL %}
            {{ email }}
        {% endfor %}
    """
    return settings.CONTACT["email"]


@register.simple_tag
def get_contact_email_primary() -> str:
    """Returns the primary contact email."""
    return settings.CONTACT["email"]["PRIMARY"]


@register.simple_tag
def get_contact_email_additional() -> list[str]:
    """Returns the list of additional contact emails."""
    return settings.CONTACT["email"]["ADDITIONAL"]


@register.simple_tag
def contact_phone() -> dict[str, str | list[str]]:
    """
    Returns the complete contact phone dictionary.

    Usage in template:
        {% contact_phone as phones %}
        {{ phones.PRIMARY }}
        {% for phone in phones.ADDITIONAL %}
            {{ phone }}
        {% endfor %}
    """
    return settings.CONTACT["phone"]


@register.simple_tag
def get_contact_phone_primary() -> str:
    """Returns the primary contact phone number."""
    return settings.CONTACT["phone"]["PRIMARY"]


@register.simple_tag
def get_contact_phone_additional() -> list[str]:
    """Returns the list of additional contact phone numbers."""
    return settings.CONTACT["phone"]["ADDITIONAL"]
