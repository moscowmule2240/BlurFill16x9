@echo off
chcp 65001 >nul

set "INPUT_FOLDER=%~1"
echo 🗂 処理対象のフォルダ: %INPUT_FOLDER%

set SCRIPT_DIR=%~dp0

if not exist "%INPUT_FOLDER%" (
    echo ❌ 指定されたフォルダが見つかりません。
    goto end
)

set VENV_PYTHON=%SCRIPT_DIR%\.venv\Scripts\python.exe
if not exist "%VENV_PYTHON%" (
    echo ❌ 仮想環境の python.exe が見つかりません: %VENV_PYTHON%
    goto end
)

"%VENV_PYTHON%" "%SCRIPT_DIR%blur_fill_16x9.py" "%INPUT_FOLDER%"

:end
echo.
echo 🔚 スクリプト終了。5秒後に閉じます...
timeout /t 5 >nul
