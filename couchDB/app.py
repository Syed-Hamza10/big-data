from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from couchdb import Server, ResourceNotFound

app = FastAPI()

# Connect to CouchDB
COUCHDB_URL = "http://admin:admin@127.0.0.1:5984/"  # Replace with your CouchDB URL
server = Server(COUCHDB_URL)

# Ensure the database exists
DB_NAME = "students"
if DB_NAME not in server:
    server.create(DB_NAME)
db = server[DB_NAME]

# Templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the homepage."""
    students = [doc for doc in db]
    return templates.TemplateResponse("index.html", {"request": request, "students": students})


@app.post("/add-student/")
async def add_student(name: str = Form(...), age: int = Form(...)):
    """Add a new student."""
    student = {"name": name, "age": age}
    doc_id, doc_rev = db.save(student)
    return RedirectResponse("/", status_code=303)


@app.get("/get-student/{student_id}")
async def get_student(student_id: str):
    """Retrieve a student by ID."""
    try:
        student = db[student_id]
        return {"id": student_id, "student": student}
    except ResourceNotFound:
        raise HTTPException(status_code=404, detail="Student not found")


@app.post("/update-student/{student_id}")
async def update_student(student_id: str, age: int = Form(...)):
    """Update a student's age."""
    try:
        student = db[student_id]
        student["age"] = age
        db[student_id] = student  # Update the document
        return RedirectResponse("/", status_code=303)
    except ResourceNotFound:
        raise HTTPException(status_code=404, detail="Student not found")


@app.post("/delete-student/{student_id}")
async def delete_student(student_id: str):
    """Delete a student by ID."""
    try:
        student = db[student_id]
        db.delete(student)
        return RedirectResponse("/", status_code=303)
    except ResourceNotFound:
        raise HTTPException(status_code=404, detail="Student not found")
