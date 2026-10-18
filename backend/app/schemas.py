from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict

Money = Decimal
class Register(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class Login(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)

class Profile(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    currency: Literal['INR', 'USD', 'EUR', 'GBP']

class ItemInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    quantity: Decimal = Field(gt=0, le=100000, decimal_places=3)
    unit: Literal['each', 'g', 'kg', 'ml', 'l'] = 'each'
    amount: Decimal = Field(ge=0, le=999999999, decimal_places=2)
    line_index: int | None = Field(default=None, ge=0)

class ReceiptEdit(BaseModel):
    merchant: str = Field(min_length=1, max_length=200)
    purchase_date: date
    category: Literal['Groceries', 'Dining', 'Transport', 'Shopping', 'Health', 'Utilities', 'Other']
    currency: Literal['INR', 'USD', 'EUR', 'GBP']
    subtotal: Decimal | None = Field(default=None, ge=0, le=999999999, decimal_places=2)
    tax: Decimal = Field(default=0, ge=0, le=999999999, decimal_places=2)
    discount: Decimal = Field(default=0, ge=0, le=999999999, decimal_places=2)
    fees: Decimal = Field(default=0, ge=0, le=999999999, decimal_places=2)
    rounding: Decimal = Field(default=0, ge=-10, le=10, decimal_places=2)
    total: Decimal = Field(ge=0, le=999999999, decimal_places=2)
    items: list[ItemInput] = Field(max_length=500)

class AlertAction(BaseModel):
    action: Literal['expected', 'dismissed', 'open']

class MatchInput(BaseModel):
    item_id: int
    historical_item_id: int
