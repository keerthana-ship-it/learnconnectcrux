import os
from flask import url_for, render_template
from flask_mail import Message
from app import app, mail
import secrets
import string

def send_verification_email(user):
    """Send account verification email to the user"""
    token = user.generate_verification_token()
    
    verification_url = url_for('verify_email', token=token, _external=True)
    
    # Check if email configuration is available
    email_configured = app.config.get('MAIL_USERNAME') != 'example@gmail.com' and app.config.get('MAIL_PASSWORD') != 'password'
    
    if email_configured:
        try:
            msg = Message(
                subject='Verify Your TechLearn Account',
                recipients=[user.email],
                html=render_template('auth/verify_email.html', 
                                    user=user, 
                                    verification_url=verification_url)
            )
            mail.send(msg)
            return True
        except Exception as e:
            app.logger.error(f"Failed to send verification email: {str(e)}")
            return False
    else:
        app.logger.warning("Email not configured. Skipping verification email.")
        # Auto-verify the user in development environment
        user.is_verified = True
        return False

def send_reset_password_email(user):
    """Send password reset email to the user"""
    token = user.generate_reset_token()
    
    reset_url = url_for('reset_password', token=token, _external=True)
    
    # Check if email configuration is available
    email_configured = app.config.get('MAIL_USERNAME') != 'example@gmail.com' and app.config.get('MAIL_PASSWORD') != 'password'
    
    if email_configured:
        try:
            msg = Message(
                subject='Reset Your TechLearn Password',
                recipients=[user.email],
                html=render_template('auth/reset_password.html', 
                                    user=user, 
                                    reset_url=reset_url)
            )
            mail.send(msg)
            return True
        except Exception as e:
            app.logger.error(f"Failed to send password reset email: {str(e)}")
            # In production, we would return False here
            # For development and testing purposes, we'll print the reset URL to logs
            app.logger.info(f"Password reset URL (development only): {reset_url}")
            return False
    else:
        app.logger.warning("Email not configured. Showing reset token in logs for development.")
        # In development, print the reset token to the console
        app.logger.info(f"Password reset token (development only): {token}")
        app.logger.info(f"Password reset URL (development only): {reset_url}")
        return False

def generate_sample_data():
    """
    Generate initial sample data for development purposes.
    This would be called when setting up the application for the first time.
    """
    from app import db
    from models import (Skill, Content, Event, Roadmap, RoadmapTopic, 
                      TopicResource, Quiz, QuizQuestion, QuizOption)
    
    # Add skills
    skills_data = [
        {"name": "Python", "description": "General-purpose programming language"},
        {"name": "Machine Learning", "description": "Field of AI focused on building systems that learn from data"},
        {"name": "Data Science", "description": "Interdisciplinary field that uses scientific methods to extract knowledge from data"},
        {"name": "Web Development", "description": "Building and maintaining websites"},
        {"name": "DevOps", "description": "Practices combining software development and IT operations"}
    ]
    
    for skill_info in skills_data:
        skill = Skill.query.filter_by(name=skill_info["name"]).first()
        if not skill:
            skill = Skill(**skill_info)
            db.session.add(skill)
    
    db.session.commit()
    
    # Add content
    python_skill = Skill.query.filter_by(name="Python").first()
    ml_skill = Skill.query.filter_by(name="Machine Learning").first()
    ds_skill = Skill.query.filter_by(name="Data Science").first()
    
    content_data = [
        {
            "title": "Python for Beginners", 
            "description": "Learn Python fundamentals",
            "content_type": "course",
            "url": "https://example.com/python-beginners",
            "difficulty_level": "beginner",
            "skills": [python_skill]
        },
        {
            "title": "Introduction to Machine Learning", 
            "description": "Understanding ML algorithms",
            "content_type": "article",
            "url": "https://example.com/intro-ml",
            "difficulty_level": "intermediate",
            "skills": [ml_skill, python_skill]
        },
        {
            "title": "Data Science Workflow", 
            "description": "End-to-end data science process",
            "content_type": "video",
            "url": "https://example.com/data-science-workflow",
            "difficulty_level": "intermediate",
            "skills": [ds_skill]
        }
    ]
    
    for content_info in content_data:
        skills = content_info.pop("skills")
        content = Content(**content_info)
        content.skills.extend(skills)
        db.session.add(content)
    
    db.session.commit()
    
    # Add events
    event_data = [
        {
            "title": "Python Meetup", 
            "description": "Monthly meetup for Python enthusiasts",
            "location": "San Francisco, CA",
            "event_date": "2023-12-15 18:00:00",
            "registration_url": "https://example.com/python-meetup",
            "organizer": "Python Community",
            "is_online": False,
            "skills": [python_skill]
        },
        {
            "title": "Machine Learning Workshop", 
            "description": "Hands-on ML workshop",
            "location": "Online",
            "event_date": "2023-12-20 10:00:00",
            "registration_url": "https://example.com/ml-workshop",
            "organizer": "AI Research Group",
            "is_online": True,
            "skills": [ml_skill, python_skill]
        }
    ]
    
    for event_info in event_data:
        skills = event_info.pop("skills")
        event = Event(**event_info)
        event.skills.extend(skills)
        db.session.add(event)
    
    db.session.commit()
    
    # Add roadmaps
    python_roadmap = Roadmap(
        title="Python Developer Roadmap",
        description="Complete path to become a Python developer"
    )
    python_roadmap.skills.append(python_skill)
    db.session.add(python_roadmap)
    db.session.commit()
    
    # Add roadmap topics
    topics_data = [
        {
            "roadmap_id": python_roadmap.id,
            "title": "Python Basics",
            "description": "Fundamentals of Python programming",
            "order": 1,
            "parent_id": None
        },
        {
            "roadmap_id": python_roadmap.id,
            "title": "Object-Oriented Programming",
            "description": "OOP concepts in Python",
            "order": 2,
            "parent_id": None
        },
        {
            "roadmap_id": python_roadmap.id,
            "title": "Web Development with Python",
            "description": "Building web applications using Python",
            "order": 3,
            "parent_id": None
        }
    ]
    
    for topic_info in topics_data:
        topic = RoadmapTopic(**topic_info)
        db.session.add(topic)
    
    db.session.commit()
    
    # Get the first topic for adding subtopics
    python_basics = RoadmapTopic.query.filter_by(title="Python Basics").first()
    
    # Add subtopics
    subtopics_data = [
        {
            "roadmap_id": python_roadmap.id,
            "title": "Variables and Data Types",
            "description": "Understanding Python variables and basic data types",
            "order": 1,
            "parent_id": python_basics.id
        },
        {
            "roadmap_id": python_roadmap.id,
            "title": "Control Flow",
            "description": "Conditionals and loops in Python",
            "order": 2,
            "parent_id": python_basics.id
        },
        {
            "roadmap_id": python_roadmap.id,
            "title": "Functions",
            "description": "Defining and using functions in Python",
            "order": 3,
            "parent_id": python_basics.id
        }
    ]
    
    for subtopic_info in subtopics_data:
        subtopic = RoadmapTopic(**subtopic_info)
        db.session.add(subtopic)
    
    db.session.commit()
    
    # Add a quiz
    python_quiz = Quiz(
        title="Python Fundamentals Quiz",
        description="Test your knowledge of Python basics",
        skill_id=python_skill.id,
        difficulty_level="beginner"
    )
    db.session.add(python_quiz)
    db.session.commit()
    
    # Add quiz questions
    q1 = QuizQuestion(
        quiz_id=python_quiz.id,
        question_text="What is the output of print(2 + 2)?"
    )
    db.session.add(q1)
    db.session.commit()
    
    # Add options to the question
    options = [
        {"question_id": q1.id, "option_text": "4", "is_correct": True},
        {"question_id": q1.id, "option_text": "22", "is_correct": False},
        {"question_id": q1.id, "option_text": "Error", "is_correct": False},
        {"question_id": q1.id, "option_text": "None", "is_correct": False}
    ]
    
    for option_info in options:
        option = QuizOption(**option_info)
        db.session.add(option)
    
    db.session.commit()
