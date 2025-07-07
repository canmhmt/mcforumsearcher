from utils.connectDB import connect_kafka_producer, connect_kafka_consumer
import time
import traceback
import json


async def produce_kafka_data(producer, topic_name, data):
    if data and not isinstance(data, list):
        try:
            await producer.send_and_wait(
                    topic_name,
                    json.dumps(data).encode("utf-8"))
        except:
            traceback.print_exc()
    elif data and isinstance(data, list):
        for obj in data:
            try:
                await producer.send_and_wait(
                        topic_name,
                        json.dumps(obj).encode("utf-8"))
            except:
                traceback.print_exc()
            print("Data sended to Kafka succesfully.")
    else:
        print("There is no data to send to Kafka.")

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

