import json
from tabulate import tabulate
from typing import *
class AttendanceTracker():

    def __init__(self) -> None: 
        try : 
            with open("attendance.json","r" ) as f:
                self.attendance = json.load(f)
        except Exception: 
            with open("attendance.json", "w+") as f:
                self.attendance = dict()

    def save(self) -> None:
        with open("attendance.json", "w+") as f:
            json.dump(self.attendance,f)
    
    def add_course(self, course_code:str) -> None:
        if course_code in self.attendance.keys(): raise ValueError("Course already exists")
        else : self.attendance[course_code] = 0
    
    def remove_course(self, course_code:str) -> None:
        if course_code not in self.attendance.keys(): raise ValueError("Course does not exists")
        else : del self.attendance[course_code]

    def remove_all_course(self) -> None:
        for course_code  in self.attendance.keys():
            del self.attendance[course_code]

    def increment_attendance(self, course_code:str)-> None:
        if course_code not in self.attendance.keys(): raise ValueError("Course does not exists")
        else: self.attendance[course_code] += 1

    def decrement_attendance(self, course_code:str)-> None:
        if course_code not in self.attendance.keys(): raise ValueError("Course does not exists")
        if self.attendance[course_code] == 0 : raise ValueError("Course has 0 absence")
        else: self.attendance[course_code] -= 1
        
    def __str__(self) -> str:
        table_headers= ['Course Code / Course Name','# of times of absences']
        attendance_table = tabulate(self.attendance.items(), headers=table_headers,tablefmt='pretty')
        return str(attendance_table)
    
    def __repr__(self) -> str: 
        return str(self.attendance)