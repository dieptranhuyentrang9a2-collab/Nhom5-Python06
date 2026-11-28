#!/usr/bin/env bash
# Đóng gói ứng dụng (macOS / Linux): dist/QuanLyCongViec
set -e
python3 -m pip install -r requirements.txt
python3 -m PyInstaller --noconfirm --onefile --windowed --name QuanLyCongViec main.py
echo "Xong! File chạy: dist/QuanLyCongViec"
