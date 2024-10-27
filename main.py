from app import app, db, login_manager
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Flipbook, PageView
from forms import LoginForm, RegisterForm, UploadForm
from utils import allowed_file, process_pdf, generate_unique_filename
from werkzeug.utils import secure_filename
from sqlalchemy import func
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        logger.info(f"Login attempt for user: {email}")
        
        user = User.query.filter_by(email=email).first()
        if not user:
            logger.warning(f"Login failed: User not found for email: {email}")
            flash('No account found with this email address', 'error')
            return render_template('login.html', form=form)
        
        if not user.check_password(password):
            logger.warning(f"Login failed: Invalid password for user: {email}")
            flash('Invalid password', 'error')
            return render_template('login.html', form=form)
        
        login_user(user)
        logger.info(f"Login successful for user: {email}")
        flash('Login successful!', 'success')
        
        next_page = request.args.get('next')
        return redirect(next_page if next_page else url_for('dashboard'))
        
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            username = form.username.data
            email = form.email.data
            
            logger.info(f"Attempting to register new user with username: {username}")
            
            user = User()
            user.username = username
            user.email = email
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered successfully: {email}")
            flash('Registration successful! Please login with your credentials.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('register.html', form=form)
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logger.info(f"User logged out: {current_user.email}")
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    flipbooks = Flipbook.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', flipbooks=flipbooks)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.pdf_file.data
        if file and allowed_file(file.filename):
            filename = generate_unique_filename(secure_filename(file.filename))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                output_dir = os.path.join(app.config['UPLOAD_FOLDER'], filename.rsplit('.', 1)[0])
                os.makedirs(output_dir, exist_ok=True)
                page_count = process_pdf(filepath, output_dir)
                
                flipbook = Flipbook()
                flipbook.title = form.title.data
                flipbook.filename = filename
                flipbook.user_id = current_user.id
                flipbook.page_count = page_count
                
                db.session.add(flipbook)
                db.session.commit()
                flash('Flipbook created successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                logger.error(f"Error processing PDF: {str(e)}")
                flash(f'Error processing PDF: {str(e)}', 'error')
        else:
            flash('Invalid file format. Please upload a PDF file.', 'error')
    return render_template('upload.html', form=form)

@app.route('/viewer/<unique_id>')
def viewer(unique_id):
    flipbook = Flipbook.query.filter_by(unique_id=unique_id).first_or_404()
    
    page_view = PageView(
        flipbook_id=flipbook.id,
        ip_address=request.remote_addr
    )
    db.session.add(page_view)
    db.session.commit()
    
    return render_template('viewer.html', flipbook=flipbook)

@app.route('/embed/<unique_id>')
def embed_viewer(unique_id):
    flipbook = Flipbook.query.filter_by(unique_id=unique_id).first_or_404()
    
    page_view = PageView(
        flipbook_id=flipbook.id,
        ip_address=request.remote_addr
    )
    db.session.add(page_view)
    db.session.commit()
    
    return render_template('embed.html', flipbook=flipbook)

@app.route('/analytics')
@login_required
def analytics():
    user_flipbooks = Flipbook.query.filter_by(user_id=current_user.id).all()
    
    analytics_data = {}
    for flipbook in user_flipbooks:
        total_views = PageView.query.filter_by(flipbook_id=flipbook.id).count()
        
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_views = db.session.query(
            func.date(PageView.viewed_at).label('date'),
            func.count(PageView.id).label('count')
        ).filter(
            PageView.flipbook_id == flipbook.id,
            PageView.viewed_at >= seven_days_ago
        ).group_by(
            func.date(PageView.viewed_at)
        ).all()
        
        dates = [(seven_days_ago + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(8)]
        views_data = {date: 0 for date in dates}
        for date, count in daily_views:
            views_data[date.strftime('%Y-%m-%d')] = count
            
        analytics_data[flipbook.id] = {
            'title': flipbook.title,
            'total_views': total_views,
            'daily_views': views_data
        }
    
    return render_template('analytics.html', analytics_data=analytics_data)

@app.route('/track_page/<unique_id>', methods=['POST'])
def track_page(unique_id):
    flipbook = Flipbook.query.filter_by(unique_id=unique_id).first_or_404()
    page_number = request.json.get('page_number')
    
    if page_number is not None:
        page_view = PageView.query.filter_by(
            flipbook_id=flipbook.id,
            ip_address=request.remote_addr
        ).order_by(PageView.id.desc()).first()
        
        if page_view:
            page_view.page_number = page_number
            db.session.commit()
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    
    # Configure server to run on all interfaces with proper host binding
    app.run(
        host='0.0.0.0',  # Bind to all interfaces
        port=port,
        debug=False      # Disable debug mode for security
    )
