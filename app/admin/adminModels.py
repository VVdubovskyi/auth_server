from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class Admin(Base):
    """Адміністратори системи"""
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    password = Column(String)
    telegram_id = Column(String, nullable=True)
    is_superadmin = Column(Boolean, default=False)  # False = звичайний адмін, True = головний адмін

    group_id = Column(Integer, ForeignKey("user_groups.id", ondelete="SET NULL"), nullable=True)
    group = relationship("Group", back_populates="admins")
    # сесії адміна
    sessions = relationship(
        "AdminSession",
        back_populates="admin",
        cascade="all, delete-orphan"
    )



class AdminSession(Base):
    """Таблиця для зберігання активних JWT токенів адміністраторів"""
    __tablename__ = "admin_sessions"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey('admin.id', ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)  # True = активний, False = неактивний

    # зв’язок з адміністратором
    admin = relationship("Admin", back_populates="sessions")
