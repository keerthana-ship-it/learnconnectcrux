from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired()])
    phone = StringField('Phone Number (Optional)', validators=[Optional(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')

class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[Optional(), Length(min=10, max=15)])
    location = StringField('Location', validators=[Optional()])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    skills = StringField('Skills (separated by commas)', validators=[Optional()])
    interests = StringField('Interests (separated by commas)', validators=[Optional()])
    education = StringField('Education', validators=[Optional()])
    experience_level = SelectField('Experience Level', choices=[
        ('', 'Select your experience level'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], validators=[Optional()])
    submit = SubmitField('Update Profile')

class ContentSearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    skill = StringField('Skill', validators=[Optional()])
    content_type = SelectField('Content Type', choices=[
        ('', 'All Types'),
        ('article', 'Articles'),
        ('video', 'Videos'),
        ('course', 'Courses'),
        ('tutorial', 'Tutorials')
    ], validators=[Optional()])
    difficulty = SelectField('Difficulty', choices=[
        ('', 'All Levels'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], validators=[Optional()])
    submit = SubmitField('Search')

class EventSearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    location = StringField('Location', validators=[Optional()])
    skill = StringField('Skill', validators=[Optional()])
    is_online = BooleanField('Online Events Only', default=False)
    submit = SubmitField('Search Events')

class QuizAnswerForm(FlaskForm):
    question_id = HiddenField('Question ID')
    selected_option = HiddenField('Selected Option')
    submit = SubmitField('Submit Answer')
