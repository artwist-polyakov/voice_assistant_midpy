FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt requirements.txt

RUN echo "[global]\njobs=1" > /etc/pip.conf
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN ["chmod", "+x", "entrypoint.sh"]
ENTRYPOINT ["./entrypoint.sh"]