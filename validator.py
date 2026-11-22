
import re
from datetime import datetime


class Validator:
    """Lớp kiểm tra tính hợp lệ của dữ liệu."""

    # Regex kiểm tra email
    EMAIL_PATTERN = r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$"

    # Regex kiểm tra username: 3-20 ký tự
    USERNAME_PATTERN = r"^[A-Za-z0-9_]{3,20}$"

    # Regex kiểm tra mã Task: T001, T002...
    TASK_ID_PATTERN = r"^T\d{3,}$"

    # Regex kiểm tra mã Project: P001, P002...
    PROJECT_ID_PATTERN = r"^P\d{3,}$"

    # Regex kiểm tra định dạng ngày YYYY-MM-DD
    DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"

    @staticmethod
    def not_empty(value):
        """Kiểm tra dữ liệu có bị trống không."""
        return value is not None and bool(str(value).strip())

    @staticmethod
    def is_valid_email(email):
        """Kiểm tra định dạng email."""
        if not isinstance(email, str):
            return False

        return bool(re.fullmatch(
            Validator.EMAIL_PATTERN, email
        ))

    @staticmethod
    def is_valid_username(username):
        """Kiểm tra tên đăng nhập."""
        if not isinstance(username, str):
            return False

        return bool(re.fullmatch(
            Validator.USERNAME_PATTERN, username
        ))

    @staticmethod
    def is_valid_task_id(task_id):
        """Kiểm tra mã công việc."""
        if not isinstance(task_id, str):
            return False

        return bool(re.fullmatch(
            Validator.TASK_ID_PATTERN, task_id
        ))

    @staticmethod
    def is_valid_project_id(project_id):
        """Kiểm tra mã dự án."""
        if not isinstance(project_id, str):
            return False

        return bool(re.fullmatch(
            Validator.PROJECT_ID_PATTERN, project_id
        ))

    @staticmethod
    def is_valid_date(date_text):
        """Kiểm tra ngày theo định dạng YYYY-MM-DD."""
        if not isinstance(date_text, str):
            return False

        if not re.fullmatch(
            Validator.DATE_PATTERN, date_text
        ):
            return False

        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_status(status):
        """Kiểm tra trạng thái công việc."""
        return status in ("todo", "doing", "done")

    @staticmethod
    def is_valid_priority(priority):
        """Kiểm tra mức độ ưu tiên."""
        return priority in ("low", "medium", "high")

    @staticmethod
    def in_range(value, min_value, max_value):
        """Kiểm tra giá trị nằm trong khoảng cho phép."""
        try:
            value = float(value)
            return min_value <= value <= max_value
        except (ValueError, TypeError):
            return False
