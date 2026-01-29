import redis
import os
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

try:
    print(f"Connecting to {os.getenv('REDIS_HOST')}...")
    ping = r.ping()
    print(f"Ping: {ping}")
    
    queue_len = r.llen("document_queue")
    print(f"Queue 'document_queue' length: {queue_len}")
    
    if queue_len > 0:
        messages = r.lrange("document_queue", 0, -1)
        print("Messages in queue:")
        for m in messages:
            print(f"  - {m}")
    else:
        print("Queue is empty.")
except Exception as e:
    print(f"Error: {e}")
