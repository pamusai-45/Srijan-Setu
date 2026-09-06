from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import current_user, login_required
from app import role_required, db
from app.university import university_bp
from app.models import (
    Challenge, ChallengeAssignment, Project, TeamMember, Proposal,
    Milestone, Notification, User, University, StatusHistory
)

def get_current_university():
    """Get the university associated with the current logged-in user, or default to the first one."""
    if current_user.university_id:
        uni = db.session.get(University, current_user.university_id)
        if uni:
            return uni
    return University.query.first()

@university_bp.route('/')
@university_bp.route('/overview')
@login_required
@role_required('university')
def overview():
    uni = get_current_university()
    if not uni:
        flash('No university profile linked.', 'warning')
        return redirect(url_for('auth.login'))

    now_time = datetime.utcnow()

    # 1. Six Dynamic Summary Cards (database-derived)
    new_assignments_count = ChallengeAssignment.query.filter_by(
        university_id=uni.id, status='Assigned'
    ).count()

    accepted_challenges_count = ChallengeAssignment.query.filter_by(
        university_id=uni.id, status='Accepted'
    ).count()

    all_projects = Project.query.filter_by(university_id=uni.id).order_by(Project.created_at.desc()).all()
    active_projects_count = sum(1 for p in all_projects if p.status == 'Active')
    completed_projects_count = sum(1 for p in all_projects if p.status == 'Completed')

    proposals_under_review_count = Proposal.query.filter_by(
        university_id=uni.id, status='Submitted'
    ).count()

    pending_milestones_count = Milestone.query.join(Project).filter(
        Project.university_id == uni.id,
        Milestone.status.in_(['Pending', 'In Progress'])
    ).count()

    # 2. Chart 1: Challenge Assignment Status (Doughnut)
    cnt_new = new_assignments_count
    cnt_acc = accepted_challenges_count
    cnt_dec = ChallengeAssignment.query.filter_by(university_id=uni.id, status='Declined').count()
    cnt_clar = ChallengeAssignment.query.filter_by(university_id=uni.id, status='Clarification Requested').count()
    assignment_status_labels = ['New', 'Accepted', 'Declined', 'Clarification Required']
    assignment_status_data = [cnt_new, cnt_acc, cnt_dec, cnt_clar]

    # 3. Chart 2: Active Project Progress (Horizontal Bar - Full Names without truncation)
    project_labels = [p.title for p in all_projects]
    project_progress = [p.progress_percent for p in all_projects]

    # 4. Chart 3: Monthly Research Activity (Line/Area for past 6 months)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
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

    all_proposals = Proposal.query.filter_by(university_id=uni.id).all()
    all_milestones = Milestone.query.join(Project).filter(Project.university_id == uni.id).all()

    monthly_activity_labels = []
    monthly_proposals_data = []
    monthly_milestones_data = []
    for y, m in trend_months:
        monthly_activity_labels.append(month_names[m - 1])
        prop_cnt = sum(1 for p in all_proposals if p.created_at and p.created_at.year == y and p.created_at.month == m)
        ms_cnt = sum(1 for ms in all_milestones if ms.completed_at and ms.completed_at.year == y and ms.completed_at.month == m)
        monthly_proposals_data.append(prop_cnt)
        monthly_milestones_data.append(ms_cnt)

    # 5. Action Required Section (4 compact actionable cards)
    proposals_action_count = Proposal.query.filter(
        Proposal.university_id == uni.id,
        Proposal.status.in_(['Draft', 'Revision Requested'])
    ).count()

    milestone_alerts_count = Milestone.query.join(Project).filter(
        Project.university_id == uni.id,
        Milestone.status.in_(['Pending', 'In Progress']),
        (Milestone.deadline != None) & ((Milestone.deadline < now_time) | (Milestone.deadline <= now_time + timedelta(days=14)))
    ).count()

    incomplete_teams_count = sum(
        1 for p in all_projects
        if p.team_members.count() < 3 or not any(tm.member_type == 'Faculty' for tm in p.team_members)
    )

    # 6. Active Projects Compact Cards (Maximum 3 projects)
    active_projects_query = Project.query.filter_by(university_id=uni.id).order_by(
        db.case((Project.status == 'Active', 1), else_=2),
        Project.created_at.desc()
    ).limit(3).all()

    active_projects_cards = []
    for proj in active_projects_query:
        faculty_mentor = None
        for tm in proj.team_members:
            if tm.member_type == 'Faculty' or 'Investigator' in tm.role:
                faculty_mentor = tm.name
                break
        if not faculty_mentor:
            faculty_member = proj.team_members.first()
            faculty_mentor = faculty_member.name if faculty_member else 'Dr. Sneha Minz'

        next_ms = proj.milestones.filter(Milestone.status != 'Completed').order_by(Milestone.deadline.asc()).first()

        active_projects_cards.append({
            'id': proj.id,
            'challenge_code': proj.challenge.code if proj.challenge else f'SS-2026-{proj.id:04d}',
            'title': proj.title,
            'domain': proj.challenge.domain if proj.challenge else 'Technology',
            'district': proj.challenge.district if proj.challenge else (uni.district or 'Ranchi'),
            'faculty_mentor': faculty_mentor,
            'team_members_count': proj.team_members.count(),
            'stage': proj.stage,
            'progress_percent': proj.progress_percent,
            'next_milestone_title': next_ms.title if next_ms else 'All milestones completed',
            'next_milestone_deadline': next_ms.deadline if next_ms else None,
            'status': proj.status
        })

    # 7. Upcoming Milestones List (Sorted by nearest deadline first)
    milestones_query = Milestone.query.join(Project).filter(
        Project.university_id == uni.id,
        Milestone.status != 'Completed'
    ).order_by(Milestone.deadline.asc()).all()

    upcoming_milestones_list = []
    for ms in milestones_query:
        is_overdue = False
        days_remaining_text = ""
        badge_variant = "secondary"

        if ms.deadline:
            diff_days = (ms.deadline.date() - now_time.date()).days
            if diff_days < 0:
                is_overdue = True
                days_remaining_text = f"Overdue by {abs(diff_days)}d"
                badge_variant = "danger"
            elif diff_days == 0:
                days_remaining_text = "Due today"
                badge_variant = "warning"
            elif diff_days == 1:
                days_remaining_text = "Due tomorrow"
                badge_variant = "info"
            else:
                days_remaining_text = f"Due in {diff_days}d"
                badge_variant = "mint"
        else:
            days_remaining_text = "No deadline set"

        upcoming_milestones_list.append({
            'id': ms.id,
            'project_id': ms.project_id,
            'project_title': ms.project.title if ms.project else 'University Project',
            'title': ms.title,
            'deadline': ms.deadline,
            'status': ms.status,
            'is_overdue': is_overdue,
            'days_remaining_text': days_remaining_text,
            'badge_variant': badge_variant
        })

    # Keep compatibility with existing tests
    accepted_count = accepted_challenges_count

    return render_template(
        'university/overview.html',
        university=uni,
        new_assignments_count=new_assignments_count,
        accepted_challenges_count=accepted_challenges_count,
        accepted_count=accepted_count,
        active_projects_count=active_projects_count,
        proposals_under_review_count=proposals_under_review_count,
        pending_milestones_count=pending_milestones_count,
        completed_projects_count=completed_projects_count,
        assignment_status_labels=assignment_status_labels,
        assignment_status_data=assignment_status_data,
        project_labels=project_labels,
        project_progress=project_progress,
        monthly_activity_labels=monthly_activity_labels,
        monthly_proposals_data=monthly_proposals_data,
        monthly_milestones_data=monthly_milestones_data,
        proposals_action_count=proposals_action_count,
        milestone_alerts_count=milestone_alerts_count,
        incomplete_teams_count=incomplete_teams_count,
        active_projects_cards=active_projects_cards,
        upcoming_milestones_list=upcoming_milestones_list
    )

@university_bp.route('/assigned')
@login_required
@role_required('university')
def assigned_challenges():
    uni = get_current_university()
    assignments = ChallengeAssignment.query.filter_by(
        university_id=uni.id
    ).order_by(ChallengeAssignment.assigned_at.desc()).all()

    return render_template(
        'university/assigned_challenges.html',
        university=uni,
        assignments=assignments
    )

@university_bp.route('/assignment/<int:assignment_id>/respond', methods=['POST'])
@login_required
@role_required('university')
def respond_assignment(assignment_id):
    assignment = ChallengeAssignment.query.get_or_404(assignment_id)
    uni = get_current_university()
    if assignment.university_id != uni.id:
        abort(403)

    action = request.form.get('action')  # 'accept', 'decline', 'clarification'
    notes = request.form.get('notes', '').strip()
    decline_reason = request.form.get('decline_reason', '').strip()

    challenge = assignment.challenge
    old_status = challenge.status

    if action == 'accept':
        assignment.status = 'Accepted'
        assignment.response_at = datetime.utcnow()
        assignment.notes = notes
        challenge.status = 'Accepted'

        # Check if project already created, else create initial project record
        project = Project.query.filter_by(challenge_id=challenge.id).first()
        if not project:
            project = Project(
                challenge_id=challenge.id,
                university_id=uni.id,
                title=f"Solution for {challenge.title}",
                stage='Planning',
                progress_percent=10,
                expected_completion=datetime.utcnow() + timedelta(days=180),
                budget=350000.0,
                status='Active'
            )
            db.session.add(project)
            db.session.flush()

            # Create standard default starter milestones
            m1 = Milestone(
                project_id=project.id,
                title="Problem Validation & Field Survey",
                description="Conduct ground baseline survey and interview affected local population.",
                deliverable="Baseline Assessment Report",
                deadline=datetime.utcnow() + timedelta(days=30),
                status='In Progress',
                order_index=1
            )
            m2 = Milestone(
                project_id=project.id,
                title="Engineering Design & Architecture",
                description="Formulate technical schematic, BOM, and simulation models.",
                deliverable="System Architecture Specification",
                deadline=datetime.utcnow() + timedelta(days=60),
                status='Pending',
                order_index=2
            )
            m3 = Milestone(
                project_id=project.id,
                title="Lab Prototype & Testing",
                description="Assemble bench-scale prototype and laboratory validation.",
                deliverable="Working Prototype Demo",
                deadline=datetime.utcnow() + timedelta(days=120),
                status='Pending',
                order_index=3
            )
            m4 = Milestone(
                project_id=project.id,
                title="Field Pilot & Handover",
                description="Deploy pilot in targeted village/block and calibrate with local operators.",
                deliverable="Pilot Verification & User Manual",
                deadline=datetime.utcnow() + timedelta(days=180),
                status='Pending',
                order_index=4
            )
            db.session.add_all([m1, m2, m3, m4])

        # Status history
        history = StatusHistory(
            challenge_id=challenge.id,
            old_status=old_status,
            new_status='Accepted',
            updated_by_id=current_user.id,
            notes=f"Accepted by {uni.name}. Project workspace initiated."
        )
        db.session.add(history)

        # Notify Govt
        govt_users = User.query.filter_by(role='government').all()
        for g in govt_users:
            notif = Notification(
                user_id=g.id,
                title="Challenge Accepted by University",
                message=f"{uni.name} has accepted challenge '{challenge.title}' ({challenge.code}).",
                link=url_for('government.project_monitoring'),
                category='success'
            )
            db.session.add(notif)

        flash(f"Challenge '{challenge.title}' has been accepted! Project workspace and starter milestones created.", 'success')

    elif action == 'decline':
        assignment.status = 'Declined'
        assignment.response_at = datetime.utcnow()
        assignment.decline_reason = decline_reason or notes
        challenge.status = 'Validated'  # Return to validated pool for re-allocation
        uni.active_workload = max(0, uni.active_workload - 1)

        history = StatusHistory(
            challenge_id=challenge.id,
            old_status=old_status,
            new_status='Validated',
            updated_by_id=current_user.id,
            notes=f"Declined by {uni.name}. Reason: {decline_reason or notes}"
        )
        db.session.add(history)

        # Notify Govt
        govt_users = User.query.filter_by(role='government').all()
        for g in govt_users:
            notif = Notification(
                user_id=g.id,
                title="University Declined Challenge",
                message=f"{uni.name} declined challenge '{challenge.title}'. Reason: {decline_reason or notes}. It is back in the allocation pool.",
                link=url_for('government.university_allocation'),
                category='warning'
            )
            db.session.add(notif)

        flash(f"Challenge '{challenge.title}' declined and returned to government pool.", 'info')

    elif action == 'clarification':
        assignment.status = 'Clarification Requested'
        assignment.notes = notes

        history = StatusHistory(
            challenge_id=challenge.id,
            old_status=old_status,
            new_status=old_status,
            updated_by_id=current_user.id,
            notes=f"Clarification requested by {uni.name}: {notes}"
        )
        db.session.add(history)

        # Notify citizen & govt
        notif = Notification(
            user_id=challenge.created_by_id,
            title="University Requested Clarification",
            message=f"{uni.name} needs more details on challenge '{challenge.title}': {notes}",
            link=url_for('citizen.challenge_detail', challenge_id=challenge.id),
            category='warning'
        )
        db.session.add(notif)

        flash("Clarification request recorded and sent to the reporter and authorities.", 'info')

    db.session.commit()
    return redirect(url_for('university.assigned_challenges'))

@university_bp.route('/projects')
@login_required
@role_required('university')
def active_projects():
    uni = get_current_university()
    projects = Project.query.filter_by(university_id=uni.id).order_by(Project.created_at.desc()).all()

    return render_template(
        'university/active_projects.html',
        university=uni,
        projects=projects
    )

@university_bp.route('/team', methods=['GET', 'POST'])
@login_required
@role_required('university')
def team_management():
    uni = get_current_university()
    projects = Project.query.filter_by(university_id=uni.id).all()
    selected_project_id = request.args.get('project_id', type=int)

    if not selected_project_id and projects:
        selected_project_id = projects[0].id

    selected_project = Project.query.get(selected_project_id) if selected_project_id else None

    if request.method == 'POST':
        project_id = request.form.get('project_id', type=int)
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', '').strip()
        department = request.form.get('department', '').strip()
        member_type = request.form.get('member_type', 'Faculty').strip()

        if not name or not email or not role or not project_id:
            flash('Please complete all required fields for the team member.', 'danger')
            return redirect(url_for('university.team_management', project_id=project_id))

        new_member = TeamMember(
            project_id=project_id,
            name=name,
            email=email,
            role=role,
            department=department,
            member_type=member_type
        )
        db.session.add(new_member)
        db.session.commit()
        flash(f"Team member '{name}' ({role}) added successfully!", 'success')
        return redirect(url_for('university.team_management', project_id=project_id))

    return render_template(
        'university/team_management.html',
        university=uni,
        projects=projects,
        selected_project=selected_project
    )

@university_bp.route('/proposals', methods=['GET', 'POST'])
@login_required
@role_required('university')
def proposals():
    uni = get_current_university()
    # Challenges accepted or with proposal
    accepted_assignments = ChallengeAssignment.query.filter(
        ChallengeAssignment.university_id == uni.id,
        ChallengeAssignment.status.in_(['Accepted', 'Assigned'])
    ).all()

    existing_proposals = Proposal.query.filter_by(university_id=uni.id).order_by(Proposal.created_at.desc()).all()

    if request.method == 'POST':
        challenge_id = request.form.get('challenge_id', type=int)
        title = request.form.get('title', '').strip()
        approach = request.form.get('approach', '').strip()
        duration_months = request.form.get('duration_months', 6, type=int)
        estimated_budget = request.form.get('estimated_budget', 0.0, type=float)
        resources_needed = request.form.get('resources_needed', '').strip()
        expected_impact = request.form.get('expected_impact', '').strip()
        action_type = request.form.get('action_type', 'submit')  # 'save_draft' or 'submit'

        if not challenge_id or not title or not approach:
            flash('Challenge, Solution Title, and Proposed Approach are required.', 'danger')
            return redirect(url_for('university.proposals'))

        status = 'Submitted' if action_type == 'submit' else 'Draft'

        proposal = Proposal.query.filter_by(challenge_id=challenge_id, university_id=uni.id).first()
        if not proposal:
            proposal = Proposal(
                challenge_id=challenge_id,
                university_id=uni.id,
                title=title,
                approach=approach,
                duration_months=duration_months,
                estimated_budget=estimated_budget,
                resources_needed=resources_needed,
                expected_impact=expected_impact,
                status=status
            )
            db.session.add(proposal)
        else:
            proposal.title = title
            proposal.approach = approach
            proposal.duration_months = duration_months
            proposal.estimated_budget = estimated_budget
            proposal.resources_needed = resources_needed
            proposal.expected_impact = expected_impact
            proposal.status = status

        challenge = Challenge.query.get(challenge_id)
        if status == 'Submitted' and challenge:
            old_status = challenge.status
            challenge.status = 'Proposal Submitted'

            history = StatusHistory(
                challenge_id=challenge.id,
                old_status=old_status,
                new_status='Proposal Submitted',
                updated_by_id=current_user.id,
                notes=f"Technical solution proposal submitted by {uni.name}."
            )
            db.session.add(history)

            # Notify Government
            govt_users = User.query.filter_by(role='government').all()
            for g in govt_users:
                notif = Notification(
                    user_id=g.id,
                    title="Solution Proposal Submitted",
                    message=f"{uni.name} submitted proposal for '{challenge.title}' (Budget: ₹{estimated_budget:,.2f}).",
                    link=url_for('government.project_monitoring'),
                    category='info'
                )
                db.session.add(notif)

        db.session.commit()
        flash(f"Proposal '{title}' has been {'submitted for government review' if status == 'Submitted' else 'saved as draft'}.", 'success')
        return redirect(url_for('university.proposals'))

    return render_template(
        'university/proposals.html',
        university=uni,
        accepted_assignments=accepted_assignments,
        proposals=existing_proposals
    )

@university_bp.route('/milestones', methods=['GET', 'POST'])
@login_required
@role_required('university')
def milestones():
    uni = get_current_university()
    projects = Project.query.filter_by(university_id=uni.id).all()
    selected_project_id = request.args.get('project_id', type=int)

    if not selected_project_id and projects:
        selected_project_id = projects[0].id

    selected_project = Project.query.get(selected_project_id) if selected_project_id else None

    if request.method == 'POST':
        project_id = request.form.get('project_id', type=int)
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        deliverable = request.form.get('deliverable', '').strip()
        deadline_str = request.form.get('deadline', '').strip()

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            except ValueError:
                deadline = datetime.utcnow() + timedelta(days=30)

        proj = Project.query.get_or_404(project_id)
        highest_order = db.session.query(db.func.max(Milestone.order_index)).filter_by(project_id=proj.id).scalar() or 0

        milestone = Milestone(
            project_id=proj.id,
            title=title,
            description=description,
            deliverable=deliverable,
            deadline=deadline,
            status='Pending',
            order_index=highest_order + 1
        )
        db.session.add(milestone)
        db.session.flush()

        # Recalculate progress
        proj.recalculate_progress()
        db.session.commit()

        flash(f"Milestone '{title}' added to project '{proj.title}'.", 'success')
        return redirect(url_for('university.milestones', project_id=proj.id))

    return render_template(
        'university/milestones.html',
        university=uni,
        projects=projects,
        selected_project=selected_project
    )

@university_bp.route('/milestone/<int:milestone_id>/update', methods=['POST'])
@login_required
@role_required('university')
def update_milestone(milestone_id):
    milestone = Milestone.query.get_or_404(milestone_id)
    new_status = request.form.get('status')  # 'Pending', 'In Progress', 'Completed'

    if new_status in ['Pending', 'In Progress', 'Completed']:
        milestone.status = new_status
        if new_status == 'Completed':
            milestone.completed_at = datetime.utcnow()
        else:
            milestone.completed_at = None

        project = milestone.project
        new_progress = project.recalculate_progress()

        # Update Project and Challenge lifecycle status based on progress
        challenge = project.challenge
        old_status = challenge.status
        
        if new_progress >= 100:
            project.stage = 'Completed'
            project.status = 'Completed'
            challenge.status = 'Completed'
        elif new_progress >= 75:
            project.stage = 'Field Pilot'
            challenge.status = 'Pilot Testing'
        elif new_progress >= 50:
            project.stage = 'Prototype Ready'
            challenge.status = 'Prototype Ready'
        else:
            project.stage = 'R&D In Progress'
            challenge.status = 'In Progress'

        if old_status != challenge.status:
            history = StatusHistory(
                challenge_id=challenge.id,
                old_status=old_status,
                new_status=challenge.status,
                updated_by_id=current_user.id,
                notes=f"Milestone '{milestone.title}' updated to {new_status}. Overall project progress now {new_progress}%."
            )
            db.session.add(history)

            # Notify Citizen and Government
            citizen_notif = Notification(
                user_id=challenge.created_by_id,
                title=f"Project Update: {challenge.status}",
                message=f"Milestone '{milestone.title}' completed! Solution stage is now {challenge.status} ({new_progress}%).",
                link=url_for('citizen.challenge_detail', challenge_id=challenge.id),
                category='success'
            )
            db.session.add(citizen_notif)

        db.session.commit()
        flash(f"Milestone status updated to '{new_status}'. Project progress is now {new_progress}%.", 'success')

    return redirect(url_for('university.milestones', project_id=milestone.project_id))

@university_bp.route('/notifications')
@login_required
@role_required('university')
def notifications():
    notifications_list = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    for n in notifications_list:
        if not n.is_read:
            n.is_read = True
    db.session.commit()
    return render_template('university/notifications.html', notifications=notifications_list)
