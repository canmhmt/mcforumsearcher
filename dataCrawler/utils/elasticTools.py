from datetime import datetime

def send_to_elasticsearch(es, index_name: str, document: dict):
    es.index(index=index_name, document=document)

def get_index_name(base_name: str, timestamp: str = None) -> str:
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp)
        except ValueError:
            dt = datetime.utcnow()
    else:
        dt = datetime.utcnow()
    return f"{base_name}-{dt.year}-{dt.month:02d}"
