# Hướng dẫn cài đặt và sử dụng

Ứng dụng **Quản lý công việc Kanban – Nhóm 5** (Python + Tkinter, lưu dữ liệu bằng JSON).

## 1. Yêu cầu
- Python **3.9 trở lên** (tải tại https://www.python.org/downloads/ – khi cài Windows nhớ tick *Add Python to PATH*, và giữ mục *tcl/tk and IDLE*).
- Không cần cài thêm thư viện nào để chạy từ mã nguồn.
- Kiểm tra: `python --version` và `python -m tkinter` (hiện cửa sổ nhỏ là Tkinter hoạt động).
  - Ubuntu/Debian nếu thiếu Tkinter: `sudo apt install python3-tk`.

## 2. Chạy từ mã nguồn
```
cd Nhom5-Python06-main
python main.py
```
Tài khoản mặc định: **admin / admin123** (có thể tự đăng ký tài khoản mới ở màn hình đăng nhập).
Dữ liệu nằm trong thư mục `data/`, bản sao lưu trong `data/backups/`.

## 3. Công cụ dòng lệnh (`tienich.py`)
| Lệnh | Tác dụng |
|---|---|
| `python tienich.py --info` | Xem phiên bản Python, hệ điều hành, thư mục dữ liệu |
| `python tienich.py --sample 30` | Sao lưu rồi xóa dữ liệu cũ, sinh dữ liệu mẫu (tài khoản mẫu mật khẩu `123456`) |
| `python tienich.py --fetch 10` | Lấy 10 công việc từ API (cần Internet; mất mạng thì dùng bản cache) |
| `python tienich.py --export all` | Xuất `tasks.csv`, `tasks.json`, `summary.txt` vào thư mục `exports/` |

## 4. Chạy kiểm thử
```
python -m unittest test_vy -v      # kiểm thử phần mở rộng (21 ca)
python test_leader.py              # kiểm thử lớp nghiệp vụ
python test_integration.py         # kiểm thử đọc/ghi JSON
```

## 5. Đóng gói thành file chạy (không cần cài Python)
- **Windows:** nhấp đúp `build.bat` → lấy file `dist\QuanLyCongViec.exe`.
- **macOS/Linux:** `./build.sh` → lấy file `dist/QuanLyCongViec`.

Gửi file trong `dist/` cho người dùng; thư mục `data/` sẽ tự tạo cạnh file chạy ở lần mở đầu tiên.
Lưu ý: đóng gói trên hệ điều hành nào thì chỉ chạy được trên hệ điều hành đó.

## 6. Xử lý sự cố
| Lỗi | Cách xử lý |
|---|---|
| `No module named tkinter` | Cài lại Python có Tcl/Tk (hoặc `sudo apt install python3-tk`) |
| Quên mật khẩu admin | Xóa `data/users.json` → mở lại ứng dụng, tài khoản `admin / admin123` được tạo lại |
| Dữ liệu bị hỏng | Chép file trong `data/backups/*.bak` đè lên file `.json` tương ứng |
| `--fetch` báo 0 công việc | Không có Internet và chưa có cache; thử lại khi có mạng |
