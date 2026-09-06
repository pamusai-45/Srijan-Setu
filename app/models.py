from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

CHALLENGE_STATUSES = [
    'Submitted',
    'Under Review',
    'Clarification Required',
    'Validated',
    'Rejected',
    'University Assigned',
    'Accepted',
    'Proposal Submitted',
    'In Progress',
    'Prototype Ready',
    'Pilot Testing',
    'Completed'
]

STATUS_COLORS = {
    'Submitted': 'secondary',
    'Under Review': 'info',
    'Clarification Required': 'warning',
    'Validated': 'primary',
    'Rejected': 'danger',
    'University Assigned': 'indigo',
    'Accepted': 'teal',
    'Proposal Submitted': 'cyan',
    'In Progress': 'primary',
    'Prototype Ready': 'mint',
    'Pilot Testing': 'warning',
    'Completed': 'success'
}

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'citizen', 'government', 'university'
    phone = db.Column(db.String(20), nullable=True)
    organization = db.Column(db.String(120), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(50), nullable=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    challenges = db.relationship('Challenge', backref='creator', lazy='dynamic', foreign_keys='Challenge.created_by_id')
    notifications = db.relationship('Notification', backref='recipient', lazy='dynamic', cascade='all, delete-orphan')
    university = db.relationship('University', backref=db.backref('representatives', lazy=True), foreign_keys=[university_id])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def initials(self):
        parts = self.full_name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        elif len(parts) == 1 and len(parts[0]) > 0:
            return parts[0][:2].upper()
        return "JG"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class University(db.Model):
    __tablename__ = 'universities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    district = db.Column(db.String(50), nullable=False)
    domains_of_expertise = db.Column(db.String(300), nullable=False)  # Comma-separated
    active_workload = db.Column(db.Integer, default=0)
    contact_email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    rating = db.Column(db.Float, default=4.8)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assignments = db.relationship('ChallengeAssignment', backref='university', lazy='dynamic')
    projects = db.relationship('Project', backref='university', lazy='dynamic')
    proposals = db.relationship('Proposal', backref='university', lazy='dynamic')

    @property
    def domains_list(self):
        return [d.strip() for d in self.domains_of_expertise.split(',') if d.strip()]

    def __repr__(self):
        return f"<University {self.name}>"


class Challenge(db.Model):
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    block = db.Column(db.String(50), nullable=True)
    village_city = db.Column(db.String(100), nullable=True)
    people_affected = db.Column(db.Integer, default=100)
    duration_months = db.Column(db.Integer, default=6)
    severity = db.Column(db.String(20), default='Medium')  # 'Low', 'Medium', 'High', 'Critical'
    address_text = db.Column(db.String(255), nullable=True)
    gps_coords = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), default='Submitted', index=True)
    priority = db.Column(db.String(20), default='Medium')  # 'Low', 'Medium', 'High', 'Critical'
    validation_notes = db.Column(db.Text, nullable=True)
    category_assigned = db.Column(db.String(100), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    media = db.relationship('ChallengeMedia', backref='challenge', lazy='dynamic', cascade='all, delete-orphan')
    history = db.relationship('StatusHistory', backref='challenge', lazy='dynamic', order_by='StatusHistory.created_at.desc()', cascade='all, delete-orphan')
    assignments = db.relationship('ChallengeAssignment', backref='challenge', lazy='dynamic', cascade='all, delete-orphan')
    project = db.relationship('Project', backref='challenge', uselist=False, cascade='all, delete-orphan')
    proposals = db.relationship('Proposal', backref='challenge', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def latest_assignment(self):
        return self.assignments.order_by(ChallengeAssignment.assigned_at.desc()).first()

    @property
    def assigned_university(self):
        assignment = self.latest_assignment
        if assignment and assignment.university:
            return assignment.university
        return None

    @property
    def status_badge_class(self):
        mapping = {
            'Submitted': 'badge-status-submitted',
            'Under Review': 'badge-status-review',
            'Clarification Required': 'badge-status-clarification',
            'Validated': 'badge-status-validated',
            'Rejected': 'badge-status-rejected',
            'University Assigned': 'badge-status-assigned',
            'Accepted': 'badge-status-accepted',
            'Proposal Submitted': 'badge-status-proposal',
            'In Progress': 'badge-status-progress',
            'Prototype Ready': 'badge-status-prototype',
            'Pilot Testing': 'badge-status-pilot',
            'Completed': 'badge-status-completed'
        }
        return mapping.get(self.status, 'badge-status-default')

    @property
    def severity_badge_class(self):
        mapping = {
            'Critical': 'badge-severity-critical',
            'High': 'badge-severity-high',
            'Medium': 'badge-severity-medium',
            'Low': 'badge-severity-low'
        }
        return mapping.get(self.severity, 'badge-severity-medium')

    @property
    def progress_percentage(self):
        order = [
            'Submitted', 'Under Review', 'Validated', 'University Assigned',
            'Accepted', 'Proposal Submitted', 'In Progress',
            'Prototype Ready', 'Pilot Testing', 'Completed'
        ]
        if self.status in order:
            idx = order.index(self.status)
            return int(((idx + 1) / len(order)) * 100)
        elif self.status == 'Rejected':
            return 100
        elif self.status == 'Clarification Required':
            return 20
        return 10

    def __repr__(self):
        return f"<Challenge {self.code}: {self.title}>"


class ChallengeMedia(db.Model):
    __tablename__ = 'challenge_media'

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), default='image')  # 'image', 'document'
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_image(self):
        return self.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))

    def __repr__(self):
        return f"<ChallengeMedia {self.original_name}>"


class StatusHistory(db.Model):
    __tablename__ = 'status_history'

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    old_status = db.Column(db.String(50), nullable=True)
    new_status = db.Column(db.String(50), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    updater = db.relationship('User', foreign_keys=[updated_by_id])

    def __repr__(self):
        return f"<StatusHistory {self.old_status} -> {self.new_status}>"


class ChallengeAssignment(db.Model):
    __tablename__ = 'challenge_assignments'

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='Assigned')  # 'Assigned', 'Accepted', 'Declined', 'Clarification Requested'
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    response_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    decline_reason = db.Column(db.Text, nullable=True)

    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id])

    def __repr__(self):
        return f"<ChallengeAssignment Challenge:{self.challenge_id} Uni:{self.university_id} ({self.status})>"


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), unique=True, nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    stage = db.Column(db.String(50), default='Planning')  # 'Planning', 'Proposal Review', 'R&D In Progress', 'Prototype Ready', 'Field Pilot', 'Completed'
    progress_percent = db.Column(db.Integer, default=15)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_completion = db.Column(db.DateTime, nullable=True)
    budget = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default='Active')  # 'Active', 'On Hold', 'Completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    team_members = db.relationship('TeamMember', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    milestones = db.relationship('Milestone', backref='project', lazy='dynamic', order_by='Milestone.order_index.asc()', cascade='all, delete-orphan')

    def recalculate_progress(self):
        total = self.milestones.count()
        if total == 0:
            return self.progress_percent
        completed = self.milestones.filter_by(status='Completed').count()
        in_progress = self.milestones.filter_by(status='In Progress').count()
        # Each completed is full weight, in_progress is half weight
        computed = int(((completed + (in_progress * 0.5)) / total) * 100)
        self.progress_percent = min(100, max(5, computed))
        return self.progress_percent

    def __repr__(self):
        return f"<Project {self.title} ({self.progress_percent}%)>"


class TeamMember(db.Model):
    __tablename__ = 'team_members'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(100), nullable=False)  # 'Principal Investigator', 'Lead Student Engineer', etc.
    department = db.Column(db.String(100), nullable=False)
    member_type = db.Column(db.String(30), default='Faculty')  # 'Faculty', 'Student', 'Researcher'
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TeamMember {self.name} ({self.role})>"


class Proposal(db.Model):
    __tablename__ = 'proposals'

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    approach = db.Column(db.Text, nullable=False)
    duration_months = db.Column(db.Integer, default=6)
    estimated_budget = db.Column(db.Float, default=250000.0)
    resources_needed = db.Column(db.Text, nullable=True)
    expected_impact = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='Draft')  # 'Draft', 'Submitted', 'Approved', 'Revision Requested'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Proposal {self.title} ({self.status})>"


class Milestone(db.Model):
    __tablename__ = 'milestones'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deliverable = db.Column(db.String(200), nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(30), default='Pending')  # 'Pending', 'In Progress', 'Completed'
    completed_at = db.Column(db.DateTime, nullable=True)
    order_index = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<Milestone {self.title} ({self.status})>"


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), default='info')  # 'info', 'success', 'warning', 'danger'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notification {self.title} (Read:{self.is_read})>"
