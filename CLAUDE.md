# HACK4UCAR 2025 — Intelligent University Management Platform

## Project Overview

**Competition:** HACK4UCAR 2025 — Organized by University of Carthage (UCAR) & ACM ENSTAB  
**Track:** Track 4 — End-to-End Smart Platform  
**Theme:** Digitalization & Institutional Intelligence

### Problem Statement

UCAR oversees 30+ affiliated institutions, each running fragmented, non-digitalized systems (paper, Excel, disconnected tools). There is no centralized data management, no real-time performance monitoring, and decision-making is slow and unreliable.

### Target Vision

Build an **AI-powered intelligent university management platform** enabling:
- Real-time centralization of operational, academic, financial, and environmental data
- Strategic decision-making driven by KPIs
- Consolidated multi-institution view scalable to 30+ institutions

---

## Architecture

### Multi-Tenant Architecture (mandatory)
- Single deployment managing all 30+ institutions in isolation
- Each institution = one tenant with scoped data access
- Central aggregation layer for cross-institution KPI comparison
- Role-based access: Super Admin (UCAR) > Institution President > Dean > Staff

### System Layers

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                     │
│   Web Dashboard (React/Next.js) + Mobile (React Native) │
├─────────────────────────────────────────────────────────┤
│                      AI LAYER                            │
│  Anomaly Detection | Predictive Analytics | NLP Chatbot │
│  Report Generation | Explainable AI Outputs             │
├─────────────────────────────────────────────────────────┤
│                   API / BACKEND LAYER                    │
│         FastAPI / Node.js + REST + WebSockets            │
├──────────────────────────┬──────────────────────────────┤
│      DATA INGESTION      │      UNIFIED DATA MODEL      │
│  OCR Pipeline (PDFs)     │  PostgreSQL (multi-tenant)   │
│  Excel Import            │  TimescaleDB (time-series)   │
│  Manual Entry Forms      │  Redis (cache / alerts)      │
└──────────────────────────┴──────────────────────────────┘
```

### Unified Data Model
- Common schema across all institutions enabling cross-institution aggregation
- `institution_id` as the tenant key on every table
- Normalized KPI tables with historical versioning for trend analysis
- Audit trail on all data mutations

---

## Key Features (Priority Order)

### 1. Multi-Institution Consolidated Dashboard
- Real-time KPI aggregation and comparison across all institutions
- Institution ranking / benchmarking views
- Drill-down: UCAR global → Institution → Department → Team
- Time-range filters: daily, weekly, monthly, annual, custom

### 2. Intelligent Alert System
- Rule-based threshold alerts (e.g., dropout rate > 15%)
- AI anomaly detection on KPI time-series
- Alert severity levels: Info / Warning / Critical
- Notification channels: in-app, email, SMS
- Alert history and acknowledgement workflow

### 3. Automated Periodic Reports
- Scheduled report generation: weekly, monthly, annual
- PDF and Excel export (mandatory per judging criteria)
- AI-generated narrative summaries accompanying the data
- Customizable report templates per institution or process domain

### 4. Predictive Analytics Engine
- Trend forecasting for budget consumption, enrollment, dropout risk
- Risk scoring per institution (composite KPI health index)
- "What-if" scenario simulation for strategic planning
- Explainable outputs: plain-language justification for each prediction

### 5. NLP Chatbot Interface
- Query institutional data in natural language (French + English + Arabic)
- Example queries: "What is the dropout rate at ENSTAB this semester?"
- Powered by Claude API (Anthropic) with RAG over institutional data
- Accessible to non-technical staff (deans, presidents, admins)

### 6. Data Ingestion Pipeline
- OCR + AI extraction from PDFs and scanned documents
- Excel/CSV bulk import with validation and conflict resolution
- Manual entry forms with field-level validation
- Data quality scoring and flagging

---

## KPI Reference Framework

### Academic
- Success rate, attendance rate, grade repetition rate, dropout rate
- Pedagogical progression, exam results by subject/department

### Employment & Insertion
- Employability rate, time-to-employment post-graduation
- National convention rate, international convention rate
- Alumni tracking (6-month, 12-month post-graduation)

### Finance
- Allocated vs consumed budget (by department, by institution)
- Budget execution rate, cost per student
- Spending breakdown by category

### ESG / CSR
- Energy consumption (kWh/student), carbon footprint
- Recycling rate, sustainable mobility rate
- Campus accessibility score

### Human Resources
- Teaching headcount, administrative headcount ratio
- Absenteeism rate, training hours completed
- Teaching load (hours/week), team stability rate

### Research
- Number of publications, active research projects
- Funding secured (TND + EUR/USD), patents filed
- Academic partnerships active

### Infrastructure & Equipment
- Classroom occupancy rate, IT equipment status
- Equipment availability rate, ongoing works count

### Partnerships
- Active national/international agreements
- Incoming student mobility count, outgoing mobility count
- International projects active

### Student Life
- Student association activity count
- Cultural/sports event frequency
- Campus service satisfaction score

---

## Dashboard Modules (Process Coverage)

Each module has its own KPI view and synthesis report:

| Module | Key Data Points |
|---|---|
| Enrollment | Admitted, enrolled, by program, by level |
| Exams | Results, pass rates, re-sit rates, grade distribution |
| Pedagogy | Course completion, teaching quality, materials coverage |
| Strategy | Institutional objectives vs actuals |
| Partnerships | Agreements, MoUs, mobility statistics |
| Student Life | Activities, satisfaction, engagement rate |
| Finance | Budget, expenses, audit readiness |
| HR | Headcount, payroll, training, attendance |
| Training | Continuing education programs, completion rates |
| Research | Publications, projects, funding, labs |
| Infrastructure | Rooms, occupancy, maintenance tickets |
| Equipment | Inventory, condition, depreciation |
| Inventory / Logistics | Supplies, stock levels, procurement |
| ESG / CSR | Environmental metrics, sustainability goals |

---

## Judging Criteria — How to Score High

| Criterion | What judges look for | Our strategy |
|---|---|---|
| **Impact** | Real usefulness for UCAR | Cover all 14+ processes, show real data flow |
| **Innovation** | AI at the core, not surface | Anomaly detection + predictive engine + NLP chatbot |
| **Usability** | Non-technical staff UX | No-code config, intuitive dashboards, French/Arabic UI |
| **Scalability** | Handles 30+ institutions | Multi-tenant DB, horizontal scaling, tested with mock data |
| **Feasibility** | Tunisian university context | Excel import (existing workflows), PDF export, offline-tolerant |

---

## Technical Stack

### Backend
- **Python / FastAPI** — main API, AI pipeline orchestration
- **PostgreSQL** — primary multi-tenant database
- **Redis** — real-time alert queue, caching
- **Celery + Beat** — scheduled report generation jobs
- **Pandas / SQLAlchemy** — data processing and ORM

### AI / ML
- **Claude API (Anthropic)** — NLP chatbot, report narrative generation, explainable AI
- **Prophet / scikit-learn** — time-series forecasting for KPI trends
- **Isolation Forest / Z-score** — anomaly detection on KPI streams
- **pytesseract / pdfplumber** — OCR pipeline for document ingestion

### Frontend
- **Next.js (React)** — main web dashboard
- **Recharts / Chart.js** — KPI visualizations and comparative charts
- **React Native / Expo** — mobile companion app
- **Tailwind CSS** — consistent, fast UI styling

### Exports & Reporting
- **ReportLab / WeasyPrint** — PDF report generation
- **openpyxl / xlsxwriter** — Excel export
- **Jinja2** — report templates

### Infrastructure
- **Docker + Docker Compose** — local dev and demo deployment
- **Nginx** — reverse proxy
- **MinIO** (or S3-compatible) — document and report storage

---

## Claude API Integration Pattern

```python
# Use prompt caching for repeated system context (institution data schemas)
# Use streaming for chatbot responses
# Use structured output for KPI extraction from documents

import anthropic

client = anthropic.Anthropic()

# Chatbot query over institutional data
def query_institution_data(question: str, institution_context: dict):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT_WITH_SCHEMA,
                "cache_control": {"type": "ephemeral"}  # cache the system prompt
            }
        ],
        messages=[
            {"role": "user", "content": f"Context: {institution_context}\n\nQuestion: {question}"}
        ]
    )
    return response.content[0].text

# Report narrative generation
def generate_report_narrative(kpi_data: dict, period: str):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"Generate a concise executive summary for this {period} institutional report:\n{kpi_data}"
        }]
    )
    return response.content[0].text
```

---

## Data Model (Core Tables)

```sql
-- Tenant / Institution
institutions (id, name, type, city, created_at)

-- Users with role-based access
users (id, institution_id, role ENUM('super_admin','president','dean','staff'), ...)

-- Unified KPI store (time-series)
kpi_records (
  id, institution_id, domain ENUM('academic','finance','hr','research',...),
  indicator_key VARCHAR, value DECIMAL, unit VARCHAR,
  period_start DATE, period_end DATE, recorded_at TIMESTAMP
)

-- Alert rules and triggered alerts
alert_rules (id, institution_id, indicator_key, operator, threshold, severity)
alerts (id, rule_id, institution_id, value_at_trigger, triggered_at, acknowledged_at)

-- Generated reports
reports (id, institution_id, type, period, file_path, generated_at, generated_by)

-- Document ingestion queue
ingestion_jobs (id, institution_id, source_type, status, file_path, extracted_data JSONB)
```

---

## Development Priorities for Hackathon

**Must have (demo-critical):**
1. Login + multi-institution selector
2. Global consolidated KPI dashboard (at least 3 domains: Academic, Finance, HR)
3. One working alert (threshold breach on dropout rate)
4. PDF report export for one module
5. NLP chatbot with 3-5 demo queries working

**Should have:**
6. Anomaly detection visualization
7. Trend chart with prediction line
8. Excel import for bulk KPI entry
9. Mobile-responsive layout

**Nice to have:**
10. OCR document ingestion
11. Full 14-module coverage
12. Email alert notifications
13. Arabic/French language toggle

---

## Demo Data Strategy

Generate realistic mock data for 5 institutions to demonstrate:
- Cross-institution KPI comparison (one institution with anomaly)
- Historical trends (3 semesters of academic data)
- Budget execution showing overspend in one department
- Dropout rate spike triggering an alert

Use a seed script: `python scripts/seed_demo_data.py`

---

## Project Structure

```
hack4ucar/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers per domain
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic (KPIs, alerts, reports)
│   │   ├── ai/           # Claude API, ML models
│   │   └── ingestion/    # OCR, Excel import pipeline
│   ├── scripts/
│   │   └── seed_demo_data.py
│   └── Dockerfile
├── frontend/
│   ├── app/              # Next.js app router
│   │   ├── dashboard/    # Main KPI dashboards
│   │   ├── reports/      # Report viewer and export
│   │   ├── alerts/       # Alert management
│   │   └── chat/         # NLP chatbot interface
│   └── Dockerfile
├── mobile/               # React Native app (optional)
├── docker-compose.yml
└── CLAUDE.md
```

---

## Pitch Structure (5-7 minutes)

1. **Problem** (1 min) — fragmented data, 30+ institutions, no visibility
2. **Solution** (2 min) — live demo of consolidated dashboard + alert + chatbot
3. **AI at the core** (1 min) — anomaly detection, prediction, NLP (not cosmetic)
4. **Scalability** (1 min) — multi-tenant architecture, how it handles 30+ institutions
5. **Impact & Feasibility** (1 min) — Tunisia context, Excel migration path, no training needed
6. **Q&A buffer** (30 sec)

---

## Key Constraints & Non-Negotiables

- AI must be **at the core**, not a surface-level UI element — judges will probe this
- UX must work for **non-technical users** (deans, presidents) — no jargon, no code
- PDF and Excel export are **mandatory** — integrate with existing workflows
- Solution must be **realistically deployable** in a Tunisian university context
- All alerts and predictions must be **explainable in plain language**
