import os
import json
import yaml
import boto3

def load_config():
    """
    Função load_config: Carrega o arquivo settings.yaml, que contém o ARN do SNS. Se o ARN não estiver configurado, 
    ela lança uma exceção.
    """
    # Caminho do arquivo de configuração (atualizado para o novo caminho)
    config_file_path = '/Users/felipeabreu/Data-streaming-pipeline-AWS/config/settings.yaml'
    
    # Carrega o arquivo YAML
    with open(config_file_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Recupera o ARN do SNS
    topic_arn = config.get('sns_topic_arn')
    if not topic_arn:
        raise ValueError("O ARN do SNS não está configurado no arquivo settings.yaml")
    
    return topic_arn

def publish_to_sns(data, topic_arn):
    """
    Função publish_to_sns: Envia uma mensagem para o SNS com os dados convertidos em JSON.
    """
    # Inicializa o cliente SNS
    sns_client = boto3.client('sns', region_name='us-east-1')
    
    # Publica a mensagem no SNS
    sns_client.publish(
        TopicArn=topic_arn,
        Message=json.dumps(data)
    )
    print(f"Mensagem publicada no SNS: {json.dumps(data)}")

def process_and_publish_data(raw_data_path):
    """
    Função process_and_publish_data: Faz a leitura dos arquivos JSON no diretório raw_data e publica os dados no SNS.
    """
    # Carrega a configuração e o ARN do SNS
    topic_arn = load_config()
    
    print(f"Iniciando o processamento de dados no caminho: {raw_data_path}")
    
    # Processa os arquivos JSON e publica os dados no SNS
    for filename in os.listdir(raw_data_path):
        if filename.endswith('.json'):
            filepath = os.path.join(raw_data_path, filename)
            print(f"Processando arquivo: {filename}")
            try:
                with open(filepath, 'r') as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            publish_to_sns(data, topic_arn)
                            print(f'Mensagem publicada: {json.dumps(data)}')
                        except json.JSONDecodeError as e:
                            print(f"Erro ao decodificar JSON no arquivo {filename}: {e}")
            except Exception as e:
                print(f"Erro ao processar o arquivo {filename}: {e}")
    print('Todas as mensagens foram publicadas com sucesso.')

# Caminho do diretório raw_data
raw_data_path = '/Users/felipeabreu/Data-streaming-pipeline-AWS/dados/raw_data'

# Executa o processamento e a publicação
process_and_publish_data(raw_data_path)



