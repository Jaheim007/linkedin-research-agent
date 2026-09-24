@echo off
title Research Agent (research-01) - Port 9001
echo ========================================================
echo   Starting Research Agent (research-01) on Port 9001
echo ========================================================
cd /d %~dp0
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe research_agent.py
) else (
    python research_agent.py
)
pause
