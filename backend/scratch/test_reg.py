import asyncio
from app.database.session import AsyncSessionLocal
from app.schemas.schemas import UserRegister
from app.services.auth_service import AuthService

async def main():
    async with AsyncSessionLocal() as db:
        s = AuthService(db)
        try:
            r = await s.register(UserRegister(
                full_name='Test User',
                email='test1234@example.com',
                password='Password@123',
                confirm_password='Password@123'
            ))
            print("SUCCESS:", r)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
