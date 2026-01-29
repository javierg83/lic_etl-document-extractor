import redis
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USERNAME", "default"),
    password=os.getenv("REDIS_PASSWORD"),
    db=int(os.getenv("REDIS_DB", "0")),
    decode_responses=True
)

queue_data = {
    "licitacion_id": 1, # Cambia esto por un ID que exista en tu DB si quieres probar la consulta
    "timestamp": datetime.now().isoformat()
}

print(f"Pushing to document_queue: {queue_data}")
r.lpush("document_queue", json.dumps(queue_data))
print("Done.")
