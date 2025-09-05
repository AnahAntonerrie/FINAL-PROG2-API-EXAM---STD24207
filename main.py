from datetime import date
from typing import List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr

app = FastAPI(title="Hotel Booking (in-memory)")

class BookingIn(BaseModel):
    client_name: str = Field(..., min_length=1, description="Nom du client")
    client_phone: str = Field(..., min_length=3, description="Téléphone du client")
    client_email: EmailStr
    room_number: int = Field(..., ge=1, description="Numéro de chambre (entier >= 1)")
    room_description: str = Field(..., min_length=1)
    booking_date: date = Field(..., description="Date de réservation (YYYY-MM-DD)")

class Booking(BookingIn):
    id: int

BOOKINGS: List[Booking] = []
_next_id = 1

def _next_booking_id() -> int:
    global _next_id
    nid = _next_id
    _next_id += 1
    return nid

@app.get("/booking", response_model=List[Booking])
def list_bookings():
    return BOOKINGS

@app.post("/booking", response_model=List[Booking], status_code=status.HTTP_200_OK)
def create_booking(payload: BookingIn):

    for b in BOOKINGS:
        if b.room_number == payload.room_number and b.booking_date == payload.booking_date:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"La chambre {payload.room_number} n'est plus disponible "
                    f"à la date {payload.booking_date.isoformat()}."
                ),
            )

    new_booking = Booking(id=_next_booking_id(), **payload.model_dump())
    BOOKINGS.append(new_booking)
    return BOOKINGS

@app.get("/")
def root():
    return {"service": "hotel-booking", "count": len(BOOKINGS)}
