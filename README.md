# UCAR — Plateforme Intelligente de Gestion Universitaire

> **HACK4UCAR 2025** · Track 4 — End-to-End Smart Platform  
> Organisé par l'Université de Carthage (UCAR) & ACM ENSTAB

Une plateforme IA multi-établissements permettant la centralisation en temps réel des données opérationnelles, académiques, financières et environnementales, au service d'une prise de décision stratégique basée sur des KPIs.

---

## Table des matières

- [Aperçu du projet](#aperçu-du-projet)
- [Architecture](#architecture)
- [Fonctionnalités](#fonctionnalités)
- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Installation & Démarrage](#installation--démarrage)
- [Comptes de démonstration](#comptes-de-démonstration)
- [Import de données (Excel / CSV)](#import-de-données-excel--csv)
- [KPIs & Domaines](#kpis--domaines)
- [API Reference](#api-reference)
- [Déploiement](#déploiement)
- [Données de démonstration](#données-de-démonstration)

---

## Aperçu du projet

### Problème

L'Université de Carthage supervise 30+ établissements affiliés, chacun utilisant des systèmes fragmentés et non numérisés (papier, Excel, outils déconnectés). Il n'existe aucune centralisation des données, aucun suivi de performance en temps réel, et la prise de décision est lente et peu fiable.

### Solution

Une plateforme unique qui :

- **Centralise** toutes les données institutionnelles en temps réel
- **Détecte** automatiquement les anomalies par intelligence artificielle
- **Prédit** les tendances futures (budget, abandon, employabilité…)
- **Génère** des rapports PDF et Excel avec résumés narratifs IA
- **Répond** aux questions en langage naturel via un chatbot multilingue (FR/EN/AR)
- **Segmente** les accès par établissement et par département

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│            FRONTEND — Next.js 14 (Static Export)                │
│     GitHub Pages · Tailwind CSS · Recharts · Zustand           │
│  /login  /dashboard  /alerts  /reports  /chat                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API (JWT)
┌──────────────────────────▼──────────────────────────────────────┐
│              BACKEND — FastAPI (Python 3.11)                     │
│  /api/v1/auth  /institutions  /departments  /kpis               │
│  /alerts  /reports  /chat  /ingestion                           │
│  Celery + Beat (jobs planifiés)                                  │
└───────┬──────────────────┬──────────────────────────────────────┘
        │                  │
   PostgreSQL           Redis
   (multi-tenant)    (cache + queue)
        │
   ┌────┴──────────────────────────────┐
   │           COUCHE IA               │
   │  Groq API (LLM)                  │
   │  Z-score → détection d'anomalies │
   │  Régression linéaire → prévision │
   │  ReportLab → génération PDF       │
   └───────────────────────────────────┘
```

### Multi-tenancy

- Chaque établissement est un **tenant isolé** via `institution_id` sur chaque table
- Les comptes **Super Admin UCAR** voient tous les établissements (vue consolidée)
- Les **Présidents** voient toutes les données de leur établissement
- Les **Départements** sont strictement limités à leur domaine de données

---

## Fonctionnalités

### 1. Tableau de bord consolidé multi-établissements

- Vue globale UCAR avec agrégation de tous les KPIs
- Sélecteur d'établissement pour drill-down institution par institution
- Comparaison inter-établissements en graphiques à barres
- Filtres par domaine : Académique · Finance · RH · Insertion · ESG · Recherche
- Détection automatique des anomalies (Z-score) avec badge visuel

### 2. Alertes intelligentes

- Règles de seuil configurables (ex : taux d'abandon > 15%)
- Déclenchement automatique toutes les heures (Celery Beat)
- Niveaux de sévérité : Info · Avertissement · Critique
- Explication en langage naturel pour chaque alerte
- Workflow d'acquittement avec historique

### 3. Rapports automatiques (PDF & Excel)

- Génération à la demande par période et par domaine
- **PDF** : mise en page institutionnelle avec résumé exécutif IA
- **Excel** : classeur multi-feuilles avec un onglet par domaine
- Téléchargement direct depuis l'interface
- Résumés narratifs générés par le LLM Groq

### 4. Moteur d'analyse prédictive

- Tendance historique sur 3 semestres affichée en graphique
- Prévision linéaire sur les 3 prochaines périodes
- Indicateur de tendance : croissant · décroissant · stable
- Calcul du coefficient de pente pour chaque indicateur

### 5. Chatbot IA (Groq)

- Requêtes en langage naturel (français)
- Contexte injecté dynamiquement depuis les données KPI en base
- Suggestions de questions intégrées
- Streaming de réponse en temps réel
- Exemples : *"Quel est le taux d'abandon à l'ENSTAB ?"*, *"Comparez les budgets des établissements"*

### 6. Import de données (Excel / CSV)

- Bouton **Importer** dans le tableau de bord
- Accepte `.xlsx`, `.xls`, `.csv`
- Normalisation automatique des colonnes et des domaines
- Comptes département : domaine auto-forcé à leur périmètre
- Résultat immédiat : nombre d'indicateurs importés + erreurs

---

## Stack technique

### Backend

| Technologie | Usage |
|---|---|
| **FastAPI** | API REST principale, orchestration IA |
| **PostgreSQL** | Base de données multi-tenant principale |
| **Redis** | Cache, queue d'alertes |
| **Celery + Beat** | Jobs planifiés (alertes horaires, rapports) |
| **SQLAlchemy 2** | ORM + modèles multi-tenant |
| **Alembic** | Migrations de base de données |
| **bcrypt** | Hashage des mots de passe |
| **python-jose** | JWT (authentification) |

### Intelligence artificielle

| Technologie | Usage |
|---|---|
| **Groq API** (`openai/gpt-oss-120b`) | Chatbot NLP, résumés de rapports, narration IA |
| **scipy / numpy** | Détection d'anomalies (Z-score) |
| **scikit-learn** | Prévision par régression linéaire |
| **pandas** | Traitement des fichiers Excel/CSV importés |

### Génération de rapports

| Technologie | Usage |
|---|---|
| **ReportLab** | Génération PDF avec mise en page institutionnelle |
| **openpyxl** | Génération Excel multi-feuilles |

### Frontend

| Technologie | Usage |
|---|---|
| **Next.js 14** | Framework React (App Router, export statique) |
| **Tailwind CSS** | Styling utilitaire |
| **Recharts** | Graphiques KPI (courbes, barres) |
| **Zustand** | State management (auth, institution) |
| **Axios** | Client HTTP avec intercepteur JWT |
| **lucide-react** | Icônes |
| **date-fns** | Formatage des dates en français |

### Infrastructure

| Technologie | Usage |
|---|---|
| **Docker + Docker Compose** | Environnement de dev et démo |
| **GitHub Actions** | CI/CD → déploiement automatique GitHub Pages |

---

## Structure du projet

```
Hack4UCAR/
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD GitHub Pages
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── auth.py             # Login, JWT, /me
│   │   │   ├── institutions.py     # CRUD établissements
│   │   │   ├── departments.py      # CRUD départements
│   │   │   ├── kpis.py             # KPIs + tendances + comparaison
│   │   │   ├── alerts.py           # Alertes + règles + acquittement
│   │   │   ├── reports.py          # Génération + téléchargement PDF/Excel
│   │   │   ├── chat.py             # Chatbot Groq (streaming SSE)
│   │   │   └── ingestion.py        # Import Excel/CSV
│   │   ├── ai/
│   │   │   ├── anomaly.py          # Z-score + prévision linéaire
│   │   │   └── chatbot.py          # Intégration Groq API
│   │   ├── core/
│   │   │   ├── config.py           # Settings (env vars)
│   │   │   ├── database.py         # Engine SQLAlchemy + session
│   │   │   └── security.py         # bcrypt + JWT
│   │   ├── dependencies/
│   │   │   └── auth.py             # get_current_user, RBAC, scoping
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── services/               # Logique métier (KPI, alertes, rapports)
│   │   ├── main.py                 # FastAPI app + CORS
│   │   └── worker.py               # Celery tasks
│   ├── alembic/                    # Migrations DB
│   ├── scripts/
│   │   └── seed_demo_data.py       # Données de démonstration
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── login/page.tsx          # Page de connexion
│   │   ├── dashboard/page.tsx      # Tableau de bord KPI
│   │   ├── alerts/page.tsx         # Gestion des alertes
│   │   ├── reports/page.tsx        # Rapports PDF/Excel
│   │   └── chat/page.tsx           # Chatbot IA
│   ├── components/
│   │   ├── layout/                 # Sidebar, Header, DashboardLayout
│   │   └── dashboard/              # KPICard, KPIChart, ComparisonChart, UploadButton
│   ├── lib/
│   │   ├── api.ts                  # Client Axios + intercepteur JWT
│   │   └── types.ts                # Types TypeScript partagés
│   ├── store/
│   │   └── auth.ts                 # Zustand store (auth + hydratation)
│   └── next.config.js              # Export statique GitHub Pages
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Installation & Démarrage

### Prérequis

- Docker & Docker Compose
- Node.js 20+ (pour le frontend en dev)
- Clé API Groq (https://console.groq.com)

### 1. Cloner et configurer

```bash
git clone https://github.com/Akrem-Alamine/Hack4UCAR.git
cd Hack4UCAR

# Copier et remplir le fichier d'environnement
cp .env.example .env
# Éditez .env et renseignez votre GROQ_API_KEY
```

### 2. Démarrer les services (Docker)

```bash
# Démarrer PostgreSQL et Redis
docker compose up -d db redis

# Builder et démarrer le backend
docker compose up -d --build backend

# Appliquer les migrations
docker compose run --rm backend alembic upgrade head

# Charger les données de démonstration
docker compose run --rm backend python -m scripts.seed_demo_data
```

### 3. Démarrer le frontend (développement)

```bash
cd frontend
npm install
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

### 4. Accéder à la plateforme

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Documentation API (Swagger) | http://localhost:8000/docs |
| Documentation API (ReDoc) | http://localhost:8000/redoc |

---

## Comptes de démonstration

> Mot de passe unique pour tous : **`demo1234`**

### Super Admin UCAR

| Email | Accès |
|---|---|
| `super@ucar.tn` | Vue consolidée de tous les établissements |

### Par établissement (exemple ENSTAB — même structure pour ENIT, ESPRIT, FST, ISETSOUSSE)

| Email | Rôle | Données accessibles |
|---|---|---|
| `president@enstab.tn` | Président | Tous les domaines de l'établissement |
| `academique@enstab.tn` | Département | Académique uniquement |
| `finance@enstab.tn` | Département | Finance uniquement |
| `rh@enstab.tn` | Département | Ressources Humaines uniquement |
| `insertion@enstab.tn` | Département | Insertion Professionnelle uniquement |
| `esg@enstab.tn` | Département | ESG / RSE uniquement |
| `recherche@enstab.tn` | Département | Recherche uniquement |

**Règle de scoping** : un compte département ne peut voir, ni importer de données en dehors de son domaine — le backend l'applique côté serveur, indépendamment de ce que le frontend envoie.

---

## Import de données (Excel / CSV)

### Format attendu

Le fichier doit contenir les colonnes suivantes (noms en minuscules, espaces ou underscores) :

| Colonne | Obligatoire | Description | Exemple |
|---|---|---|---|
| `domain` | Oui* | Domaine du KPI | `academic`, `finance`, `rh` |
| `indicator_key` | Oui | Identifiant de l'indicateur | `success_rate`, `dropout_rate` |
| `value` | Oui | Valeur numérique | `82.5` |
| `unit` | Oui | Unité de mesure | `%`, `TND`, `kWh` |
| `period_label` | Oui | Libellé de la période | `2024-2025 S1` |
| `period_start` | Oui | Début de la période | `2024-09-01` |
| `period_end` | Oui | Fin de la période | `2025-01-31` |
| `department_code` | Non | Code du département | `FIN`, `RH`, `ACAD` |
| `notes` | Non | Commentaire libre | `Données validées` |

> *Pour les comptes département, la colonne `domain` est ignorée — le domaine est automatiquement forcé à celui du compte connecté.

### Alias de domaine acceptés (français)

| Valeur dans le fichier | Domaine reconnu |
|---|---|
| `academique`, `académique` | `academic` |
| `rh`, `ressources humaines` | `hr` |
| `recherche` | `research` |
| `partenariats` | `partnerships` |
| `rse`, `esg` | `esg` |
| `insertion professionnelle` | `insertion` |

### Endpoint de consultation du template

```
GET /api/v1/ingestion/template
```

---

## KPIs & Domaines

### Académique (`academic`)

| Indicateur | Unité |
|---|---|
| `success_rate` — Taux de réussite | % |
| `attendance_rate` — Taux de présence | % |
| `dropout_rate` — Taux d'abandon | % |
| `repetition_rate` — Taux de redoublement | % |

### Finance (`finance`)

| Indicateur | Unité |
|---|---|
| `budget_allocated` — Budget alloué | TND |
| `budget_consumed` — Budget consommé | TND |
| `budget_execution_rate` — Taux d'exécution | % |
| `cost_per_student` — Coût par étudiant | TND |

### Ressources Humaines (`hr`)

| Indicateur | Unité |
|---|---|
| `teaching_headcount` — Effectif enseignant | pers. |
| `admin_headcount` — Effectif administratif | pers. |
| `absenteeism_rate` — Taux d'absentéisme | % |
| `training_hours` — Heures de formation | h |

### Insertion Professionnelle (`insertion`)

| Indicateur | Unité |
|---|---|
| `employability_rate` — Taux d'employabilité | % |
| `national_convention_rate` — Convention nationale | % |
| `international_convention_rate` — Convention internationale | % |
| `insertion_delay_months` — Délai d'insertion | mois |

### ESG / RSE (`esg`)

| Indicateur | Unité |
|---|---|
| `energy_consumption_kwh` — Consommation énergétique | kWh |
| `carbon_footprint_ton` — Empreinte carbone | t CO₂ |
| `recycling_rate` — Taux de recyclage | % |

### Recherche (`research`)

| Indicateur | Unité |
|---|---|
| `publications_count` — Publications | pub. |
| `active_projects` — Projets actifs | projets |
| `funding_tnd` — Financements | TND |

---

## API Reference

### Authentification

```http
POST /api/v1/auth/login
Content-Type: application/json

{ "email": "president@enstab.tn", "password": "demo1234" }
```

Retourne un `access_token` JWT à inclure dans tous les appels suivants :
```http
Authorization: Bearer <access_token>
```

### KPIs

```http
# Liste des KPIs (dernier enregistrement par indicateur)
GET /api/v1/kpis/?institution_id=11&domain=academic

# Tendance historique + prévision IA
GET /api/v1/kpis/trend?institution_id=11&indicator_key=dropout_rate

# Comparaison inter-établissements (Super Admin uniquement)
GET /api/v1/kpis/compare?indicator_key=success_rate

# Périodes disponibles
GET /api/v1/kpis/periods?institution_id=11
```

### Alertes

```http
# Liste des alertes actives
GET /api/v1/alerts/?unresolved_only=true

# Déclencher une vérification manuelle
POST /api/v1/alerts/check

# Acquitter une alerte
POST /api/v1/alerts/{id}/acknowledge

# Règles d'alerte
GET /api/v1/alerts/rules
POST /api/v1/alerts/rules
```

### Rapports

```http
# Demander la génération d'un rapport
POST /api/v1/reports/
{ "institution_id": 11, "type": "global", "period_label": "2024-2025 S1", "format": "pdf" }

# Télécharger un rapport généré
GET /api/v1/reports/{id}/download
```

### Chatbot IA

```http
POST /api/v1/chat/
{ "question": "Quel est le taux d'abandon ce semestre ?", "institution_id": 11 }
```

### Import de données

```http
POST /api/v1/ingestion/upload
Content-Type: multipart/form-data

file=<fichier.xlsx>
institution_id=11
period_label_override=2024-2025 S1  (optionnel)
```

### Départements

```http
GET /api/v1/departments/?institution_id=11
POST /api/v1/departments/
DELETE /api/v1/departments/{id}
```

---

## Déploiement

### Frontend — GitHub Pages

Le frontend est automatiquement déployé via GitHub Actions à chaque push sur `main`.

**Configuration requise** (GitHub → Settings → Secrets and variables → Actions) :

| Secret | Valeur |
|---|---|
| `NEXT_PUBLIC_API_URL` | URL de votre backend déployé (ex : `https://ucar-api.onrender.com`) |
| `NEXT_PUBLIC_BASE_PATH` | `/Hack4UCAR` si déployé sur `username.github.io/Hack4UCAR` |

### Backend — Options de déploiement

**Option 1 : Local (démo en présentiel)**
```bash
docker compose up -d
```
Le frontend GitHub Pages pointe vers `http://localhost:8000`.

**Option 2 : Render (cloud gratuit)**
1. Créer un service Web sur [render.com](https://render.com)
2. Connecter le repo GitHub
3. Build command : `pip install -r backend/requirements.txt`
4. Start command : `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Ajouter les variables d'environnement depuis `.env.example`

---

## Données de démonstration

Le script `seed_demo_data.py` génère :

| Élément | Quantité |
|---|---|
| Établissements | 5 (ENSTAB, ENIT, ESPRIT, FST, ISETSOUSSE) |
| Départements | 30 (6 par établissement) |
| Utilisateurs | 36 (1 président + 6 départements × 5 établissements) + 1 super admin |
| Enregistrements KPI | 330 (5 établissements × 6 domaines × ~4 indicateurs × 3 semestres) |
| Règles d'alerte | 4 (abandon critique, réussite faible, budget, absentéisme) |
| Alertes déclenchées | ~6 (dont 1 critique ENSTAB, 1 avertissement ESPRIT) |

**Scénarios de démonstration intégrés :**

- 🔴 **ENSTAB** : taux d'abandon passe de 7% → 8% → **22%** (anomalie + alerte critique)
- 🟡 **ESPRIT** : taux d'exécution budgétaire à **97.7%** (risque dépassement)
- 📈 **ENIT** : meilleur établissement toutes catégories (benchmark de référence)
- 📉 **ISETSOUSSE** : profil en amélioration progressive (tendance positive)

---

## Critères de jugement HACK4UCAR

| Critère | Notre réponse |
|---|---|
| **Impact** | Couvre 6 domaines KPI, 30+ établissements, tous les processus institutionnels |
| **Innovation** | IA au cœur : anomalie Z-score, prévision linéaire, chatbot LLM, narration automatique |
| **Utilisabilité** | Interface 100% française, accès par rôle, import Excel sans code |
| **Scalabilité** | Architecture multi-tenant, Docker, API versionnée, Celery pour les jobs lourds |
| **Faisabilité** | Import Excel (workflow existant), PDF export, données réalistes tunisiennes |

---

## Équipe

Développé pour HACK4UCAR 2025 — Université de Carthage · ACM ENSTAB
