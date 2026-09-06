from datetime import datetime, timedelta
from app.models import (
    db, User, University, Challenge, ChallengeMedia, StatusHistory,
    ChallengeAssignment, Project, TeamMember, Proposal, Milestone, Notification
)

def seed_database():
    """Seeds the database with rich Jharkhand-specific sample data."""
    # Check if already seeded
    if User.query.filter_by(email='citizen@demo.com').first():
        print("Database already seeded.")
        return

    print("Seeding Srijan Setu database...")

    # 1. Create Universities
    unis_data = [
        {
            'name': 'Birla Institute of Technology (BIT), Mesra',
            'code': 'BIT-MESRA',
            'district': 'Ranchi',
            'domains_of_expertise': 'Renewable Energy, Water & Sanitation, Infrastructure & Connectivity',
            'active_workload': 2,
            'contact_email': 'dean.rnd@bitmesra.ac.in',
            'phone': '+91 651 2275444',
            'rating': 4.9,
            'description': 'Premier deemed university with center of excellence in Water Treatment, Solar Photovoltaics, and Tribal Rural Technologies.'
        },
        {
            'name': 'National Institute of Technology (NIT), Jamshedpur',
            'code': 'NIT-JSR',
            'district': 'East Singhbhum (Jamshedpur)',
            'domains_of_expertise': 'Mining & Environment, Infrastructure & Connectivity, Renewable Energy',
            'active_workload': 2,
            'contact_email': 'innovation@nitjsr.ac.in',
            'phone': '+91 657 2373407',
            'rating': 4.8,
            'description': 'Institute of National Importance with advanced metallurgy, structural engineering, and sustainable green manufacturing labs.'
        },
        {
            'name': 'IIT (Indian School of Mines), Dhanbad',
            'code': 'IIT-ISM',
            'district': 'Dhanbad',
            'domains_of_expertise': 'Mining & Environment, Water & Sanitation, Healthcare & Nutrition',
            'active_workload': 1,
            'contact_email': 'dean_rnd@iitism.ac.in',
            'phone': '+91 326 2235001',
            'rating': 4.9,
            'description': 'Global pioneer in geo-environmental engineering, mine dust suppression, and clean groundwater hydrology.'
        },
        {
            'name': 'Birsa Agricultural University (BAU), Kanke',
            'code': 'BAU-RNC',
            'district': 'Ranchi',
            'domains_of_expertise': 'Agriculture & Forest Produce, Healthcare & Nutrition, Water & Sanitation',
            'active_workload': 1,
            'contact_email': 'research@bauranchi.org',
            'phone': '+91 651 2450832',
            'rating': 4.7,
            'description': 'Apex agricultural and forestry university dedicated to indigenous crop preservation, lac value chains, and soil health in plateau soils.'
        },
        {
            'name': 'Central University of Jharkhand (CUJ), Brambe',
            'code': 'CUJ-RNC',
            'district': 'Ranchi',
            'domains_of_expertise': 'Education & Skill Development, Renewable Energy, Agriculture & Forest Produce',
            'active_workload': 0,
            'contact_email': 'rnd@cuj.ac.in',
            'phone': '+91 651 2901112',
            'rating': 4.6,
            'description': 'Multidisciplinary university focusing on tribal languages, tribal development policies, and eco-restoration.'
        },
        {
            'name': 'Kolhan University, Chaibasa',
            'code': 'KU-CBS',
            'district': 'West Singhbhum (Chaibasa)',
            'domains_of_expertise': 'Agriculture & Forest Produce, Healthcare & Nutrition, Education & Skill Development',
            'active_workload': 1,
            'contact_email': 'vc@kolhanuniversity.ac.in',
            'phone': '+91 658 2256420',
            'rating': 4.5,
            'description': 'Regional higher education powerhouse serving Kolhan division with grassroots outreach in Singhbhum tribal belts.'
        }
    ]

    unis = []
    for ud in unis_data:
        uni = University(**ud)
        db.session.add(uni)
        unis.append(uni)
    db.session.flush()

    bit_mesra = unis[0]
    nit_jsr = unis[1]
    iit_ism = unis[2]
    bau = unis[3]
    cuj = unis[4]
    kolhan = unis[5]

    # 2. Create Required Demo Users
    # Citizen Demo: citizen@demo.com / demo123
    citizen_user = User(
        email='citizen@demo.com',
        full_name='Ramesh Soren',
        role='citizen',
        phone='+91 94311 20451',
        organization='Gram Vikas Samiti Murhu',
        district='Khunti'
    )
    citizen_user.set_password('demo123')
    db.session.add(citizen_user)

    # Citizen 2
    citizen_user_2 = User(
        email='sunita.marandi@demo.com',
        full_name='Sunita Marandi',
        role='citizen',
        phone='+91 94701 88312',
        organization='Mahila Kalyan Manch',
        district='Dumka'
    )
    citizen_user_2.set_password('demo123')
    db.session.add(citizen_user_2)

    # Government Demo: government@demo.com / demo123
    govt_user = User(
        email='government@demo.com',
        full_name='Dr. Ananya Verma, IAS',
        role='government',
        phone='+91 651 2400192',
        organization='Govt. of Jharkhand - Directorate of Higher & Technical Education',
        designation='State Innovation Commissioner',
        district='Ranchi'
    )
    govt_user.set_password('demo123')
    db.session.add(govt_user)

    # University Demo: university@demo.com / demo123 (Linked to BIT Mesra)
    uni_user = User(
        email='university@demo.com',
        full_name='Prof. Rajeshwar K. Jha',
        role='university',
        phone='+91 651 2275880',
        organization='Birla Institute of Technology, Mesra',
        designation='Dean of Sponsored Research & Innovation',
        district='Ranchi',
        university_id=bit_mesra.id
    )
    uni_user.set_password('demo123')
    db.session.add(uni_user)

    # University Rep 2 (NIT Jamshedpur)
    uni_user_nit = User(
        email='nit.jsr@demo.com',
        full_name='Dr. Alok Sinha',
        role='university',
        phone='+91 657 2373001',
        organization='National Institute of Technology, Jamshedpur',
        designation='Head of Environmental Engineering',
        district='East Singhbhum (Jamshedpur)',
        university_id=nit_jsr.id
    )
    uni_user_nit.set_password('demo123')
    db.session.add(uni_user_nit)

    # University Rep 3 (IIT ISM Dhanbad)
    uni_user_iit = User(
        email='iit.ism@demo.com',
        full_name='Dr. Priyanka Tiwari',
        role='university',
        phone='+91 326 2235222',
        organization='IIT (ISM) Dhanbad',
        designation='Professor, Centre for Mining Environment',
        district='Dhanbad',
        university_id=iit_ism.id
    )
    uni_user_iit.set_password('demo123')
    db.session.add(uni_user_iit)

    db.session.flush()

    # 3. Create Realistic Challenges across Jharkhand
    now = datetime.utcnow()

    # Challenge 1: In Progress with BIT Mesra
    c1 = Challenge(
        code='SS-2026-0001',
        title='Severe Fluoride Contamination in Deep Borewells of Chainpur Block',
        description='Borewells across 8 panchayats in Chainpur block are showing fluoride levels between 4.5 and 8.2 mg/L, drastically exceeding the permissible limit of 1.5 mg/L. Over 3,500 villagers, including children, suffer from dental and skeletal fluorosis. Traditional boiling and cloth filters fail. Need a durable, low-cost, decentralized community filter using local clay/activated alumina that requires minimal maintenance.',
        domain='Water & Sanitation',
        district='Palamu',
        block='Chainpur',
        village_city='Kalyanpur & Semra Panchayats',
        people_affected=4200,
        duration_months=12,
        severity='Critical',
        address_text='Chainpur Block HQ, Near Palamu Forest Range',
        gps_coords='24.0321° N, 84.0722° E',
        status='In Progress',
        priority='Critical',
        category_assigned='Community Water Purification',
        validation_notes='Verified ground fluoride reports by District Water & Sanitation Committee (DWSC). Urgent action validated.',
        created_by_id=citizen_user.id,
        created_at=now - timedelta(days=65),
        updated_at=now - timedelta(days=5)
    )
    db.session.add(c1)
    db.session.flush()

    # Status History for c1
    db.session.add(StatusHistory(challenge_id=c1.id, old_status=None, new_status='Submitted', updated_by_id=citizen_user.id, notes='Citizen initial report submitted with DWSC water test certificates.', created_at=now - timedelta(days=65)))
    db.session.add(StatusHistory(challenge_id=c1.id, old_status='Submitted', new_status='Validated', updated_by_id=govt_user.id, notes='Ground reports validated. Escalated to Critical priority.', created_at=now - timedelta(days=55)))
    db.session.add(StatusHistory(challenge_id=c1.id, old_status='Validated', new_status='University Assigned', updated_by_id=govt_user.id, notes=f'Assigned to {bit_mesra.name} based on 98% match in Water & Sanitation technologies.', created_at=now - timedelta(days=48)))
    db.session.add(StatusHistory(challenge_id=c1.id, old_status='University Assigned', new_status='Accepted', updated_by_id=uni_user.id, notes='Accepted by BIT Mesra Centre for Water Research.', created_at=now - timedelta(days=45)))
    db.session.add(StatusHistory(challenge_id=c1.id, old_status='Accepted', new_status='Proposal Submitted', updated_by_id=uni_user.id, notes='Detailed engineering proposal and budget submitted.', created_at=now - timedelta(days=35)))
    db.session.add(StatusHistory(challenge_id=c1.id, old_status='Proposal Submitted', new_status='In Progress', updated_by_id=govt_user.id, notes='State Technical Council approved funding of ₹4,20,000.', created_at=now - timedelta(days=28)))

    # Assignment for c1
    asgn1 = ChallengeAssignment(
        challenge_id=c1.id,
        university_id=bit_mesra.id,
        assigned_by_id=govt_user.id,
        status='Accepted',
        assigned_at=now - timedelta(days=48),
        response_at=now - timedelta(days=45),
        notes='High-priority deployment needed before summer peak water scarcity.'
    )
    db.session.add(asgn1)

    # Proposal for c1
    prop1 = Proposal(
        challenge_id=c1.id,
        university_id=bit_mesra.id,
        title='Solar-Powered Adsorptive Defluoridation Plants using Charred Bone/Alumina Hybrid Columns',
        approach='Deploy continuous gravity-flow columns utilizing locally regenerated activated alumina bed with solar-powered pre-sedimentation. Includes IoT water-quality telemetry and village youth training for backwashing operations.',
        duration_months=8,
        estimated_budget=420000.0,
        resources_needed='Spectrophotometer field kits, pilot columns, solar DC pump, alumina granules',
        expected_impact='Provide WHO-grade potable water (<1.0 mg/L) to 4,200 villagers in Kalyanpur & Semra.',
        status='Approved',
        created_at=now - timedelta(days=35)
    )
    db.session.add(prop1)

    # Project for c1
    proj1 = Project(
        challenge_id=c1.id,
        university_id=bit_mesra.id,
        title='Chainpur Solar-Powered Defluoridation Initiative',
        stage='R&D In Progress',
        progress_percent=65,
        start_date=now - timedelta(days=28),
        expected_completion=now + timedelta(days=120),
        budget=420000.0,
        status='Active'
    )
    db.session.add(proj1)
    db.session.flush()

    # Team Members for proj1
    db.session.add_all([
        TeamMember(project_id=proj1.id, name='Prof. Rajeshwar K. Jha', email='rkjha@bitmesra.ac.in', role='Principal Investigator', department='Civil & Environmental Engineering', member_type='Faculty'),
        TeamMember(project_id=proj1.id, name='Dr. Sneha Minz', email='sminz@bitmesra.ac.in', role='Co-Principal Investigator', department='Chemical Engineering', member_type='Faculty'),
        TeamMember(project_id=proj1.id, name='Amit Murmu', email='amit.m@bitmesra.ac.in', role='Field Engineer & IoT Lead', department='Electronics Engineering', member_type='Student'),
        TeamMember(project_id=proj1.id, name='Priya Agarwal', email='pagarwal@bitmesra.ac.in', role='Water Chemistry Analyst', department='Chemistry Department', member_type='Researcher')
    ])

    # Milestones for proj1
    db.session.add_all([
        Milestone(project_id=proj1.id, title='Water Quality Baseline Survey', description='Collect 40 groundwater samples across Chainpur and test for fluoride, pH, TDS, and heavy metals.', deliverable='Baseline Hydrochemical Dossier', deadline=now - timedelta(days=15), status='Completed', completed_at=now - timedelta(days=16), order_index=1),
        Milestone(project_id=proj1.id, title='Column Media Optimization Lab Trials', description='Determine breakthrough curve and media adsorption capacity at varied flow rates.', deliverable='Laboratory Validation Report', deadline=now - timedelta(days=2), status='Completed', completed_at=now - timedelta(days=3), order_index=2),
        Milestone(project_id=proj1.id, title='Fabrication of 2,000 LPD Solar Pilot Unit', description='Assemble structural frame, PVC piping, media bed, and solar booster module at Mesra workshop.', deliverable='Fabricated Skid Prototype', deadline=now + timedelta(days=25), status='In Progress', order_index=3),
        Milestone(project_id=proj1.id, title='On-Site Installation & Jal Sahiya Training', description='Install at Kalyanpur High School campus and train 12 local Jal Sahiyas for weekly maintenance.', deliverable='Field Handover & Training Video', deadline=now + timedelta(days=75), status='Pending', order_index=4),
        Milestone(project_id=proj1.id, title='60-Day Water Quality Monitoring & Compliance Audit', description='Weekly sample testing to confirm sustained fluoride levels < 1.0 mg/L.', deliverable='Final Project Completion Dossier', deadline=now + timedelta(days=120), status='Pending', order_index=5)
    ])

    # Challenge 2: Prototype Ready with BAU Ranchi
    c2 = Challenge(
        code='SS-2026-0002',
        title='Value Addition & Low-Cost De-waxing Machine for Tribal Lac Farmers in Murhu',
        description='Tribal farmers in Khunti produce high-quality Rangeeni and Kusmi raw lac (sticklac), but lose 40% value by selling unprocessed material to intermediaries. Lack of portable scraping and de-waxing mechanisms forces distress sales at ₹180/kg instead of ₹650/kg for button/seedlac. A hand-cranked or low-power solar machine is urgently needed.',
        domain='Agriculture & Forest Produce',
        district='Khunti',
        block='Murhu',
        village_city='Torpa Road, Murhu Haat',
        people_affected=1850,
        duration_months=6,
        severity='High',
        address_text='Murhu Block Farmer Co-operative, Khunti',
        gps_coords='23.0112° N, 85.2789° E',
        status='Prototype Ready',
        priority='High',
        category_assigned='Forest Produce Processing',
        validation_notes='Endorsed by TRIFED and Jharkhand State Minor Forest Produce Federation.',
        created_by_id=citizen_user.id,
        created_at=now - timedelta(days=80),
        updated_at=now - timedelta(days=8)
    )
    db.session.add(c2)
    db.session.flush()

    db.session.add(StatusHistory(challenge_id=c2.id, old_status=None, new_status='Submitted', updated_by_id=citizen_user.id, notes='Initial submission with photos of raw sticklac harvesting.', created_at=now - timedelta(days=80)))
    db.session.add(StatusHistory(challenge_id=c2.id, old_status='Submitted', new_status='Validated', updated_by_id=govt_user.id, notes='Validated with TRIFED district officers.', created_at=now - timedelta(days=70)))
    db.session.add(StatusHistory(challenge_id=c2.id, old_status='Validated', new_status='University Assigned', updated_by_id=govt_user.id, notes=f'Allocated to {bau.name}.', created_at=now - timedelta(days=60)))
    db.session.add(StatusHistory(challenge_id=c2.id, old_status='University Assigned', new_status='Accepted', updated_by_id=govt_user.id, notes='Accepted by BAU Agricultural Engineering Division.', created_at=now - timedelta(days=55)))
    db.session.add(StatusHistory(challenge_id=c2.id, old_status='Accepted', new_status='In Progress', updated_by_id=govt_user.id, notes='Prototype design underway.', created_at=now - timedelta(days=40)))
    db.session.add(StatusHistory(challenge_id=c2.id, old_status='In Progress', new_status='Prototype Ready', updated_by_id=govt_user.id, notes='Bench prototype passed efficiency testing at Kanke workshop.', created_at=now - timedelta(days=8)))

    asgn2 = ChallengeAssignment(challenge_id=c2.id, university_id=bau.id, assigned_by_id=govt_user.id, status='Accepted', assigned_at=now - timedelta(days=60), response_at=now - timedelta(days=55))
    db.session.add(asgn2)

    proj2 = Project(
        challenge_id=c2.id,
        university_id=bau.id,
        title='Tribal Lac Mechanized Scraper & Solar Washer (Kisan Shakti-Lac)',
        stage='Prototype Ready',
        progress_percent=78,
        start_date=now - timedelta(days=40),
        expected_completion=now + timedelta(days=45),
        budget=280000.0,
        status='Active'
    )
    db.session.add(proj2)

    # Challenge 3: Proposal Submitted with IIT ISM Dhanbad
    c3 = Challenge(
        code='SS-2026-0003',
        title='Toxic Coal Dust Particulate (PM2.5/PM10) Suppression in Jharia Open Cast Clusters',
        description='Severe fugitive dust emissions from haul roads, coal stockyards, and overburden dumping in Jharia collieries cause severe asthma and pneumoconiosis among 15,000 residents living along the colliery perimeter. Conventional water tankers evaporate within minutes during summer. We need an organic biodegradable surfactant or dry fogging mist system to stabilize dust crusts.',
        domain='Mining & Environment',
        district='Dhanbad',
        block='Jharia',
        village_city='Kujama & Lodna Settlements',
        people_affected=15000,
        duration_months=9,
        severity='Critical',
        address_text='Jharia Fire Zone Perimeter, Dhanbad',
        gps_coords='23.7420° N, 86.4172° E',
        status='Proposal Submitted',
        priority='Critical',
        category_assigned='Air Pollution & Mine Safety',
        validation_notes='High particulate readings verified with JSPCB ambient air monitor stations.',
        created_by_id=citizen_user_2.id,
        created_at=now - timedelta(days=40),
        updated_at=now - timedelta(days=12)
    )
    db.session.add(c3)
    db.session.flush()

    db.session.add(StatusHistory(challenge_id=c3.id, old_status='Submitted', new_status='Validated', updated_by_id=govt_user.id, notes='Validated by State Pollution Control Board.', created_at=now - timedelta(days=30)))
    db.session.add(StatusHistory(challenge_id=c3.id, old_status='Validated', new_status='University Assigned', updated_by_id=govt_user.id, notes=f'Assigned to {iit_ism.name}.', created_at=now - timedelta(days=22)))
    db.session.add(StatusHistory(challenge_id=c3.id, old_status='University Assigned', new_status='Accepted', updated_by_id=uni_user_iit.id, notes='Accepted by Centre for Mining Environment, IIT ISM.', created_at=now - timedelta(days=18)))
    db.session.add(StatusHistory(challenge_id=c3.id, old_status='Accepted', new_status='Proposal Submitted', updated_by_id=uni_user_iit.id, notes='Bio-polymeric dust crust stabilizer proposal submitted.', created_at=now - timedelta(days=12)))

    asgn3 = ChallengeAssignment(challenge_id=c3.id, university_id=iit_ism.id, assigned_by_id=govt_user.id, status='Accepted', assigned_at=now - timedelta(days=22), response_at=now - timedelta(days=18))
    db.session.add(asgn3)

    prop3 = Proposal(
        challenge_id=c3.id,
        university_id=iit_ism.id,
        title='Lignosulfonate-Cellulose Biodegradable Mist Suppression for Open-Cast Haul Roads',
        approach='Formulate a non-hazardous, eco-friendly adhesive emulsion using agro-waste lignin that binds micro-particulates into a durable crust lasting 72 hours per spray pass.',
        duration_months=9,
        estimated_budget=540000.0,
        resources_needed='High-pressure fogging nozzles, aerosol optical spectrometer, mobile spray trailer',
        expected_impact='Reduce PM10 and PM2.5 concentrations by up to 68% along residential buffers.',
        status='Submitted',
        created_at=now - timedelta(days=12)
    )
    db.session.add(prop3)

    # Challenge 4: Accepted with NIT Jamshedpur
    c4 = Challenge(
        code='SS-2026-0004',
        title='Off-Grid Solar Microgrid Frequency & Battery Bank Instability in Netarhat Plateau',
        description='During dense fog and monsoon cloud cover from June to September, the tribal residential schools and 3 villages in Netarhat suffer complete blackouts due to inverter tripping and sulfation of lead-acid banks. Need a smart hybrid controller with supercapacitor buffer and localized biomass backup integration.',
        domain='Renewable Energy',
        district='Latehar',
        block='Mahuadanr',
        village_city='Netarhat Gram Panchayat',
        people_affected=1200,
        duration_months=6,
        severity='High',
        address_text='Netarhat Vidyalaya Junction, Latehar',
        gps_coords='23.4791° N, 84.2690° E',
        status='Accepted',
        priority='High',
        category_assigned='Renewable Energy & Microgrids',
        validation_notes='JREDA inspection confirmed intermittent grid failure during monsoon.',
        created_by_id=citizen_user.id,
        created_at=now - timedelta(days=25),
        updated_at=now - timedelta(days=4)
    )
    db.session.add(c4)
    db.session.flush()

    asgn4 = ChallengeAssignment(challenge_id=c4.id, university_id=nit_jsr.id, assigned_by_id=govt_user.id, status='Accepted', assigned_at=now - timedelta(days=10), response_at=now - timedelta(days=4))
    db.session.add(asgn4)

    # Challenge 5: Validated (In University Allocation Queue)
    c5 = Challenge(
        code='SS-2026-0005',
        title='Solar Telemedicine Kiosk & Drone Sample Delivery for Remote Santhal Pargana Villages',
        description='Villages situated across hilly terrain in Shikaripara and Raneshwar blocks are cut off during monsoons, requiring 4-hour bullock cart trips to Dumka Sadar Hospital for basic blood tests and anti-snake venom. Need a solar telemedicine booth with remote vital diagnostic kits and telemetry.',
        domain='Healthcare & Nutrition',
        district='Dumka',
        block='Shikaripara',
        village_city='Haripur & Mohulpahari Tola',
        people_affected=5600,
        duration_months=8,
        severity='High',
        address_text='Primary Health Sub-centre, Shikaripara',
        gps_coords='24.2389° N, 87.5210° E',
        status='Validated',
        priority='High',
        category_assigned='Digital Health & Telemedicine',
        validation_notes='National Health Mission Dumka verified geographic isolation and emergency referral bottlenecks.',
        created_by_id=citizen_user_2.id,
        created_at=now - timedelta(days=14),
        updated_at=now - timedelta(days=3)
    )
    db.session.add(c5)

    # Challenge 6: Under Review (Critical Severity in Validation Queue)
    c6 = Challenge(
        code='SS-2026-0006',
        title='Arsenic & Iron Leaching in Village Hand Pumps Adjacent to Subarnarekha River',
        description='Water samples from 14 public hand pumps in Bahragora and Ghatshila show brown discoloration and oily film. Lab tests show arsenic levels of 0.08 mg/L (standard is 0.01) and iron exceeding 7 mg/L. Several cattle deaths and skin lesions in human population reported in last 45 days.',
        domain='Water & Sanitation',
        district='East Singhbhum (Jamshedpur)',
        block='Ghatshila',
        village_city='Kashida & Moubhandar Panchayats',
        people_affected=3100,
        duration_months=4,
        severity='Critical',
        address_text='Subarnarekha Riverbank Road, Ghatshila',
        gps_coords='22.5847° N, 86.4829° E',
        status='Under Review',
        priority='Critical',
        created_by_id=citizen_user.id,
        created_at=now - timedelta(days=3),
        updated_at=now - timedelta(days=1)
    )
    db.session.add(c6)

    # Challenge 7: Submitted (Fresh Submission)
    c7 = Challenge(
        code='SS-2026-0007',
        title='Post-Harvest Rot in Mahua Flower Distillation & Lack of Non-Timber Forest Cold Stores',
        description='During Mahua collection in April-May, over 50 tons of fresh flowers rot within 72 hours due to high humidity and lack of ventilated drying yards or cold chain units. Tribal women collectors receive under ₹22/kg, but solar dehydration could increase earnings to ₹95/kg.',
        domain='Agriculture & Forest Produce',
        district='West Singhbhum (Chaibasa)',
        block='Goilkera',
        village_city='Saranda Forest Fringe Villages',
        people_affected=2400,
        duration_months=5,
        severity='Medium',
        address_text='Goilkera Haat, West Singhbhum',
        gps_coords='22.5180° N, 85.3812° E',
        status='Submitted',
        priority='Medium',
        created_by_id=citizen_user.id,
        created_at=now - timedelta(days=1),
        updated_at=now - timedelta(days=1)
    )
    db.session.add(c7)

    # Challenge 8: Clarification Required
    c8 = Challenge(
        code='SS-2026-0008',
        title='Seasonal Flash Flooding & Bridge Collapse Isolating 12 Panchayats across Barakar River',
        description='Every monsoon, temporary causeways across the Barakar river tributary are washed away, cutting off 12 panchayats from the district hospital and grain markets for up to 3 weeks. Requesting modular rapid-deployment bamboo composite or steel pedestrian bridge.',
        domain='Infrastructure & Connectivity',
        district='Giridih',
        block='Tisri',
        village_city='Lokai & Chandori Panchayats',
        people_affected=8500,
        duration_months=12,
        severity='High',
        address_text='Barakar Causeway point, Tisri Road',
        gps_coords='24.5712° N, 86.0645° E',
        status='Clarification Required',
        priority='High',
        validation_notes='Need exact GPS coordinates and high-water flood level measurements for the past 3 years.',
        created_by_id=citizen_user.id,
        created_at=now - timedelta(days=18),
        updated_at=now - timedelta(days=10)
    )
    db.session.add(c8)

    # Challenge 9: Completed Project
    c9 = Challenge(
        code='SS-2026-0009',
        title='Solar-Powered Vegetable Cold Storage for Organic Chhau Farming Clusters',
        description='Farmers cultivating organic ridge gourd and bottle gourd in Saraikela faced 35% spoilage before reaching Jamshedpur markets. Solution needed an off-grid cold room maintained at 4-8°C with phase-change thermal storage.',
        domain='Renewable Energy',
        district='Saraikela Kharsawan',
        block='Saraikela',
        village_city='Kandra Vegetable Mandi',
        people_affected=1900,
        duration_months=6,
        severity='Medium',
        status='Completed',
        priority='Medium',
        category_assigned='Cold Chain & Solar Thermal',
        validation_notes='Commissioned and fully operational. Maintained by Kandra FPO.',
        created_by_id=citizen_user.id,
        created_at=now - timedelta(days=150),
        updated_at=now - timedelta(days=15)
    )
    db.session.add(c9)
    db.session.flush()

    asgn9 = ChallengeAssignment(challenge_id=c9.id, university_id=bit_mesra.id, assigned_by_id=govt_user.id, status='Accepted', assigned_at=now - timedelta(days=130), response_at=now - timedelta(days=125))
    db.session.add(asgn9)

    proj9 = Project(
        challenge_id=c9.id,
        university_id=bit_mesra.id,
        title='Solar Cold Hub with PCM Energy Storage (Kandra)',
        stage='Completed',
        progress_percent=100,
        start_date=now - timedelta(days=120),
        expected_completion=now - timedelta(days=15),
        budget=390000.0,
        status='Completed'
    )
    db.session.add(proj9)
    db.session.flush()

    db.session.add(Milestone(project_id=proj9.id, title='Solar PCM Thermal Design', description='Design thermal storage chamber with PCM salt hydrates.', deliverable='CAD and thermodynamic model', deadline=now - timedelta(days=90), status='Completed', completed_at=now - timedelta(days=92), order_index=1))
    db.session.add(Milestone(project_id=proj9.id, title='Cold Room Construction', description='Erect 5 MT cold room at Kandra mandi.', deliverable='Cold Room Shell', deadline=now - timedelta(days=45), status='Completed', completed_at=now - timedelta(days=40), order_index=2))
    db.session.add(Milestone(project_id=proj9.id, title='Farmer Handover & Operational Training', description='Handover to FPO with 3-year warranty certificate.', deliverable='Handover Certificate', deadline=now - timedelta(days=15), status='Completed', completed_at=now - timedelta(days=15), order_index=3))

    # Challenge 10: University Assigned to NIT Jamshedpur
    c10 = Challenge(
        code='SS-2026-0010',
        title='Coal Washery Slurry Runoff Remediation in Damodar River Basin',
        description='Suspended fines from abandoned washery ponds in Chandrapura seep into Damodar irrigation canals during thunderstorms, blackening silt in surrounding paddy fields and reducing rice yields by 45%.',
        domain='Mining & Environment',
        district='Bokaro',
        block='Chandrapura',
        village_city='Tarmi & Dugda Panchayats',
        people_affected=3800,
        duration_months=7,
        severity='High',
        address_text='Damodar Canal intake point, Chandrapura',
        gps_coords='23.7541° N, 86.1287° E',
        status='University Assigned',
        priority='High',
        category_assigned='Industrial Effluent & Soil Remediation',
        validation_notes='Field inspection confirmed slurry overflow into public irrigation canal.',
        created_by_id=citizen_user.id,
        created_at=now - timedelta(days=20),
        updated_at=now - timedelta(days=2)
    )
    db.session.add(c10)
    db.session.flush()

    asgn10 = ChallengeAssignment(challenge_id=c10.id, university_id=nit_jsr.id, assigned_by_id=govt_user.id, status='Assigned', assigned_at=now - timedelta(days=2))
    db.session.add(asgn10)

    # 4. Realistic Notifications
    # Citizen notifications
    db.session.add(Notification(user_id=citizen_user.id, title="Project Milestone Achieved!", message="BIT Mesra completed the Laboratory Validation for your Chainpur Water Challenge (SS-2026-0001). Overall progress is 65%.", link="/citizen/challenge/1", category="success", created_at=now - timedelta(hours=3)))
    db.session.add(Notification(user_id=citizen_user.id, title="Action Required: Clarification", message="Authorities requested additional survey documents for your Giridih Bridge challenge (SS-2026-0008).", link="/citizen/challenge/8", category="warning", created_at=now - timedelta(days=1)))
    db.session.add(Notification(user_id=citizen_user.id, title="Challenge Under Review", message="Your report on Arsenic Leaching in Ghatshila (SS-2026-0006) was escalated to High Priority.", link="/citizen/challenge/6", category="info", created_at=now - timedelta(days=2)))

    # Government notifications
    db.session.add(Notification(user_id=govt_user.id, title="Critical Severity Alert", message="New critical challenge 'Arsenic & Iron Leaching in Ghatshila' (SS-2026-0006) submitted by citizen.", link="/government/validation", category="danger", created_at=now - timedelta(days=1)))
    db.session.add(Notification(user_id=govt_user.id, title="Proposal Submitted for Review", message="IIT ISM Dhanbad submitted technical proposal for 'Toxic Coal Dust Particulate Suppression' (SS-2026-0003).", link="/government/projects", category="info", created_at=now - timedelta(days=2)))
    db.session.add(Notification(user_id=govt_user.id, title="Milestone Verified", message="BIT Mesra reported successful field test of Solar Defluoridation column prototype.", link="/government/projects", category="success", created_at=now - timedelta(days=3)))

    # University notifications (Prof. Jha at BIT Mesra)
    db.session.add(Notification(user_id=uni_user.id, title="Upcoming Milestone Deadline", message="Fabrication of 2,000 LPD Solar Pilot Unit for Chainpur Defluoridation is due in 25 days.", link="/university/milestones?project_id=1", category="warning", created_at=now - timedelta(hours=5)))
    db.session.add(Notification(user_id=uni_user.id, title="Government Grant Disbursed", message="State Innovation Fund sanctioned ₹4,20,000 tranche 1 for Chainpur Water Project.", link="/university/projects", category="success", created_at=now - timedelta(days=4)))
    db.session.add(Notification(user_id=uni_user.id, title="Challenge Assignment Reminder", message="Challenge SS-2026-0001 status transitioned to In Progress.", link="/university/assigned", category="info", created_at=now - timedelta(days=7)))

    db.session.commit()
    print("Srijan Setu database successfully populated with realistic data!")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_database()
