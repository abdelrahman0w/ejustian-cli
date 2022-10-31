import json

class AttendanceTracker():
    def __init__(self) -> None: 
        with open("attendance", "w+") as f:
            self.attendance = json.load(f) if f.read() else dict()

    def save(self) -> None:
        with open("attendance", "w+") as f:
            json.dump(self.attendance,f)
    
    def add_course(self, course_code:str) -> None:
        pass
    
    def remove_course(self, course_code:str) -> None:
        pass

    def increment_attendance(self, course_code:str)-> None:
        pass
    
    def decrement_attendance(self, course_code:str)-> None:
        pass
