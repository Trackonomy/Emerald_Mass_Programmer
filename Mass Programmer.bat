@echo off
mode con: cols=200 lines=500
@REM git stash -a
@REM git pull
@REM git stash pop
<<<<<<< HEAD
py TrkMassProg_Main.py
=======
TrkMassProg2.py
>>>>>>> 3730405e679ddc8f3c7a431723e0e730f68d66ba
if %ERRORLEVEL% neq 0 goto ProcessError

exit /b 0

:ProcessError
    pip install -r requirements.txt
<<<<<<< HEAD
    py TrkMassProg_Main.py
=======
    py TrkMassProg2.py
>>>>>>> 3730405e679ddc8f3c7a431723e0e730f68d66ba
exit /b 1