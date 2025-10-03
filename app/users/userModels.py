from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from core.database import Base


class Group(Base):
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    # Зв’язок з користувачами
    users = relationship("User", back_populates="group")
    # Зв’язок з адміністраторами
    admins = relationship("Admin", back_populates="group")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    password = Column(String)
    telegram_id = Column(String, nullable=True)

    # ForeignKey на групу
    group_id = Column(Integer, ForeignKey("user_groups.id", ondelete="SET NULL"), nullable=True)

    # зв’язки
    group = relationship("Group", back_populates="users")
    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class UserSession(Base):
    """Таблиця для зберігання активних JWT токенів користувачів"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)  # True = активний, False = неактивний

    user = relationship("User", back_populates="sessions", passive_deletes=False)
