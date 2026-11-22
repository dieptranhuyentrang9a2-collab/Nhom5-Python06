
import json
import os
import shutil


class JsonStorage:
    """Lớp quản lý đọc, ghi và sao lưu dữ liệu JSON."""

    def __init__(self, path, backup_dir="backups"):
        self._path = path
        self._backup_dir = backup_dir

        # Tạo thư mục chứa file dữ liệu
        folder = os.path.dirname(self._path)

        if folder:
            os.makedirs(folder, exist_ok=True)

        # Tạo thư mục sao lưu
        os.makedirs(self._backup_dir, exist_ok=True)

    # Đọc dữ liệu từ file JSON
    def load(self):
        try:
            with open(
                self._path,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)

        except FileNotFoundError:
            return []

        except json.JSONDecodeError:
            print("Lỗi: Dữ liệu JSON không hợp lệ.")
            return []

        except OSError as error:
            print("Lỗi khi đọc dữ liệu:", error)
            return []

    # Ghi dữ liệu vào file JSON
    def save(self, data):
        temp_path = self._path + ".tmp"

        try:
            folder = os.path.dirname(self._path)

            if folder:
                os.makedirs(folder, exist_ok=True)

            with open(
                temp_path,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

            # Thay thế file cũ bằng file mới
            os.replace(temp_path, self._path)

            return True

        except (OSError, TypeError, ValueError) as error:
            print("Lỗi khi lưu dữ liệu:", error)
            return False

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    # Sao lưu dữ liệu
    def backup(self):
        try:
            if not os.path.exists(self._path):
                print("Không tìm thấy file cần sao lưu.")
                return False

            os.makedirs(self._backup_dir, exist_ok=True)

            file_name = os.path.basename(self._path)
            backup_path = os.path.join(
                self._backup_dir,
                file_name + ".bak"
            )

            shutil.copy2(self._path, backup_path)

            return True

        except OSError as error:
            print("Lỗi khi sao lưu:", error)
            return False

    # Khôi phục dữ liệu
    def restore(self):
        file_name = os.path.basename(self._path)

        backup_path = os.path.join(
            self._backup_dir,
            file_name + ".bak"
        )

        try:
            with open(
                backup_path,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if self.save(data):
                return data

            return []

        except FileNotFoundError:
            print("Không tìm thấy file sao lưu.")
            return []

        except json.JSONDecodeError:
            print("File sao lưu không hợp lệ.")
            return []

        except OSError as error:
            print("Lỗi khi khôi phục:", error)
            return []
