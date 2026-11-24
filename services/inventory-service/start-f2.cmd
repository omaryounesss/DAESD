@echo off
setlocal
title DaESD F2 inventory worker
python "%~dp0connect_f2.py" --credentials "%USERPROFILE%\Downloads\daesd-omar-f2-worker-springboot.properties"
echo.
pause

