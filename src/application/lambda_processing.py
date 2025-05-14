import json
import base64
import logging
import asyncio
from kafka import KafkaProducer
from src.domain.message_process import message_processing

logger = logging.getLogger("message_orchestrator")

# Função assíncrona para processar múltiplas mensagens
async def process_messages(event, producer, topic_send, topic_send_fail, lambda_name):
    records = event.get("records", {})
    partitions = records.keys()

    list_records = []
    for partition in partitions:
        for record in records[partition]:
            list_records.append(base64.b64decode(record.get("value")))

    # Função interna para processar uma única mensagem
    async def process_single_message(received_message):
        try:
            received_message = json.loads(received_message)
            send_json = message_processing(received_message)

            producer.send(topic_send, send_json.encode("utf-8")).get(10)

        except Exception as e:
            # Loga o erro caso o processamento da mensagem falhe
            logger.error(f"Failed to process message: {e}")
            producer.send(topic_send_fail, json.dumps({
                "lambda": lambda_name,
                "eventProcessorError": {"message": str(e)},
                "payloadEvent": received_message
            }).encode("utf-8"))

    # Cria uma lista de tarefas assíncronas para processar cada mensagem
    tasks = [process_single_message(message) for message in list_records]
    
    # Executa todas as tarefas de forma assíncrona e simultânea
    await asyncio.gather(*tasks)