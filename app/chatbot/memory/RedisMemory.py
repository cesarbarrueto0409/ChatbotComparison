import redis
import json
import os

"""Memory management using Redis for storing conversation history."""
class RedisMemory:
    def __init__(self):
        self.client = redis.Redis( # Initialize Redis client
            host=os.getenv("REDIS_HOST", "localhost"), # Get Redis host from environment (.env) variables or default to localhost
            port=int(os.getenv("REDIS_PORT", 6379)), # Get Redis port from environment variables or default to 6379
            decode_responses=True # Decode responses to strings
        )
        self.ttl = int(os.getenv("REDIS_TTL", 1800)) # Time-to-live for stored data in seconds (default 30 minutes)

    # Method to retrieve conversation history from Redis
    def get_history(self, session_id: str) -> list:
        data = self.client.get(session_id) # Get data from Redis using session_id as key
        return json.loads(data) if data else [] # If data exists, parse JSON and return as a python list, else return empty list

    # Method to save conversation history to Redis with time-to-live
    def save_history(self, session_id: str, history: list):
        self.client.setex(
            session_id,
            self.ttl, # Set expiration time for the key->session_id
            json.dumps(history) # Serialize history list to JSON string
        )

    # Method to clear conversation history from Redis
    def clear(self, session_id: str):
        self.client.delete(session_id)
