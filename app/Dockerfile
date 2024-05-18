FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

# Сначала установим pipreqs, чтобы упростить процесс установки зависимостей по одной
RUN pip install --no-cache-dir pipreqs -vvv

# Создадим скрипт для установки зависимостей по одной
RUN touch install_requirements.sh && chmod +x install_requirements.sh
RUN echo '#!/bin/bash' > install_requirements.sh
RUN echo 'set -e' >> install_requirements.sh
RUN echo 'while read requirement; do' >> install_requirements.sh
RUN echo '    echo "Installing $requirement"' >> install_requirements.sh
RUN echo '    pip install --no-cache-dir $requirement -vvv' >> install_requirements.sh
RUN echo 'done < requirements.txt' >> install_requirements.sh

# Запустим скрипт установки зависимостей
RUN ./install_requirements.sh

COPY . .

RUN ["chmod", "+x", "entrypoint.sh"]
ENTRYPOINT ["./entrypoint.sh"]