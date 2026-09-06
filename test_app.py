import unittest
from app import create_app, db
from app.models import User, Challenge, University, Project, Milestone, StatusHistory
from app.seed import seed_database

class JIGTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            seed_database()

    def test_01_login_page_renders(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SRIJAN', response.data)
        self.assertIn(b'SETU', response.data)
        self.assertIn(b'PROPOSED FOR GOVT. OF JHARKHAND // SIH PS 26043', response.data)
        self.assertIn(b'Community Challenges. Collaborative Solutions.', response.data)
        self.assertIn(b'COLLABORATE', response.data)
        self.assertIn(b'Sign In to Srijan Setu', response.data)
        self.assertNotIn(b'knowledge_grid: established_jharkhand', response.data)
        self.assertIn(b'New citizen?', response.data)
        self.assertIn(b'Create an account', response.data)
        self.assertIn(b'/register', response.data)

    def test_02_authentication_and_redirect(self):
        # Test citizen login
        res_cit = self.client.post('/login', data={
            'email': 'citizen@demo.com',
            'password': 'demo123',
            'role': 'citizen'
        }, follow_redirects=True)
        self.assertEqual(res_cit.status_code, 200)
        self.assertIn(b'Citizen Workspace', res_cit.data)
        with self.app.app_context():
            user = User.query.filter_by(email='citizen@demo.com').first()
            self.assertIn(user.full_name.encode('utf-8'), res_cit.data)

        # Logout
        self.client.get('/logout', follow_redirects=True)

        # Test government login
        res_gov = self.client.post('/login', data={
            'email': 'government@demo.com',
            'password': 'demo123',
            'role': 'government'
        }, follow_redirects=True)
        self.assertEqual(res_gov.status_code, 200)
        self.assertIn(b'Authority Desk', res_gov.data)
        self.assertIn(b'Validation Queue', res_gov.data)

        # Logout
        self.client.get('/logout', follow_redirects=True)

        # Test university login
        res_uni = self.client.post('/login', data={
            'email': 'university@demo.com',
            'password': 'demo123',
            'role': 'university'
        }, follow_redirects=True)
        self.assertEqual(res_uni.status_code, 200)
        self.assertIn(b'Research & Innovation', res_uni.data)
        self.assertIn(b'Birla Institute of Technology (BIT), Mesra', res_uni.data)

    def test_03_role_protection_403(self):
        # Login as citizen
        self.client.post('/login', data={
            'email': 'citizen@demo.com',
            'password': 'demo123',
            'role': 'citizen'
        })
        # Attempt to access government validation queue
        res = self.client.get('/government/validation')
        self.assertEqual(res.status_code, 403)
        self.assertIn(b'Unauthorized Access', res.data)

    def test_04_citizen_submit_challenge(self):
        self.client.post('/login', data={
            'email': 'citizen@demo.com',
            'password': 'demo123',
            'role': 'citizen'
        })
        res = self.client.post('/citizen/submit', data={
            'title': 'Test Arsenic Contamination in Rural Well',
            'description': 'High arsenic readings confirmed by local tests in community drinking well.',
            'domain': 'Water & Sanitation',
            'district': 'Ranchi',
            'block': 'Kanke',
            'village_city': 'Boreya',
            'people_affected': 450,
            'duration_months': 3,
            'severity': 'High',
            'address_text': 'Near Panchayat Bhavan',
            'gps_coords': '23.412° N, 85.321° E'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Test Arsenic Contamination in Rural Well', res.data)
        self.assertIn(b'Submitted', res.data)

    def test_05_government_validation_action(self):
        # Login as government
        self.client.post('/login', data={
            'email': 'government@demo.com',
            'password': 'demo123',
            'role': 'government'
        })
        # Validate challenge 7 (or first available)
        with self.app.app_context():
            chal = Challenge.query.filter_by(status='Submitted').first()
            if not chal:
                chal = Challenge.query.first()
            chal_id = chal.id

        res = self.client.post(f'/government/validate/{chal_id}', data={
            'action': 'validate',
            'priority': 'High',
            'category': 'Technology',
            'notes': 'Verified with district officers.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            chal = db.session.get(Challenge, chal_id)
            self.assertEqual(chal.status, 'Validated')

    def test_06_government_allocate_action(self):
        self.client.post('/login', data={
            'email': 'government@demo.com',
            'password': 'demo123',
            'role': 'government'
        })
        with self.app.app_context():
            chal = Challenge.query.filter_by(status='Validated').first()
            if not chal:
                chal = Challenge.query.first()
                chal.status = 'Validated'
                db.session.commit()
            chal_id = chal.id

        res = self.client.post(f'/government/allocate/{chal_id}', data={
            'university_id': 1,
            'notes': 'Please expedite telemedicine prototype.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            chal = db.session.get(Challenge, chal_id)
            self.assertEqual(chal.status, 'University Assigned')

    def test_07_university_accept_and_milestone_progress(self):
        self.client.post('/login', data={
            'email': 'university@demo.com',
            'password': 'demo123',
            'role': 'university'
        })
        with self.app.app_context():
            proj = Project.query.get(1)
            ms = proj.milestones.first()
            ms.status = 'In Progress'
            db.session.commit()
            ms_id = ms.id

        # Mark milestone as Completed
        res = self.client.post(f'/university/milestone/{ms_id}/update', data={
            'status': 'Completed'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            proj_after = db.session.get(Project, 1)
            self.assertGreaterEqual(proj_after.progress_percent, 10)

    def test_08_role_tab_only_controls_interface(self):
        # Government user logs in while 'citizen' role tab is passed in form
        res = self.client.post('/login', data={
            'email': 'government@demo.com',
            'password': 'demo123',
            'role': 'citizen'  # Selected tab in UI was citizen
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        # Should be directed to government authority desk, NOT citizen workspace
        self.assertIn(b'Authority Desk', res.data)
        self.client.get('/logout', follow_redirects=True)

    def test_09_prevent_cross_role_dashboard_access_via_next(self):
        # Citizen attempts to access government overview via next param
        res = self.client.post('/login?next=%2Fgovernment%2Foverview', data={
            'email': 'citizen@demo.com',
            'password': 'demo123',
            'role': 'citizen'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        # Citizen must be redirected to citizen dashboard, NOT government dashboard
        self.assertIn(b'Citizen Workspace', res.data)
        self.assertNotIn(b'Authority Desk', res.data)
        self.client.get('/logout', follow_redirects=True)

    def test_10_citizen_self_registration(self):
        test_email = 'new.citizen.test@jharkhand.org'
        test_phone = '9876543210'
        with self.app.app_context():
            User.query.filter((User.email == test_email) | (User.phone == test_phone)).delete()
            db.session.commit()

        # Self registration for new citizen
        res = self.client.post('/register', data={
            'full_name': 'Birsa Munda Jr.',
            'email': test_email,
            'phone': '9876543210',
            'district': 'Khunti',
            'password': 'securepassword123',
            'confirm_password': 'securepassword123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Your citizen account has been created successfully', res.data)

        # Verify in DB that role is strictly citizen
        with self.app.app_context():
            created_user = User.query.filter_by(email=test_email).first()
            self.assertIsNotNone(created_user)
            self.assertEqual(created_user.role, 'citizen')
            self.assertTrue(created_user.check_password('securepassword123'))

        # Now test login with mobile number
        res_login_phone = self.client.post('/login', data={
            'email': '9876543210',
            'password': 'securepassword123',
            'role': 'citizen'
        }, follow_redirects=True)
        self.assertEqual(res_login_phone.status_code, 200)
        self.assertIn(b'Citizen Workspace', res_login_phone.data)
        self.client.get('/logout', follow_redirects=True)

    def test_11_demo_accounts_dev_mode_visibility(self):
        # In testing/non-dev mode without FLASK_DEBUG/FLASK_ENV:
        res = self.client.get('/login')
        # Demo credentials section is conditionally rendered based on is_dev_mode
        self.assertEqual(res.status_code, 200)

    def test_12_government_dashboard_redesign_verification(self):
        self.client.post('/login', data={
            'email': 'government@demo.com',
            'password': 'demo123',
            'role': 'government'
        }, follow_redirects=True)

        res = self.client.get('/government/overview')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')

        # 1. Sidebar grouped cards & overview pill
        self.assertIn('sidebar-overview-pill', html)
        self.assertIn('CHALLENGE MANAGEMENT', html)
        self.assertIn('ALLOCATION & PROJECTS', html)
        self.assertIn('INSIGHTS', html)
        self.assertIn('ACCOUNT', html)
        self.assertIn('Dr. Ananya Verma, IAS', html)
        self.assertIn('Government Official • Ranchi', html)
        self.assertIn('Logout', html)

        # 2. Main dashboard hero & topbar
        self.assertIn('gov-hero-compact', html)
        self.assertIn('PROPOSED STATE NODAL DASHBOARD', html)
        self.assertIn('Government Coordination Dashboard', html)
        self.assertIn('Validate community challenges, coordinate university assignments and monitor solution progress across Jharkhand.', html)
        self.assertIn('btn-topbar-filter', html)
        self.assertIn('Filter Statewide Challenges', html)

        # 3. Summary cards
        self.assertIn('Total Challenges', html)
        self.assertIn('Pending Validation', html)
        self.assertIn('Validated – Awaiting Allocation', html)
        self.assertIn('Assigned', html)
        self.assertIn('Active Projects', html)
        self.assertIn('Completed', html)
        self.assertIn('col-xl-2 col-lg-4 col-md-6 col-12', html)

        # 4. Analytics charts & section ordering
        self.assertIn('Challenges by Domain', html)
        self.assertIn('domainChart', html)
        self.assertIn('Status Distribution', html)
        self.assertIn('statusChart', html)
        self.assertIn('Monthly Submissions', html)
        self.assertIn('trendChart', html)

        # Confirm removed duplicate / extra charts are NOT on Overview
        self.assertNotIn('Project Lifecycle', html)
        self.assertNotIn('lifecycleChart', html)
        self.assertNotIn('districtChart', html)

        # 5. Action Required section (must appear below charts)
        self.assertIn('Action Required', html)
        self.assertIn('Awaiting Validation', html)
        self.assertIn('Awaiting Allocation', html)
        self.assertIn('Overdue Milestones', html)
        self.assertIn('Clarifications', html)

        # 6. Priority and Delay Alerts
        self.assertIn('Priority and Delay Alerts', html)

        # Verify strict dashboard ordering
        idx_welcome = html.index('gov-hero-compact')
        idx_summary = html.index('Total Challenges')
        idx_charts = html.index('domainChart')
        idx_action = html.index('Action Required')
        idx_alerts = html.index('Priority and Delay Alerts')
        self.assertTrue(idx_welcome < idx_summary < idx_charts < idx_action < idx_alerts)

        self.client.get('/logout', follow_redirects=True)

    def test_13_university_dashboard_redesign_verification(self):
        # 1. Login as University Coordinator
        self.client.post('/login', data={
            'email': 'university@demo.com',
            'password': 'demo123',
            'role': 'university'
        }, follow_redirects=True)

        res = self.client.get('/university/overview')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')

        # 2. Sidebar grouped cards & overview button
        self.assertIn('sidebar-overview-pill', html)
        self.assertIn('CHALLENGES', html)
        self.assertIn('Assigned Challenges', html)
        self.assertIn('Accepted Challenges', html)
        self.assertIn('Clarification Requests', html)
        self.assertIn('PROJECT WORKSPACE', html)
        self.assertIn('Active Projects', html)
        self.assertIn('Team Management', html)
        self.assertIn('Proposals', html)
        self.assertIn('Milestones', html)
        self.assertIn('INSIGHTS', html)
        self.assertIn('Project Analytics', html)
        self.assertIn('Research Outcomes', html)
        self.assertIn('Completed Solutions', html)
        self.assertIn('ACCOUNT', html)
        self.assertIn('Notifications', html)
        self.assertIn('University Profile', html)
        self.assertIn('Help & Support', html)
        self.assertIn('Prof. Rajeshwar K. Jha', html)
        self.assertIn('University Coordinator', html)
        self.assertIn('Logout', html)

        # 3. Topbar has Review Assignments instead of New Proposal
        self.assertIn('Review Assignments', html)
        self.assertNotIn('New Proposal', html)

        # 4. Welcome banner
        self.assertIn('uni-hero-compact', html)
        self.assertIn('ACADEMIC R&D HUB', html)
        self.assertIn('Birla Institute of Technology (BIT), Mesra', html)
        self.assertIn('Transform assigned community challenges into multidisciplinary research, prototypes and field-tested solutions.', html)
        self.assertIn('Submit Technical Proposal', html)

        # 5. Six summary cards
        self.assertIn('New Assignments', html)
        self.assertIn('Accepted Challenges', html)
        self.assertIn('Active Projects', html)
        self.assertIn('Proposals Under Review', html)
        self.assertIn('Pending Milestones', html)
        self.assertIn('Completed Projects', html)
        self.assertIn('col-xl-2 col-lg-4 col-md-6 col-12', html)

        # 6. Three animated analytics charts in responsive row
        self.assertIn('Challenge Assignment Status', html)
        self.assertIn('assignmentStatusChart', html)
        self.assertIn('Active Project Progress', html)
        self.assertIn('projectProgressChart', html)
        self.assertIn('Monthly Research Activity', html)
        self.assertIn('monthlyActivityChart', html)

        # 7. Action Required section
        self.assertIn('Action Required', html)
        self.assertIn('Proposal Actions', html)
        self.assertIn('Milestone Alerts', html)
        self.assertIn('Team Requirements', html)

        # 8. Active Projects compact cards
        self.assertIn('active-projects-section', html)
        self.assertIn('project-card-compact', html)
        self.assertIn('Faculty Mentor:', html)
        self.assertIn('Open Workspace', html)

        # 9. Upcoming Milestones
        self.assertIn('Upcoming Milestones', html)
        self.assertIn('Manage All Milestones', html)

        # 10. Dashboard section order verification within main content area
        main_html = html[html.find('<main'):]
        idx_welcome = main_html.index('uni-hero-compact')
        idx_summary = main_html.index('stat-label">New Assignments')
        idx_charts = main_html.index('assignmentStatusChart')
        idx_action = main_html.index('Action Required')
        idx_projects = main_html.index('id="active-projects-section"')
        idx_milestones = main_html.index('Upcoming Milestones')
        self.assertTrue(idx_welcome < idx_summary < idx_charts < idx_action < idx_projects < idx_milestones)

        self.client.get('/logout', follow_redirects=True)


if __name__ == '__main__':
    unittest.main()
