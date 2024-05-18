FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install fastapi==0.109.0 && \
    echo "Installed fastapi" && \
    pip install orjson==3.9.12 && \
    echo "Installed orjson" && \
    pip install pydantic==2.5.3 && \
    echo "Installed pydantic" && \
    pip install pydantic-settings==2.1.0 && \
    echo "Installed pydantic-settings" && \
    pip install uvicorn==0.12.2 && \
    echo "Installed uvicorn" && \
    pip install python-dotenv==1.0.0 && \
    echo "Installed python-dotenv" && \
    pip install aiohttp==3.9.3 && \
    echo "Installed aiohttp" && \
    pip install opentelemetry-api==1.17.0 && \
    echo "Installed opentelemetry-api" && \
    pip install opentelemetry-sdk==1.17.0 && \
    echo "Installed opentelemetry-sdk" && \
    pip install opentelemetry-instrumentation-fastapi==0.38b0 && \
    echo "Installed opentelemetry-instrumentation-fastapi" && \
    pip install opentelemetry-exporter-jaeger==1.17.0 && \
    echo "Installed opentelemetry-exporter-jaeger" && \
    pip install sentry-sdk[fastapi]==1.45.0 && \
    echo "Installed sentry-sdk"

COPY . .

RUN ["chmod", "+x", "entrypoint.sh"]
ENTRYPOINT ["./entrypoint.sh"]