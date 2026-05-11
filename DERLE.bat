@echo off
title ProNet Client Fixer - EXE Derleme Scripti
color 0A
echo.
echo  ================================================
echo   ProNet Client Fixer v.01 - EXE Derleme Araci
echo  ================================================
echo.

:: Python kontrolu
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [HATA] Python bulunamadi!
    echo  Lutfen https://python.org adresinden Python 3.x indirip kurun.
    echo  Kurulum sirasinda "Add Python to PATH" secenegini isaretleyin!
    pause
    exit /b 1
)

echo  [OK] Python bulundu.

:: pip guncelle
echo  [..] pip guncelleniyor...
python -m pip install --upgrade pip --quiet

:: PyInstaller kur
echo  [..] PyInstaller kuruluyor...
pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo  [HATA] PyInstaller kurulamadi!
    pause
    exit /b 1
)
echo  [OK] PyInstaller hazir.

:: Derleme
echo.
echo  [..] EXE derleniyor, lutfen bekleyin...
echo.

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "ProNet Client Fixer v01" ^
  --add-data "." ^
  --hidden-import=winreg ^
  --hidden-import=ctypes ^
  --hidden-import=tkinter ^
  --hidden-import=tkinter.ttk ^
  --hidden-import=tkinter.filedialog ^
  --hidden-import=tkinter.messagebox ^
  --hidden-import=tkinter.scrolledtext ^
  --uac-admin ^
  pronet_client_fixer.py

if %errorlevel% neq 0 (
    echo.
    echo  [HATA] Derleme basarisiz!
    pause
    exit /b 1
)

echo.
echo  ================================================
echo   BASARILI! EXE dosyasi olusturuldu:
echo   dist\ProNet Client Fixer v01.exe
echo  ================================================
echo.
echo  Bu dosyayi istediginiz bilgisayara tasiyabilirsiniz.
echo  Hicbir kurulum gerektirmez, cift tikla calisir.
echo.

:: dist klasorunu ac
explorer dist

pause
