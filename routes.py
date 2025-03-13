from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from urllib.parse import urlparse
from datetime import datetime
import logging

from app import app, db
from models import (User, UserProfile, Skill, Content, ContentBookmark, 
                  Event, EventBookmark, Roadmap, RoadmapTopic, Quiz, 
                  QuizQuestion, QuizOption, QuizResult)
from forms import (LoginForm, RegistrationForm, ResetRequestForm, 
                 ResetPasswordForm, ProfileForm, ContentSearchForm, 
                 EventSearchForm, QuizAnswerForm)
from utils import send_verification_email, send_reset_password_email

# Home page
@app.route('/')
def index():
    featured_content = Content.query.order_by(Content.created_at.desc()).limit(3).all()
    upcoming_events = Event.query.filter(Event.event_date > datetime.utcnow()).order_by(Event.event_date).limit(3).all()
    popular_roadmaps = Roadmap.query.limit(2).all()
    
    return render_template('index.html', 
                        featured_content=featured_content, 
                        upcoming_events=upcoming_events,
                        popular_roadmaps=popular_roadmaps)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
        
        if not user.is_verified:
            flash('Please verify your email before logging in', 'warning')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember.data)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Log In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if phone already exists
            if form.phone.data and User.query.filter_by(phone=form.phone.data).first():
                flash('Phone number already registered. Please use a different one.', 'danger')
                return render_template('auth/register.html', title='Register', form=form)
                
            user = User(username=form.username.data, email=form.email.data)
            # Only set phone if it's not empty
            if form.phone.data and form.phone.data.strip():
                user.phone = form.phone.data
                
            user.set_password(form.password.data)
            user.generate_verification_token()
            
            # Create user profile
            profile = UserProfile()
            db.session.add(profile)
            db.session.flush()
            
            user.profile_id = profile.id
            db.session.add(user)
            db.session.commit()
            
            # Send verification email or auto-verify in development
            email_sent = send_verification_email(user)
            db.session.commit()  # Commit changes after auto-verification
            
            if email_sent:
                flash('Your account has been created! Please check your email to verify your account.', 'success')
            else:
                if user.is_verified:
                    flash('Your account has been created and auto-verified for development purposes. You can now log in.', 'success')
                else:
                    flash('Your account has been created, but email verification could not be sent. Please contact support.', 'warning')
                    
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {str(e)}")
            flash('There was an error processing your registration. Please try again with different information.', 'danger')
    
    return render_template('auth/register.html', title='Register', form=form)

@app.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        flash('Invalid or expired verification link', 'danger')
        return redirect(url_for('login'))
    
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    
    flash('Your account has been verified. You can now log in.', 'success')
    return redirect(url_for('login'))

@app.route('/reset-password-request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            email_sent = send_reset_password_email(user)
            if not email_sent:
                app.logger.info(f"For development: Use token {user.reset_token} to reset password")
        
        flash('If an account with that email exists, we have sent a password reset link.', 'info')
        return redirect(url_for('login'))
    
    return render_template('auth/reset_request.html', title='Reset Password', form=form)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user:
        flash('Invalid or expired reset link', 'danger')
        return redirect(url_for('reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None
        db.session.commit()
        
        flash('Your password has been updated. You can now log in with your new password.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Profile routes
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        try:
            # Check if phone already exists and belongs to another user
            if form.phone.data and form.phone.data.strip():
                existing_user = User.query.filter_by(phone=form.phone.data).first()
                if existing_user and existing_user.id != current_user.id:
                    flash('Phone number already registered by another user. Please use a different one.', 'danger')
                    return render_template('profile.html', title='My Profile', form=form)
                current_user.phone = form.phone.data
            else:
                current_user.phone = None  # Clear the phone field if empty
                
            current_user.username = form.username.data
            current_user.email = form.email.data
            
            if not current_user.profile:
                profile = UserProfile()
                db.session.add(profile)
                db.session.flush()
                current_user.profile_id = profile.id
            
            current_user.profile.location = form.location.data
            current_user.profile.bio = form.bio.data
            current_user.profile.skills = form.skills.data
            current_user.profile.interests = form.interests.data
            current_user.profile.education = form.education.data
            current_user.profile.experience_level = form.experience_level.data
            
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('profile'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Profile update error: {str(e)}")
            flash('There was an error updating your profile. Please try again.', 'danger')
            return render_template('profile.html', title='My Profile', form=form)
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        
        if current_user.profile:
            form.location.data = current_user.profile.location
            form.bio.data = current_user.profile.bio
            form.skills.data = current_user.profile.skills
            form.interests.data = current_user.profile.interests
            form.education.data = current_user.profile.education
            form.experience_level.data = current_user.profile.experience_level
    
    # Get user's bookmarked content and events
    bookmarked_content = Content.query.join(ContentBookmark).filter(ContentBookmark.user_id == current_user.id).all()
    bookmarked_events = Event.query.join(EventBookmark).filter(EventBookmark.user_id == current_user.id).all()
    
    # Get user's quiz results
    quiz_results = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.completed_at.desc()).all()
    
    return render_template('profile.html', title='My Profile', form=form, 
                         bookmarked_content=bookmarked_content,
                         bookmarked_events=bookmarked_events,
                         quiz_results=quiz_results)

# Collect module routes
@app.route('/collect')
@login_required
def collect_dashboard():
    form = ContentSearchForm()
    
    # Get query parameters
    query = request.args.get('query', '')
    skill_name = request.args.get('skill', '')
    content_type = request.args.get('content_type', '')
    difficulty = request.args.get('difficulty', '')
    
    # Base query
    content_query = Content.query
    
    # Apply filters
    if query:
        content_query = content_query.filter(Content.title.ilike(f'%{query}%') | 
                                           Content.description.ilike(f'%{query}%'))
    
    if skill_name:
        content_query = content_query.join(Content.skills).filter(Skill.name.ilike(f'%{skill_name}%'))
    
    if content_type:
        content_query = content_query.filter(Content.content_type == content_type)
    
    if difficulty:
        content_query = content_query.filter(Content.difficulty_level == difficulty)
    
    # Get the content with pagination
    page = request.args.get('page', 1, type=int)
    contents = content_query.paginate(page=page, per_page=12)
    
    # Get all skills for filtering
    skills = Skill.query.order_by(Skill.name).all()
    
    return render_template('collect/dashboard.html', title='Learning Content', 
                         contents=contents, form=form, skills=skills,
                         current_skill=skill_name, current_type=content_type,
                         current_difficulty=difficulty, query=query)

@app.route('/collect/content/<int:content_id>')
@login_required
def content_detail(content_id):
    content = Content.query.get_or_404(content_id)
    
    # Check if the content is bookmarked by the current user
    is_bookmarked = ContentBookmark.query.filter_by(
        user_id=current_user.id, content_id=content_id
    ).first() is not None
    
    # Get related content based on skills
    skill_ids = [skill.id for skill in content.skills]
    related_content = Content.query.filter(
        Content.id != content_id,
        Content.skills.any(Skill.id.in_(skill_ids))
    ).limit(4).all()
    
    return render_template('collect/content_detail.html', title=content.title,
                         content=content, is_bookmarked=is_bookmarked,
                         related_content=related_content)

@app.route('/collect/bookmark/<int:content_id>', methods=['POST'])
@login_required
def bookmark_content(content_id):
    content = Content.query.get_or_404(content_id)
    
    # Check if already bookmarked
    existing_bookmark = ContentBookmark.query.filter_by(
        user_id=current_user.id, content_id=content_id
    ).first()
    
    if existing_bookmark:
        db.session.delete(existing_bookmark)
        db.session.commit()
        return jsonify({'status': 'removed', 'message': 'Bookmark removed'})
    
    # Create new bookmark
    bookmark = ContentBookmark(user_id=current_user.id, content_id=content_id)
    db.session.add(bookmark)
    db.session.commit()
    
    return jsonify({'status': 'added', 'message': 'Content bookmarked'})

@app.route('/collect/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions.all()
    
    if not questions:
        flash('This quiz has no questions yet.', 'info')
        return redirect(url_for('collect_dashboard'))
    
    return render_template('collect/quiz.html', title=quiz.title, quiz=quiz, questions=questions)

@app.route('/collect/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions.all()
    
    correct_answers = 0
    total_questions = len(questions)
    
    for question in questions:
        selected_option_id = request.form.get(f'question_{question.id}')
        
        if selected_option_id:
            selected_option = QuizOption.query.get(int(selected_option_id))
            if selected_option and selected_option.is_correct:
                correct_answers += 1
    
    # Calculate score as percentage
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Save quiz result
    result = QuizResult(user_id=current_user.id, quiz_id=quiz_id, score=score)
    db.session.add(result)
    db.session.commit()
    
    flash(f'Quiz completed! Your score: {score:.1f}%', 'success')
    return redirect(url_for('profile'))

# Connect module routes
@app.route('/connect')
@login_required
def events_list():
    form = EventSearchForm()
    
    # Get query parameters
    query = request.args.get('query', '')
    location = request.args.get('location', '')
    skill_name = request.args.get('skill', '')
    is_online = request.args.get('is_online', type=bool, default=False)
    
    # Base query
    events_query = Event.query.filter(Event.event_date > datetime.utcnow())
    
    # Apply filters
    if query:
        events_query = events_query.filter(Event.title.ilike(f'%{query}%') | 
                                         Event.description.ilike(f'%{query}%'))
    
    if location:
        events_query = events_query.filter(Event.location.ilike(f'%{location}%'))
    
    if skill_name:
        events_query = events_query.join(Event.skills).filter(Skill.name.ilike(f'%{skill_name}%'))
    
    if is_online:
        events_query = events_query.filter(Event.is_online == True)
    
    # Get the events with pagination
    page = request.args.get('page', 1, type=int)
    events = events_query.order_by(Event.event_date).paginate(page=page, per_page=10)
    
    # Get all skills for filtering
    skills = Skill.query.order_by(Skill.name).all()
    
    return render_template('connect/events.html', title='Technical Events', 
                         events=events, form=form, skills=skills,
                         current_location=location, current_skill=skill_name,
                         online_only=is_online, query=query)

@app.route('/connect/event/<int:event_id>')
@login_required
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if the event is bookmarked by the current user
    is_bookmarked = EventBookmark.query.filter_by(
        user_id=current_user.id, event_id=event_id
    ).first() is not None
    
    # Get related events based on skills
    skill_ids = [skill.id for skill in event.skills]
    related_events = Event.query.filter(
        Event.id != event_id,
        Event.event_date > datetime.utcnow(),
        Event.skills.any(Skill.id.in_(skill_ids))
    ).limit(3).all()
    
    return render_template('connect/event_detail.html', title=event.title,
                         event=event, is_bookmarked=is_bookmarked,
                         related_events=related_events)

@app.route('/connect/bookmark/<int:event_id>', methods=['POST'])
@login_required
def bookmark_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if already bookmarked
    existing_bookmark = EventBookmark.query.filter_by(
        user_id=current_user.id, event_id=event_id
    ).first()
    
    if existing_bookmark:
        db.session.delete(existing_bookmark)
        db.session.commit()
        return jsonify({'status': 'removed', 'message': 'Bookmark removed'})
    
    # Create new bookmark
    bookmark = EventBookmark(user_id=current_user.id, event_id=event_id)
    db.session.add(bookmark)
    db.session.commit()
    
    return jsonify({'status': 'added', 'message': 'Event bookmarked'})

# Crux module routes
@app.route('/crux')
@login_required
def roadmaps_list():
    roadmaps = Roadmap.query.all()
    
    # Get available skills for filtering
    skills = Skill.query.order_by(Skill.name).all()
    
    # Filter by skill if specified
    skill_id = request.args.get('skill_id', type=int)
    if skill_id:
        roadmaps = Roadmap.query.join(Roadmap.skills).filter(Skill.id == skill_id).all()
    
    return render_template('crux/roadmaps.html', title='Learning Roadmaps',
                         roadmaps=roadmaps, skills=skills, selected_skill_id=skill_id)

@app.route('/crux/roadmap/<int:roadmap_id>')
@login_required
def roadmap_detail(roadmap_id):
    roadmap = Roadmap.query.get_or_404(roadmap_id)
    
    # Get all top-level topics
    main_topics = RoadmapTopic.query.filter_by(
        roadmap_id=roadmap_id, parent_id=None
    ).order_by(RoadmapTopic.order).all()
    
    return render_template('crux/roadmap_detail.html', title=roadmap.title,
                         roadmap=roadmap, main_topics=main_topics)

# Development routes
@app.route('/generate-sample-data')
@login_required
def generate_data():
    from utils import generate_sample_data
    try:
        generate_sample_data()
        flash('Sample data generated successfully!', 'success')
    except Exception as e:
        app.logger.error(f"Error generating sample data: {str(e)}")
        flash('Error generating sample data. See logs for details.', 'danger')
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
