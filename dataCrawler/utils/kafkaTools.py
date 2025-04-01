from utils.connectDB import connect_kafka_producer, connect_kafka_consumer
import time
import traceback

def produce_kafka_data(producer, topic_name, data):
    try:
        producer.produce(
                topic_name,
                value = data)
    except:
        traceback.print_exc()

def consume_kafka_data(consumer):
    try:
        while True:
            data = consumer.poll(3)
            if data: 
                return True, data
            else:
                print('From Kafka -- No Data -- Retrying in few seconds.')
                time.sleep(3)
                continue
    except:
        traceback.print_exc()
        return False, None

