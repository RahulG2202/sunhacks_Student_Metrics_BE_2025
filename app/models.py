# app/models.py
import os
from dotenv import load_dotenv
from sqlalchemy import (create_engine, Column, Integer, String, Float,
                        ForeignKey, Table)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# Load environment variables from .env file for the database URL
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # A fallback for local development if .env is not set up
    # Make sure to use the no-password version if your local MySQL has no password
    DATABASE_URL = "mysql+pymysql://root@localhost/student_metrics_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Association Table for Many-to-Many relationship ---
# Foreign keys here must match the new table names.
professor_courses_association = Table(
    'professor_courses', Base.metadata,
    Column('professor_id', Integer, ForeignKey('prof_details.id')),  # UPDATED
    Column('course_id', Integer, ForeignKey('course_details.id'))  # UPDATED
)


class Professor(Base):
    __tablename__ = "prof_details"  # UPDATED
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    # The relationship to the Course model, linked by the association table
    courses = relationship(
        "Course",
        secondary=professor_courses_association,
        back_populates="professors"
    )


class Course(Base):
    __tablename__ = "course_details"  # UPDATED
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(50), unique=True,
                         nullable=False)  # e.g., "SER515"
    # e.g., "Foundations of Software Engineering"
    name = Column(String(255), nullable=False)

    # Relationship back to Professor
    professors = relationship(
        "Professor",
        secondary=professor_courses_association,
        back_populates="courses"
    )
    # Relationship to the enrollments in this course
    enrollments = relationship("Enrollment", back_populates="course")


class Student(Base):
    __tablename__ = "student_details"  # UPDATED
    id = Column(Integer, primary_key=True, index=True)
    # The Student ID from the CSV, e.g., "S1000"
    student_id_str = Column(String(50), unique=True,
                            index=True, nullable=False)
    name = Column(String(100), nullable=False)

    # Relationship to all enrollments for this student
    enrollments = relationship("Enrollment", back_populates="student")


class Enrollment(Base):
    __tablename__ = "enrollment_details"  # UPDATED
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys to link a student to a course. Must match new table names.
    student_id = Column(Integer, ForeignKey('student_details.id'))  # UPDATED
    course_id = Column(Integer, ForeignKey('course_details.id'))   # UPDATED

    # --- Data columns from the CSV ---
    quiz_score_1 = Column(Float)
    quiz_score_2 = Column(Float)
    quiz_score_3 = Column(Float)
    assignment_1 = Column(Float)
    assignment_2 = Column(Float)
    assignment_3 = Column(Float)
    attendance = Column(Float)
    mid_term_1_score = Column(Float)

    # --- AI Agent Output Columns ---
    # These are calculated per student, per course
    average_overall_score = Column(Float)
    risk_score = Column(String(50), default="Not Calculated")

    # Relationships to easily access the student and course objects
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
