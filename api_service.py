import json
import urllib.error
import urllib.request

import config

# Cột userId của API -> tên người thực hiện (API chỉ trả về số)
_ASSIGNEES = {
    1: "admin", 2: "trang", 3: "linh", 4: "hang", 5: "thuyvy",
}


class ApiService:
    """Lấy dữ liệu công việc từ API công khai và lưu bộ nhớ đệm (cache) ra JSON.

    Khi mất mạng / API lỗi, fetch() tự động dùng lại dữ liệu cache lần trước.
    """

    def __init__(self, cache_storage, url=config.API_URL, timeout=config.API_TIMEOUT):
        self._url = url
        self._timeout = timeout
        self._cache_storage = cache_storage
        self.last_source = None   # "api" hoặc "cache" -> để giao diện báo cho người dùng

    def _download(self, limit):
        request = urllib.request.Request(
            f"{self._url}?_limit={int(limit)}",
            headers={"User-Agent": "Nhom5-Kanban/1.0", "Accept": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self._timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    @staticmethod
    def _clean(raw):
        """Làm sạch dữ liệu thô: bỏ bản ghi hỏng, chuẩn hóa về dạng dùng được cho Task."""
        if not isinstance(raw, list):
            return []

        cleaned = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            title = item.get("title")
            if not isinstance(title, str) or not title.strip():
                continue

            title = " ".join(title.split())
            user_id = item.get("userId")
            cleaned.append({
                "title": title[:1].upper() + title[1:],
                "description": f"Nhập từ API (mã gốc #{item.get('id', '?')})",
                "status": "done" if item.get("completed") is True else "todo",
                "assignee": _ASSIGNEES.get(user_id, ""),
                "priority": "medium",
                "labels": ["api"],
            })
        return cleaned

    def fetch(self, limit=config.API_DEFAULT_LIMIT):
        """Lấy danh sách công việc đã làm sạch. Lỗi mạng -> dùng cache; không có cache -> []"""
        try:
            raw = self._download(limit)
            tasks = self._clean(raw)
            if tasks:
                self._cache_storage.save(tasks)
                self.last_source = "api"
                return tasks
        except (urllib.error.URLError, TimeoutError, OSError,
                ValueError, json.JSONDecodeError):
            pass

        self.last_source = "cache"
        return self.load_cache()

    def load_cache(self):
        data = self._cache_storage.load() or []
        return data if isinstance(data, list) else []

    def import_to_manager(self, task_manager, project_id, limit=config.API_DEFAULT_LIMIT):
        """Lấy dữ liệu rồi thêm vào TaskManager. Trả về số công việc đã thêm."""
        count = 0
        for item in self.fetch(limit):
            task_manager.add_task(project_id, **item)
            count += 1
        return count
