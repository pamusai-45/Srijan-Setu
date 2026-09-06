import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import current_user, login_required
from app import role_required, db
from app.citizen import citizen_bp
from app.models import Challenge, ChallengeMedia, StatusHistory, Notification, User

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@citizen_bp.route('/')
@citizen_bp.route('/overview')
@login_required
@role_required('citizen')
def overview():
    user_challenges = Challenge.query.filter_by(created_by_id=current_user.id)
    
    total_submitted = user_challenges.count()
    under_review = user_challenges.filter(Challenge.status.in_(['Submitted', 'Under Review', 'Clarification Required', 'Validated'])).count()
    assigned = user_challenges.filter(Challenge.status.in_(['University Assigned', 'Accepted', 'Proposal Submitted'])).count()
    in_progress = user_challenges.filter(Challenge.status.in_(['In Progress', 'Prototype Ready', 'Pilot Testing'])).count()
    completed = user_challenges.filter_by(status='Completed').count()
    
    recent_challenges = user_challenges.order_by(Challenge.created_at.desc()).limit(5).all()
    latest_challenge = recent_challenges[0] if recent_challenges else None

    # Determine lifecycle stage for the citizen's latest challenge:
    # 1: Submission & Ground Evidence
    # 2: State Government Validation
    # 3: University Matching & Allocation
    # 4: R&D, Prototype & Field Pilot
    # 5: Field Deployment & Completed
    latest_stage = 1
    if latest_challenge:
        st = latest_challenge.status
        if st in ['Submitted', 'Under Review', 'Clarification Required']:
            latest_stage = 1
        elif st == 'Validated':
            latest_stage = 2
        elif st in ['University Assigned', 'Accepted', 'Proposal Submitted']:
            latest_stage = 3
        elif st in ['In Progress', 'Prototype Ready', 'Pilot Testing']:
            latest_stage = 4
        elif st == 'Completed':
            latest_stage = 5

    return render_template(
        'citizen/overview.html',
        total_submitted=total_submitted,
        under_review=under_review,
        assigned=assigned,
        in_progress=in_progress,
        completed=completed,
        recent_challenges=recent_challenges,
        latest_challenge=latest_challenge,
        latest_stage=latest_stage
    )

@citizen_bp.route('/submit', methods=['GET', 'POST'])
@login_required
@role_required('citizen')
def submit_challenge():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        domain = request.form.get('domain', '').strip()
        district = request.form.get('district', '').strip()
        block = request.form.get('block', '').strip()
        village_city = request.form.get('village_city', '').strip()
        
        try:
            people_affected = int(request.form.get('people_affected', 100))
        except (ValueError, TypeError):
            people_affected = 100

        try:
            duration_months = int(request.form.get('duration_months', 6))
        except (ValueError, TypeError):
            duration_months = 6

        severity = request.form.get('severity', 'Medium').strip()
        address_text = request.form.get('address_text', '').strip()
        gps_coords = request.form.get('gps_coords', '').strip()

        # Validation
        if not title or not description or not domain or not district:
            flash('Please fill in all mandatory fields (Title, Description, Domain, District).', 'danger')
            return render_template('citizen/submit_challenge.html')

        # Generate unique code like SS-2026-XXXX
        year = datetime.utcnow().year
        count = Challenge.query.count() + 1
        code = f"SS-{year}-{count:04d}"

        new_challenge = Challenge(
            code=code,
            title=title,
            description=description,
            domain=domain,
            district=district,
            block=block,
            village_city=village_city,
            people_affected=people_affected,
            duration_months=duration_months,
            severity=severity,
            address_text=address_text,
            gps_coords=gps_coords,
            status='Submitted',
            priority=severity,
            created_by_id=current_user.id
        )

        db.session.add(new_challenge)
        db.session.flush()

        # Initial Status History
        history = StatusHistory(
            challenge_id=new_challenge.id,
            old_status=None,
            new_status='Submitted',
            updated_by_id=current_user.id,
            notes='Challenge successfully submitted by citizen.'
        )
        db.session.add(history)

        # Handle File Uploads
        uploaded_files = request.files.getlist('media_files')
        for file in uploaded_files:
            if file and file.filename != '' and allowed_file(file.filename):
                original_name = secure_filename(file.filename)
                ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else ''
                unique_filename = f"{uuid.uuid4().hex[:12]}_{original_name}"
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(save_path)

                file_type = 'image' if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp'] else 'document'
                media = ChallengeMedia(
                    challenge_id=new_challenge.id,
                    filename=unique_filename,
                    original_name=original_name,
                    file_type=file_type
                )
                db.session.add(media)

        # Notify government users
        govt_users = User.query.filter_by(role='government').all()
        for g in govt_users:
            notif = Notification(
                user_id=g.id,
                title="New Challenge Submitted",
                message=f"New challenge '{title}' ({code}) in {district} requires review.",
                link=url_for('government.validation_queue'),
                category='info'
            )
            db.session.add(notif)

        # Notify citizen themselves
        user_notif = Notification(
            user_id=current_user.id,
            title="Challenge Submission Confirmed",
            message=f"Your challenge '{title}' has been recorded with ID {code} and is queued for verification.",
            link=url_for('citizen.challenge_detail', challenge_id=new_challenge.id),
            category='success'
        )
        db.session.add(user_notif)

        db.session.commit()
        flash(f"Challenge '{title}' ({code}) has been submitted successfully! Our authorities will review it shortly.", 'success')
        return redirect(url_for('citizen.challenge_detail', challenge_id=new_challenge.id))

    return render_template('citizen/submit_challenge.html')

@citizen_bp.route('/challenges')
@login_required
@role_required('citizen')
def my_challenges():
    query = Challenge.query.filter_by(created_by_id=current_user.id)

    status_filter = request.args.get('status', '').strip()
    domain_filter = request.args.get('domain', '').strip()
    search_query = request.args.get('q', '').strip()

    if status_filter:
        query = query.filter(Challenge.status == status_filter)
    if domain_filter:
        query = query.filter(Challenge.domain == domain_filter)
    if search_query:
        query = query.filter(
            (Challenge.title.ilike(f'%{search_query}%')) |
            (Challenge.code.ilike(f'%{search_query}%')) |
            (Challenge.district.ilike(f'%{search_query}%'))
        )

    challenges = query.order_by(Challenge.created_at.desc()).all()
    return render_template(
        'citizen/my_challenges.html',
        challenges=challenges,
        selected_status=status_filter,
        selected_domain=domain_filter,
        search_query=search_query
    )

@citizen_bp.route('/challenge/<int:challenge_id>')
@login_required
@role_required('citizen')
def challenge_detail(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    if challenge.created_by_id != current_user.id:
        abort(403)

    return render_template('citizen/challenge_detail.html', challenge=challenge)

@citizen_bp.route('/notifications')
@login_required
@role_required('citizen')
def notifications():
    notifications_list = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    # Mark all as read
    for n in notifications_list:
        if not n.is_read:
            n.is_read = True
    db.session.commit()
    return render_template('citizen/notifications.html', notifications=notifications_list)

@citizen_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('citizen')
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        district = request.form.get('district', '').strip()

        if full_name:
            current_user.full_name = full_name
        current_user.phone = phone
        current_user.district = district
        db.session.commit()
        flash('Your profile has been updated successfully.', 'success')
        return redirect(url_for('citizen.profile'))

    user_challenges_count = Challenge.query.filter_by(created_by_id=current_user.id).count()
    return render_template('citizen/profile.html', user_challenges_count=user_challenges_count)
