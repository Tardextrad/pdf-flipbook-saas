from app import app, db, login_manager
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Flipbook
from forms import LoginForm, RegisterForm, UploadForm
from utils import allowed_file, process_pdf, generate_unique_filename
from werkzeug.utils import secure_filename
import os

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
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
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
            
            logo_filename = None
            if form.logo.data:
                logo = form.logo.data
                logo_filename = generate_unique_filename(secure_filename(logo.filename))
                logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
                logo.save(logo_path)
            
            try:
                output_dir = os.path.join(app.config['UPLOAD_FOLDER'], filename.rsplit('.', 1)[0])
                os.makedirs(output_dir, exist_ok=True)
                process_pdf(filepath, output_dir)
                
                flipbook = Flipbook(
                    title=form.title.data,
                    filename=filename,
                    background_color=form.background_color.data,
                    logo_filename=logo_filename,
                    custom_css=form.custom_css.data,
                    user_id=current_user.id
                )
                db.session.add(flipbook)
                db.session.commit()
                flash('Flipbook created successfully!')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Error processing PDF: {str(e)}')
        else:
            flash('Invalid file format. Please upload a PDF file.')
    return render_template('upload.html', form=form)

@app.route('/viewer/<unique_id>')
def viewer(unique_id):
    flipbook = Flipbook.query.filter_by(unique_id=unique_id).first_or_404()
    return render_template('viewer.html', flipbook=flipbook)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
