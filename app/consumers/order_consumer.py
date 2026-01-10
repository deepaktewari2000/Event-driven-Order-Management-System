import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from app.core.config import settings
from app.services.email_service import send_order_confirmation

logger = logging.getLogger(__name__)

async def consume_order_events():
    """
    Kafka consumer background task that listens for order events with retries.
    """
    retries = 5
    while retries > 0:
        consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC_ORDER_EVENTS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="order-service-group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest'
        )
        
        try:
            await consumer.start()
            logger.info(f"Started consuming events from topic: {settings.KAFKA_TOPIC_ORDER_EVENTS}")
            
            async for msg in consumer:
                event_data = msg.value
                logger.info(f"Received order event: {event_data}")
                
                # Send email confirmation
                if event_data.get("event") == "ORDER_CREATED":
                    customer_email = event_data.get("customer_email")
                    if customer_email:
                        await send_order_confirmation(customer_email, event_data)
                    else:
                        logger.warning(f"No customer email found in event for order {event_data.get('order_id')}")
            
            break # Exit retry loop if processing ends normally
                
        except Exception as e:
            retries -= 1
            logger.warning(f"Error in Kafka consumer (retries left: {retries}): {e}")
            if "UnknownTopicOrPartitionError" in str(e) or "[Error 3]" in str(e):
                logger.info("Topic might not be created yet, waiting...")
            if retries > 0:
                await asyncio.sleep(10) # Wait longer for topic creation
            else:
                logger.error("Kafka consumer failed after multiple attempts")
        finally:
            await consumer.stop()
            
    logger.info("Kafka consumer background task ended")
