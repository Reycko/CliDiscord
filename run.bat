@echo off && cls
echo Bot token?
set /p token=
echo Channel ID?
set /p chid=
echo.
:(re)start
python CliDiscord.py %token% %chid%
echo.
echo.
echo Press any key to restart the program.
pause
goto (re)start