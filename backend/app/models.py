"""Database models.

Next step:
- Merchant
- MerchantUser
- SurpriseBag
- Reservation
"""

from enum import Enum
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON

class MerchantStatus(str, Enum):
    approved = "approved"
    suspended = "suspended"

class Merchant(SQLModel, table=True):
    __tablename__ = "merchants"

    id: str = Field(primary_key=True)
    name: str
    google_place_id: str = Field(index=True, unique=True)
    address: str
    lat: float
    lng: float
    phone: str | None = None
    business_type: str
    status: MerchantStatus = MerchantStatus.approved
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MerchantUserRole(str, Enum):
    owner = "owner"
    staff = "staff"

class MerchantUser(SQLModel, table=True):
    __tablename__ = "merchant_users"

    id : str = Field(primary_key=True)
    merchant_id: str = Field(foreign_key="merchants.id")
    name: str
    phone: str | None = None
    email: str | None = None
    # email: str | None = Field(default=None, index=True, unique=True) #改了也許比較好，在研究
    # line_user_id: str | None = Field(default=None, index=True, unique=True)
    password_hash: str | None = None
    line_user_id: str | None = None
    role: MerchantUserRole = MerchantUserRole.owner
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: datetime | None = None

class SurpriseBagStatus(str, Enum):
    draft = "draft"
    active = "active"
    sold_out = "sold_out"
    expired = "expired"
    hidden = "hidden"

class DescriptionMode(str, Enum):
    hidden = "hidden"
    partial = "partial"
    full = "full"

class SurpriseBag(SQLModel, table=True):
    __tablename__ = "surprise_bags"

    id: str = Field(primary_key=True)
    merchant_id: str = Field(foreign_key="merchants.id")
    title: str
    category: str
    description: str | None = None
    description_mode: DescriptionMode = DescriptionMode.hidden
    price: float
    original_value: float | None = None
    quantity: int
    quantity_sold: int = 0
    quantity_reserved: int = 0
    pickup_start_at: datetime | None = None
    pickup_end_at: datetime | None = None
    status: SurpriseBagStatus = SurpriseBagStatus.draft
    allergens: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    dietary_flags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    storage_note: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReservationStatus(str, Enum):
    reserved = "reserved"
    picked_up = "picked_up"
    cancelled = "cancelled"
    no_show = "no_show"

class Reservation(SQLModel, table=True):
    __tablename__ = "reservations"

    id: str = Field(primary_key=True)
    customer_id: str | None = None
    merchant_id: str = Field(foreign_key="merchants.id")
    surprise_bag_id: str = Field(foreign_key="surprise_bags.id")
    customer_name: str | None = None
    customer_phone: str | None = None
    line_user_id: str | None = None
    quantity: int
    pickup_code: str | None = None
    status: ReservationStatus = ReservationStatus.reserved
    reserved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    picked_up_at: datetime | None = None
    canceled: datetime | None = None
    customer_note: str | None = None
    merchant_note: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomerStatus(str, Enum):
    active = "active"
    blocked = "blocked"

class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    id: str = Field(primary_key=True)
    display_name: str | None = None
    phone: str | None = None
    email: str | None = None
    line_user_id: str | None = None
    status: CustomerStatus = CustomerStatus.active
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Role(str, Enum):
    admin = "admin"
    support = "support"
    sales = "sales"

class StaffStatus(str, Enum):
    active = "active"
    disabled = "disabled"

class StaffUser(SQLModel, table=True):
    __tablename__ = "staff_users"

    id: str = Field(primary_key=True)
    name: str
    email: str | None = None
    password_hash: str | None = None
    role: Role = Role.support
    status: StaffStatus = StaffStatus.active
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: datetime | None = None