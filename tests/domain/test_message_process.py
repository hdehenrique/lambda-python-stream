import unittest
import json
from src.domain.message_process import message_processing, process_structure_tree

class TestMessageProcess(unittest.TestCase):
    def test_message_processing_success(self):
        # Mensagem de entrada simulada
        received_message = {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "id_client": "1",
            "order_uuid": "661b91ad-d715-4735-a0c2-ef3e4dc752a5",
            "channel_id": "8",
            "order_status": "3",
            "order_date_release": "2024-10-28 21:49:55",
            "order_date": "2024-10-28 18:49:33",
            "order_itens": "8",
            "order_number": "745080279",
            "order_points": "46",
            "order_value": "409.52",
        }

        # Resultado esperado
        expected_output = {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "id_client": 1,
            "order_id": "661b91ad-d715-4735-a0c2-ef3e4dc752a5",
            "channel_id": 8,
            "order_status": 3,
            "order_calculation_date": "2024-10-28 21:49:55",
            "order_date": "2024-10-28 18:49:33",
            "order_itens": 8,
            "order_number": "745080279",
            "order_points": 46,
            "order_value": 409.52,
        }

        # Chama a função
        result = message_processing(received_message)

        # Verifica se o resultado é o esperado
        self.assertEqual(json.loads(result), expected_output)

    def test_message_processing_missing_field(self):
        # Mensagem de entrada com campo ausente
        received_message = {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            # Campo "id_client" ausente
            "order_uuid": "661b91ad-d715-4735-a0c2-ef3e4dc752a5",
            "channel_id": "8",
            "order_status": "3",
            "order_date_release": "2024-10-28 21:49:55",
            "order_date": "2024-10-28 18:49:33",
            "order_itens": "8",
            "order_number": "745080279",
            "order_points": "46",
            "order_value": "409.52",
        }

        # Verifica se ocorre um KeyError
        with self.assertRaises(KeyError):
            message_processing(received_message)

    def test_message_processing_empty_message(self):
        # Mensagem de entrada vazia
        received_message = {}

        # Verifica se ocorre um KeyError
        with self.assertRaises(KeyError):
            message_processing(received_message)

    def test_message_processing_with_extra_fields(self):
        # Mensagem com campos extras
        received_message = {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "id_client": "1",
            "order_uuid": "661b91ad-d715-4735-a0c2-ef3e4dc752a5",
            "channel_id": "8",
            "order_status": "3",
            "order_date_release": "2024-10-28 21:49:55",
            "order_date": "2024-10-28 18:49:33",
            "order_itens": "8",
            "order_number": "745080279",
            "order_points": "46",
            "order_value": "409.52",
            "extra_field": "extra_value",  # Campo extra
        }

        # Chama a função
        result = message_processing(received_message)

        # Verifica se o campo extra não está no resultado
        self.assertNotIn("extra_field", json.loads(result))

    def test_process_structure_tree(self):
        # Testa a função process_structure_tree
        structure_tree = [{"structureLevel": 5, "structureCode": 22005}]
        expected_output = '[{"structureLevel": 5, "structureCode": 22005}]'

        # Chama a função
        result = process_structure_tree(structure_tree)

        # Verifica se o resultado é o esperado
        self.assertEqual(result, expected_output)


if __name__ == "__main__":
    unittest.main()