
import hashlib
import secrets
import hmac

from base_entity import BaseEntity


class User(BaseEntity):
    """Lớp quản lý thông tin tài khoản người dùng."""

    def __init__(
        self,
        id,
        username,
        full_name,
        email,
        role="user",
        salt=None,
        password_hash=None
    ):
        super().__init__(id)

        self.username = username
        self.full_name = full_name
        self.email = email
        self.role = role

        # Tạo salt riêng cho mỗi tài khoản
        self.salt = salt if salt else secrets.token_hex(16)

        self.password_hash = password_hash

    # Mã hóa mật khẩu bằng SHA-256 kết hợp salt
    @staticmethod
    def hash_password(password, salt):
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        )

        return hashed.hex()

    # Thiết lập mật khẩu cho tài khoản
    def set_password(self, password):
        self.password_hash = self.hash_password(
            password,
            self.salt
        )

    # Kiểm tra mật khẩu đăng nhập
    def check_password(self, password):
        if self.password_hash is None:
            return False

        hashed = self.hash_password(
            password,
            self.salt
        )

        return hmac.compare_digest(
            hashed,
            self.password_hash
        )

    # Kiểm tra quyền Admin
    def is_admin(self):
        return self.role == "admin"

    # Chuyển đối tượng User thành Dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "salt": self.salt,
            "password_hash": self.password_hash
        }
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            username=data["username"],
            full_name=data["full_name"],
            email=data["email"],
            role=data.get("role", "user"),
            salt=data.get("salt"),
            password_hash=data.get("password_hash")
        )
