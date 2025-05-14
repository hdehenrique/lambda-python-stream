import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import base64
from app import handler, topic_send, topic_send_fail
import asyncio
import pytest


class TestApp(unittest.TestCase):

    @patch("app.KafkaProducer")
    @patch("app.getenv")
    def test_kafka_producer_connection_success(self, mock_getenv, mock_kafka_producer):
        # Mock da variável de ambiente
        mock_getenv.side_effect = lambda key, default=None: "localhost:9092" if key == "msk_servers" else default

        # Mock do KafkaProducer
        mock_kafka_producer.return_value = MagicMock()

        # Testa se o KafkaProducer é inicializado corretamente dentro do handler
        try:
            handler({"records": {}}, None)
        except Exception:
            self.fail("KafkaProducer initialization failed unexpectedly!")

    @patch("app.KafkaProducer")
    def test_kafka_producer_connection_failure(self, mock_kafka_producer):
        # Testa falha na conexão com o Kafka
        mock_kafka_producer.side_effect = Exception("Connection failed")
        with self.assertRaises(Exception):
            handler({"records": {}}, None)

    @patch("app.KafkaProducer")
    @patch("app.process_messages", new_callable=AsyncMock)
    def test_handler_success(self, mock_process_messages, mock_kafka_producer):
        # Mock do KafkaProducer
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        # Evento com múltiplas partições
        event = {
            "records": {
                "partition1": [
                    {"value": base64.b64encode(b'{"uuid": "123", "id_client": "1", "order_uuid": "456", "channel_id": "8", "order_status": "3", "order_date_release": "2024-10-28 21:49:55", "order_date": "2024-10-28 18:49:33", "order_itens": "8", "order_number": "745080279", "order_points": "46", "order_value": "409.52"}').decode("utf-8")}
                ],
                "partition2": [
                    {"value": base64.b64encode(b'{"uuid": "789", "id_client": "2", "order_uuid": "101", "channel_id": "9", "order_status": "4", "order_date_release": "2024-10-29 21:49:55", "order_date": "2024-10-29 18:49:33", "order_itens": "10", "order_number": "123456789", "order_points": "50", "order_value": "500.00"}').decode("utf-8")}
                ]
            }
        }

        # Chama o handler usando asyncio.run
        asyncio.run(handler(event, None))

        # Verifica se process_messages foi chamado para cada mensagem
        self.assertEqual(mock_process_messages.call_count, 2)

        # Verifica os argumentos passados para cada chamada
        mock_process_messages.assert_any_call(
            {
                "uuid": "123",
                "id_client": "1",
                "order_uuid": "456",
                "channel_id": "8",
                "order_status": "3",
                "order_date_release": "2024-10-28 21:49:55",
                "order_date": "2024-10-28 18:49:33",
                "order_itens": "8",
                "order_number": "745080279",
                "order_points": "46",
                "order_value": "409.52",
            },
            mock_producer_instance,
            topic_send,
            topic_send_fail,
            "lambda_processing",  # Nome da Lambda
        )
        mock_process_messages.assert_any_call(
            {
                "uuid": "789",
                "id_client": "2",
                "order_uuid": "101",
                "channel_id": "9",
                "order_status": "4",
                "order_date_release": "2024-10-29 21:49:55",
                "order_date": "2024-10-29 18:49:33",
                "order_itens": "10",
                "order_number": "123456789",
                "order_points": "50",
                "order_value": "500.00",
            },
            mock_producer_instance,
            topic_send,
            topic_send_fail,
            "lambda_processing",  # Nome da Lambda
        )

    @patch("app.KafkaProducer")
    @patch("app.process_messages", new_callable=AsyncMock)
    def test_handler_invalid_message(self, mock_process_messages, mock_kafka_producer):
        # Mock do KafkaProducer
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance

        # Simula uma exceção ao processar a mensagem
        mock_process_messages.side_effect = KeyError("Missing required field: uuid")

        # Evento com mensagem inválida
        event = {
            "records": {
                "partition1": [
                    {"value": base64.b64encode(b'{"order_uuid": "123"}').decode("utf-8")}
                ]
            }
        }

        # Chama o handler
        asyncio.run(handler(event, None))

        # Verifica se a mensagem de erro foi enviada para o tópico de falhas
        mock_producer_instance.send.assert_called_once_with(
            topic_send_fail,
            b'{"lambda": "lambda_processing", "eventProcessorError": {"message": "Missing required field: uuid"}, "payloadEvent": {"order_uuid": "123"}}'
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


if __name__ == "__main__":
    unittest.main()