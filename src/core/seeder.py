#I added this in order to create default roles to use at the beginning

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.core.database import AsyncSessionLocal # Import the session factory
from src.models.user import Role

async def seed_initial_data():
    """Seeds the database with essential, non-user data (e.g., Roles)."""
    async with AsyncSessionLocal() as session:
        roles_to_seed = ["admin", "user"]
        
        for role_name in roles_to_seed:
            # Check if the role already exists
            stmt = select(Role).where(Role.name == role_name)
            existing_role = (await session.execute(stmt)).scalar_one_or_none()
            
            if not existing_role:
                # If it doesn't exist, create and add it
                new_role = Role(name=role_name, description=f"Standard {role_name} access.")
                session.add(new_role)
                print(f"➕ Added required role: {role_name}")

        try:
            # Commit all changes to the database
            await session.commit()
            print("✅ Initial data seeding complete.")
        except IntegrityError:
            # This handles cases where concurrent processes try to add the same role
            await session.rollback()
            print("⚠️ Initial data already exists (rollback performed).")
        except Exception as e:
            await session.rollback()
            print(f"❌ Error during seeding: {e}")