from fastapi import FastAPI, Body, Response, status,HTTPException
from pydantic import BaseModel
from cryptography.fernet import Fernet
import psycopg2
from psycopg2.extras import RealDictCursor

# connection to db
connexion= psycopg2.connect(
   host="dpg-ci8rn3tgkuvmfnsaadag-a.frankfurt-postgres.render.com",
   database= "youschapi",
   user= "sydney",
   password= "",
   cursor_factory=RealDictCursor
)
print("Connected to Database...")
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
    student_name: str
    student_email: str 
    student_phone: str
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

    try:
        # Insert student into the database
        query= "INSERT INTO students (student_name, student_email, student_phone, is_active, classe) VALUES (%s, %s, %s, %s, %s);"
        values=(
            student.student_name,
            student.student_email,
            student.student_phone,
            student.is_active,
            student.classe
        )
        cursor.execute(query, values)
        connexion.commit()
        # setting the status code
        response.status_code=status.HTTP_201_CREATED
        return { "message": "Student added succesfully "}
    except: 
        raise HTTPException(
              status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="INTERNAL SERVER ERROR"
           )
    

# get student by id
@app.get("/student/{student_id}", tags=["students"])
async def showStudent(student_id: int, response: Response):
    try:
        # Fetch student from the database
        cursor.execute(f"SELECT * FROM students WHERE student_id = {student_id}")
        student = cursor.fetchone()
        response.status_code=status.HTTP_200_OK
        if(student):
            return student
        else: 
           raise HTTPException(
              status.HTTP_404_NOT_FOUND,
              detail="Student was not found"
           )
    except:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Student was not found"
        ) 

#update student 
@app.put("/student/{student_id}", tags=["students"])
async def updateStudent(student_id: int, student: Student, response: Response):
    try:
        values = (
                    student.student_name,
                    student.student_email,
                    student.student_phone,
                    student.is_active,
                    student.classe,
                    student_id
                )
        # Fetch student from the database
        cursor.execute(f"SELECT * FROM students WHERE student_id = {student_id}")
        student = cursor.fetchone()
    
        if(student):
             cursor.execute("UPDATE students SET student_name = %s, student_email = %s, student_phone = %s, is_active = %s, classe = %s WHERE student_id = %s", values)
             connexion.commit()
             return {"message": "Student updated successfully"}
        else: 
           raise HTTPException(
              status.HTTP_404_NOT_FOUND,
              detail="Student was not found"
           )
    except:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INTERNAL SERVER ERROR"
        ) 


# delete student from list
@app.delete("/student/{student_id}", status_code=200, tags=["students"])
async def deleteStudent(student_id: int):
    #delete student from the list
  try:
      # Fetch student from the database
     cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
     connexion.commit()
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
