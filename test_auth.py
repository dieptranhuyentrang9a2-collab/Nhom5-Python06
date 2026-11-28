import tempfile
import os

from json_storage import JsonStorage
from auth_manager import AuthManager


def test_auth():
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "users.json")
        storage = JsonStorage(path)

        auth = AuthManager(storage)

        print("\n===== KIỂM THỬ AUTH MANAGER =====")

        # 1. Kiểm tra Admin mặc định
        print(
            "PASS: Tạo Admin mặc định"
            if auth.get_user("admin") is not None
            else "FAIL: Không tạo được Admin"
        )

        # 2. Đăng nhập Admin
        success, message = auth.login("admin", "admin123")
        print("PASS: Đăng nhập Admin" if success else "FAIL: Đăng nhập Admin")

        # 3. Kiểm tra quyền Admin
        print(
            "PASS: Kiểm tra quyền Admin"
            if auth.is_admin()
            else "FAIL: Kiểm tra quyền Admin"
        )

        # 4. Đăng ký tài khoản
        success, message = auth.register(
            "trang123",
            "123456",
            "Trang",
            "trang@gmail.com"
        )
        print("PASS: Đăng ký tài khoản" if success else f"FAIL: {message}")

        # 5. Kiểm tra tài khoản mới
        print(
            "PASS: Tìm tài khoản"
            if auth.get_user("trang123") is not None
            else "FAIL: Tìm tài khoản"
        )

        # 6. Đăng xuất Admin
        auth.logout()

        # 7. Đăng nhập tài khoản thường
        success, message = auth.login("trang123", "123456")
        print("PASS: Đăng nhập User" if success else "FAIL: Đăng nhập User")

        # 8. Kiểm tra quyền User
        print(
            "PASS: Phân quyền User"
            if not auth.is_admin()
            else "FAIL: Phân quyền User"
        )

        # 9. Đổi mật khẩu
        success, message = auth.change_password("123456", "abcdef")
        print("PASS: Đổi mật khẩu" if success else f"FAIL: {message}")

        # 10. Đăng xuất
        print(
            "PASS: Đăng xuất"
            if auth.logout()
            else "FAIL: Đăng xuất"
        )

        # 11. Đăng nhập bằng mật khẩu mới
        success, message = auth.login("trang123", "abcdef")
        print(
            "PASS: Đăng nhập bằng mật khẩu mới"
            if success
            else "FAIL: Đăng nhập bằng mật khẩu mới"
        )


if __name__ == "__main__":
    test_auth()
