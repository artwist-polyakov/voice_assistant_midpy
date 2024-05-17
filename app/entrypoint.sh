#!/bin/sh

# Путь к лог-файлу
LOG_FILE=/app/logs/logs.log

# Проверка наличия директории и файла логов
if [ ! -d "/app/logs" ]; then
  mkdir -p /app/logs
fi

if [ ! -f "$LOG_FILE" ]; then
  touch "$LOG_FILE"
  echo "Log file created at $LOG_FILE"
else
  echo "Log file already exists at $LOG_FILE"
fi

# Запуск приложения
exec uvicorn main:app --host 0.0.0.0 --port 5555