from user import User
from validator import Validator


class AuthManager:
    """Quản lý đăng ký, đăng nhập và phân quyền người dùng."""

    def __init__(self, storage, activity_log=None):
        self._storage = storage
        self._activity_log = activity_log
        self._users = []
        self.current_user = None

        # Đọc danh sách tài khoản
        data = self._storage.load() or []

        self._users = [
            User.from_dict(item) for item in data
        ]

        # Tạo tài khoản Admin mặc định nếu chưa có
        if not self._users:
            admin = User(
                id="U001",
                username="admin",
                full_name="Administrator",
                email="admin@gmail.com",
                role="admin"
            )

            admin.set_password("admin123")

            self._users.append(admin)
            self._save()

    # Lưu danh sách tài khoản
    def _save(self):
        self._storage.save([
            user.to_dict() for user in self._users
        ])

    # Ghi nhật ký hoạt động
    def _log(self, username, action):
        if self._activity_log:
            self._activity_log.write(username, action)

    # Tạo mã người dùng tiếp theo
    def _next_id(self):
        nums = [
            int(user.id[1:])
            for user in self._users
            if user.id[1:].isdigit()
        ]

        return f"U{max(nums, default=0) + 1:03d}"

    # Tìm người dùng theo username
    def get_user(self, username):
        for user in self._users:
            if user.username == username:
                return user

        return None

    # Đăng ký tài khoản
    def register(self, username, password, full_name, email):
        if not all([
            Validator.not_empty(username),
            Validator.not_empty(password),
            Validator.not_empty(full_name),
            Validator.not_empty(email)
        ]):
            return False, "Vui lòng nhập đầy đủ thông tin."

        if not Validator.is_valid_username(username):
            return False, "Tên đăng nhập không hợp lệ."

        if not Validator.is_valid_email(email):
            return False, "Email không hợp lệ."

        if len(password) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự."

        if self.get_user(username):
            return False, "Tên đăng nhập đã tồn tại."

        for user in self._users:
            if user.email.lower() == email.lower():
                return False, "Email đã được sử dụng."

        user = User(
            id=self._next_id(),
            username=username,
            full_name=full_name,
            email=email,
            role="user"
        )

        user.set_password(password)

        self._users.append(user)
        self._save()

        self._log(username, "Đăng ký tài khoản")

        return True, "Đăng ký thành công."

    # Đăng nhập
    def login(self, username, password):
        user = self.get_user(username)

        if user is None or not user.check_password(password):
            self._log(username, "Đăng nhập thất bại")
            return False, "Tên đăng nhập hoặc mật khẩu không đúng."

        self.current_user = user

        self._log(username, "Đăng nhập thành công")

        return True, "Đăng nhập thành công."

    # Đăng xuất
    def logout(self):
        if self.current_user is None:
            return False

        username = self.current_user.username

        self._log(username, "Đăng xuất")

        self.current_user = None

        return True

    # Đổi mật khẩu
    def change_password(self, old_password, new_password):
        if self.current_user is None:
            return False, "Bạn chưa đăng nhập."

        if not self.current_user.check_password(old_password):
            return False, "Mật khẩu cũ không chính xác."

        if len(new_password) < 6:
            return False, "Mật khẩu mới phải có ít nhất 6 ký tự."

        if old_password == new_password:
            return False, "Mật khẩu mới phải khác mật khẩu cũ."

        self.current_user.set_password(new_password)

        self._save()

        self._log(
            self.current_user.username,
            "Đổi mật khẩu"
        )

        return True, "Đổi mật khẩu thành công."

    # Kiểm tra quyền Admin
    def is_admin(self):
        return (
            self.current_user is not None
            and self.current_user.is_admin()
        )

    # Lấy danh sách tài khoản
    def get_all_users(self):
        return list(self._users)

    # Xóa tài khoản
    def delete_user(self, username):
        if not self.is_admin():
            return False, "Bạn không có quyền thực hiện."

        user = self.get_user(username)

        if user is None:
            return False, "Không tìm thấy tài khoản."

        if user.id == self.current_user.id:
            return False, "Không thể tự xóa tài khoản đang đăng nhập."

        self._users.remove(user)
        self._save()

        self._log(
            self.current_user.username,
            f"Xóa tài khoản {username}"
        )

        return True, "Xóa tài khoản thành công."

    # Thay đổi quyền người dùng
    def change_role(self, username, role):
        if not self.is_admin():
            return False, "Bạn không có quyền thực hiện."

        if role not in ("admin", "user"):
            return False, "Vai trò không hợp lệ."

        user = self.get_user(username)

        if user is None:
            return False, "Không tìm thấy tài khoản."

        if user.id == self.current_user.id and role != "admin":
            return False, "Không thể tự hạ quyền Admin."

        user.role = role
        self._save()

        self._log(
            self.current_user.username,
            f"Thay đổi quyền {username} thành {role}"
        )

        return True, "Thay đổi quyền thành công."
