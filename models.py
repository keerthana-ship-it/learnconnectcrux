from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=True)
    
    # Relationships
    profile = db.relationship('UserProfile', backref='user', uselist=False)
    bookmarks = db.relationship('ContentBookmark', backref='user', lazy='dynamic')
    event_bookmarks = db.relationship('EventBookmark', backref='user', lazy='dynamic')
    quiz_results = db.relationship('QuizResult', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token
    
    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        return self.reset_token


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.String(255), nullable=True)  # Comma-separated skills
    interests = db.Column(db.String(255), nullable=True)  # Comma-separated interests
    education = db.Column(db.String(255), nullable=True)
    experience_level = db.Column(db.String(50), nullable=True)  # Beginner, Intermediate, Advanced


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    content = db.relationship('Content', secondary='content_skill', back_populates='skills')
    roadmaps = db.relationship('Roadmap', secondary='roadmap_skill', back_populates='skills')


class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content_type = db.Column(db.String(50), nullable=False)  # article, video, course, etc.
    url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    difficulty_level = db.Column(db.String(50), nullable=True)  # Beginner, Intermediate, Advanced
    
    # Relationships
    skills = db.relationship('Skill', secondary='content_skill', back_populates='content')
    bookmarks = db.relationship('ContentBookmark', backref='content', lazy='dynamic')


class ContentSkill(db.Model):
    __tablename__ = 'content_skill'
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), primary_key=True)


class ContentBookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    registration_url = db.Column(db.String(500), nullable=True)
    organizer = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_online = db.Column(db.Boolean, default=False)
    
    # Relationships
    skills = db.relationship('Skill', secondary='event_skill', backref='events')
    bookmarks = db.relationship('EventBookmark', backref='event', lazy='dynamic')


class EventSkill(db.Model):
    __tablename__ = 'event_skill'
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), primary_key=True)


class EventBookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Roadmap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('Skill', secondary='roadmap_skill', back_populates='roadmaps')
    topics = db.relationship('RoadmapTopic', backref='roadmap', lazy='dynamic')


class RoadmapSkill(db.Model):
    __tablename__ = 'roadmap_skill'
    roadmap_id = db.Column(db.Integer, db.ForeignKey('roadmap.id'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), primary_key=True)


class RoadmapTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey('roadmap.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('roadmap_topic.id'), nullable=True)
    
    # Relationships
    subtopics = db.relationship('RoadmapTopic', backref=db.backref('parent', remote_side=[id]))
    resources = db.relationship('TopicResource', backref='topic', lazy='dynamic')


class TopicResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('roadmap_topic.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=True)
    resource_type = db.Column(db.String(50), nullable=False)  # article, video, exercise
    order = db.Column(db.Integer, nullable=False)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    difficulty_level = db.Column(db.String(50), nullable=False)  # Beginner, Intermediate, Advanced
    
    # Relationships
    questions = db.relationship('QuizQuestion', backref='quiz', lazy='dynamic')
    results = db.relationship('QuizResult', backref='quiz', lazy='dynamic')


class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    
    # Relationships
    options = db.relationship('QuizOption', backref='question', lazy='dynamic')


class QuizOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)


class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
