import random
from datetime import date, timedelta

import config

_TITLES = [
    "Thiết kế giao diện đăng nhập", "Viết hàm kiểm tra email", "Sửa lỗi kéo-thả thẻ",
    "Viết báo cáo chương 3", "Kiểm thử chức năng tìm kiếm", "Tối ưu đọc ghi file JSON",
    "Chuẩn bị slide thuyết trình", "Họp nhóm tuần", "Vẽ sơ đồ lớp",
    "Thêm biểu đồ thống kê", "Đóng gói ứng dụng", "Viết hướng dẫn cài đặt",
    "Rà soát mã nguồn", "Cập nhật README", "Sao lưu dữ liệu",
]
_LABELS = ["bug", "ui", "backend", "docs", "test", "urgent"]
_PROJECTS = [
    ("Ứng dụng Kanban", "Dự án chính của nhóm"),
    ("Báo cáo môn học", "Viết báo cáo và slide"),
]
_USERS = [
    ("trang", "Diệp Trần Huyền Trang", "trang@gmail.com"),
    ("linh", "Nguyễn Thùy Linh", "linh@gmail.com"),
    ("hang", "Liêu Thị Thanh Hằng", "hang@gmail.com"),
    ("thuyvy", "Trần Ngọc Thúy Vy", "thuyvy@gmail.com"),
]


class SampleDataGenerator:
    """Sinh dữ liệu mẫu bằng module random. Cùng seed -> cùng dữ liệu (dễ kiểm thử)."""

    def __init__(self, seed=config.SAMPLE_SEED):
        self._seed = seed
        self._rng = random.Random(seed)

    def generate_tasks(self, n, project_ids=("P001",), assignees=None):
        """Trả về n dict công việc (chưa có id) để truyền vào TaskManager.add_task."""
        if not isinstance(n, int) or n < 0:
            raise ValueError("Số lượng công việc phải là số nguyên không âm.")
        if not project_ids:
            raise ValueError("Cần ít nhất một mã dự án.")

        assignees = list(assignees) if assignees else [u[0] for u in _USERS]
        today = date.today()
        tasks = []
        for i in range(n):
            title = self._rng.choice(_TITLES)
            offset = self._rng.randint(-10, 20)   # âm = đã quá hạn
            tasks.append({
                "project_id": self._rng.choice(list(project_ids)),
                "title": f"{title} #{i + 1}",
                "description": f"Công việc mẫu số {i + 1}",
                "status": self._rng.choices(
                    ["todo", "doing", "done"], weights=[4, 3, 3])[0],
                "assignee": self._rng.choice(assignees),
                "due_date": (today + timedelta(days=offset)).strftime(config.DATE_FORMAT),
                "priority": self._rng.choice(["low", "medium", "high"]),
                "labels": self._rng.sample(_LABELS, self._rng.randint(0, 2)),
            })
        return tasks

    def generate_users(self):
        """Trả về danh sách dict tài khoản mẫu (username, password, full_name, email)."""
        return [
            {"username": u, "password": config.SAMPLE_PASSWORD,
             "full_name": name, "email": email}
            for u, name, email in _USERS
        ]

    def reset_all_data(self, task_storage, project_storage, user_storage,
                       log_storage, n_tasks=config.SAMPLE_TASK_COUNT):
        """Sao lưu rồi xóa toàn bộ dữ liệu, nạp lại bộ dữ liệu mẫu.

        Trả về dict thống kê số bản ghi đã tạo. Admin mặc định được AuthManager tạo lại.
        """
        # import trong hàm để tránh phụ thuộc vòng và giữ module nhẹ khi chỉ dùng generate_*
        from activity_log import ActivityLog
        from auth_manager import AuthManager
        from project_manager import ProjectManager
        from task_manager import TaskManager

        for storage in (task_storage, project_storage, user_storage, log_storage):
            if storage.load():          # chỉ sao lưu khi đang có dữ liệu
                storage.backup()
            storage.save([])

        self._rng = random.Random(self._seed)   # đặt lại -> mỗi lần reset cho cùng kết quả

        activity_log = ActivityLog(log_storage)
        auth = AuthManager(user_storage, activity_log)     # tự tạo admin
        for u in self.generate_users():
            auth.register(u["username"], u["password"], u["full_name"], u["email"])

        projects = ProjectManager(project_storage)
        project_ids = [projects.add_project(name, desc).id for name, desc in _PROJECTS]

        tasks = TaskManager(task_storage)
        for item in self.generate_tasks(n_tasks, project_ids):
            tasks.add_task(**item)

        activity_log.write("system", f"Khởi tạo dữ liệu mẫu ({n_tasks} công việc)")
        return {"users": len(auth.get_all_users()), "projects": len(project_ids),
                "tasks": n_tasks}
