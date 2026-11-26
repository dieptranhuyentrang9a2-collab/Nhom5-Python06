from task import Task, STATUSES, PRIORITIES


class TaskManager:
    def __init__(self, storage):
        self._storage = storage
        self._tasks = [
            Task.from_dict(d)
            for d in (storage.load() or [])
        ]

    def _save(self):
        self._storage.save([
            task.to_dict() for task in self._tasks
        ])

    def _next_id(self):
        nums = []

        for task in self._tasks:
            task_id = str(task.id)

            if task_id.startswith("T") and task_id[1:].isdigit():
                nums.append(int(task_id[1:]))

        return f"T{max(nums, default=0) + 1:03d}"

    def add_task(self, project_id, title, **kwargs):
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Tên công việc không được để trống.")

        task = Task(
            self._next_id(),
            project_id,
            title.strip(),
            **kwargs
        )

        self._tasks.append(task)
        self._save()

        return task

    def get_all(self):
        return list(self._tasks)

    def get_by_id(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                return task

        return None

    def update_task(self, task_id, **changes):
        task = self.get_by_id(task_id)

        if task is None:
            return False

        allowed_fields = {
            "project_id", "title", "description",
            "status", "assignee", "due_date",
            "priority", "labels", "comments"
        }

        for key in changes:
            if key not in allowed_fields:
                raise ValueError(f"Thuộc tính không hợp lệ: {key}")

        if "title" in changes:
            if not isinstance(changes["title"], str) or not changes["title"].strip():
                raise ValueError("Tên công việc không được để trống.")

        if "status" in changes:
            if changes["status"] not in STATUSES:
                raise ValueError("Trạng thái công việc không hợp lệ.")

        if "priority" in changes:
            if changes["priority"] not in PRIORITIES:
                raise ValueError("Độ ưu tiên không hợp lệ.")

        for key, value in changes.items():
            if key == "title":
                value = value.strip()

            setattr(task, key, value)

        self._save()
        return True

    def delete_task(self, task_id):
        task = self.get_by_id(task_id)

        if task is None:
            return False

        self._tasks.remove(task)
        self._save()

        return True

    def search(self, keyword):
        if not isinstance(keyword, str):
            return []

        keyword = keyword.strip().casefold()

        if not keyword:
            return []

        return [
            task for task in self._tasks
            if keyword in task.title.casefold()
            or keyword in task.description.casefold()
        ]

    def filter_by(self, **conditions):
        return [
            task for task in self._tasks
            if all(
                getattr(task, key, None) == value
                for key, value in conditions.items()
            )
        ]

    def sort_by(self, field, reverse=False):
        allowed_fields = {
            "id", "title", "status", "assignee",
            "due_date", "priority", "project_id"
        }

        if field not in allowed_fields:
            raise ValueError(f"Không thể sắp xếp theo: {field}")

        return sorted(
            self._tasks,
            key=lambda task: (
                getattr(task, field) is None,
                getattr(task, field)
            ),
            reverse=reverse
        )

    def move_task(self, task_id, status):
        task = self.get_by_id(task_id)

        if task is None:
            return False

        task.move_to(status)
        self._save()

        return True

    def get_overdue(self):
        return [
            task for task in self._tasks
            if task.is_overdue()
        ]

    def statistics(self):
        stats = {
            "total": len(self._tasks),
            "todo": 0,
            "doing": 0,
            "done": 0,
            "overdue": len(self.get_overdue())
        }

        for task in self._tasks:
            if task.status in STATUSES:
                stats[task.status] += 1

        return stats
