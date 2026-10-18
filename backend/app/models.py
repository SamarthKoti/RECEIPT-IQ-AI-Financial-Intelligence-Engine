from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, ForeignKey, Numeric, JSON, DateTime, Date, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

def now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    currency: Mapped[str] = mapped_column(String(3), default='INR')

class Session(Base):
    __tablename__ = 'sessions'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    expires: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Receipt(Base):
    __tablename__ = 'receipts'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    merchant: Mapped[str] = mapped_column(String(200), default='Unknown merchant')
    purchase_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default='Other')
    currency: Mapped[str] = mapped_column(String(3), default='INR')
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    tax: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    discount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    fees: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    rounding: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    total: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='review')
    file_hash: Mapped[str] = mapped_column(String(64), index=True)
    file_name: Mapped[str] = mapped_column(String(100))
    original_name: Mapped[str] = mapped_column(String(255))
    raw_text: Mapped[str] = mapped_column(Text, default='')
    ocr_lines: Mapped[list] = mapped_column(JSON, default=list)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    items: Mapped[list['Item']] = relationship(cascade='all, delete-orphan', lazy='selectin')
    decisions: Mapped[list['Decision']] = relationship(cascade='all, delete-orphan', lazy='selectin')

class Item(Base):
    __tablename__ = 'items'
    id: Mapped[int] = mapped_column(primary_key=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey('receipts.id'), index=True)
    name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=1)
    unit: Mapped[str] = mapped_column(String(10), default='each')
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    line_index: Mapped[int | None] = mapped_column(nullable=True)
    product_key: Mapped[str | None] = mapped_column(String(200), nullable=True)

class Decision(Base):
    __tablename__ = 'decisions'
    __table_args__ = (UniqueConstraint('receipt_id', 'alert_key'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey('receipts.id'))
    alert_key: Mapped[str] = mapped_column(String(200))
    action: Mapped[str] = mapped_column(String(20))
