import asyncio
import sys
import os

# Add the current directory to sys.path so we can import 'app'
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_admin(email, password, full_name):
    async with SessionLocal() as db:
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"User {email} already exists. Promoting to admin...")
            existing_user.role = UserRole.ADMIN
            await db.commit()
            print(f"User {email} promoted to ADMIN successfully!")
            return

        # Create new admin
        admin = User(
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        await db.commit()
        print(f"Admin user {email} created successfully!")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_admin.py <email> <password> <full_name>")
    else:
        email = sys.argv[1]
        password = sys.argv[2]
        full_name = sys.argv[3]
        asyncio.run(create_admin(email, password, full_name))
