from task_manager import TaskManager
from project_manager import ProjectManager
from activity_log import ActivityLog
from task import Task
from project import Project


# Bộ lưu trữ giả lập, không ghi vào JSON thật
class MemoryStorage:
    def __init__(self):
        self.data = []

    def load(self):
        return self.data

    def save(self, data):
        self.data = data

def expect_value_error(func):
    """Kiểm tra hàm có phát sinh ValueError hay không."""
    try:
        func()
    except ValueError:
        return True

    return False
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
def test_exceptions():
    print("\n===== KIỂM THỬ TRƯỜNG HỢP NGOẠI LỆ =====")

    # Kiểm thử TaskManager
    task_storage = MemoryStorage()
    task_manager = TaskManager(task_storage)

    assert expect_value_error(
        lambda: task_manager.add_task("P001", "")
    )
    print("PASS: Không cho thêm Task có tiêu đề rỗng")

    assert expect_value_error(
        lambda: task_manager.move_task("T001", "invalid")
    ) is False

    # Kiểm tra trạng thái không hợp lệ với Task đang tồn tại
    task = task_manager.add_task("P001", "Kiểm thử")
    assert expect_value_error(
        lambda: task_manager.move_task(task.id, "invalid")
    )
    print("PASS: Không cho chuyển sang trạng thái không hợp lệ")

    assert task_manager.update_task("T999", title="Không tồn tại") is False
    print("PASS: Không cập nhật Task không tồn tại")

    assert task_manager.delete_task("T999") is False
    print("PASS: Không xóa Task không tồn tại")

    assert expect_value_error(
        lambda: task_manager.update_task(task.id, status="invalid")
    )
    print("PASS: Không cập nhật trạng thái không hợp lệ")

    # Kiểm thử ProjectManager
    project_storage = MemoryStorage()
    project_manager = ProjectManager(project_storage)

    assert expect_value_error(
        lambda: project_manager.add_project("")
    )
    print("PASS: Không cho tạo Project có tên rỗng")

    assert project_manager.update_project(
        "P999", name="Không tồn tại"
    ) is False
    print("PASS: Không cập nhật Project không tồn tại")

    assert project_manager.delete_project("P999") is False
    print("PASS: Không xóa Project không tồn tại")

    # Kiểm thử ActivityLog
    log_storage = MemoryStorage()
    log_manager = ActivityLog(log_storage)

    assert expect_value_error(
        lambda: log_manager.write("", "Tạo công việc")
    )
    print("PASS: Không ghi nhật ký khi tên người dùng rỗng")

    assert expect_value_error(
        lambda: log_manager.write("Trang", "")
    )
    print("PASS: Không ghi nhật ký khi nội dung rỗng")

def test_data_persistence():
    print("\n===== KIỂM THỬ LƯU VÀ KHÔI PHỤC DỮ LIỆU =====")

    # 1. Kiểm tra Task
    task_storage = MemoryStorage()
    manager1 = TaskManager(task_storage)

    task = manager1.add_task(
        "P001",
        "Kiểm tra lưu dữ liệu",
        description="Kiểm tra khả năng khôi phục"
    )

    # Tạo Manager mới sử dụng cùng Storage
    manager2 = TaskManager(task_storage)

    restored_task = manager2.get_by_id(task.id)

    assert restored_task is not None
    assert restored_task.title == "Kiểm tra lưu dữ liệu"
    print("PASS: Khôi phục Task từ dữ liệu đã lưu")

    new_task = manager2.add_task("P001", "Task tiếp theo")
    assert new_task.id == "T002"
    print("PASS: ID Task tiếp tục tăng sau khi khôi phục")

    # 2. Kiểm tra Project
    project_storage = MemoryStorage()
    project_manager1 = ProjectManager(project_storage)

    project = project_manager1.add_project(
        "Dự án kiểm thử",
        "Kiểm tra lưu Project"
    )

    project_manager2 = ProjectManager(project_storage)

    restored_project = project_manager2.get_by_id(project.id)

    assert restored_project is not None
    assert restored_project.name == "Dự án kiểm thử"
    print("PASS: Khôi phục Project từ dữ liệu đã lưu")

    # 3. Kiểm tra ActivityLog
    log_storage = MemoryStorage()
    log1 = ActivityLog(log_storage)

    log1.write("Trang", "Kiểm tra lưu nhật ký")

    log2 = ActivityLog(log_storage)

    logs = log2.get_all()

    assert len(logs) == 1
    assert logs[0]["user"] == "Trang"
    print("PASS: Khôi phục nhật ký hoạt động")
def test_task_class():
    print("\n===== KIỂM THỬ LỚP TASK =====")

    task = Task(
        "T001",
        "P001",
        "Hoàn thành báo cáo",
        due_date="2000-01-01"
    )

    assert task.is_overdue() is True
    print("PASS: Nhận diện công việc quá hạn")

    task.move_to("done")
    assert task.status == "done"
    assert task.is_overdue() is False
    print("PASS: Công việc hoàn thành không còn bị tính quá hạn")

    task.add_comment("admin", "Đã kiểm tra")
    assert len(task.comments) == 1
    assert task.comments[0]["user"] == "admin"
    assert task.comments[0]["text"] == "Đã kiểm tra"
    print("PASS: Thêm bình luận cho công việc")

    task_invalid_date = Task(
        "T002",
        "P001",
        "Công việc thử nghiệm",
        due_date="ngay-khong-hop-le"
    )

    assert task_invalid_date.is_overdue() is False
    print("PASS: Xử lý ngày đến hạn không hợp lệ")


def test_project_class():
    print("\n===== KIỂM THỬ LỚP PROJECT =====")

    project = Project("P001", "Dự án Kanban")

    project.add_member("trang")
    assert "trang" in project.members
    print("PASS: Thêm thành viên vào dự án")

    project.add_member("trang")
    assert project.members.count("trang") == 1
    print("PASS: Không thêm trùng thành viên")

    project.remove_member("trang")
    assert "trang" not in project.members
    print("PASS: Xóa thành viên khỏi dự án")

if __name__ == "__main__":
    try:
        test_task_manager()
        test_project_manager()
        test_activity_log()
        test_exceptions()
        test_data_persistence()
        test_task_class()
        test_project_class()

        print("\n===== KẾT QUẢ =====")
        print("TẤT CẢ KIỂM THỬ ĐỀU THÀNH CÔNG!")

    except Exception as error:
        print("\nKIỂM THỬ THẤT BẠI!")
        print("Lỗi:", error)
        raise