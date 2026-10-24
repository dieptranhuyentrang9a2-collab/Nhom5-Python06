from base_entity import BaseEntity
 
 
class Project(BaseEntity):
    def __init__(self, id, name, description="", members=None):
        super().__init__(id)
        self.name = name
        self.description = description
        self.members = members or []
 
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "members": self.members,
        }
 
    def add_member(self, username):
        if username not in self.members:
            self.members.append(username)
 
    def remove_member(self, username):
        if username in self.members:
            self.members.remove(username)
 
