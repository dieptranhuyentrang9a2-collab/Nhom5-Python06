import re
from datetime import datetime


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

    @staticmethod
    def is_valid_date(value, fmt="%Y-%m-%d"):
        """Kiểm tra chuỗi ngày đúng định dạng (mặc định YYYY-MM-DD)."""
        if not isinstance(value, str):
            return False

        try:
            datetime.strptime(value.strip(), fmt)
            return True
        except ValueError:
            return False
