from project import Project


class ProjectManager:
    def __init__(self, storage):
        self._storage = storage
        self._projects = [
            Project.from_dict(data)
            for data in (storage.load() or [])
        ]

    def _save(self):
        self._storage.save([
            project.to_dict()
            for project in self._projects
        ])

    def _get(self, project_id):
        for project in self._projects:
            if project.id == project_id:
                return project

        return None

    def get_by_id(self, project_id):
        """Lấy dự án theo ID."""
        return self._get(project_id)

    def add_project(self, name, description=""):
        """Thêm dự án mới."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Tên dự án không được để trống.")

        nums = []

        for project in self._projects:
            project_id = str(project.id)

            if project_id.startswith("P") and project_id[1:].isdigit():
                nums.append(int(project_id[1:]))

        new_id = f"P{max(nums, default=0) + 1:03d}"

        project = Project(
            new_id,
            name.strip(),
            description
        )

        self._projects.append(project)
        self._save()

        return project

    def get_all(self):
        return list(self._projects)

    def update_project(self, project_id, **changes):
        """Cập nhật thông tin dự án."""
        project = self._get(project_id)

        if project is None:
            return False

        allowed_fields = {"name", "description"}

        for key in changes:
            if key not in allowed_fields:
                raise ValueError(f"Thuộc tính không hợp lệ: {key}")

        if "name" in changes:
            if not isinstance(changes["name"], str) or not changes["name"].strip():
                raise ValueError("Tên dự án không được để trống.")

        for key, value in changes.items():
            if key == "name":
                value = value.strip()

            setattr(project, key, value)

        self._save()
        return True

    def delete_project(self, project_id):
        """Xóa dự án."""
        project = self._get(project_id)

        if project is None:
            return False

        self._projects.remove(project)
        self._save()

        return True
    def add_member(self, project_id, username):
        """Thêm thành viên vào dự án."""
        project = self._get(project_id)

        if project is None:
            return False

        if not isinstance(username, str) or not username.strip():
            raise ValueError("Tên thành viên không hợp lệ.")

        project.add_member(username.strip())
        self._save()

        return True

    def remove_member(self, project_id, username):
        """Xóa thành viên khỏi dự án."""
        project = self._get(project_id)

        if project is None:
            return False

        if not isinstance(username, str) or not username.strip():
            return False

        username = username.strip()

        if username not in project.members:
            return False

        project.remove_member(username)
        self._save()

        return True