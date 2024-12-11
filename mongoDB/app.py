from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# FastAPI app setup
app = FastAPI(title="Student Management API")

# MongoDB setup
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["student_db"]
collection = db["students"]

# Templates and Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic Model for API
class Student(BaseModel):
    name: str
    age: int
    grade: str
    city: str

# Frontend Routes
@app.get("/")
async def index(request: Request):
    """Render the homepage."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/students/")
async def students_page(request: Request):
    """Render the student list page."""
    students = await collection.find().to_list(100)
    return templates.TemplateResponse("students.html", {"request": request, "students": students})

@app.get("/add-student/")
async def add_student_form(request: Request):
    """Render the add student form."""
    return templates.TemplateResponse("add_student.html", {"request": request})

@app.post("/add-student/")
async def add_student(name: str = Form(...), age: int = Form(...), grade: str = Form(...), city: str = Form(...)):
    """Handle the add student form submission."""
    student = {"name": name, "age": age, "grade": grade, "city": city}
    result = await collection.insert_one(student)
    if result.acknowledged:
        return RedirectResponse(url="/students/", status_code=303)
    raise HTTPException(status_code=500, detail="Student could not be added.")
