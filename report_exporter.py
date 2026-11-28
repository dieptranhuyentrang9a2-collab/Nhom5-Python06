import csv
import json
import os
from datetime import datetime

from task import STATUSES

_FIELDS = ["id", "project_id", "title", "description", "status",
           "assignee", "due_date", "priority", "labels"]


class ReportExporter:
    """Xuất báo cáo công việc ra CSV / JSON / văn bản tóm tắt."""

    def __init__(self, output_dir="exports"):
        self._output_dir = output_dir

    def _resolve(self, path):
        """Đường dẫn tương đối được đặt trong thư mục xuất; tự tạo thư mục."""
        full = path if os.path.isabs(path) else os.path.join(self._output_dir, path)
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        return full

    @staticmethod
    def _row(task):
        d = task.to_dict() if hasattr(task, "to_dict") else dict(task)
        row = {k: d.get(k, "") for k in _FIELDS}
        row["labels"] = ", ".join(d.get("labels") or [])
        return row

    def export_csv(self, tasks, path):
        full = self._resolve(path)
        # utf-8-sig để Excel mở tiếng Việt không bị lỗi font
        with open(full, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=_FIELDS)
            writer.writeheader()
            for task in tasks:
                writer.writerow(self._row(task))
        return full

    def export_json(self, tasks, path):
        full = self._resolve(path)
        data = [t.to_dict() if hasattr(t, "to_dict") else dict(t) for t in tasks]
        with open(full, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return full

    def export_summary_text(self, stats, path):
        full = self._resolve(path)
        total = stats.get("total", 0)
        lines = [
            "BÁO CÁO TỔNG HỢP CÔNG VIỆC",
            f"Thời gian xuất: {datetime.now():%Y-%m-%d %H:%M:%S}",
            "=" * 36,
            f"Tổng số công việc : {total}",
        ]
        for code, label in STATUSES.items():
            n = stats.get(code, 0)
            pct = f"{n * 100 / total:.1f}%" if total else "0.0%"
            lines.append(f"{label:<18}: {n} ({pct})")
        lines.append(f"{'Quá hạn':<18}: {stats.get('overdue', 0)}")
        with open(full, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return full
