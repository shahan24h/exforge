@echo off
cd /d S:\Pixelforge\Exforge
echo Starting ExForge at %date% %time% >> data\logs\run_log.txt
set PYTHONIOENCODING=utf-8
C:\Python314\python.exe -X utf8 main.py --now >> data\logs\run_log.txt 2>&1
echo Finished at %date% %time% >> data\logs\run_log.txt