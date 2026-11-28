import re


class Validator:

    @staticmethod
    def not_empty(value):
        return bool(value and str(value).strip())

    @staticmethod
    def is_valid_username(username):
        if not isinstance(username, str):
            return False

        return bool(re.fullmatch(r"[a-zA-Z0-9_]{3,20}", username))

    @staticmethod
    def is_valid_email(email):
        if not isinstance(email, str):
            return False

        pattern = r"^[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}$"
        return bool(re.fullmatch(pattern, email))
