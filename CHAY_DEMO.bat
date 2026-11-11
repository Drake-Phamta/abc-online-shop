@echo off
rem ABC Online Shop demo. Double-click: starts the server on a fresh demo database and opens the shop in the browser.
rem Close this window (or press Ctrl+C) to stop the server.
rem "CHAY_DEMO.bat keep" keeps the data of the previous run instead of recreating the database.
setlocal
title ABC Online Shop - demo server (close this window to stop)
set "URL=http://localhost:8080/"
set "JAR=target\abc-online-shop-1.0.0.jar"
set "RESET=--abc.db.reset=true"
if /i "%~1"=="keep" set "RESET="
cd /d "%~dp0app"

rem 0. Register the link type abcshop: for this Windows user (no admin rights, nothing else changes). The showcase
rem    pages use it to run this file when the server is not running yet ("Open the shop") and to show a file in
rem    File Explorer. It is written again on every run, so it always points to this copy of the project.
rem    Details in showcase\abcshop.ps1. To remove it: reg delete "HKCU\Software\Classes\abcshop" /f
powershell -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0showcase\abcshop.ps1" -Register >nul 2>&1

rem 1. Already running: only open the browser.
powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 '%URL%' | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 goto findjava
echo The shop is already running at %URL%
start "" "%URL%"
timeout /t 3 >nul
exit /b 0

rem 2. Java 17 or newer: JAVA_HOME first, then the usual JDK folders. The "java" on PATH may be an older Java 8.
:findjava
set "JAVA="
if defined JAVA_HOME call :tryjava "%JAVA_HOME%\bin\java.exe"
if not defined JAVA for /d %%d in ("%ProgramFiles%\Eclipse Adoptium\jdk-*" "%ProgramFiles%\Java\jdk-*" "%ProgramFiles%\Microsoft\jdk-*") do if not defined JAVA call :tryjava "%%~d\bin\java.exe"
if not defined JAVA for /f "delims=" %%j in ('where java 2^>nul') do if not defined JAVA call :tryjava "%%~j"
if defined JAVA goto build
echo.
echo Java 17 or newer was not found. Install a JDK 17 (for example Eclipse Temurin 17) and run this file again.
pause
exit /b 1

rem 3. Build the application once if the jar is missing.
:build
for %%j in ("%JAVA%") do set "JAVA_HOME=%%~dpj.."
if exist "%JAR%" goto run
echo Building the application (first run only, about one minute)...
call mvn -q package -DskipTests
if exist "%JAR%" goto run
echo.
echo The build failed. Run "mvn package" in the app folder to see the error.
pause
exit /b 1

rem 4. Open the browser as soon as the server answers, and run the server in this window.
:run
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "for ($i = 0; $i -lt 120; $i++) { try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 '%URL%' | Out-Null; Start-Process '%URL%'; break } catch { Start-Sleep -Seconds 1 } }"
echo.
echo  ABC Online Shop  -  %URL%
if defined RESET (echo  Database: fresh demo data) else (echo  Database: kept from the previous run)
echo.
echo  Accounts, password demo1234:
echo    an.nguyen@example.com    VIP customer
echo    lan.tran@example.com     new customer
echo    sales@example.com        sales staff, order board
echo    warehouse@example.com    warehouse staff, stock
echo  Cards: 4242 4242 4242 4242 approved, 4000 0000 0000 0002 declined.  Alt+L: design lens.
echo.
echo  The browser opens when the server is ready. Close this window to stop the server.
echo.
"%JAVA%" -jar "%JAR%" %RESET%
echo.
echo The server has stopped.
pause
exit /b 0

:tryjava
if not exist "%~1" exit /b 0
"%~1" -XshowSettings:properties -version 2>&1 | findstr /r /c:"java.specification.version = 1[7-9]" /c:"java.specification.version = [2-9][0-9]" >nul
if not errorlevel 1 set "JAVA=%~1"
exit /b 0
