from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app.auth import auth_bp
from app.models import db, User

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'citizen':
            return redirect(url_for('citizen.overview'))
        elif current_user.role == 'government':
            return redirect(url_for('government.overview'))
        elif current_user.role == 'university':
            return redirect(url_for('university.overview'))

    selected_role = request.args.get('role', 'citizen')
    if selected_role not in ['citizen', 'government', 'university']:
        selected_role = 'citizen'

    if request.method == 'POST':
        identifier = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role_tab = request.form.get('role', 'citizen').strip().lower()
        remember = bool(request.form.get('remember'))

        if not identifier or not password:
            flash('Please enter both your identifier and password.', 'danger')
            return render_template('auth/login.html', selected_role=role_tab)

        # Support login by email (case-insensitive) or phone/mobile number
        user = User.query.filter(
            (User.email.ilike(identifier)) | (User.phone == identifier)
        ).first()

        if user is None or not user.check_password(password):
            flash('Invalid credentials. Please check your details and password.', 'danger')
            return render_template('auth/login.html', selected_role=role_tab, email=identifier)

        # The selected role tab only controls the interface.
        # Authenticate and verify the user's actual role from the database.
        login_user(user, remember=remember)
        flash(f'Welcome back, {user.full_name}!', 'success')

        # Prevent users from accessing dashboards belonging to other roles
        next_page = request.args.get('next')
        if next_page and urlparse(next_page).netloc == '':
            # Validate next_page matches user's verified role
            allowed_prefix = f'/{user.role}/'
            if next_page.startswith(allowed_prefix):
                return redirect(next_page)
            # If target URL belonged to another role, do not permit access; route to their own dashboard

        if user.role == 'citizen':
            return redirect(url_for('citizen.overview'))
        elif user.role == 'government':
            return redirect(url_for('government.overview'))
        elif user.role == 'university':
            return redirect(url_for('university.overview'))

        return redirect(url_for('index'))

    return render_template('auth/login.html', selected_role=selected_role)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Citizen self-registration. Government and university accounts remain admin-created."""
    if current_user.is_authenticated:
        if current_user.role == 'citizen':
            return redirect(url_for('citizen.overview'))
        elif current_user.role == 'government':
            return redirect(url_for('government.overview'))
        elif current_user.role == 'university':
            return redirect(url_for('university.overview'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        district = request.form.get('district', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not full_name or not email or not password:
            flash('Full name, email, and password are required.', 'danger')
            return render_template('auth/register.html', full_name=full_name, email=email, phone=phone, district=district)

        if password != confirm_password:
            flash('Passwords do not match. Please verify and try again.', 'danger')
            return render_template('auth/register.html', full_name=full_name, email=email, phone=phone, district=district)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html', full_name=full_name, email=email, phone=phone, district=district)

        # Check for existing email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists. Please sign in instead.', 'warning')
            return render_template('auth/register.html', full_name=full_name, email=email, phone=phone, district=district)

        # Only citizens can self-register; role is strictly hardcoded
        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            district=district,
            role='citizen'
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Your citizen account has been created successfully! Please sign in.', 'success')
        return redirect(url_for('auth.login', role='citizen'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('auth.login'))

