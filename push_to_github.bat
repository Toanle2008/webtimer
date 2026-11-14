@echo off
chcp 65001 >nul
title Day Ma Nguon Web Timer Len GitHub

echo ========================================================
echo   DANG DAY MA NGUON WEB_TIMER LEN GITHUB
echo   Repo: https://github.com/Toanle2008/webtimer.git
echo ========================================================
echo.

cd /d "%~dp0"
set "GIT_PATH=C:\Program Files\Git\cmd\git.exe"

echo 1. Dang kiem tra git va commit moi nhat...
"%GIT_PATH%" config user.name "Toanle2008"
"%GIT_PATH%" config user.email "toanle2008@users.noreply.github.com"
"%GIT_PATH%" remote set-url origin https://github.com/Toanle2008/webtimer.git 2>nul || "%GIT_PATH%" remote add origin https://github.com/Toanle2008/webtimer.git
"%GIT_PATH%" branch -M main
"%GIT_PATH%" add .
"%GIT_PATH%" commit -m "Dragon City Battle Timer Cloud Server for Render" 2>nul

echo.
echo 2. Dang ket noi va day len GitHub...
echo (Neu chua dang nhap, trinh duyet se mo de ban dang nhap 1 lan)
echo.
"%GIT_PATH%" push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo   [THANH CONG] Toan bo ma nguon da duoc day len:
    echo   https://github.com/Toanle2008/webtimer
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo   [CHU Y] Neu gap loi xac thuc, ban chi can dang nhap
    echo   GitHub hoac cung cap Personal Access Token (PAT).
    echo ========================================================
)

echo.
pause
