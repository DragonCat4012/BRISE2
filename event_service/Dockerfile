FROM rabbitmq:4.2.5

RUN rabbitmq-plugins enable --offline rabbitmq_management rabbitmq_web_stomp rabbitmq_mqtt

COPY ./bin/definitions.json /etc/rabbitmq/
#COPY ./bin/rabbitmq.config /etc/rabbitmq/
COPY ./bin/rabbitmq.conf /etc/rabbitmq/rabbitmq.conf

# If you need custom logs, ensure the directory exists
USER root
RUN mkdir -p /var/log/rabbitmq && chown rabbitmq:rabbitmq /var/log/rabbitmq
USER rabbitmq

ENV RABBITMQ_LOGS=/var/log/rabbitmq/warning_log.log
EXPOSE 49153 49154 49155