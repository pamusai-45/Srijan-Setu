import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, redirect, url_for, abort, flash, request
from flask_login import LoginManager, current_user
from app.config import Config
from app.models import db, User, Notification, Challenge, Milestone, ChallengeAssignment, CHALLENGE_STATUSES

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

JHARKHAND_DISTRICTS = [
    'Ranchi', 'Dhanbad', 'East Singhbhum (Jamshedpur)', 'Bokaro', 'Hazaribagh',
    'Deoghar', 'Giridih', 'Palamu', 'Dumka', 'West Singhbhum (Chaibasa)',
    'Ramgarh', 'Saraikela Kharsawan', 'Latehar', 'Garhwa', 'Chatra',
    'Godda', 'Sahebganj', 'Pakur', 'Jamtara', 'Khunti', 'Gumla',
    'Simdega', 'Lohardaga', 'Koderma'
]

DOMAINS = [
    'Water & Sanitation',
    'Agriculture & Forest Produce',
    'Renewable Energy',
    'Healthcare & Nutrition',
    'Infrastructure & Connectivity',
    'Education & Skill Development',
    'Mining & Environment'
]

def role_required(roles):
    """Decorator to enforce role-based access control."""
    if isinstance(roles, str):
        roles = [roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload & instance folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    instance_path = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
    if instance_path:
        os.makedirs(instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.citizen.routes import citizen_bp
    from app.government.routes import government_bp
    from app.university.routes import university_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(citizen_bp, url_prefix='/citizen')
    app.register_blueprint(government_bp, url_prefix='/government')
    app.register_blueprint(university_bp, url_prefix='/university')

    # Root redirect
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == 'citizen':
                return redirect(url_for('citizen.overview'))
            elif current_user.role == 'government':
                return redirect(url_for('government.overview'))
            elif current_user.role == 'university':
                return redirect(url_for('university.overview'))
        return redirect(url_for('auth.login'))

    # Error handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('404.html', error_msg="Internal server error"), 500

    # Custom Jinja filters
    @app.template_filter('format_date')
    def format_date(value, format='%d %b %Y'):
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except Exception:
                return value
        return value.strftime(format)

    @app.template_filter('inr_format')
    def inr_format(value):
        try:
            val = float(value)
            return f"₹{val:,.2f}"
        except (ValueError, TypeError):
            return f"₹{value}"

    @app.template_filter('time_ago')
    def time_ago(value):
        if not value:
            return ""
        now = datetime.utcnow()
        diff = now - value
        seconds = diff.total_seconds()
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days}d ago"
        else:
            return value.strftime('%d %b %Y')

    # Context processors
    @app.context_processor
    def inject_global_vars():
        unread_count = 0
        user_notifications = []
        gov_pending_count = 0
        gov_overdue_milestones_count = 0
        uni_new_assignments_count = 0
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
            user_notifications = Notification.query.filter_by(
                user_id=current_user.id
            ).order_by(Notification.created_at.desc()).limit(5).all()
            if current_user.role == 'government':
                gov_pending_count = Challenge.query.filter(
                    Challenge.status.in_(['Submitted', 'Under Review'])
                ).count()
                now_time = datetime.utcnow()
                gov_overdue_milestones_count = Milestone.query.filter(
                    Milestone.deadline != None,
                    Milestone.deadline < now_time,
                    Milestone.status.in_(['Pending', 'In Progress'])
                ).count()
            elif current_user.role == 'university' and current_user.university_id:
                uni_new_assignments_count = ChallengeAssignment.query.filter_by(
                    university_id=current_user.university_id, status='Assigned'
                ).count()

        is_dev = app.debug or (os.environ.get('FLASK_DEBUG') in ['1', 'true', 'True']) or (os.environ.get('FLASK_ENV') == 'development')

        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': user_notifications,
            'gov_pending_count': gov_pending_count,
            'gov_overdue_milestones_count': gov_overdue_milestones_count,
            'uni_new_assignments_count': uni_new_assignments_count,
            'current_year': datetime.utcnow().year,
            'jharkhand_districts': JHARKHAND_DISTRICTS,
            'domains_list': DOMAINS,
            'challenge_statuses': CHALLENGE_STATUSES,
            'is_dev_mode': is_dev
        }

    return app
