@echo off
mode con: cols=200 lines=500
@REM git stash -a
@REM git pull
@REM git stash pop
TrkMassProg2_Final_FW.py
if %ERRORLEVEL% neq 0 goto ProcessError

exit /b 0

:ProcessError
    pip install -r requirements.txt
    py TrkMassProg2_Final_FW.py
exit /b 1