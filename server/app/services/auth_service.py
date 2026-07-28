from sqlalchemy.orm import Session

from app.database.models.user import User
from app.schemas.auth_schema import RegisterRequest
from app.utils.password import hash_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def register(self, request: RegisterRequest) -> User:
        existing_user = self.get_user_by_email(request.email)

        if existing_user:
            raise ValueError("Email already registered")

        user = User(
            name=request.name,
            email=request.email,
            password_hash=hash_password(request.password),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user
