import json

def process_structure_tree(tree):
    return json.dumps(tree)

def message_processing(received_message):
    required_fields = [
        "uuid", "id_client", "order_uuid", "channel_id", "order_status", "order_date_release", "order_date",
        "order_itens", "order_number", "order_points", "order_value"
    ]
    # Valida se todos os campos obrigatórios estão presentes
    for field in required_fields:
        if field not in received_message:
            raise KeyError(f"Missing required field: {field}")

    file_send = {}
    file_send["uuid"] = received_message["uuid"]
    file_send["id_client"] = int(received_message["id_client"])
    file_send["order_id"] = received_message["order_uuid"]
    file_send["channel_id"] = int(received_message["channel_id"])
    file_send["order_status"] = int(received_message["order_status"])
    file_send["order_calculation_date"] = received_message["order_date_release"]
    file_send["order_date"] = received_message["order_date"]
    file_send["order_itens"] = int(received_message["order_itens"])
    file_send["order_number"] = received_message["order_number"]
    file_send["order_points"] = int(received_message["order_points"])
    file_send["order_value"] = float(received_message["order_value"])

    # Replica os campos do required_fields para o dicionário file_send
    for field in required_fields:
        if field not in file_send:
            file_send[field] = received_message[field]

    return json.dumps(file_send)