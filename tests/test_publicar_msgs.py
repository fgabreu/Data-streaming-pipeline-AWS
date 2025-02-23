import unittest
from unittest.mock import patch, MagicMock
import json
import yaml

from publicar_msgs import publish_to_sns, load_config

class TestSNSPublish(unittest.TestCase):

    @patch('boto3.client')
    def test_publish_message(self, mock_boto_client):
        # Configura o mock do SNS
        mock_sns = MagicMock()
        mock_boto_client.return_value = mock_sns

        # Simula o conteúdo do arquivo JSON
        test_data = {"key": "value"}

        # Carrega o ARN do arquivo de configuração
        with open('config/settings.yaml', 'r') as config_file:
            config = yaml.safe_load(config_file)
        topic_arn = config['sns_topic_arn']

        # Chama a função de publicação
        publish_to_sns(test_data, topic_arn)

        # Verifica se o método publish foi chamado corretamente
        mock_sns.publish.assert_called_once_with(
            TopicArn=topic_arn,
            Message=json.dumps(test_data)
        )

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"key": "value"}')
    @patch('boto3.client')
    def test_read_and_publish_file(self, mock_boto_client, mock_open):
        # Configura o mock do SNS
        mock_sns = MagicMock()
        mock_boto_client.return_value = mock_sns

        # Caminho do arquivo (não importa neste teste, pois o open está mockado)
        test_file_path = 'dados/raw_data/test_file.json'

        # Carrega o ARN do arquivo de configuração
        with open('config/settings.yaml', 'r') as config_file:
            config = yaml.safe_load(config_file)
        topic_arn = config['sns_topic_arn']
        
        # Chama a função de publicação
        publish_to_sns(test_file_path, topic_arn)

        # Verifica se o arquivo foi aberto corretamente
        mock_open.assert_called_once_with(test_file_path, 'r')

        # Verifica se o método publish foi chamado corretamente
        mock_sns.publish.assert_called_once_with(
            TopicArn=topic_arn,
            Message='{"key": "value"}'
        )


if __name__ == '__main__':
    unittest.main()
