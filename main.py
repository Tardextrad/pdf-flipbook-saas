from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func
from app import db, login_manager, logger
from models import User, Flipbook, PageView
from forms import LoginForm, RegisterForm, UploadForm
from utils import allowed_file, process_pdf, generate_unique_filename
import os
from datetime import datetime, timedelta

def init_routes(app):
    @login_manager.user_loader
    def load_user(id):
        try:
            return db.session.get(User, int(id))
        except Exception as e:
            logger.error(f"Error loading user: {str(e)}")
            return None

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Logged in successfully.', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            flash('Invalid email or password.', 'error')
        return render_template('login.html', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegisterForm()
        if form.validate_on_submit():
            try:
                user = User()
                user.username = form.username.data
                user.email = form.email.data
                user.set_password(form.password.data)
                
                db.session.add(user)
                db.session.commit()
                
                flash('Registration successful! Please login with your credentials.', 'success')
                return redirect(url_for('login'))
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Registration error: {str(e)}")
                flash('An error occurred during registration. Please try again.', 'error')
        
        return render_template('register.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
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
        
        page_view = PageView()
        page_view.flipbook_id = flipbook.id
        page_view.ip_address = request.remote_addr
        
        db.session.add(page_view)
        db.session.commit()
        
        return render_template('viewer.html', flipbook=flipbook)

    @app.route('/embed/<unique_id>')
    def embed_viewer(unique_id):
        flipbook = Flipbook.query.filter_by(unique_id=unique_id).first_or_404()
        
        page_view = PageView()
        page_view.flipbook_id = flipbook.id
        page_view.ip_address = request.remote_addr
        
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
        if request.json and 'page_number' in request.json:
            page_number = request.json['page_number']
            
            if page_number is not None:
                page_view = PageView.query.filter_by(
                    flipbook_id=flipbook.id,
                    ip_address=request.remote_addr
                ).order_by(PageView.id.desc()).first()
                
                if page_view:
                    page_view.page_number = page_number
                    db.session.commit()
        
        return jsonify({'status': 'success'})
