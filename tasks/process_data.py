# tasks/process_data.py

import pandas as pd
from .celery_init import celery_app
from app.models import SessionLocal, Professor, Course, Student, Enrollment


@celery_app.task
def process_csv_task(file_path: str, professor_id_str: str, course_id_str: str):
    """
    Celery task that USES existing professor and course IDs to process a CSV 
    and populate the database with student enrollment data.
    """
    print(
        f"Starting to process CSV file: {file_path} for Professor ID: {professor_id_str} and Course ID: {course_id_str}")
    db = SessionLocal()
    try:
        # --- UPDATED: Convert incoming string IDs to integers ---
        try:
            professor_id = int(professor_id_str)
            course_id = int(course_id_str)
        except ValueError:
            print("Error: Professor ID and Course ID must be valid integers.")
            # Stop the task if the IDs are not numbers
            return

        # --- UPDATED: Fetch Professor BY ID (No creation) ---
        professor = db.query(Professor).filter(
            Professor.id == professor_id).first()
        if not professor:
            print(
                f"Error: Professor with ID {professor_id} not found in the database. Aborting task.")
            return

        # --- UPDATED: Fetch Course BY ID (No creation) ---
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            print(
                f"Error: Course with ID {course_id} not found in the database. Aborting task.")
            return

        # --- REMOVED: The section for associating professor and course is no longer needed ---
        # We assume the association is already correctly set in the database.

        # --- 4. Process the CSV file (This part remains the same) ---
        df = pd.read_csv(file_path)

        original_columns = df.columns
        df.columns = [
            col.strip().lower().replace(' ', '_').replace('(', '').replace(')', '')
            for col in original_columns
        ]
        print(f"Sanitized columns: {list(df.columns)}")

        # --- 5. Iterate over each student row in the CSV ---
        for index, row in df.iterrows():
            student_id_str = row['student_id']
            student_name = row['student_name']

            # Find or Create Student (This logic remains, as the CSV is the source of new students)
            student = db.query(Student).filter(
                Student.student_id_str == student_id_str).first()
            if not student:
                student = Student(
                    student_id_str=student_id_str, name=student_name)
                db.add(student)
                db.commit()
                db.refresh(student)

            # Check if an enrollment for this student in this course already exists to avoid duplicates
            existing_enrollment = db.query(Enrollment).filter(
                Enrollment.student_id == student.id,
                Enrollment.course_id == course.id
            ).first()

            if not existing_enrollment:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    quiz_score_1=row.get('quiz_score_1'),
                    quiz_score_2=row.get('quiz_score_2'),
                    quiz_score_3=row.get('quiz_score_3'),
                    assignment_1=row.get('assignment_1'),
                    assignment_2=row.get('assignment_2'),
                    assignment_3=row.get('assignment_3'),
                    attendance=row.get('attendance_out_of_10'),
                    mid_term_1_score=row.get('mid_term_1_score'),
                    average_overall_score=row.get('class_average')
                )
                db.add(enrollment)

        db.commit()
        print(
            f"Successfully processed and saved data for {len(df)} students for course '{course.name}'.")

    except Exception as e:
        db.rollback()
        print(f"An error occurred during CSV processing: {e}")
        raise e
    finally:
        db.close()

    return {"status": "success", "message": f"Processed {file_path}"}
