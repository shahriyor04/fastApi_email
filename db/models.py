from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    email : Mapped[str] = mapped_column(String(255))
    deta: Mapped[datetime] = mapped_column(DateTime(), default=datetime.today())


class Email(Base):
    __tablename__ = "emails"
    id : Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))


class Send_email(Base):
    __tablename__ = "send_email"
    id: Mapped[int] = mapped_column(primary_key=True)
    username : Mapped[str] = mapped_column(String(255))
    to_email : Mapped[str] = mapped_column(String(255))
    subject : Mapped[str] = mapped_column(String(255))
    body : Mapped[str] =   mapped_column(String(255))

class Send_emails(Base):
    __tablename__ = "send_emails"
    id: Mapped[int] = mapped_column(primary_key=True)
    username : Mapped[str] = mapped_column(String(255))
    emails : Mapped[str] = mapped_column(String(255))
    subject : Mapped[str] = mapped_column(String(255))
    body : Mapped[str] =   mapped_column(String(255))

