from datetime import datetime


class ActivityLog:
    def __init__(self, storage):
        self._storage = storage

    def write(self, user, action):
        """Ghi nhận hoạt động của người dùng."""
        if not isinstance(user, str) or not user.strip():
            raise ValueError("Tên người dùng không được để trống.")

        if not isinstance(action, str) or not action.strip():
            raise ValueError("Nội dung hoạt động không được để trống.")

        logs = self._storage.load() or []

        logs.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user.strip(),
            "action": action.strip(),
        })

        self._storage.save(logs)

    def get_all(self):
        """Lấy toàn bộ nhật ký hoạt động."""
        logs = self._storage.load() or []
        return list(logs)

    def get_by_user(self, username):
        """Lấy nhật ký theo người thực hiện."""
        if not isinstance(username, str) or not username.strip():
            return []

        username = username.strip().casefold()

        return [
            log for log in self.get_all()
            if isinstance(log, dict)
            and isinstance(log.get("user"), str)
            and log["user"].strip().casefold() == username
        ]
