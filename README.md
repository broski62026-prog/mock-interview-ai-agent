# Mock Interview AI Agent

A demo-based AI mock interview application that allows users to configure an interview, answer AI-generated interview questions, receive answer evaluations, and get a final performance report.

## Technologies Used

- Python
- Django
- FastAPI
- PostgreSQL
- OpenAI Agents SDK
- Groq API
- Qwen Model
- HTML
- CSS
- JavaScript

## Features

- User registration and login
- Interview configuration
- Technical, non-technical, and behavioral interviews
- AI-generated interview questions
- Easy, medium, and hard difficulty levels
- Timer for each question
- Answer submission and skipping
- AI-based answer evaluation
- Final interview report
- Interview history
- User-specific interview numbering
- PostgreSQL database storage

## Project Structure

mock-interview-ai-agent/
|
+-- accounts/
+-- api_server/
+-- config/
+-- frontend/
+-- interviews/
+-- test/
+-- manage.py
+-- requirements.txt
+-- .env.example
+-- .gitignore
+-- README.md

## Setup

### 1. Clone the repository

git clone https://github.com/broski62026-prog/mock-interview-ai-agent.git

cd mock-interview-ai-agent

### 2. Create a virtual environment

python -m venv .venv

### 3. Activate the virtual environment

Windows PowerShell:

.venv\Scripts\Activate.ps1

### 4. Install dependencies

pip install -r requirements.txt

### 5. Configure environment variables

Create a .env file in the project root.

Add your PostgreSQL connection and Groq API key:

DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/mock_interview_db
GROQ_API_KEY=your_groq_api_key

Do not commit the .env file to GitHub.

### 6. Run Django migrations

python manage.py migrate

## Running the Project

### Start Django

python manage.py runserver

Django will run at:

http://127.0.0.1:8000

### Start FastAPI

Open another PowerShell terminal.

Activate the virtual environment and run:

uvicorn api_server.main:app --reload --port 8001

FastAPI will run at:

http://127.0.0.1:8001

FastAPI documentation:

http://127.0.0.1:8001/docs
