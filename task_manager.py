from task import Task
 
 
class TaskManager:
    def __init__(self, storage):
        self._storage = storage
        self._tasks = [Task.from_dict(d) for d in (storage.load() or [])]
 
    def _save(self):
        self._storage.save([t.to_dict() for t in self._tasks])
 
    def _next_id(self):
        nums = [int(t.id[1:]) for t in self._tasks
                if t.id[1:].isdigit()]
        return f"T{max(nums, default=0) + 1:03d}"
 
    def add_task(self, project_id, title, **kwargs):
        task = Task(self._next_id(), project_id, title, **kwargs)
        self._tasks.append(task)
        self._save()
        return task
 
    def get_all(self):
        return list(self._tasks)
 
    def get_by_id(self, task_id):
        for t in self._tasks:
            if t.id == task_id:
                return t
        return None
 
    def update_task(self, task_id, **changes):
        task = self.get_by_id(task_id)
        if task is None:
            return False
        for key, value in changes.items():
            if hasattr(task, key) and key != "id":
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
        kw = keyword.lower()
        return [t for t in self._tasks
                if kw in t.title.lower() or kw in t.description.lower()]
 
    def filter_by(self, **conditions):
        """Ví dụ: filter_by(status="todo", assignee="trang")"""
        return [t for t in self._tasks
                if all(getattr(t, k, None) == v for k, v in conditions.items())]
 
    def sort_by(self, field, reverse=False):
        return sorted(self._tasks,
                      key=lambda t: (getattr(t, field) is None, getattr(t, field)),
                      reverse=reverse)
 
    def move_task(self, task_id, status):
        task = self.get_by_id(task_id)
        if task is None:
            return False
        task.move_to(status)
        self._save()
        return True
 
    def get_overdue(self):
        return [t for t in self._tasks if t.is_overdue()]
 
    def statistics(self):
        stats = {"total": len(self._tasks), "todo": 0, "doing": 0,
                 "done": 0, "overdue": len(self.get_overdue())}
        for t in self._tasks:
            if t.status in stats:
                stats[t.status] += 1
        return stats
