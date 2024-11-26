@echo off
REM Batch file to run the MetaDataScanner Python program

REM Set the Python executable path if necessary
set PYTHON_EXEC=python

REM Set the script location
set SCRIPT_PATH="%~dp0setup.py"

REM Run the Python script
%PYTHON_EXEC% %SCRIPT_PATH%

REM Pause to keep the window open after execution
pause
