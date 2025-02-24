import sys
sys.path.append('/opt')

import json
import boto3
import mysql.connector
import os
import uuid
from datetime import datetime

# Configurar acesso ao S3
s3_client = boto3.client('s3')

# Configurar acesso ao RDS MySQL usando variáveis de ambiente
RDS_HOST = os.environ['RDS_HOST']
RDS_PORT = os.environ['RDS_PORT']
RDS_USER = os.environ['RDS_USER']
RDS_PASSWORD = os.environ['RDS_PASSWORD']
RDS_DATABASE = os.environ['RDS_DATABASE']

# Configurar o nome do bucket S3
BUCKET_NAME = "historico-consumo-fazendas"

def lambda_handler(event, context):
    for record in event['Records']:
        mensagem = json.loads(record['Sns']['Message'])

        # Determinar a fazenda
        fazenda = "fazenda_um" if mensagem.get("cod_cliente") == "FazendaUm" else "fazenda_dois"

        # Apicação das regras de negócios conforme a solicitação
        ## Criação do campo consumo_meta
        mensagem['consumo_meta'] = mensagem['peso_medio'] * 0.0176
        ## Criação do campo id_treated_data
        mensagem['id_treated_data'] = str(uuid.uuid4())
        ## Criação do campo row_ts
        mensagem['row_ts'] = datetime.utcnow().isoformat()

         # Inserir os dados na tbela final 'historico_consumo' no banco RDS MySQL
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(
                host=RDS_HOST,
                port=RDS_PORT,
                user=RDS_USER,
                password=RDS_PASSWORD,
                database=RDS_DATABASE
            )
            cursor = conn.cursor()

            # Verificar duplicatas no RDS MySQL
            check_query = "SELECT id_treated_data FROM historico_consumo WHERE id_treated_data = %s"
            cursor.execute(check_query, (mensagem['id_treated_data'],))
            result = cursor.fetchone()

            if result:
                print(f"Registro duplicado encontrado: {mensagem['id_treated_data']}")
                continue  # Ignora a inserção se o registro já existe

            insert_query = """
                INSERT INTO historico_consumo (
                    id_treated_data, id_curral, id_raca, id_lote, 
                    peso_entrada, peso_medio, quantidade_animais, 
                    dia_confinamento, consumo_real, consumo_meta, 
                    data, cod_cliente, row_ts
                ) VALUES (
                    %(id_treated_data)s, %(id_curral)s, %(id_raca)s, %(id_lote)s, 
                    %(peso_entrada)s, %(peso_medio)s, %(quantidade_animais)s, 
                    %(dia_confinamento)s, %(consumo_real)s, %(consumo_meta)s, 
                    %(data)s, %(cod_cliente)s, %(row_ts)s
                )
            """
            cursor.execute(insert_query, mensagem)
            conn.commit()
            print(f"Dados inseridos no RDS MySQL: {mensagem}")

        except mysql.connector.Error as e:
            print(f"Erro ao inserir no RDS MySQL: {e}")
            if conn:
                conn.rollback()
            return {'statusCode': 500, 'body': 'Erro ao inserir no RDS MySQL'}
        except Exception as e:
            print(f"Erro inesperado: {e}")
            if conn:
                conn.rollback()
            return {'statusCode': 500, 'body': 'Erro inesperado'}

        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

        # Salvar no S3 com subpastas por fazenda e data
        data = datetime.utcnow().strftime("%Y/%m/%d")  # Obtém a data no formato YYYY/MM/DD
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")  # Obtém o timestamp completo
        timestamp = timestamp[:-3] # Remover os últimos 3 dígitos dos microssegundos (deixa milissegundos)

        s3_path = f"historico_diario/{fazenda}/{data}/historico_consumo_{timestamp}.json"
        try:
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=s3_path,
                Body=json.dumps(mensagem)
            )
            print(f"Backup salvo no S3: {s3_path}")
        except boto3.exceptions.S3UploadFailedError as e:
            print(f"Erro ao salvar no S3: {e}")
            return {'statusCode': 500, 'body': 'Erro ao salvar no S3'}

    return {'statusCode': 200, 'body': 'Mensagens processadas com sucesso'}