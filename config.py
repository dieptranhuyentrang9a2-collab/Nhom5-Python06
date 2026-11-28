"""File cấu hình chung của ứng dụng (hằng số, không phải class).

Người phụ trách: Trần Ngọc Thúy Vy.
Mọi module cần đường dẫn / tham số nên import từ đây thay vì viết cứng.
"""
import sys
from pathlib import Path

APP_NAME = "Quản lý công việc Kanban - Nhóm 5"
APP_VERSION = "1.0.0"

# Khi đóng gói bằng PyInstaller (--onefile) mã nguồn chạy trong thư mục tạm,
# nên dữ liệu phải nằm cạnh file .exe chứ không nằm cạnh file .py.
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"
EXPORT_DIR = BASE_DIR / "exports"

# Tên các file dữ liệu JSON
TASKS_FILE = "tasks.json"
PROJECTS_FILE = "projects.json"
USERS_FILE = "users.json"
LOGS_FILE = "logs.json"
API_CACHE_FILE = "api_cache.json"

# Định dạng ngày thống nhất toàn dự án
DATE_FORMAT = "%Y-%m-%d"

# Dịch vụ API công khai (miễn phí) dùng để lấy dữ liệu mẫu
API_URL = "https://jsonplaceholder.typicode.com/todos"
API_TIMEOUT = 8          # giây
API_DEFAULT_LIMIT = 20   # số bản ghi lấy về mỗi lần

# Sinh dữ liệu mẫu
SAMPLE_SEED = 2026       # seed cố định -> kết quả lặp lại được khi kiểm thử
SAMPLE_TASK_COUNT = 20
SAMPLE_PASSWORD = "123456"

# Tài khoản Admin mặc định (khớp AuthManager)
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
