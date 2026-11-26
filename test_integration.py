import tempfile
import os

from json_storage import JsonStorage
from task_manager import TaskManager
from project_manager import ProjectManager
from activity_log import ActivityLog


def test_integration():
    print("\n===== KIỂM THỬ TÍCH HỢP JSON STORAGE =====")

    with tempfile.TemporaryDirectory() as temp_dir:
        backup_dir = os.path.join(temp_dir, "backups")

        # Kiểm thử Task
        task_storage = JsonStorage(
            os.path.join(temp_dir, "tasks.json"),
            backup_dir
        )
        task_manager = TaskManager(task_storage)

        task = task_manager.add_task(
            "P001",
            "Kiểm thử tích hợp"
        )
        assert task.id == "T001"
        print("PASS: Ghi Task vào file JSON")

        new_task_manager = TaskManager(task_storage)
        assert new_task_manager.get_by_id("T001") is not None
        print("PASS: Đọc lại Task từ file JSON")

        # Kiểm thử Project
        project_storage = JsonStorage(
            os.path.join(temp_dir, "projects.json"),
            backup_dir
        )
        project_manager = ProjectManager(project_storage)

        project = project_manager.add_project("Dự án Kanban")
        assert project.id == "P001"
        print("PASS: Ghi Project vào file JSON")

        new_project_manager = ProjectManager(project_storage)
        assert new_project_manager.get_by_id("P001") is not None
        print("PASS: Đọc lại Project từ file JSON")

        # Kiểm thử ActivityLog
        log_storage = JsonStorage(
            os.path.join(temp_dir, "logs.json"),
            backup_dir
        )
        activity_log = ActivityLog(log_storage)

        activity_log.write("trang", "Tạo công việc")
        assert len(activity_log.get_all()) == 1
        print("PASS: Ghi nhật ký vào JSON")

        new_activity_log = ActivityLog(log_storage)
        assert len(new_activity_log.get_all()) == 1
        print("PASS: Đọc lại nhật ký từ JSON")

        # Kiểm thử Backup và Restore
        assert task_storage.backup() is True
        print("PASS: Sao lưu dữ liệu JSON")

        task_storage.save([])
        restored_data = task_storage.restore()

        assert len(restored_data) == 1
        assert restored_data[0]["id"] == "T001"
        print("PASS: Khôi phục dữ liệu từ backup")

    print("\nTẤT CẢ KIỂM THỬ TÍCH HỢP ĐỀU THÀNH CÔNG!")


if __name__ == "__main__":
    test_integration()
