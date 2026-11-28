"""Kiểm thử phần việc của Vy: ApiService, SampleDataGenerator, ReportExporter, EnvInfo.

Chạy:  python -m unittest test_vy -v   (không cần mạng, không ghi vào data/ thật)
"""
import csv
import json
import os
import tempfile
import unittest
from unittest import mock

import config
from api_service import ApiService
from env_info import EnvInfo
from json_storage import JsonStorage
from report_exporter import ReportExporter
from sample_data_generator import SampleDataGenerator
from task_manager import TaskManager


class MemoryStorage:
    def __init__(self):
        self.data = []

    def load(self):
        return self.data

    def save(self, data):
        self.data = data
        return True

    def backup(self):
        return True


RAW = [
    {"userId": 1, "id": 1, "title": "delectus aut autem", "completed": False},
    {"userId": 5, "id": 2, "title": "  quis   ut nam  ", "completed": True},
    {"userId": 9, "id": 3, "title": "", "completed": False},        # tiêu đề rỗng
    "rác", None,                                                    # không phải dict
]


class TestConfig(unittest.TestCase):
    def test_paths(self):
        self.assertEqual(config.BACKUP_DIR.parent, config.DATA_DIR)
        self.assertTrue(config.API_URL.startswith("https://"))


class TestEnvInfo(unittest.TestCase):
    def test_get_info(self):
        info = EnvInfo.get_info()
        for key in ("python", "platform", "version", "data_dir"):
            self.assertIn(key, info)
        self.assertFalse(info["frozen"])

    def test_parse_args(self):
        a = EnvInfo.parse_args(["--info", "--sample", "5", "--export", "csv"])
        self.assertTrue(a.info)
        self.assertEqual(a.sample, 5)
        self.assertEqual(a.export, "csv")
        self.assertIsNone(a.fetch)
        self.assertEqual(EnvInfo.parse_args(["--sample"]).sample, config.SAMPLE_TASK_COUNT)

    def test_parse_args_invalid(self):
        with self.assertRaises(SystemExit):
            EnvInfo.parse_args(["--export", "pdf"])


class TestApiService(unittest.TestCase):
    def test_clean(self):
        out = ApiService._clean(RAW)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["title"], "Delectus aut autem")
        self.assertEqual(out[0]["status"], "todo")
        self.assertEqual(out[1]["title"], "Quis ut nam")
        self.assertEqual(out[1]["status"], "done")
        self.assertEqual(out[1]["assignee"], "thuyvy")

    def test_clean_invalid_input(self):
        self.assertEqual(ApiService._clean(None), [])
        self.assertEqual(ApiService._clean({"a": 1}), [])

    def test_fetch_ok_saves_cache(self):
        cache = MemoryStorage()
        svc = ApiService(cache)
        with mock.patch.object(svc, "_download", return_value=RAW):
            tasks = svc.fetch(3)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(svc.last_source, "api")
        self.assertEqual(len(cache.data), 2)

    def test_fetch_network_error_uses_cache(self):
        import urllib.error
        cache = MemoryStorage()
        cache.data = ApiService._clean(RAW)
        svc = ApiService(cache)
        with mock.patch.object(svc, "_download",
                               side_effect=urllib.error.URLError("offline")):
            tasks = svc.fetch()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(svc.last_source, "cache")

    def test_fetch_error_no_cache(self):
        svc = ApiService(MemoryStorage())
        with mock.patch.object(svc, "_download", side_effect=TimeoutError):
            self.assertEqual(svc.fetch(), [])

    def test_import_to_manager(self):
        svc = ApiService(MemoryStorage())
        manager = TaskManager(MemoryStorage())
        with mock.patch.object(svc, "_download", return_value=RAW):
            n = svc.import_to_manager(manager, "P001")
        self.assertEqual(n, 2)
        self.assertEqual(manager.get_by_id("T002").status, "done")


class TestSampleData(unittest.TestCase):
    def test_generate_tasks_count_and_fields(self):
        tasks = SampleDataGenerator(1).generate_tasks(15, ["P001", "P002"])
        self.assertEqual(len(tasks), 15)
        for t in tasks:
            self.assertIn(t["status"], ("todo", "doing", "done"))
            self.assertIn(t["priority"], ("low", "medium", "high"))
            self.assertIn(t["project_id"], ("P001", "P002"))

    def test_same_seed_same_data(self):
        self.assertEqual(SampleDataGenerator(7).generate_tasks(10),
                         SampleDataGenerator(7).generate_tasks(10))

    def test_different_seed_differs(self):
        self.assertNotEqual(SampleDataGenerator(1).generate_tasks(10),
                            SampleDataGenerator(2).generate_tasks(10))

    def test_invalid_n(self):
        with self.assertRaises(ValueError):
            SampleDataGenerator().generate_tasks(-1)
        with self.assertRaises(ValueError):
            SampleDataGenerator().generate_tasks(3, [])

    def test_generate_users_valid_for_validator(self):
        from validator import Validator
        for u in SampleDataGenerator().generate_users():
            self.assertTrue(Validator.is_valid_username(u["username"]))
            self.assertTrue(Validator.is_valid_email(u["email"]))

    def test_reset_all_data(self):
        with tempfile.TemporaryDirectory() as d:
            bk = os.path.join(d, "bk")
            s = [JsonStorage(os.path.join(d, n), bk)
                 for n in ("t.json", "p.json", "u.json", "l.json")]
            stats = SampleDataGenerator().reset_all_data(*s, n_tasks=12)
            self.assertEqual(stats, {"users": 5, "projects": 2, "tasks": 12})
            self.assertEqual(len(s[0].load()), 12)
            # chạy lần 2: kết quả không cộng dồn
            stats = SampleDataGenerator().reset_all_data(*s, n_tasks=4)
            self.assertEqual(len(s[0].load()), 4)
            self.assertTrue(any(u["username"] == "admin" for u in s[2].load()))


class TestReportExporter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.exp = ReportExporter(self.tmp.name)
        self.manager = TaskManager(MemoryStorage())
        self.manager.add_task("P001", "Việc có dấu, và \"ngoặc\"", status="done",
                              labels=["ui", "bug"])
        self.manager.add_task("P001", "Việc 2", due_date="2000-01-01")

    @staticmethod
    def _read(path):
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_csv(self):
        path = self.exp.export_csv(self.manager.get_all(), "a/tasks.csv")
        with open(path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["title"], 'Việc có dấu, và "ngoặc"')
        self.assertEqual(rows[0]["labels"], "ui, bug")

    def test_json(self):
        path = self.exp.export_json(self.manager.get_all(), "tasks.json")
        with open(path, encoding="utf-8") as f:
            self.assertEqual(json.load(f)[1]["id"], "T002")

    def test_summary(self):
        path = self.exp.export_summary_text(self.manager.statistics(), "s.txt")
        text = self._read(path)
        self.assertIn("Tổng số công việc : 2", text)
        self.assertIn("Quá hạn", text)
        self.assertIn("50.0%", text)

    def test_summary_empty(self):
        path = self.exp.export_summary_text({}, "e.txt")
        self.assertIn("0.0%", self._read(path))

    def test_empty_export(self):
        path = self.exp.export_csv([], "empty.csv")
        self.assertTrue(os.path.getsize(path) > 0)   # vẫn có dòng tiêu đề


if __name__ == "__main__":
    unittest.main(verbosity=2)
