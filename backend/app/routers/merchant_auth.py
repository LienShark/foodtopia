from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session , select
from uuid import uuid4

from app.db import get_session
from app.models import Merchant, MerchantUser, MerchantStatus, MerchantUserRole
from app.schemas import (
    MerchantRegisterRequest, 
    MerchantRegisterResponse, 
    MerchantEmailLoginRequest, 
    TokenResponse, 
    MerchantLineLoginRequest,
)
from app.auth import hash_password
from app.auth import verify_password, create_access_token, get_current_merchant_user


router = APIRouter(prefix="/merchant-auth", tags=["merchant auth"])


@router.post("/register", response_model=MerchantRegisterResponse)
def register_merchant(
    payload: MerchantRegisterRequest,
    session: Session = Depends(get_session), ):
    if payload.approval_code != "FOODTOPIA2026":
        raise HTTPException(status_code=400, detail="invalid approval code")
    
    existing_merchant = session.exec(
        select(Merchant).where(
            Merchant.google_place_id == payload.merchant.google_place_id
        )
    ).first()
    if existing_merchant:
        raise HTTPException(status_code=409, detail="merchant already registered")
    
    if payload.owner.email:
        existing_email_user = session.exec(
            select(MerchantUser).where(
                MerchantUser.email == payload.owner.email
            )
        ).first()
        if existing_email_user:
            raise HTTPException(status_code=409, detail="email already registered")
        
    if payload.owner.line_user_id:
        existing_line_user = session.exec(
            select(MerchantUser).where(
                MerchantUser.line_user_id == payload.owner.line_user_id
            )
        ).first()
        if existing_line_user:
            raise HTTPException(status_code=409, detail="LINE account already registered")
    
    password_hash = None
    if payload.owner.password:
        password_hash = hash_password(payload.owner.password)

    merchant = Merchant(
        id=f"merchant_{uuid4().hex}",
        name=payload.merchant.name,
        google_place_id=payload.merchant.google_place_id,
        address=payload.merchant.address,
        lat=payload.merchant.lat,
        lng=payload.merchant.lng,
        phone=payload.merchant.phone,
        business_type=payload.merchant.business_type,
        status=MerchantStatus.approved,
    )

    owner = MerchantUser(
        id=f"merchant_user_{uuid4().hex}",
        merchant_id=merchant.id,
        name=payload.owner.name,
        phone=payload.owner.phone,
        email=payload.owner.email,
        password_hash=password_hash,
        line_user_id=payload.owner.line_user_id,
        role=MerchantUserRole.owner,
    )

    session.add(merchant)
    session.add(owner)
    session.commit()
    session.refresh(merchant)
    session.refresh(owner)

    return {
        "merchant": merchant,
        "owner": owner,
    }


@router.post("/login/email", response_model=TokenResponse)
def login_merchant_email(
    payload: MerchantEmailLoginRequest,
    session: Session = Depends(get_session),
):
    merchant_user = session.exec(
        select(MerchantUser).where(MerchantUser.email == payload.email)
    ).first()

    if not merchant_user:
        raise HTTPException(status_code=401, detail="請確認您的email或密碼是否正確")

    if not merchant_user.password_hash:
        raise HTTPException(status_code=401, detail="請使用line 登入綁定密碼後再使用email登入")

    if not verify_password(payload.password, merchant_user.password_hash):
        raise HTTPException(status_code=401, detail="請確認您的email或密碼是否正確")

    access_token = create_access_token(
        {
            "sub": merchant_user.id,
            "merchant_id": merchant_user.merchant_id,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/login/line", response_model=TokenResponse)
def login_merchant_line(
    payload: MerchantLineLoginRequest,
    session: Session = Depends(get_session),
):
    merchant_user = session.exec(
        select(MerchantUser).where(MerchantUser.line_user_id == payload.line_user_id)
    ).first()

    if not merchant_user:
        raise HTTPException(status_code=401, detail="請先完成綁定程序再登入")
    
    access_token = create_access_token(
        {
            "sub": merchant_user.id,
            "merchant_id": merchant_user.merchant_id,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me")
def read_current_merchant_user(
    current_user: MerchantUser = Depends(get_current_merchant_user),
) -> MerchantUser:
    return current_user
