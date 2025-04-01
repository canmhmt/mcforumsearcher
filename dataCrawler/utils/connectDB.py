from elasticsearch import Elasticsearch
from confluent_kafka import Producer, Consumer
import redis
import psycopg2

def connect_elasticsearch():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if es.ping():
        print("Connected to Elasticsearch")
    else:
        print("Could not connect to Elasticsearch")
    return es

def connect_kafka_producer():
    producer = Producer({'bootstrap.servers': "localhost:9092"})
    print("Connected to Confluent Kafka Producer")
    return producer

def connect_kafka_consumer():
    consumer = Consumer({
        'bootstrap.servers': "localhost:9092",
        'group.id': "forum_kafka_consumer",
        'auto.offset.reset': 'earliest'
    })
    print(f"Connected to Confluent Kafka Consumer")
    return consumer

def connect_redis(host='localhost', port=6379, db=0):
    r = redis.Redis(host=host, port=port, db=db)
    return r

def connect_postgres(dbname, user, password, host='localhost', port=5432):
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    print("Connected to PostgreSQL")
    return conn
