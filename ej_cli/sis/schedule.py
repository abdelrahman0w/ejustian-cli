from pydantic import BaseModel


class Course(BaseModel):
    name: str
    code: str
    type: str
    time: str
    venue: str
    instructor: str


class WeekDay(BaseModel):
    day: str
    courses: list[Course]


class Schedule(BaseModel):
    week_days: list[WeekDay]
