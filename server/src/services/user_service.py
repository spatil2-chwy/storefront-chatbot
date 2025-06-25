from typing import Dict, Optional
from src.models.user import User, UserCreate

class UserService:
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.current_user_id = 1
        self._initialize_dummy_data()

    def _initialize_dummy_data(self):
        # dummy test user
        user_data = UserCreate(email="test@example.com", name="Test User")
        user_id = self.current_user_id
        self.current_user_id += 1
        user = User(id=user_id, email=user_data.email, name=user_data.name)
        self.users[user_id] = user

    async def get_user(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self.users.values() if u.email == email), None)

    async def create_user(self, user_data: UserCreate) -> User:
        user_id = self.current_user_id
        self.current_user_id += 1
        user = User(id=user_id, email=user_data.email, name=user_data.name)
        self.users[user_id] = user
        return user
