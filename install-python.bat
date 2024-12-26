@echo off
cd /d %~dp0

powershell.exe -ExecutionPolicy Bypass -File .\py.ps1

init.bat

PAUSE