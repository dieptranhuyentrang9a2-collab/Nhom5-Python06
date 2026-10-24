from abc import ABC, abstractmethod
 class BaseEntity(ABC):
    """Lớp cha trừu tượng cho Task, Project, User."""
   def __init__(self, id):
        self._id = id
    @property
    def id(self):
        return self._id
    @abstractmethod
    def to_dict(self):
        """Chuyển đối tượng thành dict để lưu JSON."""
    @classmethod
    def from_dict(cls, data):
        """Tạo đối tượng từ dict đọc từ JSON."""
        return cls(**data)
 
