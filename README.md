# Construção de um Pipeline de Dados em Tempo Real na AWS


# Tecnologias Utilizadas:

*   **Python:** Linguagem de programação para desenvolvimento da função Lambda e envio de mensagens.
*   **Amazon SNS:** Serviço de mensagens assíncrono para ingestão de dados.
*   **AWS Lambda:** Serviço de computação serverless para processamento de dados em tempo real.
*   **Amazon S3:** Serviço de armazenamento de objetos para data lake e backups.
*   **Amazon RDS:** Serviço de banco de dados relacional para data warehouse.
*   **MySQL:** Banco de dados utilizado no Amazon RDS, que será o Data Warehouse da tabela final.
*   **Draw.io:** Ferramenta para criação do diagrama de arquitetura.


# Arquitetura Detalhada:

A arquitetura do pipeline é composta pelos seguintes componentes:

1.  **Data Producer (On-Premise):**
    *   Responsável por gerar os dados de histórico de consumo no formato JSON.
    *   Simula o envio de dados em tempo real para o pipeline.
    *   Pode representar sistemas de gestão de fazendas, sensores ou outras fontes de dados.

2.  **Amazon SNS (Simple Notification Service):**
    *   Serviço de mensagens assíncrono que recebe os dados do Data Producer.
    *   Desacopla a fonte de dados do pipeline de processamento, garantindo a escalabilidade e a resiliência.
    *   Encaminha as mensagens para a função AWS Lambda.

3.  **AWS Lambda:**
    *   Serviço de computação serverless que executa a lógica de processamento dos dados.
    *   Realiza as seguintes tarefas:
        *   Enriquecimento dos dados: cálculo de `consumo_meta`, geração de `id_treated_data` e `row_ts`.
        *   Armazenamento dos dados no Amazon RDS (data warehouse).
        *   Armazenamento dos dados no Amazon S3 (data lake e backups).
        *   Implementação de idempotência para evitar duplicidade de dados.
    *   Escala automaticamente para lidar com a carga de trabalho, sem a necessidade de gerenciar servidores.

4.  **Amazon S3 (Simple Storage Service):**
    *   Serviço de armazenamento de objetos que armazena os dados processados em um data lake.
    *   Os dados são organizados em partições por fazenda e data, facilitando a consulta e a análise.
    *   Utilizado também para armazenar backups dos dados processados.

5.  **Amazon RDS (Relational Database Service):**
    *   Serviço de banco de dados relacional que armazena os dados processados em um data warehouse.
    *   Permite consultas e análises de dados em tempo real, utilizando a linguagem SQL.
    *   Garante a integridade e a consistência dos dados.

A seguinte imagem ilustra a arquitetura do pipeline:

![Arquitetura do Projeto](/Users/felipeabreu/Data-streaming-pipeline-AWS/Arquitetura do Projeto/arquietetura_projeto_aws.jpg)


# Fluxo de Dados:

1.  O Data Producer envia os dados de histórico de consumo no formato JSON para o tópico do Amazon SNS.
2.  O Amazon SNS recebe os dados e os envia para a função AWS Lambda.
3.  A função AWS Lambda processa os dados, realiza transformações e os armazena no Amazon RDS e no Amazon S3.
4.  Os dados armazenados no Amazon RDS podem ser consultados e analisados utilizando ferramentas de Business Intelligence (BI).
5.  Os dados armazenados no Amazon S3 podem ser utilizados para análises de Big Data e para backups de longo prazo.


# Padrões de Projeto:

*   **Filas de Mensagens (Amazon SNS):** Permitem o desacoplamento entre os componentes do pipeline, garantindo a escalabilidade e a resiliência.
*   **Computação Serverless (AWS Lambda):** Permite o processamento de dados em tempo real sem a necessidade de gerenciar servidores.
*   **Data Lake (Amazon S3):** Permite o armazenamento de grandes volumes de dados em diferentes formatos, facilitando a análise de Big Data.
*   **Data Warehouse (Amazon RDS):** Permite a análise de dados em tempo real utilizando a linguagem SQL.
*   **Idempotência:** Garante que as mensagens sejam processadas apenas uma vez, evitando a duplicidade de dados.



# Processo de desenvolvimento:

1. Envio de Mensagens (Data Producer):

Objetivo: Simular o envio de dados de histórico de consumo para o Amazon SNS.
Linguagem: Python.
Bibliotecas: boto3 (SDK da AWS para Python).
Código:: 01.publicar_msgs.py (Localizado dentro da pasta scripts)

Explicação:

O código utiliza a biblioteca boto3 para interagir com o Amazon SNS.
É criado um cliente SNS e configurado o ARN do tópico para onde as mensagens serão enviadas.
Os dados de exemplo são definidos em um dicionário Python e convertidos para JSON.
A função sns.publish() é utilizada para enviar a mensagem para o tópico SNS.


2. Função Lambda (Data Processing):

Objetivo: Processar as mensagens recebidas do Amazon SNS, enriquecer os dados e armazená-los no Amazon S3 e no Amazon RDS.
Linguagem: Python.
Bibliotecas: boto3, mysql.connector, uuid, datetime.
Script de Criação: : 02.processar_lambda.py (Localizado dentro da pasta scripts)

Explicação:

A função Lambda é acionada por mensagens do Amazon SNS (O SNS funciona como gatilho da função Lambda).
Para cada mensagem recebida, os seguintes passos são executados:
- Determinação da fazenda com base no campo cod_cliente.
- Enriquecimento dos dados (Regras de Negócio solicitados para o Entregavel): 
   * cálculo de consumo_meta
   * geração de id_treated_data (UUID)
   * row_ts (timestamp).
- Armazenamento dos dados no Amazon RDS:
   * Conexão com o banco de dados MySQL utilizando as variáveis de ambiente.
   * Execução da query INSERT para inserir os dados na tabela **historico_consumo**.
   * Implementação de idempotência: verificação de duplicatas pelo id_treated_data.
- Armazenamento dos dados no Amazon S3:
   * Criação do nome do arquivo JSON com timestamp e organização em subpastas por fazenda e data.
   * Upload do arquivo para o bucket S3.
- Tratamento de erros e logs para monitoramento.

OBSERVAÇÃO:

Para conectar a função AWS Lambda ao banco de dados RDS MySQL, foi necessário criar uma camada (Layer) contendo o conector MySQL para Python (mysql-connector-python). Isso se deve ao fato de que o ambiente de execução padrão do AWS Lambda não inclui essa biblioteca.

Passos utilizados para criar a camada:

Criar um pacote de implantação:

Em um ambiente Python local, instale a biblioteca mysql-connector-python em um diretório específico:

*  mkdir python
*  pip install mysql-connector-python -t ./python

Crie um arquivo zip contendo o diretório python:

*  zip -r mysql-connector-layer.zip python


Criar a camada no AWS Lambda:

No console do AWS Lambda, navegue até "Camadas" e clique em "Criar camada".
Forneça um nome para a camada (por exemplo, mysql-connector-layer).
Faça o upload do arquivo mysql-connector-layer.zip.
Selecione as arquiteturas compatíveis (x86_64 e/ou arm64).
Clique em "Criar".


Adicionar a camada à função Lambda:

No console do AWS Lambda, navegue até sua função.
Em "Camadas", clique em "Adicionar uma camada".
Selecione a camada mysql-connector-layer e a versão desejada.
Clique em "Adicionar".

Ao criar a camada com o conector MySQL, você permite que sua função Lambda se conecte e interaja com o banco de dados RDS MySQL, possibilitando a execução de queries SQL e o armazenamento dos dados processados.

O pacote de implantação com os arquivos da biblioteca **mysql-connector-python** estão no arquivo zip dentro da sub pasta mysql-connector-pyton.



3. Criação da Tabela no RDS (Data Warehouse):

Objetivo: Criar a tabela historico_consumo no banco de dados MySQL para armazenar os dados processados.
Linguagem: SQL.
Nome do Banco de Dados: fazendas
Script de Criação: tabela.sql (Localizado dentro da sub pasta "script_tabela_RDS-MySQL")

Explicação:
Os tipos de dados das colunas são definidos de acordo com os dados que serão armazenados.
A coluna id_treated_data é definida como chave primária para garantir a unicidade dos registros.
Estrutura da tabela **historico_consumo**


|    Nome do Campo   | Tipo de Dado |                          Descrição                          |
|:------------------:|:------------:|:-----------------------------------------------------------:|
| id_treated_data    | VARCHAR(255) | Identificador único do registro processado. Chave primária. |
| id_curral          | VARCHAR(255) | Identificador do curral.                                    |
| id_raca            | VARCHAR(255) | Identificador da raça do animal.                            |
| id_lote            | VARCHAR(255) | Identificador do lote de animais.                           |
| peso_entrada       | FLOAT        | Peso de entrada do lote.                                    |
| peso_medio         | FLOAT        | Peso médio dos animais no lote.                             |
| quantidade_animais | INT          | Quantidade de animais no lote.                              |
| dia_confinamento   | INT          | Dias de confinamento.                                       |
| consumo_real       | FLOAT        | Consumo real do lote.                                       |
| consumo_meta       | FLOAT        | Consumo meta calculado.                                     |
| data               | DATETIME     | Data do registro de consumo.                                |
| cod_cliente        | VARCHAR(255) | Código do cliente (fazenda).                                |
| row_ts             | DATETIME     | Timestamp de processamento do registro.                     |



4. Estruturação do Data Lake (Amazon S3):

Objetivo: Organizar os arquivos JSON no bucket S3 em uma estrutura hierárquica para facilitar a consulta e a análise dos dados.

Estrutura de Pastas do Data Lake:

historico-consumo-fazendas/
└── historico_diario/
    ├── fazenda_um/
    │   └── 2024/
    │       └── 03/
    │           └── 20/
    │               └── historico_consumo_2024-03-20 10:30:45.123.json
    └── fazenda_dois/
        └── 2024/
            └── 03/
                └── 20/
                    └── historico_consumo_2024-03-20 11:15:30.456.json

Explicação:

O bucket historico-consumo-fazendas armazena todos os dados de histórico de consumo.
A pasta historico_diario armazena os dados diários.
As subpastas fazenda_um e fazenda_dois representam as fazendas.
As subpastas 2024/03/20 representam o ano, mês e dia dos dados.
Os arquivos JSON são nomeados com o timestamp completo para garantir a unicidade.



