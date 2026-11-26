
from base_entity import BaseEntity


class Project(BaseEntity):
    def __init__(self, id, name, description="", members=None):
        super().__init__(id)

        self.name = name
        self.description = description
        self.members = [] if members is None else members

    def to_dict(self):
        """Chuyển thông tin dự án thành dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "members": self.members,
        }

    def add_member(self, username):
        """Thêm thành viên vào dự án."""
        if username not in self.members:
            self.members.append(username)

    def remove_member(self, username):
        """Xóa thành viên khỏi dự án."""
        if username in self.members:
            self.members.remove(username)
