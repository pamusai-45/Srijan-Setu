from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import current_user, login_required
from sqlalchemy import func
from app import role_required, db
from app.government import government_bp
from app.models import Challenge, ChallengeMedia, StatusHistory, University, ChallengeAssignment, Project, Milestone, Notification, User

def calculate_university_match(challenge, university):
    """Calculate an intelligent match score (0-100%) between a challenge and a university."""
    score = 30  # Baseline accreditation score

    # Domain expertise match
    domains = [d.strip().lower() for d in university.domains_of_expertise.split(',')]
    if challenge.domain.lower() in domains:
        score += 45
    elif any(word in university.domains_of_expertise.lower() for word in challenge.domain.lower().split()):
        score += 25

    # District proximity
    if challenge.district.lower() in university.district.lower() or university.district.lower() in challenge.district.lower():
        score += 15

    # Workload balance (fewer active projects = higher readiness)
    if university.active_workload <= 2:
        score += 10
    elif university.active_workload <= 4:
        score += 5

    return min(99, score)

@government_bp.route('/')
@government_bp.route('/overview')
@login_required
@role_required('government')
def overview():
    now_time = datetime.utcnow()

    # 1. Real summary card metrics
    total_challenges = Challenge.query.count()
    pending_validation = Challenge.query.filter(Challenge.status.in_(['Submitted', 'Under Review'])).count()
    validated_awaiting_allocation = Challenge.query.filter_by(status='Validated').count()
    assigned = Challenge.query.filter(Challenge.status.in_(['University Assigned', 'Accepted', 'Proposal Submitted'])).count()
    active_projects = Project.query.filter_by(status='Active').count()
    completed = Challenge.query.filter_by(status='Completed').count()

    # Distinct districts with submissions
    distinct_districts_count = db.session.query(func.count(func.distinct(Challenge.district))).scalar() or 0

    # 2. Action Required items
    pending_validation_challenges = Challenge.query.filter(
        Challenge.status.in_(['Submitted', 'Under Review'])
    ).order_by(
        db.case((Challenge.severity == 'Critical', 1), (Challenge.severity == 'High', 2), else_=3),
        Challenge.created_at.desc()
    ).all()

    validated_allocation_challenges = Challenge.query.filter_by(status='Validated').order_by(
        Challenge.created_at.desc()
    ).all()

    # Overdue projects and milestones
    overdue_milestones = Milestone.query.join(Project).filter(
        Milestone.deadline != None,
        Milestone.deadline < now_time,
        Milestone.status.in_(['Pending', 'In Progress'])
    ).all()
    overdue_milestone_project_ids = set(m.project_id for m in overdue_milestones)
    overdue_completion_projects = Project.query.filter(
        Project.status == 'Active',
        Project.expected_completion != None,
        Project.expected_completion < now_time
    ).all()
    all_overdue_project_ids = overdue_milestone_project_ids.union(p.id for p in overdue_completion_projects)
    overdue_projects = Project.query.filter(Project.id.in_(all_overdue_project_ids)).all() if all_overdue_project_ids else []
    overdue_projects_count = len(overdue_projects)

    # Clarification responses / requests
    clarification_challenges = Challenge.query.filter(Challenge.status == 'Clarification Required').order_by(
        Challenge.updated_at.desc()
    ).all()
    clarification_count = len(clarification_challenges)

    # 3. Chart 1: Domain distribution
    domain_counts = db.session.query(
        Challenge.domain, func.count(Challenge.id)
    ).group_by(Challenge.domain).all()
    domain_labels = [d[0] for d in domain_counts]
    domain_values = [d[1] for d in domain_counts]

    # 4. Chart 2: Status distribution
    status_counts = db.session.query(
        Challenge.status, func.count(Challenge.id)
    ).group_by(Challenge.status).all()
    status_labels = [s[0] for s in status_counts]
    status_values = [s[1] for s in status_counts]

    # District counts (for district analytics)
    district_counts = db.session.query(
        Challenge.district, func.count(Challenge.id)
    ).group_by(Challenge.district).order_by(func.count(Challenge.id).desc()).limit(5).all()
    district_labels = [d[0] for d in district_counts]
    district_values = [d[1] for d in district_counts]

    # 5. Project Lifecycle Funnel (Ordered sequence)
    lifecycle_labels = ['Submitted', 'Under Review', 'Validated', 'Assigned', 'In Progress', 'Pilot Testing', 'Completed']
    lifecycle_counts = [
        Challenge.query.filter_by(status='Submitted').count(),
        Challenge.query.filter_by(status='Under Review').count(),
        Challenge.query.filter_by(status='Validated').count(),
        Challenge.query.filter(Challenge.status.in_(['University Assigned', 'Accepted', 'Proposal Submitted'])).count(),
        Challenge.query.filter(Challenge.status.in_(['In Progress', 'Prototype Ready'])).count(),
        Challenge.query.filter_by(status='Pilot Testing').count(),
        Challenge.query.filter_by(status='Completed').count(),
    ]

    # 6. Monthly Submission Trend & Growth Comparison
    all_chals_dates = [c.created_at for c in Challenge.query.all() if c.created_at]
    trend_months = []
    curr_y = now_time.year
    curr_m = now_time.month
    for i in range(5, -1, -1):
        m = curr_m - i
        y = curr_y
        while m <= 0:
            m += 12
            y -= 1
        trend_months.append((y, m))

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    trend_labels = [f"{month_names[m-1]}" for y, m in trend_months]
    trend_values = []
    for y, m in trend_months:
        cnt = sum(1 for dt in all_chals_dates if dt.year == y and dt.month == m)
        trend_values.append(cnt)

    curr_month_val = trend_values[-1]
    prev_month_val = trend_values[-2] if len(trend_values) > 1 else 0
    if prev_month_val > 0:
        pct_change = round(((curr_month_val - prev_month_val) / prev_month_val) * 100)
        if pct_change > 0:
            trend_comparison = f"+{pct_change}% from previous month"
            trend_direction = "up"
        elif pct_change < 0:
            trend_comparison = f"{pct_change}% from previous month"
            trend_direction = "down"
        else:
            trend_comparison = "0% from previous month"
            trend_direction = "neutral"
    else:
        if curr_month_val > 0:
            trend_comparison = f"+{curr_month_val * 100}% from previous month"
            trend_direction = "up"
        else:
            trend_comparison = "0% from previous month"
            trend_direction = "neutral"

    # 7. Priority and Delay Alerts Table
    seen_challenge_ids = set()
    priority_delay_alerts = []

    # Overdue milestone alerts
    for ms in overdue_milestones:
        chal = ms.project.challenge if ms.project else None
        if chal and chal.id not in seen_challenge_ids:
            seen_challenge_ids.add(chal.id)
            days_overdue = (now_time - ms.deadline).days if ms.deadline else 0
            owner = ms.project.university.name if ms.project and ms.project.university else 'Academic Partner'
            priority_delay_alerts.append({
                'code': chal.code,
                'title': chal.title,
                'district': chal.district,
                'priority_delay': f"Overdue ({days_overdue}d)" if days_overdue > 0 else "Milestone Overdue",
                'is_overdue': True,
                'current_owner': owner,
                'action_url': url_for('government.project_monitoring'),
                'action_label': 'Review Project'
            })

    # High & Critical challenges needing review
    high_priority_chals = Challenge.query.filter(
        Challenge.severity.in_(['Critical', 'High']),
        ~Challenge.status.in_(['Completed', 'Rejected'])
    ).order_by(
        db.case((Challenge.severity == 'Critical', 1), else_=2),
        Challenge.created_at.desc()
    ).all()

    for chal in high_priority_chals:
        if chal.id not in seen_challenge_ids:
            seen_challenge_ids.add(chal.id)
            if chal.status in ['Submitted', 'Under Review']:
                owner = "Validation Desk"
                action_url = url_for('government.validation_queue')
                action_label = "Validate"
            elif chal.status == 'Validated':
                owner = "Allocation Cell"
                action_url = url_for('government.university_allocation')
                action_label = "Allocate"
            elif chal.status == 'Clarification Required':
                owner = "Citizen Reporter"
                action_url = url_for('government.all_challenges', status='Clarification Required')
                action_label = "Review"
            elif chal.assigned_university:
                owner = chal.assigned_university.name
                action_url = url_for('government.project_monitoring')
                action_label = "Inspect"
            else:
                owner = "District Nodal Officer"
                action_url = url_for('government.all_challenges')
                action_label = "Inspect"

            priority_delay_alerts.append({
                'code': chal.code,
                'title': chal.title,
                'district': chal.district,
                'priority_delay': chal.severity,
                'is_overdue': False,
                'current_owner': owner,
                'action_url': action_url,
                'action_label': action_label
            })

    priority_delay_alerts = priority_delay_alerts[:8]

    # Keep compatibility with existing templates/tests
    pending_review = pending_validation
    validated = validated_awaiting_allocation

    return render_template(
        'government/overview.html',
        total_challenges=total_challenges,
        pending_validation=pending_validation,
        pending_review=pending_review,
        validated=validated,
        validated_awaiting_allocation=validated_awaiting_allocation,
        assigned=assigned,
        active_projects=active_projects,
        completed=completed,
        distinct_districts_count=distinct_districts_count,
        pending_validation_challenges=pending_validation_challenges,
        validated_allocation_challenges=validated_allocation_challenges,
        overdue_projects=overdue_projects,
        overdue_projects_count=overdue_projects_count,
        clarification_challenges=clarification_challenges,
        clarification_count=clarification_count,
        district_labels=district_labels,
        district_values=district_values,
        domain_labels=domain_labels,
        domain_values=domain_values,
        status_labels=status_labels,
        status_values=status_values,
        lifecycle_labels=lifecycle_labels,
        lifecycle_counts=lifecycle_counts,
        trend_labels=trend_labels,
        trend_values=trend_values,
        trend_comparison=trend_comparison,
        trend_direction=trend_direction,
        priority_delay_alerts=priority_delay_alerts
    )

@government_bp.route('/validation')
@login_required
@role_required('government')
def validation_queue():
    # Show challenges requiring review
    queue = Challenge.query.filter(
        Challenge.status.in_(['Submitted', 'Under Review', 'Clarification Required'])
    ).order_by(
        # Critical severity first
        db.case(
            (Challenge.severity == 'Critical', 1),
            (Challenge.severity == 'High', 2),
            (Challenge.severity == 'Medium', 3),
            else_=4
        ),
        Challenge.created_at.asc()
    ).all()

    return render_template('government/validation_queue.html', queue=queue)

@government_bp.route('/validate/<int:challenge_id>', methods=['POST'])
@login_required
@role_required('government')
def validate_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    action = request.form.get('action')  # 'validate', 'reject', 'clarification'
    notes = request.form.get('notes', '').strip()
    category = request.form.get('category', challenge.domain).strip()
    priority = request.form.get('priority', challenge.priority).strip()

    old_status = challenge.status

    if action == 'validate':
        challenge.status = 'Validated'
        challenge.priority = priority
        challenge.category_assigned = category
        challenge.validation_notes = notes
        flash_msg = f"Challenge {challenge.code} has been successfully VALIDATED."
        notif_msg = f"Your challenge '{challenge.title}' has been validated by authorities and queued for university allocation."
        notif_cat = 'success'

    elif action == 'reject':
        challenge.status = 'Rejected'
        challenge.validation_notes = notes
        flash_msg = f"Challenge {challenge.code} has been REJECTED."
        notif_msg = f"Your challenge '{challenge.title}' was reviewed and not accepted for state intervention. Reason: {notes}"
        notif_cat = 'danger'

    elif action == 'clarification':
        challenge.status = 'Clarification Required'
        challenge.validation_notes = notes
        flash_msg = f"Clarification requested for challenge {challenge.code}."
        notif_msg = f"Authorities requested additional clarification on your challenge '{challenge.title}': {notes}"
        notif_cat = 'warning'
    else:
        flash('Invalid action specified.', 'danger')
        return redirect(url_for('government.validation_queue'))

    # Record history
    history = StatusHistory(
        challenge_id=challenge.id,
        old_status=old_status,
        new_status=challenge.status,
        updated_by_id=current_user.id,
        notes=notes or f"Status updated to {challenge.status} by {current_user.full_name}"
    )
    db.session.add(history)

    # Notify citizen
    notif = Notification(
        user_id=challenge.created_by_id,
        title=f"Challenge Status: {challenge.status}",
        message=notif_msg,
        link=url_for('citizen.challenge_detail', challenge_id=challenge.id),
        category=notif_cat
    )
    db.session.add(notif)

    db.session.commit()
    flash(flash_msg, 'success' if action == 'validate' else 'info')
    return redirect(url_for('government.validation_queue'))

@government_bp.route('/challenges')
@login_required
@role_required('government')
def all_challenges():
    query = Challenge.query

    status_filter = request.args.get('status', '').strip()
    domain_filter = request.args.get('domain', '').strip()
    district_filter = request.args.get('district', '').strip()
    severity_filter = request.args.get('severity', '').strip()
    priority_filter = request.args.get('priority', '').strip()
    search_query = request.args.get('q', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    if status_filter:
        query = query.filter(Challenge.status == status_filter)
    if domain_filter:
        query = query.filter(Challenge.domain == domain_filter)
    if district_filter:
        query = query.filter(Challenge.district == district_filter)
    if severity_filter:
        query = query.filter(Challenge.severity == severity_filter)
    if priority_filter:
        query = query.filter(Challenge.priority == priority_filter)
    if date_from:
        try:
            df = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Challenge.created_at >= df)
        except ValueError:
            pass
    if date_to:
        try:
            dt = datetime.strptime(date_to, '%Y-%m-%d')
            from datetime import timedelta
            query = query.filter(Challenge.created_at < dt + timedelta(days=1))
        except ValueError:
            pass
    if search_query:
        query = query.filter(
            (Challenge.title.ilike(f'%{search_query}%')) |
            (Challenge.code.ilike(f'%{search_query}%')) |
            (Challenge.district.ilike(f'%{search_query}%'))
        )

    challenges = query.order_by(Challenge.created_at.desc()).all()
    return render_template(
        'government/all_challenges.html',
        challenges=challenges,
        selected_status=status_filter,
        selected_domain=domain_filter,
        selected_district=district_filter,
        selected_severity=severity_filter,
        selected_priority=priority_filter,
        search_query=search_query,
        date_from=date_from,
        date_to=date_to
    )

@government_bp.route('/allocation')
@login_required
@role_required('government')
def university_allocation():
    # Validated challenges without active assignment
    validated_challenges = Challenge.query.filter_by(status='Validated').all()
    universities = University.query.all()

    # Pre-calculate match scores for each validated challenge
    recommendations = {}
    for chal in validated_challenges:
        uni_matches = []
        for uni in universities:
            score = calculate_university_match(chal, uni)
            uni_matches.append({
                'university': uni,
                'match_score': score
            })
        # Sort by match score descending
        uni_matches.sort(key=lambda x: x['match_score'], reverse=True)
        recommendations[chal.id] = uni_matches

    # Also show already assigned ones for reference
    assigned_challenges = Challenge.query.filter(
        Challenge.status.in_(['University Assigned', 'Accepted', 'Proposal Submitted', 'In Progress', 'Prototype Ready', 'Pilot Testing', 'Completed'])
    ).order_by(Challenge.updated_at.desc()).all()

    return render_template(
        'government/university_allocation.html',
        validated_challenges=validated_challenges,
        universities=universities,
        recommendations=recommendations,
        assigned_challenges=assigned_challenges
    )

@government_bp.route('/allocate/<int:challenge_id>', methods=['POST'])
@login_required
@role_required('government')
def allocate_university(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    university_id = request.form.get('university_id')
    notes = request.form.get('notes', '').strip()

    if not university_id:
        flash('Please select a university to assign.', 'danger')
        return redirect(url_for('government.university_allocation'))

    university = University.query.get_or_404(int(university_id))

    old_status = challenge.status
    challenge.status = 'University Assigned'

    # Create assignment record
    assignment = ChallengeAssignment(
        challenge_id=challenge.id,
        university_id=university.id,
        assigned_by_id=current_user.id,
        status='Assigned',
        notes=notes
    )
    db.session.add(assignment)

    # Increment university workload
    university.active_workload += 1

    # Status history
    history = StatusHistory(
        challenge_id=challenge.id,
        old_status=old_status,
        new_status='University Assigned',
        updated_by_id=current_user.id,
        notes=f"Assigned to {university.name}. Notes: {notes}"
    )
    db.session.add(history)

    # Notify university representatives
    uni_users = User.query.filter_by(university_id=university.id).all()
    for u in uni_users:
        notif = Notification(
            user_id=u.id,
            title="New Challenge Assigned",
            message=f"Government assigned challenge '{challenge.title}' ({challenge.code}) to your institution.",
            link=url_for('university.assigned_challenges'),
            category='info'
        )
        db.session.add(notif)

    # Notify citizen
    citizen_notif = Notification(
        user_id=challenge.created_by_id,
        title="University Assigned",
        message=f"Your challenge '{challenge.title}' has been assigned to {university.name} for technical solution development.",
        link=url_for('citizen.challenge_detail', challenge_id=challenge.id),
        category='success'
    )
    db.session.add(citizen_notif)

    db.session.commit()
    flash(f"Challenge '{challenge.title}' assigned to {university.name} successfully!", 'success')
    return redirect(url_for('government.university_allocation'))

@government_bp.route('/projects')
@login_required
@role_required('government')
def project_monitoring():
    query = Project.query

    status_filter = request.args.get('status', '').strip()
    university_filter = request.args.get('university_id', '').strip()
    search_query = request.args.get('q', '').strip()

    if status_filter:
        query = query.filter(Project.status == status_filter)
    if university_filter:
        query = query.filter(Project.university_id == int(university_filter))
    if search_query:
        query = query.filter(Project.title.ilike(f'%{search_query}%'))

    projects = query.order_by(Project.created_at.desc()).all()
    universities = University.query.all()

    return render_template(
        'government/project_monitoring.html',
        projects=projects,
        universities=universities,
        selected_status=status_filter,
        selected_university=university_filter,
        search_query=search_query
    )

@government_bp.route('/analytics')
@login_required
@role_required('government')
def analytics():
    # District challenge counts
    district_counts = db.session.query(
        Challenge.district, func.count(Challenge.id)
    ).group_by(Challenge.district).order_by(func.count(Challenge.id).desc()).all()

    # Domain breakdown
    domain_counts = db.session.query(
        Challenge.domain, func.count(Challenge.id)
    ).group_by(Challenge.domain).all()

    # Severity distribution
    severity_counts = db.session.query(
        Challenge.severity, func.count(Challenge.id)
    ).group_by(Challenge.severity).all()

    # University workloads & project completions
    universities = University.query.all()

    return render_template(
        'government/analytics.html',
        district_counts=district_counts,
        domain_counts=domain_counts,
        severity_counts=severity_counts,
        universities=universities
    )

@government_bp.route('/notifications')
@login_required
@role_required('government')
def notifications():
    notifications_list = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    for n in notifications_list:
        if not n.is_read:
            n.is_read = True
    db.session.commit()
    return render_template('government/notifications.html', notifications=notifications_list)
