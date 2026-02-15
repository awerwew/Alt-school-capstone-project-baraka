# Course Enrollment Platform

This is a well structured course enrollment application created to register, organize and manage students subjects of concern.

## Features

This API allows you to do the following:
- Create users (students/admins)
- Create courses
- Enroll students in courses
- Enforce course capacity limits
- Activates role base clearance
- Database migrations with Alembic

## A DBdiagram preview of this application

A DBdiagram showing the relationship within the models of this app
![Reference image](<img width="8192" height="6052" alt="image" src="https://github.com/user-attachments/assets/60aa3b18-1aa6-448c-82fe-e397b5f94790" />
)

## A flowchart showing the flow of algorithm of the application

This will help you understand the steps and processes embeded in the logic of the application.
![Reference image](//documents/Course%20Enrollment-2026-02-15-092759.png)


## Setup instruction

- clone repository

```bash
# create a virtual environment
python -m venv venv

# to activate environment
.\venv\Scripts\activate # note for windows users and that's what i use

# Install dependencies
pip install -r requirements.txt


# Configure environment variables in your .env file
DATABASE_URL =postgresql://postgres:*******1111@localhost/CourseEnrollmentPlatform
ALGORITHM=''
SECRET_KEY=''
TOKEN_EXPIRES=30

```



# How to run migrations

```bash
# Install a database management tool
pip install alembic 

# Initialize alembic
alembic init alembic

# General migration
alembic revision --autogenerate -m "initial migration"

# To apply migration
alembic upgrade head

# Rollback on migration
alembic downgrade -1

# To Run the application 
uvicorn app.main:app  # Start my FastAPI web app from main.py.
uvicorn app.main:app --reload # this automatically restart it whenever I change the code.

```
# How to run Tests

```bash
# Install pytest
pip install pytest

# Run pytest on the terminal for actual testing
pytest

# Also you can check for the test coverage using
pytest --cov=.


```

