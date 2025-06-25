from typing import Dict, Optional
from datetime import datetime
from src.models.user import User, UserCreate

class UserService:
    def __init__(self):
        # keyed by customer_key
        self.users: Dict[int, User] = {}
        self._initialize_dummy_data()

    def _initialize_dummy_data(self):
        # Load a single sample user based on provided CSV
        csv_data = [
            {"customer_key": 24612503152,
             "customer_id": 72030138,
             "operating_revenue_trailing_365": 63742.65384,
             "customer_order_first_placed_dttm": "2019-09-17 00:00:00.000",
             "customer_address_zip": "64503-1542",
             "customer_address_city": "SAINT JOSEPH",
             "customer_address_state": "MO"},
        ]
        for rec in csv_data:
            # parse datetime string
            rec["customer_order_first_placed_dttm"] = datetime.strptime(
                rec["customer_order_first_placed_dttm"], "%Y-%m-%d %H:%M:%S.%f"
            )
            user = User(**rec)
            self.users[user.customer_key] = user

    async def get_user(self, customer_key: int) -> Optional[User]:
        return self.users.get(customer_key)

    async def create_user(self, user_data: UserCreate) -> User:
        user = User(**user_data.dict())
        self.users[user.customer_key] = user
        return user