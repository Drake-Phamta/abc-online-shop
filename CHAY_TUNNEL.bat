@echo off
rem Public address for the demo shop through a Cloudflare quick tunnel (no account, the address changes every time).
rem Double-click: starts the shop if needed, prints https://....trycloudflare.com and opens it. Close this window to stop.
title ABC Online Shop - public tunnel (close this window to stop)
powershell -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0tools\quick_tunnel.ps1"
pause
