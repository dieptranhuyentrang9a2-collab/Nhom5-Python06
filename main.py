import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import tkinter.font as tkfont


# =========================================================
# KẾT NỐI CÁC MODULE NGHIỆP VỤ
# =========================================================

from json_storage import JsonStorage
from task_manager import TaskManager
from project_manager import ProjectManager
from auth_manager import AuthManager
from activity_log import ActivityLog
from validator import Validator
from task import STATUSES, PRIORITIES

FONT_BODY = "Segoe UI"
FONT_DISPLAY = "Trebuchet MS"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"

# =========================================================
# KHỞI TẠO HỆ THỐNG LƯU TRỮ VÀ QUẢN LÝ DỮ LIỆU
# =========================================================

DATA_DIR.mkdir(parents=True, exist_ok=True)


def make_storage(file_name):
    """Tạo JsonStorage trong thư mục data, bản sao lưu nằm trong data/backups."""
    return JsonStorage(str(DATA_DIR / file_name), str(BACKUP_DIR))


task_storage = make_storage("tasks.json")
project_storage = make_storage("projects.json")
user_storage = make_storage("users.json")
log_storage = make_storage("logs.json")

# Khởi tạo bộ quản lý công việc, dự án, tài khoản và nhật ký
task_manager = TaskManager(task_storage)
project_manager = ProjectManager(project_storage)
activity_log = ActivityLog(log_storage)
auth_manager = AuthManager(user_storage, activity_log)

# =========================================================
# BẢNG MÀU
# =========================================================

COLORS = {
    "blue": "#7186D8",
    "blue_light": "#E9ECFF",
    "text": "#30365F",
    "muted": "#8589A8",
    "white": "#FFFFFF",
    "border": "#E6E5F2",
    "board": "#EDF0FA",
    "green": "#4D9B83",
    "green_light": "#E0F4ED",
    "yellow": "#C18B3A",
    "yellow_light": "#FFF2D9",
    "red": "#D66F83",
    "red_light": "#FCE8ED",
    "purple": "#8B79C8",
    "purple_light": "#F0ECFF",
    "lavender": "#E7E5F7",
    "mint": "#DDF1EC",
    "surface": "#FBFAFF",
    "ink": "#34395F"
}

# Màu riêng cho từng trạng thái (dùng ở cột, thẻ thống kê, biểu đồ)
STATUS_STYLES = {
    "todo": {"accent": "#C18B3A", "tint": "#FFF2D9", "icon": "○"},
    "doing": {"accent": "#7186D8", "tint": "#EEF0FF", "icon": "◷"},
    "done": {"accent": "#4D9B83", "tint": "#E0F4ED", "icon": "✓"}
}

PRIORITY_STYLES = {
    "high": (COLORS["red_light"], COLORS["red"]),
    "medium": (COLORS["yellow_light"], COLORS["yellow"]),
    "low": (COLORS["green_light"], COLORS["green"])
}


# =========================================================
# HÀM TIỆN ÍCH GIAO DIỆN
# =========================================================

def setup_theme(root):
    """Chọn font có sẵn trên máy và cấu hình kiểu ttk cho toàn ứng dụng."""
    global FONT_BODY, FONT_DISPLAY

    available_fonts = set(tkfont.families(root))
    FONT_BODY = next(
        (name for name in ("Inter", "Aptos", "Segoe UI", "Arial")
         if name in available_fonts),
        "TkDefaultFont"
    )
    FONT_DISPLAY = next(
        (name for name in ("Inter Display", "Segoe UI Variable Display",
                           "Aptos Display", "Trebuchet MS", FONT_BODY)
         if name in available_fonts),
        FONT_BODY
    )

    root.option_add("*Font", f"{{{FONT_BODY}}} 10")

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "TCombobox",
        fieldbackground="#F8F8FE",
        background="#E9ECFF",
        foreground=COLORS["text"],
        bordercolor="#DCDDF0",
        padding=7
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", "#F8F8FE")],
        selectbackground=[("readonly", "#E9ECFF")],
        selectforeground=[("readonly", COLORS["text"])]
    )


def center_window(window, parent, width, height):
    """Đặt cửa sổ con vào giữa cửa sổ cha."""
    parent.update_idletasks()
    x = parent.winfo_rootx() + max(0, (parent.winfo_width() - width) // 2)
    y = parent.winfo_rooty() + max(0, (parent.winfo_height() - height) // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def clear_window(root):
    """Xóa toàn bộ widget trên cửa sổ (dùng khi chuyển Đăng nhập <-> Kanban)."""
    for widget in root.winfo_children():
        widget.destroy()


# =========================================================
# HỘP THOẠI THÊM / SỬA CÔNG VIỆC
# =========================================================

class TaskForm(tk.Toplevel):

    def __init__(self, parent, on_save, task=None, default_project_id=None):
        super().__init__(parent)

        self.on_save = on_save
        self.task = task
        self.default_project_id = default_project_id

        self.title("Thông tin công việc")
        center_window(self, parent, 480, 700)
        self.resizable(False, False)
        self.configure(bg=COLORS["white"])
        self.transient(parent)
        self.grab_set()

        self.create_form()

    def create_form(self):
        header = tk.Frame(self, bg=COLORS["blue"], height=75)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Sửa công việc" if self.task else "Thêm công việc",
            bg=COLORS["blue"],
            fg="white",
            font=(FONT_DISPLAY, 21, "bold")
        ).pack(side="left", padx=25, pady=20)

        form = tk.Frame(self, bg="white")
        form.pack(fill="both", expand=True, padx=28, pady=15)

        self.title_var = tk.StringVar(
            value=self.task.title if self.task else ""
        )
        self.description_var = tk.StringVar(
            value=self.task.description if self.task else ""
        )
        self.assignee_var = tk.StringVar(
            value=self.task.assignee if self.task else ""
        )
        self.due_date_var = tk.StringVar(
            value=(self.task.due_date or "") if self.task else ""
        )

        # Combobox hiển thị nhãn tiếng Việt, khi lưu sẽ đổi lại thành mã.
        status_key = self.task.status if self.task else "todo"
        priority_key = self.task.priority if self.task else "medium"

        self.status_var = tk.StringVar(
            value=STATUSES.get(status_key, status_key)
        )
        self.priority_var = tk.StringVar(
            value=PRIORITIES.get(priority_key, priority_key)
        )

        projects = project_manager.get_all()

        self.project_options = {
            f"{project.id} - {project.name}": project.id
            for project in projects
        }

        if self.task:
            current_project = self.task.project_id
        elif self.default_project_id:
            current_project = self.default_project_id
        else:
            current_project = projects[0].id if projects else ""

        project_display = next(
            (
                label for label, project_id
                in self.project_options.items()
                if project_id == current_project
            ),
            ""
        )

        self.project_var = tk.StringVar(value=project_display)

        title_entry = self.add_entry(form, "Tên công việc", self.title_var)
        self.add_entry(form, "Mô tả", self.description_var)

        self.add_combo(
            form, "Dự án", self.project_var,
            list(self.project_options.keys())
        )
        self.add_combo(
            form, "Trạng thái", self.status_var,
            list(STATUSES.values())
        )
        self.add_combo(
            form, "Độ ưu tiên", self.priority_var,
            list(PRIORITIES.values())
        )

        self.add_entry(form, "Người phụ trách", self.assignee_var)
        self.add_entry(
            form, "Hạn hoàn thành (YYYY-MM-DD)", self.due_date_var
        )

        tk.Button(
            form,
            text="Lưu công việc",
            bg=COLORS["blue"],
            fg="white",
            activebackground="#5D72C8",
            activeforeground="white",
            relief="flat",
            font=(FONT_BODY, 10, "bold"),
            cursor="hand2",
            command=self.save_task,
            pady=10
        ).pack(fill="x", pady=(22, 5))

        self.bind("<Return>", lambda _e: self.save_task())
        self.bind("<Escape>", lambda _e: self.destroy())
        title_entry.focus_set()

    def add_entry(self, parent, label, variable):
        tk.Label(
            parent,
            text=label,
            bg="white",
            fg=COLORS["text"],
            font=(FONT_BODY, 9, "bold")
        ).pack(anchor="w", pady=(9, 4))

        entry = tk.Entry(
            parent,
            textvariable=variable,
            font=(FONT_BODY, 10),
            relief="solid",
            bd=1
        )
        entry.pack(fill="x", ipady=7)
        return entry

    def add_combo(self, parent, label, variable, values):
        tk.Label(
            parent,
            text=label,
            bg="white",
            fg=COLORS["text"],
            font=(FONT_BODY, 9, "bold")
        ).pack(anchor="w", pady=(9, 4))

        ttk.Combobox(
            parent,
            textvariable=variable,
            values=values,
            state="readonly"
        ).pack(fill="x", ipady=4)

    @staticmethod
    def _label_to_key(mapping, label):
        """Đổi nhãn tiếng Việt về mã (vd: 'Cần làm' -> 'todo')."""
        for key, text in mapping.items():
            if text == label:
                return key
        return label

    def save_task(self):
        title = self.title_var.get().strip()
        due_date = self.due_date_var.get().strip()

        if not title:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập tên công việc.",
                parent=self
            )
            return

        project_id = self.project_options.get(self.project_var.get())

        if not project_id:
            messagebox.showwarning(
                "Thiếu dự án",
                "Vui lòng chọn dự án.",
                parent=self
            )
            return

        if due_date and not Validator.is_valid_date(due_date):
            messagebox.showwarning(
                "Ngày không hợp lệ",
                "Ngày phải có dạng YYYY-MM-DD.",
                parent=self
            )
            return

        data = {
            "project_id": project_id,
            "title": title,
            "description": self.description_var.get().strip(),
            "status": self._label_to_key(STATUSES, self.status_var.get()),
            "priority": self._label_to_key(
                PRIORITIES, self.priority_var.get()
            ),
            "assignee": self.assignee_var.get().strip(),
            "due_date": due_date or None
        }

        try:
            if self.task:
                success = task_manager.update_task(self.task.id, **data)

                if not success:
                    raise ValueError("Không tìm thấy công việc.")

                action = f"Sửa công việc {self.task.id}"
            else:
                task = task_manager.add_task(**data)
                action = f"Thêm công việc {task.id}"

            self.on_save(action)
            self.destroy()

        except (ValueError, OSError) as error:
            messagebox.showerror("Lỗi", str(error), parent=self)


# =========================================================
# KHUNG BO GÓC DÙNG CHUNG
# =========================================================

class RoundedPanel(tk.Frame):
    """Khung nền bo góc vẽ bằng Canvas, dùng làm nền cho nội dung."""

    def __init__(self, parent, bg="#FFFFFF", radius=16, padding=8, **kwargs):
        parent_bg = parent.cget("bg") if "bg" in parent.keys() else "#FFFFFF"
        super().__init__(parent, bg=parent_bg, bd=0, highlightthickness=0, **kwargs)
        self.panel_bg = bg
        self.outline_color = None
        self.radius = max(4, int(radius))
        self.padding = max(0, int(padding))

        self.canvas = tk.Canvas(
            self,
            bg=parent_bg,
            bd=0,
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.pack(fill="both", expand=True)

        self.body = tk.Frame(self.canvas, bg=bg, bd=0, highlightthickness=0)
        self.window_id = self.canvas.create_window(
            (self.padding, self.padding),
            window=self.body,
            anchor="nw"
        )
        self.shape_id = None

        self.canvas.bind("<Configure>", self._redraw)
        self.body.bind("<Configure>", self._fit_height)
        self.after_idle(self._fit_height)

    def _rounded_points(self, x1, y1, x2, y2, r):
        return [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1
        ]

    def set_outline(self, color=None):
        """Đổi màu viền (dùng để làm nổi cột khi kéo thả thẻ qua)."""
        if color != self.outline_color:
            self.outline_color = color
            self._redraw()

    def _redraw(self, event=None):
        if not self.winfo_exists():
            return

        width = max(2, self.canvas.winfo_width())
        height = max(2, self.canvas.winfo_height())
        inset = self.padding
        self.canvas.coords(self.window_id, inset, inset)
        self.canvas.itemconfigure(
            self.window_id,
            width=max(1, width - inset * 2),
            height=max(self.body.winfo_reqheight(), height - inset * 2)
        )
        if self.shape_id is not None:
            self.canvas.delete(self.shape_id)
        points = self._rounded_points(
            1, 1, width-1, height-1,
            min(self.radius, width//2, height//2)
        )
        self.shape_id = self.canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=24,
            fill=self.panel_bg,
            outline=self.outline_color or self.panel_bg,
            width=3 if self.outline_color else 1
        )
        self.canvas.tag_lower(self.shape_id)

    def _fit_height(self, event=None):
        if not self.winfo_exists():
            return
        self.update_idletasks()
        needed = self.body.winfo_reqheight() + self.padding * 2
        if needed > 1:
            self.canvas.configure(height=needed)
        self._redraw()


# =========================================================
# THANH CUỘN TỐI GIẢN - CHỈ HIỆN KHI RÊ CHUỘT
# =========================================================

class HoverScrollbar(tk.Canvas):
    """Thanh cuộn mảnh, ẩn khi không tương tác; kéo trực tiếp bằng chuột."""

    def __init__(self, parent, command, bg="#EDF0FA", **kwargs):
        super().__init__(
            parent, width=10, bg=bg, highlightthickness=0,
            bd=0, relief="flat", **kwargs
        )
        self.command = command
        self.first = 0.0
        self.last = 1.0
        self.hovered = False
        self.dragging = False
        self.bind("<Configure>", self._draw)
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<Button-1>", self._click)
        self.bind("<B1-Motion>", self._drag)

    def set(self, first, last):
        self.first = float(first)
        self.last = float(last)
        self._draw()

    def _enter(self, _event=None):
        self.hovered = True
        self._draw()

    def _leave(self, _event=None):
        self.hovered = False
        self.dragging = False
        self._draw()

    def _draw(self, _event=None):
        self.delete("all")
        height = max(1, self.winfo_height())
        width = max(1, self.winfo_width())
        if self.last - self.first >= 0.999:
            return
        if self.hovered:
            self.create_rectangle(
                width // 2 - 2, 5, width // 2 + 2, height - 5,
                fill="#E4E0F5", outline=""
            )
            top = max(5, int(self.first * height))
            bottom = min(height - 5, max(top + 28, int(self.last * height)))
            self.create_rounded_thumb(width // 2 - 3, top, width // 2 + 3, bottom)

    def create_rounded_thumb(self, x1, y1, x2, y2):
        self.create_oval(x1, y1, x2, y1 + 7, fill="#9889D2", outline="")
        self.create_rectangle(x1, y1 + 3, x2, y2 - 3, fill="#9889D2", outline="")
        self.create_oval(x1, max(y1, y2 - 7), x2, y2, fill="#9889D2", outline="")

    def _scroll_to(self, y):
        height = max(1, self.winfo_height())
        fraction = min(1.0, max(0.0, y / height))
        span = max(0.01, self.last - self.first)
        self.command("moveto", min(1.0 - span, max(0.0, fraction - span / 2)))

    def _click(self, event):
        self.dragging = True
        self._scroll_to(event.y)

    def _drag(self, event):
        if self.dragging:
            self._scroll_to(event.y)


# =========================================================
# THẺ CÔNG VIỆC (có kéo thả)
# =========================================================

class TaskCard(RoundedPanel):

    DRAG_THRESHOLD = 6  # px: kéo quá ngưỡng này mới tính là kéo thả

    def __init__(self, parent, task, app):
        super().__init__(parent, bg="#FFFFFF", radius=17, padding=2)

        self.task = task
        self.app = app

        self._press_xy = None
        self._dragging = False
        self._ghost = None

        self.pack(fill="x", padx=9, pady=7)

        priority_bg, priority_fg = PRIORITY_STYLES.get(
            task.priority, ("#F1F2F4", COLORS["muted"])
        )

        # Vạch màu mảnh theo độ ưu tiên giúp nhận diện nhanh từng thẻ.
        tk.Frame(self.body, bg=priority_fg, height=3).pack(fill="x")

        content = tk.Frame(self.body, bg="white", cursor="fleur")
        content.pack(fill="x", padx=14, pady=13)

        # Mã công việc
        tk.Label(
            content,
            text=task.id,
            bg="white",
            fg=COLORS["muted"],
            font=(FONT_BODY, 8)
        ).pack(anchor="w")
        # Tiêu đề
        tk.Label(
            content,
            text=task.title,
            bg="white",
            fg=COLORS["text"],
            font=(FONT_BODY, 11, "bold"),
            wraplength=260,
            justify="left"
        ).pack(anchor="w", pady=(5, 6))

        # Thanh nút (đưa lên cao để luôn nhìn thấy)
        actions = tk.Frame(content, bg="white")
        actions.pack(fill="x", pady=(4, 8))

        tk.Button(
            actions,
            text="Sửa",
            bg="#EEF0FF",
            fg=COLORS["blue"],
            relief="flat",
            cursor="hand2",
            command=self.edit,
            padx=9
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            actions,
            text="Xóa",
            bg="#F0F1FB",
            fg=COLORS["muted"],
            relief="flat",
            cursor="hand2",
            command=self.delete,
            padx=9
        ).pack(side="left", padx=5)

        tk.Button(
            actions,
            text="Chuyển →",
            bg="#EEEAFE",
            fg="#806FC0",
            relief="flat",
            cursor="hand2",
            command=self.move,
            padx=9
        ).pack(side="right")

        # Mô tả
        if task.description:
            tk.Label(
                content,
                text=task.description,
                bg="white",
                fg=COLORS["muted"],
                font=(FONT_BODY, 9),
                wraplength=260,
                justify="left"
            ).pack(anchor="w", pady=(0, 7))

        # Nhãn ưu tiên
        tk.Label(
            content,
            text=f"  {PRIORITIES.get(task.priority, task.priority)}  ",
            bg=priority_bg,
            fg=priority_fg,
            font=(FONT_BODY, 8, "bold"),
            padx=5,
            pady=3
        ).pack(anchor="w", pady=5)

        # Người phụ trách
        tk.Label(
            content,
            text=f"Người phụ trách: {task.assignee or 'Chưa phân công'}",
            bg="white",
            fg=COLORS["muted"],
            font=(FONT_BODY, 8)
        ).pack(anchor="w", pady=3)

        # Hạn hoàn thành
        overdue = task.is_overdue()
        due_text = task.due_date or "Chưa đặt hạn"
        if overdue:
            due_text += "  (quá hạn)"

        tk.Label(
            content,
            text=f"Hạn hoàn thành: {due_text}",
            bg="white",
            fg=COLORS["red"] if overdue else COLORS["muted"],
            font=(FONT_BODY, 8, "bold" if overdue else "normal")
        ).pack(anchor="w", pady=3)

        # Gắn sự kiện kéo thả
        self._bind_drag(self.canvas)

    # ---------------- Các nút ----------------

    def edit(self):
        TaskForm(self.winfo_toplevel(), self.app.on_data_changed, self.task)

    def delete(self):
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có muốn xóa công việc '{self.task.title}'?",
            parent=self.winfo_toplevel()
        )

        if confirm:
            try:
                task_manager.delete_task(self.task.id)
                self.app.on_data_changed(f"Xóa công việc {self.task.id}")
            except (ValueError, OSError) as error:
                messagebox.showerror("Lỗi", str(error))

    def move(self):
        statuses = list(STATUSES.keys())
        current = self.task.status if self.task.status in statuses else statuses[-1]
        next_status = statuses[(statuses.index(current) + 1) % len(statuses)]
        self.move_to(next_status)

    def move_to(self, status):
        try:
            if task_manager.move_task(self.task.id, status):
                self.app.on_data_changed(
                    f"Chuyển {self.task.id} sang {STATUSES.get(status, status)}"
                )
        except (ValueError, OSError) as error:
            messagebox.showerror("Lỗi", str(error))

    # ---------------- Kéo thả ----------------

    def _bind_drag(self, widget):
        """Gắn sự kiện chuột cho widget và mọi widget con (bỏ qua nút bấm)."""
        if isinstance(widget, tk.Button):
            return
        widget.bind("<ButtonPress-1>", self._drag_start, add="+")
        widget.bind("<B1-Motion>", self._drag_motion, add="+")
        widget.bind("<ButtonRelease-1>", self._drag_end, add="+")
        for child in widget.winfo_children():
            self._bind_drag(child)

    def _drag_start(self, event):
        self._press_xy = (event.x_root, event.y_root)
        self._dragging = False

    def _drag_motion(self, event):
        if self._press_xy is None:
            return

        dx = event.x_root - self._press_xy[0]
        dy = event.y_root - self._press_xy[1]

        if not self._dragging:
            if abs(dx) < self.DRAG_THRESHOLD and abs(dy) < self.DRAG_THRESHOLD:
                return
            self._dragging = True
            self._create_ghost()

        if self._ghost is not None:
            self._ghost.geometry(f"+{event.x_root + 12}+{event.y_root + 8}")

        self.app.highlight_column(
            self.app.column_at(event.x_root, event.y_root)
        )

    def _drag_end(self, event):
        was_dragging = self._dragging
        self._press_xy = None
        self._dragging = False
        self._destroy_ghost()

        if not was_dragging:
            return

        target = self.app.column_at(event.x_root, event.y_root)
        self.app.highlight_column(None)

        if target and target != self.task.status:
            self.move_to(target)

    def _create_ghost(self):
        """Tạo 'bóng' của thẻ đi theo con trỏ khi kéo."""
        ghost = tk.Toplevel(self)
        ghost.overrideredirect(True)
        try:
            ghost.attributes("-alpha", 0.88)
            ghost.attributes("-topmost", True)
        except tk.TclError:
            pass

        accent = PRIORITY_STYLES.get(
            self.task.priority, ("#F1F2F4", COLORS["blue"])
        )[1]
        frame = tk.Frame(
            ghost, bg="white",
            highlightbackground=accent, highlightthickness=2
        )
        frame.pack()
        tk.Label(
            frame, text=f"{self.task.id}  ·  {self.task.title}",
            bg="white", fg=COLORS["text"],
            font=(FONT_BODY, 10, "bold"), padx=14, pady=10,
            wraplength=240, justify="left"
        ).pack()
        self._ghost = ghost

    def _destroy_ghost(self):
        if self._ghost is not None:
            self._ghost.destroy()
            self._ghost = None


# =========================================================
# BIỂU ĐỒ THỐNG KÊ VẼ BẰNG CANVAS
# =========================================================

class StatsChart(RoundedPanel):
    """Vẽ 3 biểu đồ: cột theo trạng thái, thanh theo ưu tiên, vòng hoàn thành."""

    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF", radius=20, padding=3)

        self.stats = {"total": 0, "todo": 0, "doing": 0, "done": 0, "overdue": 0}
        self.priority_counts = {key: 0 for key in PRIORITIES}

        self.chart = tk.Canvas(
            self.body, bg="#FFFFFF", highlightthickness=0, bd=0, height=320
        )
        self.chart.pack(fill="both", expand=True, padx=22, pady=18)
        self.chart.bind("<Configure>", lambda _e: self.draw_chart())

    def update_statistics(self, stats, priority_counts):
        self.stats = dict(stats)
        self.priority_counts = dict(priority_counts)
        self.draw_chart()

    # ---- vẽ ----

    def draw_chart(self):
        c = self.chart
        c.delete("all")

        width = max(c.winfo_width(), 600)
        height = max(c.winfo_height(), 240)

        split1 = int(width * 0.46)
        split2 = int(width * 0.76)

        self._draw_status_bars(0, split1 - 24, height)
        self._draw_priority_bars(split1 + 24, split2 - 24, height)
        self._draw_completion_ring(split2 + 24, width, height)

        for x in (split1, split2):
            c.create_line(x, 10, x, height - 10, fill=COLORS["border"])

    def _title(self, x, text):
        self.chart.create_text(
            x, 4, text=text, anchor="nw",
            fill=COLORS["text"], font=(FONT_DISPLAY, 12, "bold")
        )

    def _draw_status_bars(self, x1, x2, height):
        c = self.chart
        self._title(x1, "Công việc theo trạng thái")

        items = [
            ("Cần làm", self.stats.get("todo", 0), STATUS_STYLES["todo"]["accent"]),
            ("Đang làm", self.stats.get("doing", 0), STATUS_STYLES["doing"]["accent"]),
            ("Hoàn thành", self.stats.get("done", 0), STATUS_STYLES["done"]["accent"]),
            ("Quá hạn", self.stats.get("overdue", 0), COLORS["red"]),
        ]

        left = x1 + 30
        right = x2
        top = 48
        bottom = height - 34

        # Thang chia trục Y: 4 khoảng, làm tròn lên số nguyên
        max_value = max([value for _, value, _ in items] + [1])
        step = max(1, -(-max_value // 4))
        scale_max = step * 4

        for i in range(5):
            value = step * i
            y = bottom - (bottom - top) * value / scale_max
            c.create_line(left, y, right, y, fill="#EEEDF7")
            c.create_text(
                left - 8, y, text=str(value), anchor="e",
                fill=COLORS["muted"], font=(FONT_BODY, 8)
            )

        slot = (right - left) / len(items)
        bar_width = min(54, slot * 0.5)

        for i, (label, value, color) in enumerate(items):
            cx = left + slot * (i + 0.5)
            bar_top = bottom - (bottom - top) * value / scale_max
            if value > 0:
                c.create_rectangle(
                    cx - bar_width / 2, bar_top, cx + bar_width / 2, bottom,
                    fill=color, outline=""
                )
            c.create_text(
                cx, bar_top - 10, text=str(value),
                fill=color, font=(FONT_BODY, 10, "bold")
            )
            c.create_text(
                cx, bottom + 16, text=label,
                fill=COLORS["muted"], font=(FONT_BODY, 9)
            )

    def _draw_priority_bars(self, x1, x2, height):
        c = self.chart
        self._title(x1, "Theo độ ưu tiên")

        total = max(1, sum(self.priority_counts.values()))
        order = ["high", "medium", "low"]

        row_top = 64
        row_gap = max(56, (height - 90) / 3)
        track_left = x1
        track_right = x2

        for i, key in enumerate(order):
            value = self.priority_counts.get(key, 0)
            tint, color = PRIORITY_STYLES[key]
            y = row_top + row_gap * i

            c.create_text(
                track_left, y, text=PRIORITIES[key], anchor="w",
                fill=COLORS["text"], font=(FONT_BODY, 9, "bold")
            )
            c.create_text(
                track_right, y, text=str(value), anchor="e",
                fill=color, font=(FONT_BODY, 10, "bold")
            )

            bar_y = y + 18
            c.create_rectangle(
                track_left, bar_y, track_right, bar_y + 10,
                fill=tint, outline=""
            )
            fill_right = track_left + (track_right - track_left) * value / total
            if value > 0:
                c.create_rectangle(
                    track_left, bar_y, fill_right, bar_y + 10,
                    fill=color, outline=""
                )

    def _draw_completion_ring(self, x1, x2, height):
        c = self.chart
        self._title(x1, "Tỉ lệ hoàn thành")

        total = self.stats.get("total", 0)
        done = self.stats.get("done", 0)
        percent = done / total if total else 0

        size = min(x2 - x1, height - 70)
        radius = max(30, size / 2 - 12)
        cx = (x1 + x2) / 2
        cy = 40 + (height - 40) / 2
        ring = 14

        box = (cx - radius, cy - radius, cx + radius, cy + radius)
        c.create_oval(*box, outline=COLORS["green_light"], width=ring)

        if percent > 0:
            extent = -359.9 if percent >= 1 else -360 * percent
            c.create_arc(
                *box, start=90, extent=extent, style="arc",
                outline=COLORS["green"], width=ring
            )

        c.create_text(
            cx, cy - 8, text=f"{percent * 100:.0f}%",
            fill=COLORS["text"], font=(FONT_DISPLAY, 22, "bold")
        )
        c.create_text(
            cx, cy + 20, text=f"{done}/{total} công việc",
            fill=COLORS["muted"], font=(FONT_BODY, 9)
        )


# =========================================================
# CỬA SỔ ĐĂNG NHẬP / ĐĂNG KÝ
# =========================================================

class LoginWindow:

    def __init__(self, root, auth, on_success):
        self.root = root
        self.auth = auth
        self.on_success = on_success
        self.mode = "login"

        self.root.title("Kanban - Đăng nhập")
        self.root.geometry("1000x680")
        self.root.minsize(760, 620)
        self.root.configure(bg="#E9E8F8")

        self.frame = tk.Frame(root, bg="#E9E8F8")
        self.frame.pack(fill="both", expand=True)

        self.card = RoundedPanel(self.frame, bg="#FFFFFF", radius=24, padding=4)
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=430)

        self.show_login()

    # ---------- dựng giao diện ----------

    def _clear_card(self):
        for widget in self.card.body.winfo_children():
            widget.destroy()

    def _header(self, subtitle):
        body = self.card.body

        tk.Label(
            body, text="KANBAN", bg="white", fg="#7180C9",
            font=(FONT_DISPLAY, 26, "bold")
        ).pack(pady=(28, 2))

        tk.Label(
            body, text=subtitle, bg="white", fg=COLORS["muted"],
            font=(FONT_BODY, 10)
        ).pack()

        # Thanh chuyển tab Đăng nhập / Đăng ký
        tabs = tk.Frame(body, bg="#F0F1FB")
        tabs.pack(fill="x", padx=36, pady=(20, 6))

        for key, text, command in (
            ("login", "Đăng nhập", self.show_login),
            ("register", "Đăng ký", self.show_register),
        ):
            active = key == self.mode
            tk.Button(
                tabs, text=text, command=command,
                bg=COLORS["blue"] if active else "#F0F1FB",
                fg="white" if active else COLORS["text"],
                activebackground="#5D72C8", activeforeground="white",
                relief="flat", bd=0, cursor="hand2",
                font=(FONT_BODY, 10, "bold" if active else "normal"),
                pady=8
            ).pack(side="left", fill="x", expand=True, padx=3, pady=3)

    def _field(self, label, variable, show=None):
        body = self.card.body
        tk.Label(
            body, text=label, bg="white", fg=COLORS["text"],
            font=(FONT_BODY, 9, "bold")
        ).pack(anchor="w", padx=36, pady=(10, 4))

        entry = tk.Entry(
            body, textvariable=variable, show=show or "",
            font=(FONT_BODY, 10), relief="solid", bd=1,
            bg="#F8F8FE", fg=COLORS["text"]
        )
        entry.pack(fill="x", padx=36, ipady=7)
        return entry

    def _submit_button(self, text, command):
        tk.Button(
            self.card.body, text=text, command=command,
            bg=COLORS["blue"], fg="white",
            activebackground="#5D72C8", activeforeground="white",
            relief="flat", cursor="hand2",
            font=(FONT_BODY, 10, "bold"), pady=10
        ).pack(fill="x", padx=36, pady=(22, 8))

    def show_login(self, username=""):
        self.mode = "login"
        self._clear_card()
        self.root.title("Kanban - Đăng nhập")
        self._header("Đăng nhập để quản lý công việc")

        self.username_var = tk.StringVar(value=username)
        self.password_var = tk.StringVar()
        self.show_pw_var = tk.BooleanVar(value=False)

        user_entry = self._field("Tên đăng nhập", self.username_var)
        self.password_entry = self._field("Mật khẩu", self.password_var, show="•")

        tk.Checkbutton(
            self.card.body, text="Hiện mật khẩu",
            variable=self.show_pw_var, command=self._toggle_password,
            bg="white", fg=COLORS["muted"], activebackground="white",
            selectcolor="white", font=(FONT_BODY, 9), bd=0,
            highlightthickness=0
        ).pack(anchor="w", padx=32, pady=(6, 0))

        self._submit_button("Đăng nhập", self.do_login)

        tk.Label(
            self.card.body,
            text="Tài khoản mặc định: admin / admin123",
            bg="white", fg=COLORS["muted"], font=(FONT_BODY, 8)
        ).pack(pady=(0, 26))

        self.root.bind("<Return>", lambda _e: self.do_login())
        (self.password_entry if username else user_entry).focus_set()

    def show_register(self):
        self.mode = "register"
        self._clear_card()
        self.root.title("Kanban - Đăng ký")
        self._header("Tạo tài khoản mới")

        self.reg_fullname_var = tk.StringVar()
        self.reg_email_var = tk.StringVar()
        self.reg_username_var = tk.StringVar()
        self.reg_password_var = tk.StringVar()
        self.reg_confirm_var = tk.StringVar()

        first = self._field("Họ và tên", self.reg_fullname_var)
        self._field("Email", self.reg_email_var)
        self._field("Tên đăng nhập (3-20 ký tự: chữ, số, _)", self.reg_username_var)
        self._field("Mật khẩu (ít nhất 6 ký tự)", self.reg_password_var, show="•")
        self._field("Nhập lại mật khẩu", self.reg_confirm_var, show="•")

        self._submit_button("Tạo tài khoản", self.do_register)
        tk.Frame(self.card.body, bg="white", height=14).pack()

        self.root.bind("<Return>", lambda _e: self.do_register())
        first.focus_set()

    def _toggle_password(self):
        self.password_entry.configure(show="" if self.show_pw_var.get() else "•")

    # ---------- xử lý ----------

    def do_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập tên đăng nhập và mật khẩu.",
                parent=self.root
            )
            return

        success, message = self.auth.login(username, password)

        if not success:
            messagebox.showerror("Đăng nhập thất bại", message, parent=self.root)
            self.password_var.set("")
            return

        self.root.unbind("<Return>")
        self.on_success(self.auth.current_user)

    def do_register(self):
        password = self.reg_password_var.get()

        if password != self.reg_confirm_var.get():
            messagebox.showwarning(
                "Mật khẩu không khớp",
                "Mật khẩu nhập lại không trùng khớp.",
                parent=self.root
            )
            return

        username = self.reg_username_var.get().strip()
        success, message = self.auth.register(
            username,
            password,
            self.reg_fullname_var.get().strip(),
            self.reg_email_var.get().strip()
        )

        if not success:
            messagebox.showerror("Đăng ký thất bại", message, parent=self.root)
            return

        messagebox.showinfo(
            "Thành công",
            f"{message}\nHãy đăng nhập bằng tài khoản '{username}'.",
            parent=self.root
        )
        self.show_login(username)


# =========================================================
# GIAO DIỆN CHÍNH
# =========================================================

class MainWindow:

    def __init__(self, root, current_user=None, on_logout=None):
        self.root = root
        self.current_user = current_user
        self.on_logout = on_logout

        # Kết nối bộ quản lý dữ liệu
        self.task_manager = task_manager
        self.project_manager = project_manager

        self.root.title("Kanban - Quản lý công việc")
        self.root.geometry("1440x860")
        self.root.minsize(1120, 700)
        self.root.configure(bg="#E9E8F8")

        self.search_var = tk.StringVar()
        self.selected_project_id = None   # None = tất cả dự án
        self.view = "board"               # "board" hoặc "overview"
        self._refresh_pending = False

        self.create_header()
        self.create_workspace()

        # Con lăn chuột: Windows/macOS dùng <MouseWheel>, Linux dùng Button-4/5
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel)
        self.root.bind_all("<Button-5>", self._on_mousewheel)

        self.show_board()

    # -----------------------------------------------------
    # TIỆN ÍCH CHUNG
    # -----------------------------------------------------

    @property
    def username(self):
        return self.current_user.username if self.current_user else "khach"

    def log(self, action):
        """Ghi nhật ký hoạt động; lỗi ghi log không làm hỏng thao tác chính."""
        try:
            activity_log.write(self.username, action)
        except (ValueError, OSError):
            pass

    def on_data_changed(self, action=None):
        """Gọi sau mỗi lần thêm/sửa/xóa/chuyển: ghi log rồi vẽ lại."""
        if action:
            self.log(action)
        self.schedule_refresh()

    def schedule_refresh(self):
        """Vẽ lại sau khi sự kiện hiện tại kết thúc (an toàn khi thẻ tự hủy)."""
        if not self._refresh_pending:
            self._refresh_pending = True
            self.root.after_idle(self._do_scheduled_refresh)

    def _do_scheduled_refresh(self):
        self._refresh_pending = False
        if self.root.winfo_exists() and self.content.winfo_exists():
            self.refresh()

    # -----------------------------------------------------
    # THANH ĐIỀU HƯỚNG
    # -----------------------------------------------------

    def create_header(self):
        header = tk.Frame(
            self.root,
            bg="white",
            height=78,
            highlightbackground="#E6E5F2",
            highlightthickness=1
        )
        header.pack(fill="x")
        header.pack_propagate(False)
        self.header = header

        brand = tk.Frame(header, bg="white")
        brand.pack(side="left", padx=25)

        tk.Label(
            brand,
            text="KANBAN",
            bg="white",
            fg="#7180C9",
            font=(FONT_DISPLAY, 23, "bold")
        ).pack(anchor="w")

        user_name = self.current_user.full_name if self.current_user else "bạn"

        tk.Label(
            brand,
            text=f"Xin chào, {user_name}! 👋",
            bg="white",
            fg="#8993C8",
            font=(FONT_BODY, 9, "bold")
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Quản lý công việc",
            bg="white",
            fg=COLORS["text"],
            font=(FONT_BODY, 11)
        ).pack(side="left", padx=18)

        # Nút đăng xuất + nhãn vai trò
        if self.current_user is not None:
            tk.Button(
                header,
                text="Đăng xuất",
                bg="#F0F1FB",
                fg=COLORS["muted"],
                activebackground=COLORS["red_light"],
                activeforeground=COLORS["red"],
                relief="flat",
                cursor="hand2",
                font=(FONT_BODY, 9, "bold"),
                command=self.logout,
                padx=12,
                pady=6
            ).pack(side="right", padx=(8, 25))

        role_text = "ADMIN" if (
            self.current_user and self.current_user.is_admin()
        ) else "WORKSPACE"

        tk.Label(
            header,
            text=role_text,
            bg="#EEF0FF",
            fg=COLORS["blue"],
            font=(FONT_BODY, 9, "bold"),
            padx=12,
            pady=6
        ).pack(side="right", padx=(25 if self.current_user is None else 0, 0))

    # -----------------------------------------------------
    # KHU VỰC LÀM VIỆC
    # -----------------------------------------------------

    def create_workspace(self):
        workspace = tk.Frame(
            self.root,
            bg="#DCEFEA",
            highlightbackground="#FFFFFF",
            highlightthickness=1
        )
        workspace.pack(fill="both", expand=True, padx=30, pady=22)
        self.workspace = workspace

        self.create_sidebar(workspace)

        self.content = tk.Frame(workspace, bg="#FBFAFF")
        self.content.pack(side="left", fill="both", expand=True, padx=(15, 0))

        self.create_toolbar()
        self.create_project_info()
        self.create_statistics()
        self.create_board()
        self.create_chart()

    # -----------------------------------------------------
    # SIDEBAR
    # -----------------------------------------------------

    def create_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg="#F0EEFB", width=205)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.nav_buttons = {}
        self.active_nav = "board"

        tk.Label(
            sidebar,
            text="MENU",
            bg="#F0EEFB",
            fg=COLORS["muted"],
            font=(FONT_BODY, 9, "bold")
        ).pack(anchor="w", padx=18, pady=(22, 12))

        self.sidebar_button(sidebar, "▦   Tổng quan", self.show_overview, key="overview")
        self.sidebar_button(sidebar, "▤   Bảng công việc", self.show_board, key="board")
        self.sidebar_button(sidebar, "▧   Dự án", self.show_projects, key="projects")

        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=15, pady=18)

        tk.Label(
            sidebar,
            text="DỰ ÁN CỦA BẠN",
            bg="#F0EEFB",
            fg=COLORS["muted"],
            font=(FONT_BODY, 8, "bold")
        ).pack(anchor="w", padx=18, pady=5)

        self.project_list = tk.Frame(sidebar, bg="#F0EEFB")
        self.project_list.pack(fill="x", padx=10)

        tk.Button(
            sidebar,
            text="+ Tạo dự án mới",
            bg="#E8EAFE",
            fg=COLORS["blue"],
            relief="flat",
            cursor="hand2",
            command=self.add_project
        ).pack(fill="x", padx=12, pady=15, ipady=7)

    def sidebar_button(self, parent, text, command, key=None):
        active = key == self.active_nav
        button = tk.Button(
            parent,
            text=text,
            bg="#E5E8FC" if active else "#F0EEFB",
            fg=COLORS["blue"] if active else COLORS["text"],
            activebackground="#E5E8FC",
            activeforeground=COLORS["blue"],
            relief="flat",
            anchor="w",
            font=(FONT_BODY, 10, "bold" if active else "normal"),
            cursor="hand2",
            command=command,
            padx=14,
            pady=11,
            bd=0,
            highlightthickness=0
        )
        button.pack(fill="x", padx=9, pady=3)
        if key:
            self.nav_buttons[key] = button
        button.bind("<Enter>", lambda _e, b=button: b.configure(
            bg="#E5E8FC", fg=COLORS["blue"]
        ))
        button.bind("<Leave>", lambda _e, b=button, k=key: self._restore_nav_button(b, k))
        return button

    def _restore_nav_button(self, button, key):
        active = key == self.active_nav
        button.configure(
            bg="#E5E8FC" if active else "#F0EEFB",
            fg=COLORS["blue"] if active else COLORS["text"],
            font=(FONT_BODY, 10, "bold" if active else "normal")
        )

    def set_active_nav(self, key):
        self.active_nav = key
        for button_key, button in self.nav_buttons.items():
            self._restore_nav_button(button, button_key)

    # -----------------------------------------------------
    # THANH CÔNG CỤ
    # -----------------------------------------------------

    def create_toolbar(self):
        toolbar = tk.Frame(self.content, bg="white")
        toolbar.pack(fill="x", pady=(15, 10))

        left = tk.Frame(toolbar, bg="white")
        left.pack(side="left")

        tk.Label(
            left,
            text="Không gian làm việc",
            bg="white",
            fg=COLORS["text"],
            font=(FONT_DISPLAY, 20, "bold")
        ).pack(anchor="w")

        tk.Label(
            left,
            text="Theo dõi và quản lý tiến độ công việc · kéo thả thẻ để đổi trạng thái",
            bg="white",
            fg=COLORS["muted"],
            font=(FONT_BODY, 9)
        ).pack(anchor="w", pady=4)

        right = tk.Frame(toolbar, bg="white")
        right.pack(side="right")

        tk.Button(
            right,
            text="+ Thêm công việc",
            bg=COLORS["blue"],
            fg="white",
            activebackground="#5D72C8",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            font=(FONT_BODY, 9, "bold"),
            command=self.add_task,
            padx=12,
            pady=9
        ).pack(side="right", padx=(8, 0))

        search = tk.Frame(
            right,
            bg="#F0F1FB",
            highlightbackground="#E6E5F2",
            highlightthickness=1
        )
        search.pack(side="right")

        tk.Label(
            search,
            text="⌕",
            bg="#F0F1FB",
            fg=COLORS["muted"],
            font=(FONT_BODY, 14)
        ).pack(side="left", padx=7)

        tk.Entry(
            search,
            textvariable=self.search_var,
            bg="#F0F1FB",
            fg=COLORS["text"],
            relief="flat",
            width=19,
            font=(FONT_BODY, 9)
        ).pack(side="left", ipady=8, padx=5)

        self.search_var.trace_add("write", lambda *_: self.refresh())

    # -----------------------------------------------------
    # THÔNG TIN DỰ ÁN
    # -----------------------------------------------------

    def create_project_info(self):
        info = RoundedPanel(self.content, bg="#F2EFFB", radius=18, padding=2)
        info.pack(fill="x", pady=8)

        self.project_title = tk.Label(
            info.body,
            text="Tất cả công việc",
            bg="#F2EFFB",
            fg=COLORS["text"],
            font=(FONT_DISPLAY, 15, "bold")
        )
        self.project_title.pack(anchor="w", padx=15, pady=(12, 3))

        self.project_description = tk.Label(
            info.body,
            text="Quản lý các công việc trong không gian làm việc",
            bg="#F2EFFB",
            fg=COLORS["muted"],
            font=(FONT_BODY, 9)
        )
        self.project_description.pack(anchor="w", padx=15, pady=(0, 12))

    # -----------------------------------------------------
    # THỐNG KÊ
    # -----------------------------------------------------

    def create_statistics(self):
        stats_frame = tk.Frame(self.content, bg="#FBFAFF")
        stats_frame.pack(fill="x", pady=(11, 12))

        self.stat_labels = {}
        items = [
            ("total", "Tổng công việc", "✦", COLORS["blue"], "#EEF0FF"),
            ("todo", "Cần làm", "○", COLORS["yellow"], "#FFF4DF"),
            ("doing", "Đang thực hiện", "◷", "#7186D8", "#EEF0FF"),
            ("done", "Hoàn thành", "✓", COLORS["green"], "#E5F5EF"),
            ("overdue", "Quá hạn", "!", COLORS["red"], "#FCEBF0")
        ]

        for col in range(len(items)):
            stats_frame.grid_columnconfigure(col, weight=1, uniform="stats")

        for col, (key, title, symbol, color, tint) in enumerate(items):
            card = RoundedPanel(stats_frame, bg="#FFFFFF", radius=17, padding=2)
            card.grid(row=0, column=col, sticky="nsew", padx=5, pady=2)

            accent = tk.Frame(card.body, bg=color, height=4)
            accent.pack(fill="x", padx=13, pady=(9, 7))

            top = tk.Frame(card.body, bg="#FFFFFF")
            top.pack(fill="x", padx=13)
            tk.Label(
                top, text=symbol, bg=tint, fg=color,
                font=(FONT_BODY, 11, "bold"), width=3, pady=3
            ).pack(side="left")
            tk.Label(
                top, text=title, bg="#FFFFFF", fg=COLORS["muted"],
                font=(FONT_BODY, 9, "bold")
            ).pack(side="left", padx=8)

            label = tk.Label(
                card.body, text="0", bg="#FFFFFF", fg=color,
                font=(FONT_DISPLAY, 23, "bold")
            )
            label.pack(anchor="w", padx=16, pady=(3, 10))
            self.stat_labels[key] = label

    # -----------------------------------------------------
    # BẢNG KANBAN
    # -----------------------------------------------------

    def create_board(self):
        board = tk.Frame(self.content, bg="#FBFAFF")
        self.board = board

        self.columns = {}
        settings = [
            ("todo", "CẦN LÀM"),
            ("doing", "ĐANG THỰC HIỆN"),
            ("done", "HOÀN THÀNH")
        ]

        for status, title in settings:
            shell = RoundedPanel(board, bg="#EDF0FA", radius=20, padding=3)
            shell.pack(side="left", fill="both", expand=True, padx=7, pady=3)
            column = shell.body
            palette = STATUS_STYLES[status]

            tk.Frame(column, bg=palette["accent"], height=4).pack(fill="x")

            heading = tk.Frame(column, bg="#EDF0FA")
            heading.pack(fill="x", padx=16, pady=(13, 10))

            title_group = tk.Frame(heading, bg="#EDF0FA")
            title_group.pack(side="left")

            tk.Label(
                title_group, text=palette["icon"], bg=palette["tint"],
                fg=palette["accent"], font=(FONT_BODY, 11, "bold"),
                width=3, pady=3
            ).pack(side="left", padx=(0, 9))

            tk.Label(
                title_group, text=title, bg="#EDF0FA",
                fg=COLORS["text"], font=(FONT_DISPLAY, 12, "bold")
            ).pack(side="left")

            count = tk.Label(
                heading, text="0", bg=palette["tint"],
                fg=palette["accent"], font=(FONT_BODY, 9, "bold"),
                padx=9, pady=4
            )
            count.pack(side="right")

            body_area = tk.Frame(column, bg="#EDF0FA")
            body_area.pack(fill="both", expand=True, padx=(7, 5), pady=(0, 8))

            canvas = tk.Canvas(
                body_area, bg="#EDF0FA", highlightthickness=0,
                bd=0, yscrollincrement=24
            )
            scrollbar = HoverScrollbar(body_area, command=canvas.yview, bg="#EDF0FA")
            inner = tk.Frame(canvas, bg="#EDF0FA")
            window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

            inner.bind(
                "<Configure>",
                lambda event, c=canvas: c.configure(scrollregion=c.bbox("all"))
            )
            canvas.bind(
                "<Configure>",
                lambda event, c=canvas, w=window_id: c.itemconfigure(w, width=event.width)
            )
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y", padx=(1, 0))

            self.columns[status] = {
                "frame": inner,
                "count": count,
                "canvas": canvas,
                "scrollbar": scrollbar,
                "shell": shell
            }

    def _on_mousewheel(self, event):
        """Cuộn đúng cột đang nằm dưới con trỏ (kể cả khi trỏ lên thẻ)."""
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        canvases = {str(col["canvas"]): col["canvas"] for col in self.columns.values()}

        while widget is not None:
            canvas = canvases.get(str(widget))
            if canvas is not None:
                if canvas.yview() == (0.0, 1.0):
                    return  # nội dung ngắn, không cần cuộn
                if getattr(event, "num", None) == 4:
                    step = -1
                elif getattr(event, "num", None) == 5:
                    step = 1
                else:
                    delta = event.delta
                    step = int(-delta / 120) if abs(delta) >= 120 else (-1 if delta > 0 else 1)
                canvas.yview_scroll(step, "units")
                return
            widget = widget.master

    # ---- hỗ trợ kéo thả ----

    def column_at(self, x_root, y_root):
        """Trả về trạng thái của cột đang nằm dưới tọa độ màn hình (hoặc None)."""
        if not self.board.winfo_ismapped():
            return None

        for status, column in self.columns.items():
            shell = column["shell"]
            left, top = shell.winfo_rootx(), shell.winfo_rooty()
            if (left <= x_root <= left + shell.winfo_width()
                    and top <= y_root <= top + shell.winfo_height()):
                return status
        return None

    def highlight_column(self, status):
        for key, column in self.columns.items():
            color = STATUS_STYLES[key]["accent"] if key == status else None
            column["shell"].set_outline(color)

    # -----------------------------------------------------
    # BIỂU ĐỒ (trang Tổng quan)
    # -----------------------------------------------------

    def create_chart(self):
        self.chart = StatsChart(self.content)

    def _show_view(self, view):
        self.view = view
        self.board.pack_forget()
        self.chart.pack_forget()

        if view == "overview":
            self.chart.pack(fill="both", expand=True, padx=5, pady=(8, 4))
        else:
            self.board.pack(fill="both", expand=True, pady=(8, 0))

    # -----------------------------------------------------
    # CẬP NHẬT GIAO DIỆN
    # -----------------------------------------------------

    def get_visible_tasks(self):
        """Lọc công việc theo dự án đang chọn và từ khóa tìm kiếm."""
        tasks = self.task_manager.get_all()

        if self.selected_project_id:
            tasks = [t for t in tasks if t.project_id == self.selected_project_id]

        keyword = self.search_var.get().strip().casefold()
        if keyword:
            tasks = [
                task for task in tasks
                if keyword in (task.title or "").casefold()
                or keyword in (task.description or "").casefold()
                or keyword in (task.assignee or "").casefold()
                or keyword in str(task.id).casefold()
            ]
        return tasks

    def refresh(self):
        tasks = self.get_visible_tasks()

        stats = {
            "total": len(tasks),
            "todo": sum(1 for t in tasks if t.status == "todo"),
            "doing": sum(1 for t in tasks if t.status == "doing"),
            "done": sum(1 for t in tasks if t.status == "done"),
            "overdue": sum(1 for t in tasks if t.is_overdue())
        }

        for key, label in self.stat_labels.items():
            label.config(text=str(stats[key]))

        priority_counts = {
            key: sum(1 for t in tasks if t.priority == key)
            for key in PRIORITIES
        }
        self.chart.update_statistics(stats, priority_counts)

        for status in STATUSES:
            column = self.columns[status]
            frame = column["frame"]

            for widget in frame.winfo_children():
                widget.destroy()

            status_tasks = [task for task in tasks if task.status == status]
            column["count"].config(text=str(len(status_tasks)))

            for task in status_tasks:
                TaskCard(frame, task, self)

            if not status_tasks:
                self.show_empty_state(frame, status)

            column["canvas"].yview_moveto(0)

        self.refresh_project_list()

    def show_empty_state(self, parent, status):
        """Hiển thị trạng thái rỗng có chủ đích, tránh cảm giác cột bị bỏ trống."""
        empty_info = {
            "todo": ("○", "Chưa có việc cần làm", "Các công việc mới sẽ xuất hiện tại đây."),
            "doing": ("◷", "Chưa có việc đang làm", "Kéo một thẻ vào đây khi bắt đầu làm."),
            "done": ("✓", "Chưa có việc hoàn thành", "Những việc đã xong sẽ được lưu ở đây.")
        }
        symbol, title, subtitle = empty_info.get(
            status, ("✦", "Chưa có công việc", "Công việc sẽ xuất hiện tại đây.")
        )
        palette = STATUS_STYLES.get(status, {"tint": "#EEF0FF", "accent": COLORS["blue"]})

        wrap = tk.Frame(parent, bg="#EDF0FA")
        wrap.pack(fill="x", pady=(45, 18), padx=12)

        tk.Label(
            wrap, text=symbol, bg=palette["tint"], fg=palette["accent"],
            font=(FONT_DISPLAY, 19, "bold"), width=3, pady=8
        ).pack(pady=(0, 12))

        tk.Label(
            wrap, text=title, bg="#EDF0FA", fg=COLORS["text"],
            font=(FONT_BODY, 10, "bold")
        ).pack()

        tk.Label(
            wrap, text=subtitle, bg="#EDF0FA", fg=COLORS["muted"],
            font=(FONT_BODY, 8), wraplength=250, justify="center"
        ).pack(pady=(5, 0))

    # -----------------------------------------------------
    # DANH SÁCH DỰ ÁN
    # -----------------------------------------------------

    def refresh_project_list(self):
        for widget in self.project_list.winfo_children():
            widget.destroy()

        projects = self.project_manager.get_all()

        if not projects:
            tk.Label(
                self.project_list,
                text="Chưa có dự án",
                bg="#F0EEFB",
                fg=COLORS["muted"],
                font=(FONT_BODY, 9)
            ).pack(anchor="w", padx=10, pady=8)

        for project in projects:
            selected = project.id == self.selected_project_id
            tk.Button(
                self.project_list,
                text=f"▸  {project.name}",
                bg="#E5E8FC" if selected else "#F0EEFB",
                fg=COLORS["blue"] if selected else COLORS["text"],
                font=(FONT_BODY, 10, "bold" if selected else "normal"),
                relief="flat",
                anchor="w",
                cursor="hand2",
                command=lambda p=project: self.root.after_idle(
                    lambda: self.select_project(p)
                ),
                padx=10,
                pady=8
            ).pack(fill="x", pady=2)

    def select_project(self, project):
        self.selected_project_id = project.id
        self.set_active_nav("projects")
        self.project_title.config(text=project.name)
        self.project_description.config(
            text=project.description or "Các công việc thuộc dự án"
        )
        self._show_view("board")
        self.refresh()

    # -----------------------------------------------------
    # CÁC CHỨC NĂNG MENU
    # -----------------------------------------------------

    def show_overview(self):
        self.selected_project_id = None
        self.set_active_nav("overview")
        self.project_title.config(text="Tổng quan")
        self.project_description.config(
            text="Biểu đồ tổng hợp toàn bộ công việc trong hệ thống"
        )
        self._show_view("overview")
        self.refresh()

    def show_board(self):
        self.selected_project_id = None
        self.set_active_nav("board")
        self.project_title.config(text="Bảng công việc")
        self.project_description.config(
            text="Theo dõi công việc theo từng trạng thái — kéo thả thẻ giữa các cột"
        )
        self._show_view("board")
        self.refresh()

    def show_projects(self):
        self.selected_project_id = None
        self.set_active_nav("projects")
        self.project_title.config(text="Danh sách dự án")
        count = len(self.project_manager.get_all())
        self.project_description.config(
            text=f"Đang quản lý {count} dự án — chọn một dự án ở thanh bên để lọc công việc"
        )
        self._show_view("board")
        self.refresh()

    # -----------------------------------------------------
    # THÊM CÔNG VIỆC
    # -----------------------------------------------------

    def add_task(self):
        if not self.project_manager.get_all():
            messagebox.showinfo(
                "Thông báo",
                "Bạn cần tạo dự án trước khi thêm công việc.",
                parent=self.root
            )
            self.add_project()
            return

        TaskForm(
            self.root,
            self.on_data_changed,
            default_project_id=self.selected_project_id
        )

    # -----------------------------------------------------
    # TẠO DỰ ÁN
    # -----------------------------------------------------

    def add_project(self):
        dialog = tk.Toplevel(self.root)

        dialog.title("Tạo dự án mới")
        center_window(dialog, self.root, 400, 280)
        dialog.resizable(False, False)
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Tạo dự án mới",
            bg="white",
            fg=COLORS["text"],
            font=(FONT_BODY, 16, "bold")
        ).pack(pady=20)

        name_var = tk.StringVar()
        description_var = tk.StringVar()

        tk.Label(dialog, text="Tên dự án", bg="white", fg=COLORS["text"]).pack(anchor="w", padx=25)

        name_entry = tk.Entry(dialog, textvariable=name_var, font=(FONT_BODY, 10))
        name_entry.pack(fill="x", padx=25, pady=7, ipady=5)

        tk.Label(dialog, text="Mô tả dự án", bg="white", fg=COLORS["text"]).pack(anchor="w", padx=25)

        tk.Entry(
            dialog, textvariable=description_var, font=(FONT_BODY, 10)
        ).pack(fill="x", padx=25, pady=7, ipady=5)

        def save_project():
            try:
                project = self.project_manager.add_project(
                    name_var.get(),
                    description_var.get().strip()
                )

                messagebox.showinfo(
                    "Thành công",
                    f"Đã tạo dự án: {project.name}",
                    parent=dialog
                )

                dialog.destroy()
                self.on_data_changed(f"Tạo dự án {project.id}")

            except (ValueError, OSError) as error:
                messagebox.showerror("Lỗi", str(error), parent=dialog)

        tk.Button(
            dialog,
            text="Lưu dự án",
            bg=COLORS["blue"],
            fg="white",
            relief="flat",
            cursor="hand2",
            command=save_project,
            pady=9
        ).pack(fill="x", padx=25, pady=15)

        dialog.bind("<Return>", lambda _e: save_project())
        dialog.bind("<Escape>", lambda _e: dialog.destroy())
        name_entry.focus_set()

    # -----------------------------------------------------
    # ĐĂNG XUẤT
    # -----------------------------------------------------

    def logout(self):
        if not messagebox.askyesno(
            "Đăng xuất", "Bạn có muốn đăng xuất?", parent=self.root
        ):
            return

        auth_manager.logout()

        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.root.unbind_all(sequence)

        if self.on_logout:
            self.on_logout()


# =========================================================
# CHẠY CHƯƠNG TRÌNH
# =========================================================

def show_login(root):
    clear_window(root)
    LoginWindow(root, auth_manager, on_success=lambda user: open_main(root, user))


def open_main(root, user):
    clear_window(root)
    MainWindow(root, user, on_logout=lambda: show_login(root))


def main():
    root = tk.Tk()
    setup_theme(root)
    show_login(root)
    root.mainloop()


if __name__ == "__main__":
    main()
