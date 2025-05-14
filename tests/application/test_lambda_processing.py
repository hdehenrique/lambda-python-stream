import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import base64
import asyncio
from src.application.lambda_processing import process_messages
from app import handler, topic_send, topic_send_fail

@pytest.mark.asyncio
@patch("src.application.lambda_processing.message_processing")
@patch("src.application.lambda_processing.KafkaProducer")
async def test_process_messages_success(mock_kafka_producer, mock_message_processing):
    # Mock do KafkaProducer
    mock_producer_instance = MagicMock()
    mock_kafka_producer.return_value = mock_producer_instance

    # Mock do processamento de mensagens
    mock_message_processing.return_value = '{"processed": "message"}'

    # Evento com múltiplas partições
    event = {
        "records": {
            "partition1": [
                {"value": base64.b64encode(b'{"uuid": "123", "order_id": "456", "country_iso": "BR"}').decode("utf-8")}
            ],
            "partition2": [
                {"value": base64.b64encode(b'{"uuid": "789", "order_id": "101", "country_iso": "US"}').decode("utf-8")}
            ]
        }
    }

    # Chama a função process_messages
    await process_messages(event, mock_producer_instance, "topic_send", "topic_send_fail", "lambda_processing")

    # Verifica se o processamento foi chamado para cada mensagem
    assert mock_message_processing.call_count == 2

    # Verifica os argumentos passados para cada chamada
    mock_message_processing.assert_any_call(
        {"uuid": "123", "order_id": "456", "country_iso": "BR"}
    )
    mock_message_processing.assert_any_call(
        {"uuid": "789", "order_id": "101", "country_iso": "US"}
    )

    # Verifica se as mensagens foram enviadas para o Kafka
    assert mock_producer_instance.send.call_count == 2

@pytest.mark.asyncio
@patch("src.application.lambda_processing.message_processing")
@patch("src.application.lambda_processing.KafkaProducer")
async def test_process_messages_failure(mock_kafka_producer, mock_message_processing):
    # Mock do KafkaProducer
    mock_producer_instance = MagicMock()
    mock_kafka_producer.return_value = mock_producer_instance

    # Simula uma exceção ao processar a mensagem
    mock_message_processing.side_effect = Exception("Processing error")

    # Evento com uma mensagem
    event = {
        "records": {
            "partition1": [
                {"value": base64.b64encode(b'{"uuid": "123", "order_id": "456", "country_iso": "BR"}').decode("utf-8")}
            ]
        }
    }

    # Chama a função process_messages
    await process_messages(event, mock_producer_instance, "topic_send", "topic_send_fail", "lambda_processing")

    # Verifica se a mensagem de erro foi enviada para o tópico de falhas
    mock_producer_instance.send.assert_called_once_with(
        "topic_send_fail",
        b'{"lambda": "lambda_processing", "eventProcessorError": {"message": "Processing error"}, "payloadEvent": {"uuid": "123", "order_id": "456", "country_iso": "BR"}}'
    )

@pytest.mark.asyncio
@patch("app.KafkaProducer")
@patch("app.process_messages", new_callable=AsyncMock)
async def test_handler_success(mock_process_messages, mock_kafka_producer):
    # Mock do KafkaProducer
    mock_producer_instance = MagicMock()
    mock_kafka_producer.return_value = mock_producer_instance

    # Evento com múltiplas partições
    event = {
        "records": {
            "partition1": [
                {"value": base64.b64encode(b'{"uuid": "123", "id_client": "1", "order_uuid": "456", "channel_id": "8", "order_status": "3", "order_date_release": "2024-10-28 21:49:55", "order_date": "2024-10-28 18:49:33", "order_itens": "8", "order_number": "745080279", "order_points": "46", "order_value": "409.52"}').decode("utf-8")}
            ]
        }
    }

    # Chama o handler
    await handler(event, None)

    # Verifica se process_messages foi chamado
    assert mock_process_messages.call_count == 1

@pytest.mark.asyncio
@patch("app.KafkaProducer")
@patch("app.message_processing")
async def test_handler_multiple_partitions(mock_message_processing, mock_kafka_producer):
    # Mock do KafkaProducer
    mock_producer_instance = MagicMock()
    mock_kafka_producer.return_value = mock_producer_instance

    # Mock do processamento de mensagens
    mock_message_processing.return_value = '{"processed": "message"}'

    # Evento com múltiplas partições
    event = {
        "records": {
            "partition1": [
                {"value": base64.b64encode(b'{"uuid": "123", "order_id": "456", "country_iso": "BR"}').decode("utf-8")}
            ],
            "partition2": [
                {"value": base64.b64encode(b'{"uuid": "789", "order_id": "101", "country_iso": "US"}').decode("utf-8")}
            ]
        }
    }

    # Chama o handler
    await handler(event, None)

    # Verifica se o processamento foi chamado para cada mensagem
    assert mock_message_processing.call_count == 2

    # Verifica se o KafkaProducer enviou as mensagens
    assert mock_producer_instance.send.call_count == 2

if __name__ == "__main__":
    unittest.main()