import logging
import aiosmtplib
from email.message import EmailMessage
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

async def send_order_confirmation(customer_email: str, order_details: Dict[str, Any]):
    """
    Send an asynchronous order confirmation email using SMTP.
    """
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = customer_email
    message["Subject"] = f"Order Confirmation - #{order_details.get('order_id')}"

    # Simple text content
    content = f"""
    Hello,
    
    Thank you for your order!
    
    Order Details:
    --------------
    Order ID: {order_details.get('order_id')}
    Product: {order_details.get('product_id')}
    Quantity: {order_details.get('quantity')}
    Total Price: ${order_details.get('total_price')}
    Status: {order_details.get('status')}
    
    We will notify you once your order is shipped.
    
    Best regards,
    The Order Management Team
    """
    message.set_content(content)

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=False, # MailHog doesn't use TLS by default
        )
        logger.info(f"Order confirmation email sent to {customer_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {customer_email}: {e}")
