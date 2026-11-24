@echo off
setlocal
title DaESD F2 Tasklist activation
echo Stop the old inventory worker with Ctrl+C before running this launcher.
python "%~dp0..\..\scripts\deploy_f2.py"
if errorlevel 1 (
  echo Deployment failed. The new worker was not started.
  pause
  exit /b 1
)
call "%~dp0start-f2.cmd"

