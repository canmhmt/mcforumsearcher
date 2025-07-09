import os
import redis.asyncio as redis
import psycopg2
from psycopg2 import OperationalError
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from confluent_kafka import Producer, Consumer, KafkaException
from aiokafka import AIOKafkaProducer
from dotenv import load_dotenv

load_dotenv()

def create_elasticsearch_client():
    try:
        es = Elasticsearch(
            os.getenv("ELASTICSEARCH_HOST"),
            basic_auth=(
                os.getenv("ELASTICSEARCH_USERNAME"),
                os.getenv("ELASTICSEARCH_PASSWORD")
            ),
            verify_certs=False,
            request_timeout=10
        )
        if es.ping():
            return es
        else:
            print("Elasticsearch ping failed")
            return None
    except es_exceptions.ConnectionError as e:
        print("Elasticsearch connection error:", e)
        return None

async def connect_kafka_producer():
    try:
        producer = AIOKafkaProducer(bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
        return producer
    except Exception as e:
        print("Kafka Producer connection failed:", e)
        return None

def connect_kafka_consumer():
    try:
        consumer = Consumer({
            'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            'group.id': os.getenv("KAFKA_CONSUMER_GROUP", "forum_kafka_consumer"),
            'auto.offset.reset': 'earliest'
        })
        return consumer
    except KafkaException as e:
        print("Kafka Consumer connection failed:", e)
        return None

async def connect_redis(host='localhost', port=6379, db=0):
    try:
        r = redis.Redis(host=host, port=port, db=db, socket_timeout=5)
        await r.ping()
        return r
    except redis.RedisError as e:
        print("Redis connection failed:", e)
        return None

def connect_psql(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", 5432)
):
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            connect_timeout=5
        )
        return conn
    except OperationalError as e:
        print("PostgreSQL connection failed:", e)
        return None
