"""Lab Assignment 2 - call every operation of the booking service and print the status codes.

Usage: python test_bookings.py http://127.0.0.1:8000
Start the service fresh before running this script.
"""
import sys

import httpx

base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"

room = {"room_id": "A101", "building": "Engineering", "capacity": 40}
booking = {"room_id": "A101", "day": "2026-11-25", "start_hour": 10, "end_hour": 12,
           "purpose": "Study group"}


def show(label, response):
    body = response.text if response.content else "(no body)"
    print(f"{label:<48} -> {response.status_code} {body}")


with httpx.Client(base_url=base, timeout=5.0) as client:
    print("--- Rooms ---")
    show("POST   /rooms (A101)", client.post("/rooms", json=room))
    show("POST   /rooms (A101 again)", client.post("/rooms", json=room))
    show("POST   /rooms (capacity 0)", client.post("/rooms", json={**room, "room_id": "X1", "capacity": 0}))
    show("GET    /rooms", client.get("/rooms"))
    show("GET    /rooms/A101", client.get("/rooms/A101"))
    show("GET    /rooms/Z999", client.get("/rooms/Z999"))

    print("\n--- Bookings ---")
    show("PUT    /bookings/b1 (10-12)", client.put("/bookings/b1", json=booking))
    show("PUT    /bookings/b2 (12-13, touches b1)",
         client.put("/bookings/b2", json={**booking, "start_hour": 12, "end_hour": 13}))
    show("PUT    /bookings/b3 (11-13, overlaps b1)",
         client.put("/bookings/b3", json={**booking, "start_hour": 11, "end_hour": 13}))
    show("PUT    /bookings/b4 (end before start)",
         client.put("/bookings/b4", json={**booking, "start_hour": 12, "end_hour": 10}))
    show("PUT    /bookings/b5 (starts at 7)",
         client.put("/bookings/b5", json={**booking, "start_hour": 7}))
    show("PUT    /bookings/b6 (room Z999)",
         client.put("/bookings/b6", json={**booking, "room_id": "Z999"}))
    show("PUT    /bookings/b1 (same id, other purpose)",
         client.put("/bookings/b1", json={**booking, "purpose": "Another meeting"}))
    show("GET    /bookings/b1", client.get("/bookings/b1"))
    show("GET    /bookings/b99", client.get("/bookings/b99"))
    show("GET    /rooms/A101/bookings", client.get("/rooms/A101/bookings"))
    show("GET    /rooms/Z999/bookings", client.get("/rooms/Z999/bookings"))
    show("DELETE /bookings/b2", client.delete("/bookings/b2"))
    show("DELETE /bookings/b2 (again)", client.delete("/bookings/b2"))

    print("\n--- Step 4: the same booking sent twice (lost reply) ---")
    retry = {**booking, "start_hour": 14, "end_hour": 16, "purpose": "Extra lab session"}
    show("PUT    /bookings/r1 (attempt 1)", client.put("/bookings/r1", json=retry))
    show("PUT    /bookings/r1 (attempt 2)", client.put("/bookings/r1", json=retry))
    count = len(client.get("/rooms/A101/bookings").json())
    print(f"Bookings for A101 now: {count} (b1 and r1)")