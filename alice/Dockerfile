FROM python:3.10.20-bookworm@sha256:2cffd68eda34762d010cba5de2e4462fcdab15ac2a53722b7cb17e8c76255cb3

WORKDIR /app

COPY requirements-bootstrap.txt requirements-bootstrap.txt

RUN python -m pip install --no-cache-dir --disable-pip-version-check --require-hashes --only-binary=:all: -r requirements-bootstrap.txt

COPY requirements.txt requirements.txt

RUN python -m pip install --no-cache-dir --disable-pip-version-check --require-hashes --only-binary=:all: -r requirements.txt

COPY . .

RUN mkdir -p logs

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5555"]
