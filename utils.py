import os
import django
import dj_database_url


def abbr_to_jid(abbr):
    if abbr == "pr":
        return "ocd-jurisdiction/country:us/territory:pr/government"
    elif abbr == "dc":
        return "ocd-jurisdiction/country:us/district:dc/government"
    else:
        return f"ocd-jurisdiction/country:us/state:{abbr}/government"


def init_django():
    from django.conf import settings

    DATABASE_URL = os.environ.get("DATABASE_URL", "postgis://localhost/openstatesorg")
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
    settings.configure(
        DATABASES=DATABASES,
        INSTALLED_APPS=("opencivicdata.core", "opencivicdata.legislative", "v1"),
    )
    django.setup()
