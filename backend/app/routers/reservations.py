from fastapi import APIRouter

router = APIRouter(tags=["reservations"])


@router.post("/reservations")
def create_reservation() -> dict[str, str]:
    return {"message": "TODO: create reservation"}


@router.get("/merchant/reservations")
def list_merchant_reservations() -> dict[str, str]:
    return {"message": "TODO: list merchant reservations"}


@router.patch("/merchant/reservations/{reservation_id}/picked-up")
def mark_reservation_picked_up(reservation_id: str) -> dict[str, str]:
    return {
        "message": "TODO: mark reservation picked up",
        "reservation_id": reservation_id,
    }
