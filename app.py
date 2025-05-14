import json
import base64
import logging
import asyncio
from os import getenv
from kafka import KafkaProducer
from src.domain.message_process import message_processing
from src.helper.logger.logger import Logger
from src.helper.logger.log_manager import setup_global_logger, set_log_context, get_log_context
from src.application.lambda_processing import process_messages


logger = Logger("app.py")
setup_global_logger()

env = getenv("lambda_env")
lambda_name = getenv("lambda_name")
topic_send = "topic-send-messages"
topic_send_fail = 'topic-failed-messages'

msk_servers = getenv("msk_servers", "localhost:9092").split(",")


def handler(event, _):
    set_log_context(event_source="MSK")
    context = get_log_context()
    correlation_id = context["correlationId"]
    event_source = context["eventSource"]

    try:
        # Executa a lógica assíncrona usando asyncio.run
        return asyncio.run(async_handler(event, _))
    except Exception as e:
        logger.error(f"Error in handler: {e}")
        raise e


async def async_handler(event, _):
    try:
        producer = KafkaProducer(bootstrap_servers=msk_servers)
    except Exception as e:
        logger.error(f"Failed to connect to Kafka: {e}")
        raise e

    records = event.get("records", {})
    for partition, messages in records.items():
        for message in messages:
            try:
                decoded_message = json.loads(base64.b64decode(message["value"]).decode("utf-8"))
                send_json = message_processing(decoded_message)
                await process_messages(decoded_message, producer, topic_send, topic_send_fail, lambda_name)
                producer.send(topic_send, send_json.encode("utf-8")).get(10)
            except KeyError as e:
                logger.error(f"Missing required field: {e}")
                send_json = json.dumps({
                    "lambda": lambda_name,
                    "eventProcessorError": {"message": f"Missing required field: {e}"},
                    "payloadEvent": decoded_message  # Usa a mensagem decodificada
                })
                producer.send(topic_send_fail, send_json.encode("utf-8")).get(10)
            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                send_json = json.dumps({
                    "lambda": lambda_name,
                    "eventProcessorError": {"message": str(e)},
                    "payloadEvent": decoded_message  # Usa a mensagem decodificada
                })
                producer.send(topic_send_fail, send_json.encode("utf-8")).get(10)

    return {"status": "success", "message": "Messages processed successfully"}
