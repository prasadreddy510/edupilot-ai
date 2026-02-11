"""
Redis caching service for AI responses
"""

import redis
import json
import hashlib
from typing import Optional, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis caching service"""

    def __init__(self):
        """Initialize Redis connection"""
        try:
            # Parse Redis URL
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
            self.enabled = True
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}. Caching disabled.")
            self.redis_client = None
            self.enabled = False

        # Default TTL (time to live) in seconds
        self.default_ttl = 3600  # 1 hour

    def _generate_key(self, prefix: str, data: dict) -> str:
        """
        Generate cache key from data

        Args:
            prefix: Key prefix (e.g., "explanation", "questions")
            data: Dictionary of data to hash

        Returns:
            Cache key string
        """
        # Sort dict keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        hash_value = hashlib.md5(sorted_data.encode()).hexdigest()
        return f"edupilot:{prefix}:{hash_value}"

    def get(self, prefix: str, data: dict) -> Optional[Any]:
        """
        Get value from cache

        Args:
            prefix: Cache key prefix
            data: Data to generate key from

        Returns:
            Cached value or None
        """
        if not self.enabled:
            return None

        try:
            key = self._generate_key(prefix, data)
            value = self.redis_client.get(key)

            if value:
                logger.debug(f"Cache hit for key: {key}")
                return json.loads(value)

            logger.debug(f"Cache miss for key: {key}")
            return None

        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None

    def set(
        self,
        prefix: str,
        data: dict,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache

        Args:
            prefix: Cache key prefix
            data: Data to generate key from
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            key = self._generate_key(prefix, data)
            ttl = ttl or self.default_ttl

            serialized_value = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized_value)

            logger.debug(f"Cached value for key: {key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False

    def delete(self, prefix: str, data: dict) -> bool:
        """
        Delete value from cache

        Args:
            prefix: Cache key prefix
            data: Data to generate key from

        Returns:
            True if deleted, False otherwise
        """
        if not self.enabled:
            return False

        try:
            key = self._generate_key(prefix, data)
            result = self.redis_client.delete(key)
            logger.debug(f"Deleted cache key: {key}")
            return bool(result)

        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern

        Args:
            pattern: Redis key pattern (e.g., "edupilot:explanation:*")

        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                count = self.redis_client.delete(*keys)
                logger.info(f"Cleared {count} keys matching pattern: {pattern}")
                return count
            return 0

        except Exception as e:
            logger.error(f"Error clearing pattern: {str(e)}")
            return 0

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        if not self.enabled:
            return {"enabled": False, "error": "Redis not connected"}

        try:
            info = self.redis_client.info("stats")
            return {
                "enabled": True,
                "total_connections": info.get("total_connections_received", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }

        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"enabled": False, "error": str(e)}

    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)


# Global instance
cache_service = CacheService()
