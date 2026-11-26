from datetime import date, datetime

from base_entity import BaseEntity

STATUSES = ("todo", "doing", "done")
PRIORITIES = ("low", "medium", "high")


class Task(BaseEntity):
    def __init__(self, id, project_id, title, description="", status="todo",
                 assignee="", due_date=None, priority="medium",
                 labels=None, comments=None):

        super().__init__(id)

        self.project_id = project_id
        self.title = title
        self.description = description
        self.status = status
        self.assignee = assignee
        self.due_date = due_date
        self.priority = priority
        self.labels = [] if labels is None else labels
        self.comments = [] if comments is None else comments

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "assignee": self.assignee,
            "due_date": self.due_date,
            "priority": self.priority,
            "labels": self.labels,
            "comments": self.comments,
        }

    def is_overdue(self):
        """Kiểm tra công việc quá hạn."""
        if not self.due_date or self.status == "done":
            return False

        try:
            due = datetime.strptime(
                self.due_date, "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError):
            return False

        return due < date.today()

    def move_to(self, status):
        """Thay đổi trạng thái công việc."""
        if status not in STATUSES:
            raise ValueError(f"Trạng thái không hợp lệ: {status}")

        self.status = status

    def add_comment(self, user, text):
        """Thêm bình luận vào công việc."""
        self.comments.append({
            "user": user,
            "text": text,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
