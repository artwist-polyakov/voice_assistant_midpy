#!/bin/bash

wait_for_elastic() {
  tries=1
  echo "Waiting for Elastisearch."
  until curl "elasticsearch:$ELASTIC_PORT/_cluster/health?wait_for_status=yellow&timeout=30s"; do
    >&2 echo "Elastisearch is unavailable - waiting for it... 😴 ($tries)"
    sleep 1
    tries=$(expr $tries + 1)
  done
  echo "Elasticsearch is ready!"
}

wait_for_elastic

uvicorn main:app --proxy-headers --host 0.0.0.0 --port 5556