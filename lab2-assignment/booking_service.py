"""Lab Assignment 2 - a REST service for booking campus rooms."""
from datetime import date

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, model_validator

app = FastAPI(title="Campus Room Booking Service")


class Room(BaseModel):
    """One room that can be booked."""
    room_id: str = Field(min_length=2, max_length=10, examples=["B205"])
    building: str = Field(min_length=1, examples=["Science"])
    capacity: int = Field(ge=1, examples=[30])


class Booking(BaseModel):
    """One booking of one room, on one day, from start_hour to end_hour."""
    room_id: str = Field(examples=["B205"])
    day: date = Field(examples=["2026-11-25"])
    start_hour: int = Field(ge=8, le=20, examples=[10])
    end_hour: int = Field(ge=8, le=20, examples=[12])
    purpose: str = Field(min_length=3, examples=["Study group"])

    @model_validator(mode="after")
    def end_after_start(self):
        if self.end_hour <= self.start_hour:
            raise ValueError("end_hour must be after start_hour")
        return self


# The data lives in the memory of this process.
rooms: dict[str, Room] = {}
bookings: dict[str, Booking] = {}


def overlaps(a: Booking, b: Booking) -> bool:
    """Two bookings overlap if they share a room, a day, and at least one hour."""
    return (a.room_id == b.room_id and a.day == b.day
            and a.start_hour < b.end_hour and b.start_hour < a.end_hour)

# ---------- Rooms ----------

@app.post("/rooms", status_code=201)
def create_room(room: Room) -> Room:
    if room.room_id in rooms:
        raise HTTPException(status_code=409, detail=f"Room {room.room_id} already exists")
    rooms[room.room_id] = room
    return room


@app.get("/rooms")
def list_rooms() -> list[Room]:
    return list(rooms.values())


@app.get("/rooms/{room_id}")
def get_room(room_id: str) -> Room:
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    return rooms[room_id]


@app.get("/rooms/{room_id}/bookings")
def list_room_bookings(room_id: str) -> dict[str, Booking]:
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    return {bid: b for bid, b in bookings.items() if b.room_id == room_id}



# ---------- Bookings ----------

@app.put("/bookings/{booking_id}", status_code=201)
def put_booking(booking_id: str, booking: Booking, response: Response) -> Booking:
    if booking.room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"Room {booking.room_id} not found")

    if booking_id in bookings:
        if bookings[booking_id] == booking:          # the same request sent again
            response.status_code = 200
            return bookings[booking_id]
        raise HTTPException(status_code=409,
                            detail=f"Booking id {booking_id} is already used for a different booking")

    for other_id, other in bookings.items():
        if overlaps(booking, other):
            raise HTTPException(status_code=409,
                                detail=f"Overlaps with booking {other_id} "
                                       f"({other.start_hour}-{other.end_hour})")

    bookings[booking_id] = booking
    return booking


@app.get("/bookings/{booking_id}")
def get_booking(booking_id: str) -> Booking:
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    return bookings[booking_id]


@app.delete("/bookings/{booking_id}", status_code=204)
def delete_booking(booking_id: str) -> Response:
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    del bookings[booking_id]
    return Response(status_code=204)