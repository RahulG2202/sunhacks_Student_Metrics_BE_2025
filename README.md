# ClassPulse(Student Metric Dashboard)

ClassPulse is designed as a professor-only early warning system that converts raw student data into actionable insights. Professors begin by uploading a CSV file containing quizzes, assignments, attendance, and midterm scores. The platform then handles the heavy lifting in the background performing data cleaning, normalization, and pattern detection before applying a custom risk-classification algorithm.
Within seconds, ClassPulse categorizes students into high, medium, or low risk groups and generates individual dashboards for each student. These dashboards allow professors to deep dive into performance breakdowns, identifying whether attendance, quizzes, or assignments are the main issues. Importantly, the data and analysis remain accessible only to professors, ensuring privacy while empowering them to take timely, targeted interventions.

# Tech Stack

- Python, FastAPI, alembic, celery, redis, pandas, scikit-learn, numpy.

## Database name: student_metrics_db
