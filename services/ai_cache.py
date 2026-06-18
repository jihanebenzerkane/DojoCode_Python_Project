import hashlib
import json
import time
from functools import lru_cache

class AICache:
    """
    Cache LRU pour les réponses IA fréquentes.
    Clé: hash du (prompt + code_context)
    """
    
    def __init__(self, maxsize: int = 100, ttl: int = 3600):
        self.cache = {}
        self.maxsize = maxsize
        self.ttl = ttl  # Time to live en secondes
    
    def _make_key(self, system_prompt: str, user_message: str, code: str) -> str:
        content = f"{system_prompt}:{user_message}:{code}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, system_prompt: str, user_message: str, code: str) -> str | None:
        key = self._make_key(system_prompt, user_message, code)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['response']
            else:
                del self.cache[key]
        return None
    
    def set(self, system_prompt: str, user_message: str, code: str, response: str):
        key = self._make_key(system_prompt, user_message, code)
        if len(self.cache) >= self.maxsize:
            # Eviction LRU
            oldest = min(self.cache, key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest]
        
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }