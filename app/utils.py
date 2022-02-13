import re
from passlib.hash import pbkdf2_sha256

_PATTERNS = {
    "address": r"\w+",
    "phone": r"\(\+\d{2}\)\s\d{3}-\d{3}-\d{2}-\d{2}",
    "name": r"^([A-Z-a-z-]+)$",
    "birth_date": r"(\d{8})|(\d{4}-\d{2}-\d{2})",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
}

_CARD_ISSUER_PATTERNS = {
    "American Express": "^3[47][0-9]{13}$",
    "Diners Club": "^3(?:0[0-5]|[68][0-9])[0-9]{11}$",
    "Discover": "^65[4-9][0-9]{13}|64[4-9][0-9]{13}|6011[0-9]{12}|(622(?:12[6-9]|1[3-9][0-9]|[2-8][0-9][0-9]|9[01][0-9]|92[0-5])[0-9]{10})$",
    "JCB": "^(?:2131|1800|35\d{3})\d{11}$",
    "Mastercard": "^5[1-5][0-9]{14}$",
    "Visa": "^4[0-9]{12}(?:[0-9]{3})?$"
}

class ValidationError(Exception):
    pass

def validate_with_pattern(pattern, raise_exception=False):
    if not pattern:
        raise ValueError("Error: Pattern value cannot be empty or None")

    if pattern not in _PATTERNS:
        raise ValueError(f"Invalid Pattern '{pattern}': Not found")

    regex_pattern = _PATTERNS.get(pattern)

    def wrapper_func(func):
        def validator_func(*args, **kwargs):
            value = args[1]
            if not re.match(regex_pattern, value):
                if raise_exception:
                    raise ValidationError(f"Value '{value}' is not valid.")
                # Discard value
                args = list(args)
                args[1] = None
            
            func(*args, **kwargs)

        return validator_func

    return wrapper_func


def get_card_issuer(card_number):
    for issuer, pattern in _CARD_ISSUER_PATTERNS.items():
        if re.search(pattern, card_number):
            return issuer
    return "Unknown"


def hash_password(password):
    return pbkdf2_sha256.hash(password)


def check_password(password, hash):
    return pbkdf2_sha256.verify(password, hash)
