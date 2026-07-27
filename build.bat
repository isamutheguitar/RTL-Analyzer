@echo off
REM ============================================================
REM  Dual-Channel RTL Analyzer — PyInstaller ビルドスクリプト
REM  使用方法: build.bat をダブルクリック or コマンドプロンプトで実行
REM ============================================================

echo [RTL Analyzer] 依存パッケージをインストールしています...
pip install PySide6 sounddevice numpy scipy matplotlib pyinstaller

echo.
echo [RTL Analyzer] PyInstaller でビルド中...

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "RTL_Analyzer" ^
    --icon NONE ^
    --add-data "." ^
    --hidden-import "sounddevice" ^
    --hidden-import "scipy.signal" ^
    --hidden-import "scipy.signal._upfirdn" ^
    --hidden-import "scipy.signal._upfirdn_apply" ^
    --hidden-import "matplotlib.backends.backend_qtagg" ^
    --hidden-import "matplotlib.backends.backend_agg" ^
    --hidden-import "PySide6.QtSvg" ^
    --hidden-import "PySide6.QtOpenGL" ^
    --collect-all "sounddevice" ^
    --collect-all "matplotlib" ^
    --collect-all "scipy" ^
    main.py

echo.
if exist "dist\RTL_Analyzer.exe" (
    echo [SUCCESS] ビルド成功: dist\RTL_Analyzer.exe
) else (
    echo [ERROR] ビルドに失敗した可能性があります。上のログを確認してください。
)

pause
