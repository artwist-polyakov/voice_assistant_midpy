FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN echo "[global]\njobs=1" > /etc/pip.conf
RUN pip install --upgrade pip -vvv
RUN pip install --no-cache-dir -r requirements.txt -vvv

COPY . .

RUN ["chmod", "+x", "entrypoint.sh"]
ENTRYPOINT ["./entrypoint.sh"]