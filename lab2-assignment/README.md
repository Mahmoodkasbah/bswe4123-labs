# Lab Assignment 2 - Campus Room Booking Service

**Name:** محمود كسبة

**Student ID:** 120220219

**Instructor:** Esraa Ferwana

## 1. API Design

| Action            | Method | Endpoint                    | Request body                                | Success   | Errors        |
| ----------------- | ------ | --------------------------- | ------------------------------------------- | --------- | ------------- |
| Add Room          | POST   | `/rooms`                    | room_id, building, capacity                 | 201       | 409, 422      |
| Get All Rooms     | GET    | `/rooms`                    | —                                           | 200       | None          |
| Get Room by ID    | GET    | `/rooms/{room_id}`          | —                                           | 200       | 404           |
| Get Room Bookings | GET    | `/rooms/{room_id}/bookings` | —                                           | 200       | 404           |
| Book a Room       | PUT    | `/bookings/{booking_id}`    | room_id, day, start_hour, end_hour, purpose | 201 / 200 | 404, 409, 422 |
| Get Booking by ID | GET    | `/bookings/{booking_id}`    | —                                           | 200       | 404           |
| Delete Booking    | DELETE | `/bookings/{booking_id}`    | —                                           | 204       | 404           |

What the error codes mean:

- **404:** the room or the booking does not exist.
- **409:** the room already exists, the booking overlaps another booking, or the booking id is already used for a different booking.
- **422:** invalid data, for example an end hour before the start hour, or an hour outside 8:00–20:00.

## 2. Safe to Retry (Idempotency)

If I used `POST /bookings` and the server chose a new id every time, a lost reply would be a problem. Sending the same booking again would either create a second booking for the same time, or fail with 409 because it overlaps its own first copy.

So I used **PUT with a booking_id chosen by the client**. Sending the same request again with the same `booking_id` points to the same booking, so no duplicate is created.

The booking works as follows:

- **First request:** if the booking id is new and the data is valid, the booking is created and the server returns **201 Created**.
- **Same request again:** if I send the same booking id with the same data, the server returns **200 OK** without creating another booking.
- **Same id with different data:** the server returns **409 Conflict**, because this booking id is already used.

The server checks if the `booking_id` already exists **before** it checks for overlaps. Otherwise the retry would overlap with its own first copy and return 409.

I tested this in `test_bookings.py` by sending the same request for `r1` twice. The first request returned 201, and the second returned 200. I then counted the bookings of room A101 and there were still only 2 (`b1` and `r1`), so the retry did not create a duplicate.

## 3. Client Script Output (test_bookings.py)

I ran the script with `python test_bookings.py http://127.0.0.1:8000` on a freshly started service.

Summary:

| Test                             | Status |
| -------------------------------- | ------ |
| POST /rooms (create A101)        | 201    |
| POST /rooms (duplicate)          | 409    |
| POST /rooms (capacity 0)         | 422    |
| GET /rooms                       | 200    |
| GET /rooms/A101                  | 200    |
| GET /rooms/Z999                  | 404    |
| Book 10–12                       | 201    |
| Book 12–13 (touches, no overlap) | 201    |
| Book 11–13 (overlap)             | 409    |
| End hour before start hour       | 422    |
| Start at 7:00 (outside hours)    | 422    |
| Unknown room                     | 404    |
| Same id, different data          | 409    |
| GET /bookings/b1                 | 200    |
| GET unknown booking              | 404    |
| GET /rooms/A101/bookings         | 200    |
| GET /rooms/Z999/bookings         | 404    |
| DELETE /bookings/b2              | 204    |
| DELETE /bookings/b2 again        | 404    |
| Same booking, attempt 1          | 201    |
| Same booking, attempt 2          | 200    |

Full output:

```
--- Rooms ---
POST   /rooms (A101)                             -> 201 {"room_id":"A101","building":"Engineering","capacity":40}
POST   /rooms (A101 again)                       -> 409 {"detail":"Room A101 already exists"}
POST   /rooms (capacity 0)                       -> 422 {"detail":[{"type":"greater_than_equal","loc":["body","capacity"],"msg":"Input should be greater than or equal to 1","input":0,"ctx":{"ge":1}}]}
GET    /rooms                                    -> 200 [{"room_id":"A101","building":"Engineering","capacity":40}]
GET    /rooms/A101                               -> 200 {"room_id":"A101","building":"Engineering","capacity":40}
GET    /rooms/Z999                               -> 404 {"detail":"Room Z999 not found"}

--- Bookings ---
PUT    /bookings/b1 (10-12)                      -> 201 {"room_id":"A101","day":"2026-11-25","start_hour":10,"end_hour":12,"purpose":"Study group"}
PUT    /bookings/b2 (12-13, touches b1)          -> 201 {"room_id":"A101","day":"2026-11-25","start_hour":12,"end_hour":13,"purpose":"Study group"}
PUT    /bookings/b3 (11-13, overlaps b1)         -> 409 {"detail":"Overlaps with booking b1 (10-12)"}
PUT    /bookings/b4 (end before start)           -> 422 {"detail":[{"type":"value_error","loc":["body"],"msg":"Value error, end_hour must be after start_hour","input":{"room_id":"A101","day":"2026-11-25","start_hour":12,"end_hour":10,"purpose":"Study group"},"ctx":{"error":{}}}]}
PUT    /bookings/b5 (starts at 7)                -> 422 {"detail":[{"type":"greater_than_equal","loc":["body","start_hour"],"msg":"Input should be greater than or equal to 8","input":7,"ctx":{"ge":8}}]}
PUT    /bookings/b6 (room Z999)                  -> 404 {"detail":"Room Z999 not found"}
PUT    /bookings/b1 (same id, other purpose)     -> 409 {"detail":"Booking id b1 is already used for a different booking"}
GET    /bookings/b1                              -> 200 {"room_id":"A101","day":"2026-11-25","start_hour":10,"end_hour":12,"purpose":"Study group"}
GET    /bookings/b99                             -> 404 {"detail":"Booking b99 not found"}
GET    /rooms/A101/bookings                      -> 200 {"b1":{"room_id":"A101","day":"2026-11-25","start_hour":10,"end_hour":12,"purpose":"Study group"},"b2":{"room_id":"A101","day":"2026-11-25","start_hour":12,"end_hour":13,"purpose":"Study group"}}
GET    /rooms/Z999/bookings                      -> 404 {"detail":"Room Z999 not found"}
DELETE /bookings/b2                              -> 204 (no body)
DELETE /bookings/b2 (again)                      -> 404 {"detail":"Booking b2 not found"}

--- Step 4: the same booking sent twice (lost reply) ---
PUT    /bookings/r1 (attempt 1)                  -> 201 {"room_id":"A101","day":"2026-11-25","start_hour":14,"end_hour":16,"purpose":"Extra lab session"}
PUT    /bookings/r1 (attempt 2)                  -> 200 {"room_id":"A101","day":"2026-11-25","start_hour":14,"end_hour":16,"purpose":"Extra lab session"}
Bookings for A101 now: 2 (b1 and r1)
```
