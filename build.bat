@echo off
REM Đóng gói ứng dụng thành dist\QuanLyCongViec.exe (chạy trên Windows)
chcp 65001 >nul
python -m pip install -r requirements.txt || goto :err
python -m PyInstaller --noconfirm --onefile --windowed --name QuanLyCongViec main.py || goto :err
echo.
echo Xong! File chay: dist\QuanLyCongViec.exe
echo Du lieu se duoc tao trong thu muc "data" canh file .exe
pause
exit /b 0
:err
echo Dong goi that bai.
pause
exit /b 1
