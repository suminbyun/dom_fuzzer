import random

FORCE_BOOLEAN_PROPERTIES = {
    "disabled",
    "checked",
    "readonly",
    "required",
    "multiple",
    "hidden",
    "open",
    "inert",
    "spellcheck",
    "draggable",
    "autofocus",
    "selected"
}

PROPERTY_NAME_MAP = {
    "for": "htmlFor",
    "class": "className"
}

WRAPPER_ONLY_PROPERTIES = {
    "textContent": lambda: f"0x{random.randint(0, 0xFFFFFFFFFFFFFFFF):016x}"
}
