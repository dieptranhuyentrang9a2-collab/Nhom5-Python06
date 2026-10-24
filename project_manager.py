from project import Project
 
 
class ProjectManager:
    def __init__(self, storage):
        self._storage = storage
        self._projects = [Project.from_dict(d) for d in (storage.load() or [])]
 
    def _save(self):
        self._storage.save([p.to_dict() for p in self._projects])
 
    def _get(self, project_id):
        for p in self._projects:
            if p.id == project_id:
                return p
        return None
 
    def add_project(self, name, description=""):
        nums = [int(p.id[1:]) for p in self._projects if p.id[1:].isdigit()]
        project = Project(f"P{max(nums, default=0) + 1:03d}", name, description)
        self._projects.append(project)
        self._save()
        return project
 
    def get_all(self):
        return list(self._projects)
 
    def update_project(self, project_id, **changes):
        project = self._get(project_id)
        if project is None:
            return False
        for key, value in changes.items():
            if hasattr(project, key) and key != "id":
                setattr(project, key, value)
        self._save()
        return True
 
    def delete_project(self, project_id):
        project = self._get(project_id)
        if project is None:
            return False
        self._projects.remove(project)
        self._save()
        return True
 
    def add_member(self, project_id, username):
        project = self._get(project_id)
        if project is None:
            return False
        project.add_member(username)
        self._save()
        return True
 
