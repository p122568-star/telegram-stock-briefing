@echo off
chcp 65001 > nul
echo ========================================================
echo   매일 아침 08:00 텔레그램 증시 브리핑 작업 스케줄러 등록
echo ========================================================

SET SCRIPT_PATH=%~dp0telegram_stock_briefing.py
SET TASK_NAME=StockTelegramBriefing

:: 파이썬 실행 파일 경로 탐색
FOR /F "tokens=*" %%i IN ('where python 2^>nul') DO (
    SET PYTHON_EXE=%%i
    GOTO FOUND_PYTHON
)

:FOUND_PYTHON
IF "%PYTHON_EXE%"=="" (
    echo [오류] 시스템에서 python 실행 파일을 찾을 수 없습니다. Python을 설치해 주세요.
    pause
    exit /b 1
)

echo 사용 중인 Python 경로: %PYTHON_EXE%
echo 실행 대상 스크립트: %SCRIPT_PATH%
echo.

schtasks /Create /TN "%TASK_NAME%" /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\"" /SC DAILY /ST 08:00 /F

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 성공적으로 윈도우 작업 스케줄러에 등록되었습니다!
    echo    - 작업 이름: %TASK_NAME%
    echo    - 실행 시간: 매일 오전 08:00
) ELSE (
    echo.
    echo ❌ 작업 스케줄러 등록 실패. 관리자 권한으로 실행해 보세요.
)

echo.
pause
