"""Pydantic request and response schemas."""

from datetime import datetime

from pydantic import model_validator
from sqlmodel import Field, SQLModel

from app.models import (
    DescriptionMode,
    MerchantStatus,
    MerchantUserRole,
    SurpriseBagStatus,
)


class MerchantCreate(SQLModel):
    name: str
    google_place_id: str
    address: str
    lat: float
    lng: float
    phone: str | None = None
    business_type: str


class MerchantOwnerCreate(SQLModel):
    name: str
    phone: str | None = None
    email: str | None = None
    password: str | None = None
    line_user_id: str | None = None

    @model_validator(mode="after")
    def validate_login_method(self) -> "MerchantOwnerCreate":
        has_email = bool(self.email)
        has_password = bool(self.password)
        has_line = bool(self.line_user_id)

        if has_email != has_password:
            raise ValueError("email and password must be provided together")

        if not has_line and not (has_email and has_password):
            raise ValueError("provide either line_user_id or email/password")

        return self


class MerchantRegisterRequest(SQLModel):
    merchant: MerchantCreate
    owner: MerchantOwnerCreate
    approval_code: str


class MerchantRead(SQLModel):
    id: str
    name: str
    google_place_id: str
    address: str
    lat: float
    lng: float
    phone: str | None = None
    business_type: str
    status: MerchantStatus


class MerchantUserRead(SQLModel):
    id: str
    merchant_id: str
    name: str
    phone: str | None = None
    email: str | None = None
    line_user_id: str | None = None
    role: MerchantUserRole


class MerchantRegisterResponse(SQLModel):
    merchant: MerchantRead
    owner: MerchantUserRead


#=======================登入 / login ==========================
class MerchantEmailLoginRequest(SQLModel):
    email: str
    password: str


class MerchantLineLoginRequest(SQLModel):
    line_user_id: str


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer" 

#======================= 建立福袋 ==========================
class SurpriseBagCreate(SQLModel):
    title: str
    category: str
    description: str | None = None
    description_mode: DescriptionMode = DescriptionMode.hidden
    price: float
    original_value: float | None = None
    quantity: int
    pickup_start_at: datetime | None = None
    pickup_end_at: datetime | None = None
    allergens: list[str] = Field(default_factory=list)
    dietary_flags: list[str] = Field(default_factory=list)
    storage_note: str | None = None

    @model_validator(mode="after")
    def validate_surprise_bag(self) -> "SurpriseBagCreate":
        if self.price <= 0:
            raise ValueError("price must be greater than 0")

        if self.original_value is not None and self.original_value < self.price:
            raise ValueError("original_value must be greater than or equal to price")

        if self.quantity <= 0:
            raise ValueError("quantity must be greater than 0")

        if (
            self.pickup_start_at
            and self.pickup_end_at
            and self.pickup_end_at <= self.pickup_start_at
        ):
            raise ValueError("pickup_end_at must be later than pickup_start_at")

        return self


class SurpriseBagRead(SQLModel):
    id: str
    merchant_id: str

    title: str
    category: str
    description: str | None = None
    description_mode: DescriptionMode

    price: float
    original_value: float | None = None

    quantity: int
    quantity_sold: int
    quantity_reserved: int

    pickup_start_at: datetime | None = None
    pickup_end_at: datetime | None = None

    status: SurpriseBagStatus

    allergens: list[str] = Field(default_factory=list)
    dietary_flags: list[str] = Field(default_factory=list)
    storage_note: str | None = None

    created_at: datetime
    updated_at: datetime


class PublicSurpriseBagRead(SQLModel):
    id: str
    merchant_id: str
    merchant_name: str

    title: str
    category: str
    description: str | None = None
    description_mode: DescriptionMode

    price: float
    original_value: float | None = None
    available_quantity: int

    pickup_start_at: datetime | None = None
    pickup_end_at: datetime | None = None

    allergens: list[str] = Field(default_factory=list)
    dietary_flags: list[str] = Field(default_factory=list)
