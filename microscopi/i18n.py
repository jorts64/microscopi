import gettext
import locale
import os

APP_NAME = "microscopi"

def init_i18n():
    locale.setlocale(locale.LC_ALL, "")

    localedir = os.path.join(
        os.path.dirname(__file__),
        "locale"
    )

    gettext.bindtextdomain(APP_NAME, localedir)
    gettext.textdomain(APP_NAME)

    return gettext.gettext


# `_` se importará desde aquí
_ = init_i18n()
