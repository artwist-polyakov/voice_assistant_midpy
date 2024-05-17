FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Отключение проблемных скриптов APT
RUN mv /etc/apt/apt.conf.d/docker-clean /etc/apt/apt.conf.d/docker-clean.bak

# Установка системных зависимостей
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Восстановление конфигурации APT
RUN mv /etc/apt/apt.conf.d/docker-clean.bak /etc/apt/apt.conf.d/docker-clean

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt requirements.txt

# Настройка pip для однопоточной установки
RUN echo "[global]\njobs=1" > /etc/pip.conf
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копирование оставшегося кода
COPY . .

# Предоставление прав на выполнение скрипта entrypoint.sh
RUN ["chmod", "+x", "entrypoint.sh"]
ENTRYPOINT ["./entrypoint.sh"]