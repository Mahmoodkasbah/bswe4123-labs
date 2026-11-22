"""Lab 2 - a REST service that manages university courses."""
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

app = FastAPI(title="Courses Service")


class Course(BaseModel):
    """What a client sends and receives for one course."""
    code: str = Field(min_length=3, max_length=12, examples=["BSWE4321"])
    title: str = Field(min_length=3, examples=["Distributed Software Systems"])
    credits: int = Field(ge=1, le=6, examples=[2])
    capacity: int = Field(ge=1, examples=[40])


# The resources live in the memory of this process (for now).
courses: dict[str, Course] = {}


@app.get("/courses")
def list_courses() -> list[Course]:
    return list(courses.values())


@app.get("/courses/{code}")
def get_course(code: str) -> Course:
    if code not in courses:
        raise HTTPException(status_code=404, detail=f"Course {code} not found")
    return courses[code]


@app.post("/courses", status_code=201)
def create_course(course: Course) -> Course:
    if course.code in courses:
        raise HTTPException(status_code=409, detail=f"Course {course.code} already exists")
    courses[course.code] = course
    return course


@app.put("/courses/{code}")
def replace_course(code: str, course: Course) -> Course:
    if course.code != code:
        raise HTTPException(status_code=400, detail="The code in the URL and in the body differ")
    courses[code] = course           # create it, or replace it completely
    return course


@app.delete("/courses/{code}", status_code=204)
def delete_course(code: str) -> Response:
    if code not in courses:
        raise HTTPException(status_code=404, detail=f"Course {code} not found")
    del courses[code]
    return Response(status_code=204)