"""Công cụ dòng lệnh: thông tin môi trường, sinh dữ liệu mẫu, lấy API, xuất báo cáo.

Ví dụ:
    python tienich.py --info
    python tienich.py --sample 30
    python tienich.py --fetch 10
    python tienich.py --export all
"""
import sys

import config
from api_service import ApiService
from env_info import EnvInfo
from json_storage import JsonStorage
from project_manager import ProjectManager
from report_exporter import ReportExporter
from sample_data_generator import SampleDataGenerator
from task_manager import TaskManager


def _storage(name):
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return JsonStorage(str(config.DATA_DIR / name), str(config.BACKUP_DIR))


def run(argv=None):
    args = EnvInfo.parse_args(argv)
    did_something = False

    if args.info:
        print(EnvInfo.format_info())
        did_something = True

    if args.sample is not None:
        stats = SampleDataGenerator().reset_all_data(
            _storage(config.TASKS_FILE), _storage(config.PROJECTS_FILE),
            _storage(config.USERS_FILE), _storage(config.LOGS_FILE), args.sample)
        print(f"Đã tạo dữ liệu mẫu: {stats}")
        did_something = True

    if args.fetch is not None:
        projects = ProjectManager(_storage(config.PROJECTS_FILE))
        project = projects.get_all()[0] if projects.get_all() \
            else projects.add_project("Dữ liệu từ API")
        service = ApiService(_storage(config.API_CACHE_FILE))
        n = service.import_to_manager(
            TaskManager(_storage(config.TASKS_FILE)), project.id, args.fetch)
        print(f"Đã nhập {n} công việc (nguồn: {service.last_source}) vào dự án {project.id}.")
        did_something = True

    if args.export:
        manager = TaskManager(_storage(config.TASKS_FILE))
        tasks, exporter = manager.get_all(), ReportExporter(str(config.EXPORT_DIR))
        paths = []
        if args.export in ("csv", "all"):
            paths.append(exporter.export_csv(tasks, "tasks.csv"))
        if args.export in ("json", "all"):
            paths.append(exporter.export_json(tasks, "tasks.json"))
        if args.export in ("txt", "all"):
            paths.append(exporter.export_summary_text(manager.statistics(), "summary.txt"))
        print("Đã xuất:", *paths, sep="\n  ")
        did_something = True

    if not did_something:
        print("Chưa chọn thao tác nào. Dùng --help để xem hướng dẫn.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
