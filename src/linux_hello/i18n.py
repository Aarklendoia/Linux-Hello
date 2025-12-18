"""Internationalization support for linux-hello."""

import gettext
import locale
import os
import sys

# Chemin du répertoire des traductions
LOCALE_DIR = "/usr/share/locale"

# Charger la locale système en temps réel
def get_translation():
    """Charger la traduction pour la locale actuelle."""
    try:
        lang = os.environ.get('LANG', locale.getdefaultlocale()[0] or 'en')
        # Extraire le code de langue (fr, en, etc.)
        if lang:
            lang = lang.split('_')[0].lower()
        else:
            lang = 'en'
    except Exception:
        lang = "en"

    try:
        translation = gettext.translation(
            "linux-hello",
            localedir=LOCALE_DIR,
            languages=[lang],
            fallback=True
        )
    except Exception:
        translation = gettext.NullTranslations()
    
    return translation

# Initialiser la traduction
_translation = get_translation()

# Fonction de traduction
def _(message):
    """Traduire un message."""
    # Recharger la traduction à chaque appel pour prendre en compte les changements LANG
    global _translation
    current_lang = os.environ.get('LANG', '')
    if current_lang:
        _translation = get_translation()
    return _translation.gettext(message)

# Pour les traductions plurielles si nécessaire
def ngettext(singular, plural, n):
    """Traduire un message au singulier ou au pluriel."""
    global _translation
    current_lang = os.environ.get('LANG', '')
    if current_lang:
        _translation = get_translation()
    return _translation.ngettext(singular, plural, n)


