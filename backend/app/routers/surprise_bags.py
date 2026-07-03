from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.auth import get_current_merchant_user
from app.db import get_session
from app.models import (
    DescriptionMode,
    Merchant,
    MerchantUser,
    SurpriseBag,
    SurpriseBagStatus,
)
from app.schemas import (
    PublicSurpriseBagRead,
    SurpriseBagCreate,
    SurpriseBagRead,
)

router = APIRouter(tags=["surprise bags"])

# NOTE: 這段福袋 API 除了新增福袋是我自己寫的外 都是 vibe coding 草稿，尚未做完整測試與邊界條件檢查。


def _available_quantity(surprise_bag: SurpriseBag) -> int:
    return max(
        surprise_bag.quantity
        - surprise_bag.quantity_sold
        - surprise_bag.quantity_reserved,
        0,
    )


def _public_description(surprise_bag: SurpriseBag) -> str | None:
    if surprise_bag.description_mode == DescriptionMode.hidden:
        return None
    return surprise_bag.description


def _to_public_surprise_bag(
    surprise_bag: SurpriseBag,
    merchant: Merchant,
) -> PublicSurpriseBagRead:
    return PublicSurpriseBagRead(
        id=surprise_bag.id,
        merchant_id=surprise_bag.merchant_id,
        merchant_name=merchant.name,
        title=surprise_bag.title,
        category=surprise_bag.category,
        description=_public_description(surprise_bag),
        description_mode=surprise_bag.description_mode,
        price=surprise_bag.price,
        original_value=surprise_bag.original_value,
        available_quantity=_available_quantity(surprise_bag),
        pickup_start_at=surprise_bag.pickup_start_at,
        pickup_end_at=surprise_bag.pickup_end_at,
        allergens=surprise_bag.allergens,
        dietary_flags=surprise_bag.dietary_flags,
    )


@router.post("/merchant/surprise-bags", response_model=SurpriseBagRead)
def create_surprise_bag(
    payload: SurpriseBagCreate,
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: Session = Depends(get_session),
) -> SurpriseBag:
    surprise_bag = SurpriseBag(
        id=f"surprise_bag_{uuid4().hex}",
        merchant_id=current_user.merchant_id,
        title=payload.title,
        category=payload.category,
        description=payload.description,
        description_mode=payload.description_mode,
        price=payload.price,
        original_value=payload.original_value,
        quantity=payload.quantity,
        quantity_sold=0,
        quantity_reserved=0,
        pickup_start_at=payload.pickup_start_at,
        pickup_end_at=payload.pickup_end_at,
        status=SurpriseBagStatus.active,
        allergens=payload.allergens,
        dietary_flags=payload.dietary_flags,
        storage_note=payload.storage_note,
    )

    session.add(surprise_bag)
    session.commit()
    session.refresh(surprise_bag)

    return surprise_bag


@router.get("/merchant/surprise-bags", response_model=list[SurpriseBagRead])
def list_merchant_surprise_bags(
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: Session = Depends(get_session),
) -> list[SurpriseBag]:
    return session.exec(
        select(SurpriseBag).where(
            SurpriseBag.merchant_id == current_user.merchant_id
        )
    ).all()


@router.get("/surprise-bags", response_model=list[PublicSurpriseBagRead])
def list_public_surprise_bags(
    sort: str = Query(default="new", pattern="^(new|popular)$"),
    category: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> list[PublicSurpriseBagRead]:
    statement = select(SurpriseBag).where(
        SurpriseBag.status == SurpriseBagStatus.active
    )

    if category:
        statement = statement.where(SurpriseBag.category == category)

    surprise_bags = session.exec(statement).all()

    if sort == "popular":
        surprise_bags = sorted(
            surprise_bags,
            key=lambda item: item.quantity_sold + item.quantity_reserved,
            reverse=True,
        )
    else:
        surprise_bags = sorted(
            surprise_bags,
            key=lambda item: item.created_at,
            reverse=True,
        )

    return [
        _to_public_surprise_bag(surprise_bag, merchant)
        for surprise_bag in surprise_bags[:limit]
        if (merchant := session.get(Merchant, surprise_bag.merchant_id))
    ]


@router.get(
    "/surprise-bags/{surprise_bag_id}",
    response_model=PublicSurpriseBagRead,
)
def read_public_surprise_bag(
    surprise_bag_id: str,
    session: Session = Depends(get_session),
) -> PublicSurpriseBagRead:
    surprise_bag = session.get(SurpriseBag, surprise_bag_id)
    if not surprise_bag or surprise_bag.status != SurpriseBagStatus.active:
        raise HTTPException(status_code=404, detail="surprise bag not found")

    merchant = session.get(Merchant, surprise_bag.merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="merchant not found")

    return _to_public_surprise_bag(surprise_bag, merchant)


@router.get(
    "/merchants/{merchant_id}/surprise-bags",
    response_model=list[PublicSurpriseBagRead],
)
def list_public_merchant_surprise_bags(
    merchant_id: str,
    session: Session = Depends(get_session),
) -> list[PublicSurpriseBagRead]:
    merchant = session.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="merchant not found")

    surprise_bags = session.exec(
        select(SurpriseBag)
        .where(SurpriseBag.merchant_id == merchant_id)
        .where(SurpriseBag.status == SurpriseBagStatus.active)
    ).all()

    surprise_bags = sorted(
        surprise_bags,
        key=lambda item: item.created_at,
        reverse=True,
    )

    return [
        _to_public_surprise_bag(surprise_bag, merchant)
        for surprise_bag in surprise_bags
    ]
