@echo off
:: Lanza el script como administrador
powershell -Command "Start-Process pythonw.exe -ArgumentList 'sysguardian.py' -Verb runAs"
