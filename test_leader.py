from task_manager import TaskManager
from project_manager import ProjectManager
from activity_log import ActivityLog


# Bộ lưu trữ giả lập, không ghi vào JSON thật
class MemoryStorage:
    def __init__(self):
        self.data = []

    def load(self):
        return self.data

    def save(self, data):
        self.data = data


def test_task_manager():
    print("\n===== KIỂM THỬ TASK MANAGER =====")

    storage = MemoryStorage()
    manager = TaskManager(storage)

    # 1. Thêm công việc
    task1 = manager.add_task(
        "P001",
        "Hoàn thành báo cáo",
        description="Viết báo cáo đồ án",
        status="todo",
        priority="high"
    )

    task2 = manager.add_task(
        "P001",
        "Thiết kế giao diện",
        description="Thiết kế giao diện Kanban",
        status="doing",
        priority="low"
    )

    assert task1.id == "T001"
    assert task2.id == "T002"
    print("PASS: Thêm công việc và tạo ID")

    # 2. Tìm công việc
    assert manager.get_by_id("T001") is not None
    print("PASS: Tìm công việc theo ID")

    # 3. Cập nhật
    manager.update_task("T001", title="Hoàn thành báo cáo nhóm")
    assert manager.get_by_id("T001").title == "Hoàn thành báo cáo nhóm"
    print("PASS: Cập nhật công việc")

    # 4. Tìm kiếm
    results = manager.search("báo cáo")
    assert len(results) == 1
    print("PASS: Tìm kiếm công việc")

    # 5. Lọc
    results = manager.filter_by(status="doing")
    assert len(results) == 1
    print("PASS: Lọc công việc")

    # 6. Sắp xếp
    results = manager.sort_by("title")
    assert len(results) == 2
    print("PASS: Sắp xếp công việc")

    # 7. Chuyển trạng thái
    manager.move_task("T001", "done")
    assert manager.get_by_id("T001").status == "done"
    print("PASS: Chuyển trạng thái")

    # 8. Thống kê
    stats = manager.statistics()
    assert stats["total"] == 2
    assert stats["done"] == 1
    assert stats["doing"] == 1
    print("PASS: Thống kê công việc")

    # 9. Xóa
    assert manager.delete_task("T002") is True
    assert manager.get_by_id("T002") is None
    print("PASS: Xóa công việc")


def test_project_manager():
    print("\n===== KIỂM THỬ PROJECT MANAGER =====")

    storage = MemoryStorage()
    manager = ProjectManager(storage)

    # 1. Thêm dự án
    project = manager.add_project(
        "Đồ án Kanban",
        "Quản lý công việc nhóm"
    )

    assert project.id == "P001"
    print("PASS: Thêm dự án và tạo ID")

    # 2. Tìm dự án
    assert manager.get_by_id("P001") is not None
    print("PASS: Tìm dự án theo ID")

    # 3. Cập nhật
    manager.update_project("P001", name="Kanban Python")
    assert manager.get_by_id("P001").name == "Kanban Python"
    print("PASS: Cập nhật dự án")

    # 4. Thêm thành viên
    manager.add_member("P001", "Trang")
    assert "Trang" in manager.get_by_id("P001").members
    print("PASS: Thêm thành viên")

    # 5. Xóa thành viên
    assert manager.remove_member("P001", "Trang") is True
    assert "Trang" not in manager.get_by_id("P001").members
    print("PASS: Xóa thành viên")

    # 6. Xóa dự án
    assert manager.delete_project("P001") is True
    assert manager.get_by_id("P001") is None
    print("PASS: Xóa dự án")


def test_activity_log():
    print("\n===== KIỂM THỬ ACTIVITY LOG =====")

    storage = MemoryStorage()
    log_manager = ActivityLog(storage)

    # 1. Ghi nhật ký
    log_manager.write("Trang", "Tạo công việc mới")

    assert len(log_manager.get_all()) == 1
    print("PASS: Ghi nhật ký hoạt động")

    # 2. Lọc nhật ký
    results = log_manager.get_by_user("trang")
    assert len(results) == 1
    print("PASS: Lọc nhật ký theo người dùng")


if __name__ == "__main__":
    try:
        test_task_manager()
        test_project_manager()
        test_activity_log()

        print("\n===== KẾT QUẢ =====")
        print("TẤT CẢ KIỂM THỬ ĐỀU THÀNH CÔNG!")

    except Exception as error:
        print("\nKIỂM THỬ THẤT BẠI!")
        print("Lỗi:", error)
        raise
