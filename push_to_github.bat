@echo off
chcp 65001 > nul
echo ===================================================
echo   GitHub 자동 연동 및 브리핑 업로드 스크립트
echo ===================================================
echo.
set /p REPO_URL="GitHub 저장소 URL을 입력하세요 (예: https://github.com/username/telegram-briefing.git): "

if "%REPO_URL%"=="" (
    echo [오류] 저장소 URL이 입력되지 않았습니다.
    pause
    exit /b 1
)

echo.
echo [1/3] Git 저장소 설정 및 브랜치 확인...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo.
echo [2/3] GitHub로 코드 업로드 (push)...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================================
    echo ✅ GitHub 업로드 성공!
    echo.
    echo 📌 마지막 텔레그램 토큰 등록 안내 (GitHub 웹 사이트):
    echo 1. 생성하신 GitHub 저장소 > Settings > Secrets and variables > Actions 이동
    echo 2. 'New repository secret' 클릭 후 등록:
    echo    - TELEGRAM_BOT_TOKEN : 8623383036:AAEas1taS1coGDZ6dueYnz5HHYhGZD50TWw
    echo    - TELEGRAM_CHAT_ID   : 8784137781
    echo ===================================================
) else (
    echo.
    echo ❌ GitHub 업로드에 실패했습니다. GitHub 계정 인증 또는 저장소 주소를 확인해주세요.
)

pause
