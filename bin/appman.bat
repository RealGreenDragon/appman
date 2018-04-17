@echo off

REM Run appman.py using embed python
%~dp0\python-embed\python -B %~dp0\..\appman.py %*
