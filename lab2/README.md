# Lab 2: Your First REST Service

**Name:** Mahmood Kasbah

**Student ID:** 120220219

## Experiment 1: Explore the API in the browser

| Step | Request                                               | Status code |
| ---- | ----------------------------------------------------- | ----------- |
| 1    | POST /courses (BSWE4321)                              | 201         |
| 1    | POST /courses (BSWE4123)                              | 201         |
| 1    | POST /courses (MATH2301)                              | 201         |
| 1    | POST /courses (BSWE4321 again)                        | 409         |
| 2    | GET /courses                                          | 200         |
| 2    | GET /courses/BSWE4321                                 | 200         |
| 2    | GET /courses/XYZ999                                   | 404         |
| 3    | PUT /courses/BSWE4321 (capacity 45)                   | 200         |
| 4    | POST /courses with "credits": "two" and "capacity": 0 | 422         |
| 5    | DELETE /courses/MATH2301                              | 204         |
| 5    | GET /courses/MATH2301 after delete                    | 404         |

**Who rejected the invalid data in step 4?**

Pydantic rejected the invalid data, not my code. The function `create_course` never checks the values of `credits` or `capacity`. FastAPI checks the request body against the `Course` model before the function runs.

The reply had two errors:

- `credits`: `"two"` is not a valid integer, because of `credits: int = Field(ge=1, le=6, ...)`.
- `capacity`: `0` is less than 1, because of `capacity: int = Field(ge=1, ...)`.

Because the data did not match the model, FastAPI returned **422 Unprocessable Content** and `create_course` was never called.

## Experiment 2: Call the API from a client

```
POST   /courses                    -> 201 {"code":"BSWE4321","title":"Distributed Software Systems","credits":2,"capacity":40}
GET    /courses/BSWE4321           -> 200 {"code":"BSWE4321","title":"Distributed Software Systems","credits":2,"capacity":40}
GET    /courses/XYZ999             -> 404 {"detail":"Course XYZ999 not found"}
PUT    /courses/BSWE4321 (cap 45)  -> 200 {"code":"BSWE4321","title":"Distributed Software Systems","credits":2,"capacity":45}
GET    /courses                    -> 200 [{"code":"BSWE4321","title":"Distributed Software Systems","credits":2,"capacity":45}]
POST   /courses (invalid data)     -> 422 {"detail":[{"type":"int_parsing","loc":["body","credits"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"two"},{"type":"greater_than_equal","loc":["body","capacity"],"msg":"Input should be greater than or equal to 1","input":0,"ctx":{"ge":1}}]}
DELETE /courses/BSWE4321           -> 204 (no body)
GET    /courses/BSWE4321           -> 404 {"detail":"Course BSWE4321 not found"}
```

**Did the browser and the Python client get the same answers? Why?**

Yes. The browser (`/docs`) and the Python client (`try_api.py` with `httpx`) got the same status codes for the same operations, because both send normal HTTP requests to the same endpoints, and the server treats them the same way. The server does not know which program sent the request.

The only difference was the first `POST /courses`, which returned `201` instead of `409`. This was not caused by the client. The service was running with `--reload`, so saving `try_api.py` inside `lab2` restarted the server. The courses are stored only in memory (`courses = {}`), so the data from Experiment 1 was lost before the script ran.
