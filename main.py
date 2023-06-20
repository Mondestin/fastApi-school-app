from fastapi import FastAPI, Body, Response, status,HTTPException
from pydantic import BaseModel
from cryptography.fernet import Fernet
import psycopg2
from psycopg2.extras import RealDictCursor

# connection to db
connexion= psycopg2.connect(
   host="localhost",
   database= "youschapi",
   user= "postgres",
   password= "API",
   cursor_factory=RealDictCursor
)
cursor=connexion.cursor()

# Metadata
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "students",
        "description": "Manage students that was register",
    },
]

# Student Model
class Student(BaseModel):
    id: int
    name: str
    email: str 
    phone: str
    is_active: bool
    classe: str

# User Model
class User(BaseModel):
    # id: int
    username: str
    email: str 
    password: str

# key encryption and decrypt
key = Fernet.generate_key()
fernet = Fernet(key)

app= FastAPI(
   title="Yousch API",
   version="1.2",
   description="Yousch API is a school managment system API",
   openapi_tags=tags_metadata) #variable names for the server
# app.openapi = my_schema

# init list of students
students = [
    {
    "id": 1,
    "name": "John",
    "email": "test@yousch.com",
    },
    {
    "id": 2,
    "name": "John Doe",
    "email": "test-2@yousch.com",
    }
]

# init list of students
users = [
    {
    "id": 1,
    "name": "John user",
    "email": "john@yousch.com",
    "password": "hkb@çèè-éè-'(é)"
    },
    {
    "id": 2,
    "name": "John Doe user",
    "email": "john-user@yousch.com",
    "password": "ghé__è'('pjdf@"
    }
]


# default route
@app.get("/")
async def root():
    return {"message": "hello from main"}

# -----------------STUDENTS CRUD---------------------------
# get students list
@app.get("/students",tags=["students"])
async def getStudents():

    # Fetch students from the database
        query = "SELECT * FROM students"
        cursor.execute(query)
        students = cursor.fetchall()

    # return list of students
        return {
            "students" :students,
            "limit": 10,
            "total" : 2,
            "skip": 0
            }

# post student
@app.post("/student", tags=["students"])
async def createStudent(student: Student, response: Response):
    # add new student in array of students
    students.append(student)
    # setting the status code
    response.status_code=status.HTTP_201_CREATED
    return { "message": "Student " + student.name + " added succesfully "}

# get student by id
@app.get("/student/{student_id}", tags=["students"])
async def showStudent(student_id: int, response: Response):
    try:
        # Fetch student from the database
        query = "SELECT * FROM students WHERE student_id = %s"
        
        cursor.execute(query, (student_id))
        student = cursor.fetchone()
        response.status_code=status.HTTP_200_OK
        return student_id
    except:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Student was not found"
        ) 

    



#update student 
@app.put("/student/{student_id}", tags=["students"])
async def updateStudent(student_id: int, student: Student, response: Response):
    
    # check if the student was found
    try: 
     #find student in the array and update 
     students[student_id-1]=student.dict()
     # setting the status code
     response.status_code=status.HTTP_200_OK
     return student
    except:
      raise HTTPException(
         status.HTTP_404_NOT_FOUND,
         detail="Student was not found"
      ) 


# delete student from list
@app.delete("/student/{id}", status_code=200, tags=["students"])
async def deleteStudent(id: int):
    #delete student from the list
  try:
     students.pop(id)
     return { "message": "Student deleted succesfully"}
  except: 
     raise HTTPException(
         status.HTTP_404_NOT_FOUND,
         detail="Student was not found"
      )
# -----------------END OF STUDENTS CRUD-----------------

# -----------------USERS CRUD---------------------------
# get users list
@app.get("/users",tags=["users"])
async def getUsers():
    # return list of users
    return {
           "users" :users,
           "limit": 10,
           "total" : 2,
           "skip": 0
        }

# post user
@app.post("/user",tags=["users"])
async def createUser(user: User, response: Response):
    # add new user in array of users
    new_user={
       "id": len(users)+1,
       "name": user.name,
       "email": user.email,
       "password": fernet.encrypt(user.password.encode())
    }
    users.append(new_user)
    # setting the status code
    response.status_code=status.HTTP_201_CREATED
    return { "message": "User " + user.name + " added succesfully "}

# get user by id
@app.get("/user/{user_id}",tags=["users"])
async def showUser(user_id: int, response: Response):
    
    # check if the user was found
    try: 
     #find user in the array
     user=users[user_id-1]
     # setting the status code
     response.status_code=status.HTTP_200_OK
     return user
    except:
      raise HTTPException(
         status.HTTP_404_NOT_FOUND,
         detail="User was not found"
      ) 
#update user 
@app.put("/user/{user_id}",tags=["users"])
async def updateUser(user_id: int, user: User, response: Response):
    
    # check if the user was found
    try: 
     #find user in the array and update 
     users[user_id-1]=user.dict()
     # setting the status code
     response.status_code=status.HTTP_200_OK
     return user
    except:
      raise HTTPException(
         status.HTTP_404_NOT_FOUND,
         detail="User was not found"
      ) 


# delete user from list
@app.delete("/user/{id}", status_code=200, tags=["users"])
async def deleteUser(id: int):
    #delete user from the list
  try:
     users.pop(id)
     return { "message": "User deleted succesfully"}
  except: 
     raise HTTPException(
         status.HTTP_404_NOT_FOUND,
         detail="User was not found"
      )
# -----------------END OF USERS CRUD---------------------------s