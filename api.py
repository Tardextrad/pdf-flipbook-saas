from flask import Blueprint, jsonify, request
from models import User, Flipbook, PageView
from app import db
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import func
from functools import wraps
import jwt
import os

api = Blueprint('api', __name__)

def generate_access_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(minutes=15)  # Short-lived access token
    }
    return jwt.encode(payload, os.environ.get('FLASK_SECRET_KEY'), algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            data = jwt.decode(token, os.environ.get('FLASK_SECRET_KEY'), algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
            return f(current_user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired', 'code': 'TOKEN_EXPIRED'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
    return decorated

@api.route('/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        access_token = generate_access_token(user)
        refresh_token = user.generate_refresh_token()
        db.session.commit()
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    return jsonify({'error': 'Invalid credentials'}), 401

@api.route('/auth/refresh', methods=['POST'])
def refresh_token():
    data = request.get_json()
    if not data or 'refresh_token' not in data:
        return jsonify({'error': 'Refresh token is required'}), 400
        
    refresh_token = data['refresh_token']
    user = User.query.filter_by(refresh_token=refresh_token).first()
    
    if not user or not user.is_refresh_token_valid(refresh_token):
        return jsonify({'error': 'Invalid or expired refresh token'}), 401
        
    # Generate new access token
    access_token = generate_access_token(user)
    
    # Optionally rotate refresh token for better security
    new_refresh_token = user.generate_refresh_token()
    db.session.commit()
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': new_refresh_token
    })

@api.route('/auth/logout', methods=['POST'])
@token_required
def api_logout(current_user):
    current_user.revoke_refresh_token()
    db.session.commit()
    return jsonify({'message': 'Successfully logged out'})

@api.route('/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
        
    try:
        user = User()
        user.username = data['username']
        user.email = data['email']
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        access_token = generate_access_token(user)
        refresh_token = user.generate_refresh_token()
        db.session.commit()
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/flipbooks', methods=['GET'])
@token_required
def list_flipbooks(current_user):
    flipbooks = Flipbook.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'flipbooks': [{
            'id': f.id,
            'title': f.title,
            'unique_id': f.unique_id,
            'created_at': f.created_at.isoformat(),
            'page_count': f.page_count,
            'view_count': len(f.views)
        } for f in flipbooks]
    })

@api.route('/flipbooks/<unique_id>', methods=['GET'])
@token_required
def get_flipbook(current_user, unique_id):
    flipbook = Flipbook.query.filter_by(unique_id=unique_id).first_or_404()
    if flipbook.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized access'}), 403
    return jsonify({
        'id': flipbook.id,
        'title': flipbook.title,
        'unique_id': flipbook.unique_id,
        'created_at': flipbook.created_at.isoformat(),
        'page_count': flipbook.page_count,
        'pages': [
            f'/static/uploads/{flipbook.filename.rsplit(".", 1)[0]}/page_{i+1}.jpg'
            for i in range(flipbook.page_count)
        ]
    })

@api.route('/analytics', methods=['GET'])
@token_required
def get_analytics(current_user):
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
            
        analytics_data[str(flipbook.id)] = {
            'title': flipbook.title,
            'total_views': total_views,
            'daily_views': views_data
        }
    
    return jsonify(analytics_data)
