import argparse
import platform
import sys

import config


class EnvInfo:
    """Lớp tiện ích dùng module sys / platform: thông tin môi trường và tham số dòng lệnh."""

    @staticmethod
    def get_info():
        """Trả về dict thông tin môi trường chạy (phục vụ mục "Giới thiệu" và báo cáo)."""
        return {
            "app": config.APP_NAME,
            "version": config.APP_VERSION,
            "python": sys.version.split()[0],
            "platform": sys.platform,
            "os": f"{platform.system()} {platform.release()}",
            "executable": sys.executable,
            "frozen": bool(getattr(sys, "frozen", False)),
            "data_dir": str(config.DATA_DIR),
            "encoding": sys.getdefaultencoding(),
        }

    @staticmethod
    def format_info():
        """Chuỗi nhiều dòng để hiển thị lên hộp thoại hoặc terminal."""
        labels = {
            "app": "Ứng dụng", "version": "Phiên bản", "python": "Python",
            "platform": "Nền tảng", "os": "Hệ điều hành",
            "executable": "Trình thông dịch", "frozen": "Bản đóng gói",
            "data_dir": "Thư mục dữ liệu", "encoding": "Mã hóa",
        }
        info = EnvInfo.get_info()
        return "\n".join(f"{labels[k]}: {v}" for k, v in info.items())

    @staticmethod
    def parse_args(argv=None):
        """Đọc tham số dòng lệnh. argv=None -> dùng sys.argv[1:]."""
        parser = argparse.ArgumentParser(
            prog="tienich",
            description="Công cụ dòng lệnh của ứng dụng Quản lý công việc Kanban",
        )
        parser.add_argument("--info", action="store_true",
                            help="In thông tin môi trường rồi thoát")
        parser.add_argument("--sample", type=int, metavar="N", nargs="?",
                            const=config.SAMPLE_TASK_COUNT,
                            help="Xóa dữ liệu cũ (có sao lưu) và sinh N công việc mẫu")
        parser.add_argument("--fetch", type=int, metavar="N", nargs="?",
                            const=config.API_DEFAULT_LIMIT,
                            help="Lấy N công việc từ API và nhập vào hệ thống")
        parser.add_argument("--export", choices=["csv", "json", "txt", "all"],
                            help="Xuất báo cáo công việc ra thư mục exports/")
        return parser.parse_args(argv)
