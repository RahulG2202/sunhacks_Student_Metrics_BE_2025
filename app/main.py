from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware  # Import CORS
from sqlalchemy.orm import Session
from . import models
from .models import SessionLocal, engine
from tasks.process_data import process_csv_task

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",  # The origin of your React app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# in app/main.py

@app.post("/api/upload-course-data")
async def upload_course_data(
    # --- UPDATED: Expecting IDs from the frontend form ---
    professorId: str = Form(...),
    courseId: str = Form(...),
    file: UploadFile = File(...)
):
    if file.content_type != 'text/csv':
        raise HTTPException(
            400, detail="Invalid file type. Please upload a CSV.")

    # Save the uploaded file to a temporary location
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # --- UPDATED: Trigger the background Celery task with the new ID parameters ---
    process_csv_task.delay(
        file_path=file_path,
        professor_id_str=professorId,  # Pass the professor ID
        course_id_str=courseId       # Pass the course ID
    )

    return {
        "message": "File received and is being processed in the background. "
                   "The dashboard will update shortly."
    }
