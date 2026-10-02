MASTER PROMPT — AI-CTDRS WEB APPLICATION

You are acting as a SENIOR FULL-STACK ENGINEER, AI/ML ENGINEER, CYBERSECURITY ENGINEER, UI/UX ENGINEER, and TECHNICAL PROJECT LEAD.

I need you to build the web application for this project:

“AI-POWERED CYBER THREAT DETECTION AND RESPONSE SYSTEM (AI-CTDRS)”

IMPORTANT:
This is an urgent academic/demo project. Prioritize a working, convincing, presentable web application over unnecessary complexity. Do not spend the available development time over-engineering features that are not necessary for the demo.

==================================================
1. SOURCE OF TRUTH
==================================================

I have provided project documentation containing the intended implementation, architecture, methodology, datasets, ML approach, API structure, database entities, UI modules, and deployment approach.

Before changing anything:

1. Inspect the entire existing repository.
2. Inspect package.json / requirements.txt / pyproject.toml.
3. Inspect the frontend structure.
4. Inspect the backend structure.
5. Inspect existing API routes.
6. Inspect existing database/models.
7. Inspect existing ML/model files.
8. Inspect environment variables.
9. Inspect README/documentation.
10. Determine what is already implemented before writing new code.

DO NOT blindly recreate the project from scratch if useful code already exists.

Reuse existing working components wherever possible.

The project documentation describes a system with:

FRONTEND:
- React
- TypeScript
- Tailwind CSS
- Chart.js
- Dark SOC/security-dashboard design

BACKEND:
- Django
- Django REST Framework
- PostgreSQL for production
- SQLite for development
- JWT authentication
- REST APIs
- WebSockets/Django Channels where applicable

AI/ML:
- Random Forest
- XGBoost
- SHAP
- LIME
- Network intrusion/threat classification
- Threat severity/confidence
- Explainable AI

DATA:
- CIC-IDS2017
- NSL-KDD
- CIC-IDS2018

The documented system contains concepts including:
- Authentication
- Threat analysis
- Threat history
- Incidents
- Alerts
- Dashboard/analytics
- Explainability
- User management
- Settings
- Audit/history
- Automated/assisted response

Do not invent functionality and claim it already exists.

If something is not implemented, either implement a practical MVP version or clearly isolate it as a simulated/demo capability.

==================================================
2. PRIMARY OBJECTIVE
==================================================

Build a fully usable web application that demonstrates the AI-CTDRS concept from beginning to end.

The core flow should be:

USER LOGIN
      ↓
SECURITY DASHBOARD
      ↓
SUBMIT / SIMULATE THREAT DATA
      ↓
AI THREAT ANALYSIS
      ↓
THREAT CLASSIFICATION
      ↓
SEVERITY + CONFIDENCE
      ↓
EXPLANATION
      ↓
ALERT
      ↓
INCIDENT CREATION
      ↓
RESPONSE ACTION
      ↓
AUDIT / HISTORY

The application must feel like a real Security Operations Center (SOC) platform.

==================================================
3. DEVELOPMENT PRIORITY
==================================================

Work in this order:

PHASE 1 — INSPECT
- Understand the existing repository.
- Identify what works.
- Identify broken features.
- Identify missing pieces.

PHASE 2 — CORE APPLICATION
Make sure the following work first:

1. Login/register if authentication is already part of the project.
2. Dashboard.
3. Threat analysis.
4. Threat result.
5. Threat history.
6. Alerts.
7. Incidents.
8. Basic response action.
9. Analytics.
10. Explainability.

PHASE 3 — POLISH
After functionality works:
- Improve UI.
- Improve loading states.
- Improve error handling.
- Improve responsive design.
- Improve charts.
- Improve navigation.
- Improve empty states.
- Improve security-dashboard presentation.

PHASE 4 — DEPLOYMENT
Only after the application works locally:
- Verify production build.
- Verify environment variables.
- Verify API communication.
- Verify CORS.
- Verify frontend routing.
- Verify backend health endpoint.
- Prepare deployment configuration.

==================================================
4. UI / UX REQUIREMENTS
==================================================

The interface must look like a professional cybersecurity SOC dashboard.

Use a dark security-oriented interface.

Suggested visual language:

- Dark background
- Dark cards/panels
- Blue/cyan security accents
- Red = critical/high threat
- Orange = medium
- Yellow = warning
- Green = safe/low
- Clear typography
- Strong hierarchy
- Minimal unnecessary decoration

The application should NOT look like a generic CRUD dashboard.

It should visually communicate:

CYBERSECURITY
AI
THREAT DETECTION
SOC
REAL-TIME MONITORING
INCIDENT RESPONSE

Main navigation should include appropriate sections such as:

- Dashboard
- Threat Analysis
- Threats
- Incidents
- Alerts
- Analytics
- Users/Admin
- Settings

Do not add pages that have no useful purpose.

==================================================
5. DASHBOARD
==================================================

Create a useful SOC dashboard.

Display cards such as:

- Total Threats
- Critical Threats
- Active Incidents
- Unresolved Alerts
- Detection Accuracy
- Average Confidence

Include useful visualizations such as:

- Threats over time
- Threat categories
- Severity distribution
- Detection status
- Recent threats
- Recent alerts

If real backend data is unavailable, create a clean demo-data layer.

IMPORTANT:
Demo data must be clearly structured so that it can later be replaced by real API data.

Do not hard-code random values throughout UI components.

==================================================
6. THREAT ANALYSIS
==================================================

This is one of the most important pages.

Create a professional threat-analysis interface.

The user should be able to submit threat/network-flow information.

Possible fields include the documented network-flow features.

The system should send the data to the backend analysis endpoint where available.

Expected response:

- Threat type
- Severity
- Confidence
- Detection status
- Explanation
- Recommended action
- Timestamp
- Threat ID

Example threat categories may include:

- Benign
- DDoS
- PortScan
- Botnet
- Infiltration
- Web Attack
- Brute Force

Do not falsely claim that an AI model analyzed data if the backend is only using mock/demo logic.

If the real ML model is available, use it.

If the real model is unavailable, create a clearly structured DEMO/ SIMULATION analysis service that can later be replaced with the actual model.

==================================================
7. AI EXPLAINABILITY
==================================================

The interface should support SHAP/LIME-style explanations where available.

Display:

- Important features
- Feature contribution
- Why the model classified the traffic as suspicious
- Confidence
- Threat classification

Example:

THREAT DETECTED

Type:
DDoS

Severity:
CRITICAL

Confidence:
97.4%

Top contributing features:
- Flow Duration
- Packet Length Mean
- Destination Port
- Flow Packets/s

Recommended Action:
Block / Isolate / Investigate

If actual SHAP/LIME output exists, use it.

Do not fabricate SHAP/LIME results and present them as genuine model explanations.

==================================================
8. THREAT MANAGEMENT
==================================================

Create a Threats page containing a professional table.

Columns can include:

- ID
- Threat Type
- Source IP
- Destination IP
- Severity
- Confidence
- Status
- Detected At
- Action

Support:

- Search
- Filtering
- Severity filtering
- Status filtering
- Threat-type filtering
- View details

Threat details should show:

- Network information
- Classification
- Severity
- Confidence
- Explanation
- Timeline
- Response status

==================================================
9. INCIDENT MANAGEMENT
==================================================

Incidents should group related threats.

Each incident should have:

- Incident ID
- Title
- Severity
- Status
- Assigned analyst
- Related threats
- Created date
- Updated date
- Resolution information

Statuses can include:

- Open
- Investigating
- Contained
- Resolved

Provide an incident-details page/panel.

==================================================
10. ALERT SYSTEM
==================================================

Create an alert system.

Alerts should communicate events such as:

- Critical threat detected
- High-risk traffic detected
- Incident created
- Threat contained
- Response action completed

Use clear severity indicators.

Where WebSockets are already implemented, use them.

If WebSockets are not currently functional, do not waste excessive time building an elaborate real-time infrastructure.

Implement a reliable fallback using API polling/demo event simulation if necessary.

==================================================
11. RESPONSE SYSTEM
==================================================

Implement a practical response layer.

Possible actions:

- Investigate
- Mark as acknowledged
- Contain
- Block source
- Isolate
- Resolve incident

For an academic/demo system, response actions may be simulated.

IMPORTANT:

Do not actually execute dangerous host/network commands on the development machine.

For example, do NOT automatically modify:

- firewall rules
- operating-system processes
- network interfaces
- system files

Instead, represent the response action safely in the application:

Response:
“Source IP blocked”

Status:
“Simulated / Demo Response”

Record the action in the audit/history system.

==================================================
12. AUTHENTICATION
==================================================

Use the existing authentication implementation if present.

Expected functionality:

- Login
- Register if required
- JWT authentication
- Refresh token
- Profile
- Logout
- Protected routes

Roles:

ADMIN
SECURITY ANALYST

Implement role-based access where appropriate.

Do not weaken authentication just to make the demo work.

==================================================
13. BACKEND API
==================================================

Use the existing API architecture where possible.

Important endpoints may include:

/api/auth/login/
/api/auth/register/
/api/auth/profile/

/api/threats/
/api/threats/analyze/

/api/incidents/

/api/alerts/

/api/analytics/dashboard/

/api/settings/

Before creating duplicate endpoints, inspect whether equivalent endpoints already exist.

Maintain clean API separation.

Return consistent JSON structures.

Handle:

- validation errors
- authentication errors
- server errors
- missing data
- malformed requests

==================================================
14. DATABASE
==================================================

Use the existing database architecture.

Core entities should support:

USER
THREAT
INCIDENT
ALERT

Threat data should support fields such as:

- source IP
- destination IP
- threat type
- severity
- confidence
- status
- timestamps
- network-flow features where applicable
- explanation
- response status

Incident data should support:

- related threats
- assignment
- status
- actions
- resolution
- timestamps

Alerts should support:

- message
- severity
- status
- related threat/incident
- timestamp

Do not destroy existing migrations or database data unnecessarily.

==================================================
15. ML INTEGRATION
==================================================

IMPORTANT:

First inspect the repository to determine which ML models actually exist.

The project documentation describes Random Forest + XGBoost and explainability with SHAP/LIME.

The proposal also discusses deep-learning approaches.

DO NOT randomly introduce another ML architecture just because it sounds impressive.

Use the models that actually exist in the codebase.

If models exist:
- load them properly
- create a clean prediction service
- expose predictions through the backend
- return confidence/classification
- connect results to the frontend

If models do not exist:
- create a clean ML service interface
- implement a reliable demo classifier/simulation
- make it obvious in code that it is replaceable with the trained model

Do not pretend a fake model is a trained production model.

==================================================
16. DATASET HANDLING
==================================================

Do not unnecessarily bundle multi-gigabyte datasets into the web application.

If dataset files already exist:
- inspect how they are used
- use them appropriately

If they do not exist:
- do not download huge datasets unless absolutely necessary

The web application does not need the entire CIC-IDS2017 dataset bundled into the frontend.

==================================================
17. SECURITY
==================================================

Apply basic web security.

Check:

- JWT handling
- CORS
- environment variables
- input validation
- API authorization
- password hashing
- sensitive data exposure
- XSS risks
- unsafe HTML rendering
- error leakage
- insecure API endpoints

Never put secrets directly in frontend code.

Use environment variables.

==================================================
18. PERFORMANCE
==================================================

The application must remain lightweight enough for a demo deployment.

Avoid:

- unnecessary dependencies
- giant frontend bundles
- duplicate libraries
- unnecessary ML packages
- huge datasets shipped to the browser

Lazy-load large frontend components where useful.

==================================================
19. ERROR HANDLING
==================================================

Never allow a backend failure to make the UI look completely broken.

Implement:

- loading states
- error states
- retry buttons
- empty states
- API unavailable state
- authentication expiry handling

For example:

“AI Analysis Service Unavailable”

rather than a blank screen.

==================================================
20. DEMO MODE
==================================================

The application must have a reliable demo path.

I should be able to start the application and demonstrate:

1. Login
2. Open dashboard
3. Analyze traffic
4. Detect a threat
5. Show severity
6. Show confidence
7. Show explanation
8. Create/view incident
9. Receive/view alert
10. Perform response action
11. View the result in history/dashboard

If real infrastructure is unavailable, use a clearly separated demo service.

The demo must NEVER randomly fail.

==================================================
21. RESPONSIVENESS
==================================================

The application must work on:

- Desktop
- Laptop
- Tablet
- Mobile

Prioritize desktop because this is a SOC dashboard, but do not allow mobile layouts to completely break.

==================================================
22. CODE QUALITY
==================================================

Follow clean architecture.

Do not put massive amounts of logic inside React components.

Separate:

- API services
- hooks
- components
- pages
- types
- utilities
- state management

Backend should separate:

- views/controllers
- serializers
- models
- services
- ML logic
- response logic

Use TypeScript types properly.

Avoid unnecessary `any`.

Do not duplicate code.

==================================================
23. GIT SAFETY
==================================================

IMPORTANT:

DO NOT destroy existing work.

Before making major changes:

- inspect git status
- inspect current branch
- inspect recent commits

Work safely.

Do not force-reset the repository.

Do not delete existing functionality unless it is clearly broken and unnecessary.

Do not make destructive database changes without understanding the consequences.

If a feature branch already exists, continue using it.

If appropriate, create a feature branch such as:

feature/ai-ctdrs-web-app

==================================================
24. TESTING
==================================================

Before declaring the project complete, test:

FRONTEND:
- build
- routing
- login
- dashboard
- threat analysis
- threat list
- incidents
- alerts
- analytics

BACKEND:
- health endpoint
- authentication
- threat analysis endpoint
- threat retrieval
- incident creation
- alert retrieval
- analytics endpoint

Also test:

- invalid login
- invalid API request
- empty threat data
- backend unavailable
- expired authentication
- mobile layout

Fix errors before proceeding.

==================================================
25. DEPLOYMENT
==================================================

After local functionality is working:

Frontend:
- verify production build
- configure API URL through environment variables
- configure SPA routing

Backend:
- verify production configuration
- CORS
- allowed hosts
- environment variables
- database connection
- static files
- health endpoint

Target architecture may use:

Frontend → Netlify/Vercel
Backend → Render
Database → PostgreSQL

But do not change the hosting platform if the repository is already configured for another valid platform.

==================================================
26. IMPORTANT TIME CONSTRAINT
==================================================

This is an urgent delivery.

Do NOT spend hours trying to implement every theoretical feature.

If there is a conflict between:

A) an advanced feature that takes hours

and

B) a reliable working feature needed for the demonstration,

choose B.

Priority:

1. Application starts
2. Authentication works
3. Dashboard works
4. Threat analysis works
5. Results work
6. Threat history works
7. Incidents work
8. Alerts work
9. Response simulation works
10. Analytics work
11. UI polish
12. Deployment
13. Optional advanced features

==================================================
27. DO NOT FAKE COMPLETION
==================================================

Never tell me:

“Everything works”

unless you actually tested it.

For every major feature, verify it.

If something cannot be completed, state:

- what is missing
- why it is missing
- what currently works
- what would be required to finish it

Do not hide errors.

==================================================
28. FINAL REPORT
==================================================

When implementation is complete, provide a concise final report containing:

1. What you found in the existing repository.
2. What you changed.
3. Features completed.
4. Features simulated/demo-only.
5. Backend status.
6. Frontend status.
7. ML status.
8. Database status.
9. Tests performed.
10. Build result.
11. Deployment readiness.
12. Any remaining blockers.

Also provide:

LOCAL FRONTEND URL
LOCAL BACKEND URL
HEALTH ENDPOINT
LOGIN TEST ACCOUNT if one exists
DEMO FLOW

==================================================
29. MOST IMPORTANT INSTRUCTION
==================================================

DO NOT START BY WRITING CODE.

FIRST:
- inspect the repository
- understand the architecture
- identify existing functionality
- identify missing functionality
- identify the fastest safe implementation path

Then implement systematically.

Do not ask me unnecessary questions when the repository already contains enough information to make the decision.

Make reasonable engineering decisions yourself.

Only stop and ask me when a decision genuinely requires information that cannot be determined from the repository or project documentation.

START NOW.

FIRST ACTION:
Inspect the repository and give me a concise implementation assessment before making destructive or major architectural changes.