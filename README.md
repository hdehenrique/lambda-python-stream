# Processamento em streaming com AWS Lambda e Python

Este projeto implementa uma **AWS Lambda em Python** para leitura de mensagens de um tópico Kafka, processamento das mensagens recebidas e envio para outro tópico Kafka. A solução foi projetada para ser escalável, eficiente e fácil de integrar com sistemas baseados em eventos.

---

## Funcionalidades

- **Leitura de Mensagens Kafka**:
  - A Lambda é acionada por eventos que contêm mensagens codificadas em Base64 provenientes de um tópico Kafka.
  - As mensagens são decodificadas e transformadas para o formato esperado.

- **Processamento de Mensagens**:
  - As mensagens recebidas são JSONs contendo mais de **35 campos**. Apenas os campos mapeados são extraídos e processados, garantindo que apenas os dados relevantes sejam enviados para o próximo estágio.
  - As mensagens são validadas e transformadas utilizando regras de negócio específicas.
  - Logs detalhados são gerados para monitoramento e depuração.

- **Envio para Outro Tópico Kafka**:
  - Após o processamento, as mensagens são enviadas para um tópico Kafka de destino.
  - Mensagens com erros são enviadas para um tópico de falhas para análise posterior.

- **Paralelismo para Alta Performance**:
  - O projeto utiliza **operações assíncronas** com `asyncio` para processar múltiplas mensagens simultaneamente.
  - Essa abordagem melhora a performance e a escalabilidade, permitindo que a Lambda lide com grandes volumes de dados de forma eficiente.

---

## Fluxo de Operação

1. **Recebimento de Mensagens**:
   - A Lambda é acionada por eventos que contêm mensagens codificadas em Base64.
   - As mensagens são decodificadas e transformadas em objetos JSON.

2. **Validação e Processamento**:
   - As mensagens são validadas para garantir que todos os campos obrigatórios estão presentes.
   - Apenas os campos mapeados no código são extraídos e processados.
   - O processamento é realizado de forma **assíncrona**, permitindo que múltiplas mensagens sejam tratadas em paralelo.

3. **Envio para Kafka**:
   - Mensagens processadas com sucesso são enviadas para o tópico Kafka de destino.
   - Mensagens que falham no processamento são enviadas para um tópico de falhas, com detalhes do erro.

---

## Estrutura do Projeto

```plaintext
lambda-python-stream/
├── src/
│   ├── application/
│   │   └── lambda_processing.py  # Lógica principal de processamento
│   ├── domain/
│   │   └── message_process.py    # Regras de negócio e transformação de mensagens
│   ├── helper/
│   │   └── logger/               # Configuração de logs
├── tests/
│   ├── application/
│   │   └── test_lambda_processing.py  # Testes para lambda_processing.py
│   ├── domain/
│   │   └── test_message_process.py    # Testes para message_process.py
│   └── test_app.py                    # Testes para o fluxo principal da aplicação
├── README.md                      # Documentação do projeto
├── requirements.txt               # Dependências do projeto
└── Environments                   # Configuração de variáveis de ambiente
```

---

## Destaque: Paralelismo com `asyncio`

O projeto utiliza o módulo `asyncio` para implementar **paralelismo assíncrono**, permitindo que múltiplas mensagens sejam processadas simultaneamente. Isso é alcançado através de:

- **Funções assíncronas (`async def`)**:
  - A função `process_messages` é projetada para processar mensagens de forma assíncrona, utilizando `await` para operações que podem ser suspensas, como envio de mensagens para o Kafka.

- **Execução em paralelo**:
  - Mensagens de diferentes partições são processadas simultaneamente, maximizando o uso de recursos e reduzindo o tempo de execução.

- **Benefícios**:
  - Melhor utilização de recursos computacionais.
  - Redução do tempo de processamento em cenários de alto volume de dados.
  - Escalabilidade para lidar com cargas maiores sem comprometer a performance.

Exemplo de paralelismo no código:

```python
async def process_messages(event, producer, topic_send, topic_send_fail, lambda_name):
    records = event.get("records", {})
    tasks = []

    for partition, messages in records.items():
        for message in messages:
            tasks.append(process_single_message(message, producer, topic_send, topic_send_fail, lambda_name))

    # Executa todas as tarefas de forma assíncrona
    await asyncio.gather(*tasks)
```

---

## Configuração

### Variáveis de Ambiente

Certifique-se de configurar as seguintes variáveis de ambiente para o funcionamento correto da Lambda:

| Variável            | Descrição                                                                 |
|---------------------|---------------------------------------------------------------------------|
| `LAMBDA_ENV`        | Define o ambiente de execução (ex.: `dev`, `prod`).                      |
| `MSK_SERVERS`       | Lista de servidores Kafka para conexão.                                  |
| `LAMBDA_NAME`       | Nome da Lambda para identificação nos logs e mensagens de erro.          |

### Exemplo de Configuração

```yaml
version: '1.0'

aws-account-henrique:
  master:
    lambda_name: lambda-python-stream
    lambda_env: aws-account-henrique
    msk_servers: parameter://aws-henrique/parameterstore/kafka_bootstrap_servers
```

---

## Dependências

As dependências do projeto estão listadas no arquivo `requirements.txt`. Para instalá-las, execute:

```bash
pip install -r requirements.txt
```

Principais bibliotecas utilizadas:
- `kafka-python`: Para integração com Kafka.
- `pytest`: Para execução de testes.
- `pytest-cov`: Para geração de relatórios de cobertura de código.
- `asyncio`: Para lidar com operações assíncronas.

---

## Testes

O projeto inclui testes unitários para garantir a qualidade do código. Para executar os testes, use:

```bash
pytest --cov=src --cov-report=term-missing
```

### Estrutura de Testes

- **`test_lambda_processing.py`**:
  - Testa o fluxo de processamento completo da Lambda.
  - Verifica a interação com o Kafka e o envio de mensagens.

- **`test_message_process.py`**:
  - Testa as regras de negócio e transformação de mensagens.

- **`test_app.py`**:
  - Testa o fluxo principal da aplicação.

---

## Logs

A Lambda utiliza um sistema de logs centralizado para monitoramento e depuração. Os logs incluem:
- Mensagens processadas com sucesso.
- Erros encontrados durante o processamento.
- Detalhes de mensagens enviadas para o tópico de falhas.

---

## Contribuição

Contribuições para melhorias no código ou documentação são bem-vindas. Siga estas etapas para contribuir:
1. Faça um fork do repositório.
2. Crie uma branch para sua feature ou correção: `git checkout -b minha-feature`.
3. Envie suas alterações: `git push origin minha-feature`.
4. Abra um Pull Request.

---

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

## Autor

Este projeto foi desenvolvido por **Henrique**. Para dúvidas ou sugestões, entre em contato pelo GitHub.

---

## Links Úteis

- [Documentação do Kafka](https://kafka.apache.org/documentation/)
- [Documentação do Python](https://docs.python.org/3/)
- [pytest](https://docs.pytest.org/)
