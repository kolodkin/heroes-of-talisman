#!/usr/bin/env python3
"""
Script to create default users for development/testing.
Creates mark@test.com and adam@test.com with password 'test'.
If users already exist, their passwords will be reset.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)

# Import from server package
from server.database import SessionLocal, create_db_and_tables
from server.models import User
from server.auth import get_password_hash


async def create_or_update_user(session: AsyncSession, email: str, password: str) -> None:
    """Create a new user or update existing user's password."""

    # Check if user already exists
    result = await session.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    hashed_password = get_password_hash(password)

    if existing_user:
        # Update existing user's password
        existing_user.password = hashed_password
        print(f"✓ Updated password for existing user: {email}")
    else:
        # Create new user
        new_user = User(email=email, password=hashed_password, created_at=datetime.now(timezone.utc))
        session.add(new_user)
        print(f"✓ Created new user: {email}")

    await session.commit()


async def main():
    """Main function to create default users."""
    print("Creating default users...")

    try:
        # Ensure database tables exist
        await create_db_and_tables()

        # Create session
        async with SessionLocal() as session:
            # Create or update users
            await create_or_update_user(session, "mark@test.com", "test")
            await create_or_update_user(session, "adam@test.com", "test")

        print("\n✅ Default users created successfully!")
        print("Users created:")
        print("  - mark@test.com (password: test)")
        print("  - adam@test.com (password: test)")

    except Exception as e:
        print(f"\n❌ Error creating users: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
