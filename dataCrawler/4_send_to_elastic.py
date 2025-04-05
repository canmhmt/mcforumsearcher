from utils.connectDB import create_elasticsearch_client, connect_kafka_consumer
from utils.kafkaTools import consume_kafka_data
from utils.elasticTools import get_index_name, send_to_elasticsearch 
import json
import warnings

warnings.filterwarnings('ignore')
consumer = connect_kafka_consumer()

def process_message(msg_value: str, es, base_index: str):
    try:
        data = json.loads(msg_value)
        index_name = get_index_name(base_index, data.get('timestamp'))
        send_to_elasticsearch(es, index_name, data)
        print(f"Data sended to Elasticsearch: {index_name}")
    except Exception as e:
        print(f"Err: {e}")

def create_elastic_process():
    consumer.subscribe(['parsed_final_topic'])
    while True:
        status, kafka_data = consume_kafka_data(consumer)
        base_index = "forum-object"
        es = create_elasticsearch_client()
        if status:
            process_message(kafka_data.value().decode('utf-8'), es, base_index)

if __name__ == '__main__':
    create_elastic_process()
