#!/bin/sh

export RABBIT_MQ_HOST=${RABBIT_MQ_HOST:-"localhost"}
export RABBIT_MQ_PORT=${RABBIT_MQ_PORT:-5672}
export RABBIT_MQ_SUBJECT_QUEUE=${RABBIT_MQ_SUBJECT_QUEUE:-"_subject"}
export RABBIT_MQ_PERSON_QUEUE=${RABBIT_MQ_PERSON_QUEUE:-"_persons"}
export RABBIT_MQ_RATING_ORDER_QUEUE=${RABBIT_MQ_RATING_ORDER_QUEUE:-"_rating"}
export RABBIT_MQ_GENRE_FILTER_QUEUE=${RABBIT_MQ_GENRE_FILTER_QUEUE:-"_genre"}
export RABBIT_MQ_EXCHANGE=${RABBIT_MQ_EXCHANGE:-"_my_exchange"}
export RABBIT_MQ_DATE_FILTER_QUEUE=${RABBIT_MQ_DATE_FILTER_QUEUE:-"_date"}
export RABBIT_MQ_TITLE_TEXT_QUEUE=${RABBIT_MQ_TITLE_TEXT_QUEUE:-"_title"}
export RABBIT_MQ_DESCRIPTION_TEXT_QUEUE=${RABBIT_MQ_DESCRIPTION_TEXT_QUEUE:-"_description"}

#waiting for rabbitmq-server to start
set -e
until timeout 1 bash -c 'cat < /dev/null > /dev/tcp/${RABBIT_MQ_HOST}/${RABBIT_MQ_PORT}'; do
  >&2 echo "RabbitMQ is unavailable - sleeping"
  sleep 1
done

>&2 echo "RabbitMQ is up - executing command"

#executing command

rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} declare exchange name=${RABBIT_MQ_EXCHANGE} type=fanout

rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} declare queue name=${RABBIT_MQ_SUBJECT_QUEUE} durable=true
rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} declare queue name=${RABBIT_MQ_PERSON_QUEUE} durable=true
rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} declare queue name=${RABBIT_MQ_RATING_ORDER_QUEUE} durable=true
rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} declare queue name=${RABBIT_MQ_GENRE_FILTER_QUEUE} durable=true
rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} declare queue name=${RABBIT_MQ_DATE_FILTER_QUEUE} durable=true
rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} declare queue name=${RABBIT_MQ_TITLE_TEXT_QUEUE} durable=true
rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} declare queue name=${RABBIT_MQ_DESCRIPTION_TEXT_QUEUE} durable=true

rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} --vhost=/ declare binding source=${RABBIT_MQ_EXCHANGE} destination_type=queue destination=${RABBIT_MQ_SUBJECT_QUEUE}
rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} --vhost=/ declare binding source=${RABBIT_MQ_EXCHANGE} destination_type=queue destination=${RABBIT_MQ_PERSON_QUEUE}
rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} --vhost=/ declare binding source=${RABBIT_MQ_EXCHANGE} destination_type=queue destination=${RABBIT_MQ_RATING_ORDER_QUEUE}
rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} --vhost=/ declare binding source=${RABBIT_MQ_EXCHANGE} destination_type=queue destination=${RABBIT_MQ_GENRE_FILTER_QUEUE}
rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} --vhost=/ declare binding source=${RABBIT_MQ_EXCHANGE} destination_type=queue destination=${RABBIT_MQ_DATE_FILTER_QUEUE}
rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} --vhost=/ declare binding source=${RABBIT_MQ_EXCHANGE} destination_type=queue destination=${RABBIT_MQ_TITLE_TEXT_QUEUE}
rabbitmqadmin -H ${RABBIT_MQ_HOST} -P ${RABBIT_MQ_PORT} --vhost=/ declare binding source=${RABBIT_MQ_EXCHANGE} destination_type=queue destination=${RABBIT_MQ_DESCRIPTION_TEXT_QUEUE}

echo "Initialization completed"