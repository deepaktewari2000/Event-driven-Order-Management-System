import json
import logging
from typing import Optional, Any
from aiokafka import AIOKafkaProducer
from app.core.config import settings
import asyncio

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        """Initialize and start the Kafka producer with retries."""
        retries = 5
        while retries > 0:
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                await self.producer.start()
                logger.info("Kafka producer started successfully")
                return
            except Exception as e:
                retries -= 1
                logger.warning(f"Failed to start Kafka producer (retries left: {retries}): {e}")
                if retries > 0:
                    await asyncio.sleep(5)
                else:
                    logger.error("Could not start Kafka producer after several attempts")
                    self.producer = None

    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")

    async def send_message(self, topic: str, message: Any):
        """
        Send a message to a Kafka topic.
        
        Args:
            topic: The topic to send to
            message: The message to send (must be serializable to JSON)
        """
        if not self.producer:
            logger.warning("Kafka producer not initialized, skipping message send")
            return

        try:
            await self.producer.send_and_wait(topic, message)
            logger.debug(f"Sent message to topic {topic}: {message}")
        except Exception as e:
            logger.error(f"Failed to send message to Kafka: {e}")

# Global instance
kafka_producer = KafkaProducer()
