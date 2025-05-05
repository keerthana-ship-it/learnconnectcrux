# Deployment Guide for TechLearn

This guide will help you deploy your TechLearn application to a platform like Render or any other platform that supports Python web applications.

## Prerequisites

- A GitHub account
- A Render account (free tier available)
- A PostgreSQL database (Render provides this)

## Step 1: Create a requirements.txt

Create a `requirements.txt` file with the following contents:

```
email-validator
flask
flask-login
flask-mail
flask-sqlalchemy
flask-wtf
gunicorn
psycopg2-binary
sqlalchemy
werkzeug
wtforms
```

## Step 2: Push to GitHub

1. Create a new repository on GitHub
2. Initialize a local git repository in your project folder:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

## Step 3: Deploy on Render

1. Log in to your Render account
2. Go to the Dashboard and click "New Web Service"
3. Connect your GitHub repository
4. Configure your web service:
   - **Name**: TechLearn (or any name you prefer)
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --reuse-port main:app`

5. Add the following environment variables:
   - `DATABASE_URL`: Your PostgreSQL database URL
   - `SESSION_SECRET`: A random secure string for session encryption

6. Click "Create Web Service"

## Step 4: Set Up Database

1. In the Render dashboard, go to "PostgreSQL" and create a new PostgreSQL database
2. Connect your web service to this database by setting the `DATABASE_URL` environment variable to the database's external URL

## Step 5: Initialize Database

After deployment, you'll need to create the database tables:

1. Go to your web service's "Shell" tab
2. Run the following commands:
   ```bash
   python
   ```
   
   Then in the Python shell:
   ```python
   from app import app, db
   with app.app_context():
       db.create_all()
       exit()
   ```

## Step 6: Generate Sample Data (Optional)

1. Access your deployed application
2. Log in with an account
3. Visit the `/generate-sample-data` endpoint to populate the database with sample data

## Important Notes for Deployment

1. Make sure your application is configured to listen on the port specified by the `PORT` environment variable, which Render sets automatically
2. Ensure your database connection string is properly configured using the `DATABASE_URL` environment variable
3. If you're using email functionality, configure the email settings using environment variables