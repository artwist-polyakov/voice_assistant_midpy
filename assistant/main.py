from fastapi import FastAPI
import sentry_sdk

sentry_sdk.init(
    dsn="https://4f00dac96532d2ac5f94f2bd9453cc39@o4507097467846656.ingest.de.sentry.io/4507226490011728",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

app = FastAPI()

@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
