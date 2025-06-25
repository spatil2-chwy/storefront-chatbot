from typing import List
from sqlalchemy.orm import Session, joinedload
from src.models.user import User
from src.models.pet import PetProfile

class UserService:
    def get_users(self, db: Session) -> List[User]:
        return db.query(User).all()

    def get_user(self, db: Session, customer_key: int) -> User | None:
        return (
            db.query(User)
              .options(joinedload(User.pets))
              .filter(User.customer_key == customer_key)
              .one_or_none()
        )

    def create_user(self, db: Session, user_data: User) -> User:
        db.add(user_data)
        db.commit()
        db.refresh(user_data)
        return user_data

    def update_user(self, db: Session, customer_key: int, user_data: User) -> User | None:
        user = db.query(User).filter(User.customer_key == customer_key).one_or_none()
        if not user:
            return None
        for attr, value in vars(user_data).items():
            if attr.startswith('_') or attr == 'customer_key':
                continue
            setattr(user, attr, value)
        db.commit()
        db.refresh(user)
        return user

    def delete_user(self, db: Session, customer_key: int) -> bool:
        user = db.query(User).filter(User.customer_key == customer_key).one_or_none()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True

    def get_pets_by_user(self, db: Session, customer_key: int) -> List[PetProfile]:
        return (
            db.query(PetProfile)
              .filter(PetProfile.customer_id == customer_key)
              .all()
        )
