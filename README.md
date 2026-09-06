# Srijan Setu (SIH Problem Statement 26043)

> **“Community Challenges. Collaborative Solutions.”**

**Srijan Setu** is a responsive, full-stack Flask web application built for **Smart India Hackathon (SIH) Problem Statement 26043**. It bridges grassroots community challenges across all 24 districts of Jharkhand directly with state government authorities and higher education institutions (such as BIT Mesra, NIT Jamshedpur, IIT ISM Dhanbad, and Birsa Agricultural University).

---

## 🚀 Key Features

1. **Split-Screen Authentication System**:
   - Modern split-screen layout with subtle radial gradients, decorative curved dividing arc, and branding.
   - 3-Role selector tabs (`Citizen`, `Government`, `University`).
   - Show/hide password eye toggle.
   - 1-Click demo credential quick-fill buttons for lightning-fast evaluations.
   - Secure password hashing using Werkzeug.

2. **Citizen Portal (`/citizen`)**:
   - Overview banner with quick stats and submission status timeline.
   - **Submit Challenge Form**: Real Jharkhand districts, blocks, quantitative impact metrics (people affected, persistence), GPS coordinates, and file/evidence upload (photos, PDFs).
   - **My Challenges**: Filterable data table with search, status pills, severity indicators, and detail views.
   - **Challenge Detail Dossier**: Evidence photo gallery, live workflow progress bar, assigned university profile, and full audit history timeline.

3. **Government Authority Portal (`/government`)**:
   - Overview with dynamic **Chart.js** charts (Domain Distribution, Status Breakdown, Monthly Submissions).
   - **Validation Queue**: Review ground reports & evidence, assign priority levels (`Critical`, `High`, `Medium`, `Low`), categorize, and Validate, Reject, or Request Clarification.
   - **Smart University Allocation**: Recommends universities ranked by calculated AI/domain match score, active research workload, and institutional rating.
   - **Project Monitoring**: Supervise active university projects, milestone completion rates, budgets, and deadlines.
   - **Statewide Analytics**: District-level challenge density breakdown and academic partner workload leaderboards.

4. **University Research Portal (`/university`)**:
   - Overview with milestone deadlines and active project progress horizontal bar chart.
   - **Assigned Challenges Queue**: Review state allocations; Accept, Decline with reason, or Request Clarification.
   - **Active Projects Workspace**: Real-time project tracking.
   - **Team Management**: Formulate interdisciplinary research teams with faculty investigators, research scholars, and student engineers.
   - **Technical Proposals**: Formulate engineering methodologies, equipment budgets, and community impacts for state funding.
   - **Milestones Management**: Define deliverables and toggle status (`Pending` ➔ `In Progress` ➔ `Completed`), which **automatically recalculates overall project progress percentage**.

5. **12 Challenge Status States**:
   `Submitted` &rarr; `Under Review` &rarr; `Clarification Required` / `Validated` / `Rejected` &rarr; `University Assigned` &rarr; `Accepted` &rarr; `Proposal Submitted` &rarr; `In Progress` &rarr; `Prototype Ready` &rarr; `Pilot Testing` &rarr; `Completed`.

---

## 🔑 Demo Accounts

You can click the 1-click demo buttons on the login page or enter:

| Role | Email | Password | Representative Entity |
| :--- | :--- | :--- | :--- |
| **Citizen** | `citizen@demo.com` | `demo123` | Ramesh Soren (Gram Vikas Samiti, Khunti) |
| **Government** | `government@demo.com` | `demo123` | Dr. Ananya Verma, IAS (Directorate of Higher & Tech Education) |
| **University** | `university@demo.com` | `demo123` | Prof. Rajeshwar K. Jha (BIT Mesra, Ranchi) |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14, Flask, Flask-Login, Flask-SQLAlchemy (SQLite)
- **Frontend**: HTML5, Vanilla CSS, Bootstrap 5, Bootstrap Icons, Chart.js, Vanilla JavaScript
- **Architecture**: Modular Flask Blueprints (`auth`, `citizen`, `government`, `university`)
- **Color Theme**:
  - Primary Dark Green: `#0B2B20`
  - Secondary Green: `#124C3A`
  - Accent Mint: `#63B99A`
  - Light Mint: `#DDF1E9`
  - Cream Background: `#F7F5EC`
  - White Cards with soft elevation

---

## 💻 Windows Setup & Run Instructions

### Step 1: Open PowerShell or Command Prompt
Navigate to the project directory:
```powershell
cd "c:\Users\Sai Pamu\SIH 2026"
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Application
```powershell
python run.py
```

The database will be automatically initialized and pre-seeded with realistic Jharkhand challenges, universities, projects, and notifications on first run!

### Step 4: Access in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 📁 Directory Structure

```
SIH 2026/
├── app/
│   ├── __init__.py          # Flask application factory, filters, role protection
│   ├── config.py            # App configurations & upload paths
│   ├── models.py            # 11 SQLAlchemy models + 12 status lifecycle
│   ├── seed.py              # Realistic Jharkhand database seeder
│   ├── auth/                # Authentication Blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── citizen/             # Citizen Blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── government/          # Government Blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── university/          # University Blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css     # Brand color tokens, sidebar, tables, badges
│   │   │   └── login.css    # Split-screen styling matching reference
│   │   ├── js/
│   │   │   ├── main.js      # Global UI behaviors & toasts
│   │   │   ├── login.js     # Show/hide password & 1-click quick-fill
│   │   │   └── charts.js    # Chart.js configs for dashboards
│   │   └── uploads/         # Uploaded challenge evidence
│   └── templates/
│       ├── base.html        # Shared dashboard layout (dark green sidebar + cream body)
│       ├── 403.html         # Custom 403 Forbidden page
│       ├── 404.html         # Custom 404 Not Found page
│       ├── auth/login.html  # Split-screen login page
│       ├── citizen/         # 5 Citizen templates
│       ├── government/      # 6 Government templates
│       └── university/      # 6 University templates
├── instance/
│   └── jig.sqlite           # SQLite database
├── run.py                   # Development runner
├── requirements.txt
└── README.md
```
