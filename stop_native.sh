#!/usr/bin/env bash
pkill -f "uvicorn virtual_robot.main:app" 2>/dev/null || true
pkill -f "uvicorn app.main:app" 2>/dev/null || true
echo "Native services stopped."
