# UCAR — Plateforme Intelligente de Gestion Universitaire

> **HACK4UCAR 2025** · Track 4 — End-to-End Smart Platform  
> Organisé par l'Université de Carthage (UCAR) & ACM ENSTAB

Une plateforme IA multi-établissements permettant la centralisation en temps réel des données opérationnelles, académiques, financières et environnementales, au service d'une prise de décision stratégique basée sur des KPIs.

---

## Table des matières

- [Aperçu du projet](#aperçu-du-projet)
- [Couverture des 4 Tracks](#couverture-des-4-tracks)
- [Architecture](#architecture)
- [Fonctionnalités](#fonctionnalités)
- [Sécurité](#sécurité)
- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Installation & Démarrage](#installation--démarrage)
- [Comptes de démonstration](#comptes-de-démonstration)
- [Import de données](#import-de-données)
- [KPIs & Domaines](#kpis--domaines)
- [API Reference](#api-reference)
- [Déploiement public](#déploiement-public)
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
- **Répond** aux questions en langage naturel via un chatbot streaming
- **Sécurise** les accès par tenant, par rôle et par domaine
- **Ingère** des données depuis des fichiers Excel, CSV, PDF et images

---

## Couverture des 4 Tracks

### Track 1 — Digitalisation & Structuration des données

| Fonctionnalité | Détails |
|---|---|
| Import Excel / CSV standard | Colonnes standard avec validation ligne par ligne |
| Normalisation IA automatique | Si les colonnes ne correspondent pas, Groq les mappe automatiquement |
| Import PDF & images (OCR) | pdfplumber + pytesseract (`fra+ara+eng`) |
| Extraction de KPIs depuis PDF | Groq identifie et structure les indicateurs depuis du texte libre |
| Validation de qualité IA | Score de confiance 0–100 par indicateur extrait |
| File d'attente asynchrone | Jobs d'ingestion trackés en base (pending → processing → completed) |
| Template téléchargeable | `GET /api/v1/ingestion/template` retourne le format attendu |
| Validation des types de fichier | Extension + magic bytes (contenu binaire) vérifiés |
| Limite de taille | Rejet automatique des fichiers > 50 Mo |

### Track 2 — Analytics Intelligentes & Benchmarking

| Fonctionnalité | Détails |
|---|---|
| Détection d'anomalies Z-score | Comparaison valeur courante vs historique, seuil Z > 3 + déviation > 15% |
| Prévision linéaire | Régression sklearn sur 3 semestres → prévision des 3 périodes suivantes |
| Indice de santé institutionnel | Score composite 0–100 pondéré par domaine (18 indicateurs) |
| Niveaux de risque | Faible (≥75) · Moyen (≥50) · Élevé (<50) |
| Classement inter-établissements | Ranking tous établissements par score global avec médailles 🥇🥈🥉 |
| Analyse IA par domaine | Groq génère points forts, points d'attention et recommandations |
| Comparaison graphique | Graphiques à barres inter-établissements |
| Vérification horaire des alertes | Celery Beat déclenche `run_alert_check` toutes les heures |
| Rapports planifiés | PDF hebdomadaires (lundi 7h) et mensuels (1er du mois 6h) |

### Track 3 — Assistants IA & Rapports

| Fonctionnalité | Détails |
|---|---|
| Chatbot NLP en français | Groq LLM avec contexte KPI injecté dynamiquement |
| Streaming temps réel (SSE) | Réponse mot par mot via Server-Sent Events |
| Arrêt du streaming | Bouton ✕ pour interrompre la réponse en cours |
| Rapport PDF institutionnel | ReportLab avec mise en page UCAR + résumé exécutif IA |
| Rapport Excel multi-feuilles | openpyxl avec un onglet par domaine KPI |
| Narration automatique | Groq génère le résumé narratif de chaque rapport |
| Insights par domaine | Analyse contextuelle `GET /api/v1/kpis/insights` |
| Explications des anomalies | Groq explique chaque anomalie en langage naturel |

### Track 4 — Plateforme End-to-End

| Fonctionnalité | Détails |
|---|---|
| Multi-tenancy | `institution_id` sur chaque table, isolation garantie côté serveur |
| RBAC 4 niveaux | Super Admin → Président → Doyen → Staff département |
| Tableau de bord consolidé | Vue globale UCAR + drill-down institution |
| Alertes intelligentes | Seuils configurables, niveaux Info / Warning / Critical |
| Sélecteur d'institution | Changement de contexte sans rechargement |
| Accès public via tunnel | Cloudflare Tunnel → accessible depuis n'importe quel appareil |
| API versionnée | `/api/v1/` avec documentation Swagger intégrée |
| Déploiement Docker | Un seul `docker compose up` lance l'ensemble de la stack |

---

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE TUNNEL (public)                      │
│              https://<slug>.trycloudflare.com                      │
└──────────────────────────────┬────────────────────────────────────┘
                               │
┌──────────────────────────────▼────────────────────────────────────┐
│                    NGINX REVERSE PROXY (:80)                       │
│  /api/*  →  backend:8000    /  →  frontend:3000                   │
│  Security headers · client_max_body_size 50M · server_tokens off  │
└──────────────┬──────────────────────────────────┬─────────────────┘
               │                                  │
┌──────────────▼──────────────┐   ┌───────────────▼───────────────┐
│   BACKEND — FastAPI :8000   │   │  FRONTEND — Next.js :3000     │
│  /api/v1/auth               │   │  /login                       │
│  /api/v1/institutions       │   │  /dashboard                   │
│  /api/v1/kpis               │   │  /alerts                      │
│  /api/v1/alerts             │   │  /reports                     │
│  /api/v1/reports            │   │  /chat                        │
│  /api/v1/chat               │   │  /ingestion                   │
│  /api/v1/ingestion          │   └───────────────────────────────┘
│  /api/v1/departments        │
│  Celery Worker + Beat       │
└────────┬───────────┬────────┘
         │           │
    PostgreSQL     Redis
    (multi-tenant) (cache + queue)
         │
    ┌────┴──────────────────────────────┐
    │           COUCHE IA               │
    │  Groq LLM (chatbot + rapports)   │
    │  Z-score → anomalies             │
    │  Régression linéaire → prévision │
    │  pdfplumber + pytesseract (OCR)  │
    │  ReportLab + openpyxl (exports)  │
    └───────────────────────────────────┘
```

### Multi-tenancy

- Chaque établissement est un **tenant isolé** via `institution_id` sur chaque table
- Les comptes **Super Admin UCAR** voient tous les établissements (vue consolidée)
- Les **Présidents** voient toutes les données de leur établissement
- Les comptes **département** sont strictement limités à leur domaine de données
- Toute tentative d'accès cross-tenant est bloquée par le backend (HTTP 403)

---

## Fonctionnalités

### 1. Tableau de bord consolidé multi-établissements

- Vue globale UCAR avec agrégation de tous les KPIs
- Sélecteur d'établissement pour drill-down institution par institution
- Indice de santé composite (0–100) avec barre de progression par domaine
- Classement inter-établissements avec médailles pour les 3 premiers
- Comparaison graphique inter-établissements en barres
- Filtres par domaine : Académique · Finance · RH · Insertion · ESG · Recherche
- Détection automatique des anomalies avec badge visuel rouge et icône d'alerte
- Bouton **Analyse IA** pour obtenir des insights Groq par domaine

### 2. Alertes intelligentes

- Règles de seuil configurables (ex : taux d'abandon > 15%)
- Déclenchement automatique toutes les heures (Celery Beat)
- Niveaux de sévérité : Info · Avertissement · Critique
- Explication en langage naturel pour chaque alerte
- Workflow d'acquittement avec horodatage
- Vérification manuelle via `POST /api/v1/alerts/check`

### 3. Rapports automatiques (PDF & Excel)

- Génération à la demande par période, domaine et format
- **PDF** : mise en page institutionnelle UCAR avec résumé exécutif généré par Groq
- **Excel** : classeur multi-feuilles avec un onglet par domaine KPI
- Téléchargement direct depuis l'interface
- Génération en arrière-plan (non-bloquant) avec statut en temps réel
- Rapports hebdomadaires et mensuels générés automatiquement

### 4. Moteur d'analyse prédictive

- Tendance historique sur 3 semestres affichée en graphique
- Prévision par régression linéaire sur les 3 prochaines périodes
- Indicateur de tendance : croissant · décroissant · stable
- Anomalie Z-score avec seuil combiné (Z > 3 ET déviation absolue > 15%)
- Indice de santé institutionnel par domaine + score global

### 5. Chatbot IA streaming

- Questions en langage naturel (français)
- Réponse en streaming temps réel (Server-Sent Events)
- Contexte KPI injecté dynamiquement depuis la base de données
- Rendu Markdown dans l'interface (gras, listes, titres)
- Suggestions de questions pré-définies
- Mode standard (non-streaming) disponible en bascule

### 6. Pipeline d'ingestion de données (Track 1)

#### Fichiers structurés (Excel / CSV)
- Normalisation automatique des noms de colonnes
- Si les colonnes ne correspondent pas → Groq mappe automatiquement
- Validation ligne par ligne avec rapport d'erreurs détaillé
- Alias de domaine français reconnus (`académique`, `rh`, `recherche`…)

#### Documents non structurés (PDF / Images)
- OCR via pdfplumber (PDF natif) ou pytesseract (PDF scanné / images)
- Support multilingue : français + arabe + anglais
- Extraction structurée des KPIs via Groq avec score de confiance
- Validation qualité de l'extraction (score 0–100)
- Seuls les KPIs avec confiance ≥ 50% sont importés automatiquement
- Interface de suivi des jobs avec statut en temps réel

---

## Sécurité

La plateforme implémente une défense en profondeur couvrant les principales catégories d'attaque.

### Authentification & Tokens

| Mesure | Détail |
|---|---|
| Hashage bcrypt | Tous les mots de passe hashés avec sel aléatoire (bcrypt 4.1) |
| JWT signé HS256 | Tokens signés avec clé 64 caractères hexadécimaux |
| Expiration des tokens | Expiration configurable (défaut : 480 minutes) |
| Validation stricte | `decode_token` vérifie la signature ET l'expiration |
| Clé faible détectée | Warning au démarrage si `JWT_SECRET_KEY` est le défaut |
| Limite de taille mot de passe | Maximum 128 caractères (prévention DoS bcrypt) |

### Contrôle d'accès (RBAC + Multi-tenancy)

| Mesure | Détail |
|---|---|
| 4 niveaux de rôle | `super_admin` · `president` · `dean` · `staff` |
| Isolation par tenant | `institution_id` vérifié sur chaque requête sensible |
| Scoping département | Un compte staff ne peut accéder qu'à son `domain_scope` |
| Protection IDOR — `GET /institutions/{id}` | 403 si l'utilisateur n'appartient pas à cet établissement |
| Protection IDOR — `GET /ingestion/jobs/{id}` | 403 si le job n'appartient pas à l'institution de l'utilisateur |
| Protection IDOR — `GET /reports/{id}/download` | 403 si le rapport n'appartient pas à l'institution de l'utilisateur |
| Protection IDOR — `POST /alerts/{id}/acknowledge` | 403 si l'alerte n'appartient pas à l'institution de l'utilisateur |
| Tenant check — `POST /reports/` | `institution_id` forcé au périmètre de l'utilisateur |
| Tenant check — `POST /alerts/rules` | `institution_id` forcé au périmètre de l'utilisateur |
| Tenant check — `POST /kpis/` | `institution_id` forcé au périmètre de l'utilisateur |

### Protection contre les attaques par force brute

| Mesure | Détail |
|---|---|
| Rate limiting — Login | **20 requêtes / minute** par IP → HTTP 429 au-delà |
| Rate limiting — Chatbot | **30 requêtes / minute** par IP (protection API tokens AI) |
| IP réelle derrière proxy | Lecture de `X-Forwarded-For` pour le comptage derrière nginx |
| Implémentation | `slowapi 0.1.9` (conforme WSGI/ASGI) |

### Injection SQL

| Mesure | Détail |
|---|---|
| ORM SQLAlchemy exclusif | Zéro requête SQL brute — toutes les requêtes via `.filter()` / `.query()` |
| Paramétrage automatique | SQLAlchemy envoie les valeurs comme paramètres liés à PostgreSQL |
| Zéro f-string SQL | Aucune interpolation de chaîne dans les requêtes base de données |

### Sécurité des fichiers uploadés

| Mesure | Détail |
|---|---|
| Validation magic bytes | Extension + signature binaire vérifiées pour chaque format |
| Limite de taille | Rejet à 50 Mo (côté application + nginx `client_max_body_size`) |
| Noms de fichiers sécurisés | `Path(filename).name` — les traversées de chemin (`../`) sont neutralisées |
| Formats autorisés | Whitelist explicite : `.xlsx`, `.xls`, `.csv`, `.pdf`, `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.gif`, `.webp` |

Signatures binaires vérifiées :

| Extension | Magic bytes attendus |
|---|---|
| `.xlsx` | `PK\x03\x04` (ZIP) |
| `.xls` | `\xd0\xcf\x11\xe0` (OLE2) |
| `.pdf` | `%PDF` |
| `.png` | `\x89PNG` |
| `.jpg` / `.jpeg` | `\xff\xd8\xff` |

### Injection de formules Excel (CSV Injection)

| Mesure | Détail |
|---|---|
| Sanitisation `_xlsx_safe()` | Tout champ string commençant par `=`, `+`, `-`, `@`, `\t`, `\r` reçoit un espace en préfixe |
| Champs concernés | `indicator_label` et `unit` dans les rapports Excel générés |
| Portée | Appliqué dans la feuille Résumé ET dans tous les onglets par domaine |

### En-têtes de sécurité HTTP

Appliqués à chaque réponse via middleware FastAPI ET nginx :

| En-tête | Valeur | Protection |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Empêche le MIME-sniffing |
| `X-Frame-Options` | `SAMEORIGIN` | Protège contre le clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Filtre XSS navigateurs anciens |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limite les données de référent |
| `Server` | *(masqué)* | `server_tokens off` dans nginx — version cachée |

### Validation des entrées

| Mesure | Détail |
|---|---|
| Email validé | `pydantic EmailStr` sur le champ email du login |
| Mot de passe borné | `min_length=1`, `max_length=128` |
| Question chatbot bornée | `min_length=1`, `max_length=2000` |
| Schémas Pydantic | Validation de type automatique sur tous les endpoints |

### Documentation API (Swagger / ReDoc)

| Mesure | Détail |
|---|---|
| Contrôlé par `DEBUG` | `docs_url` et `redoc_url` exposés uniquement si `DEBUG=true` |
| Défaut sécurisé | `DEBUG=false` par défaut — docs masqués en production |
| Endpoint `/openapi.json` | Également conditionné par `DEBUG` |

### CORS

| Mesure | Détail |
|---|---|
| Origines configurables | Variable `CORS_ORIGINS` dans `.env` |
| Méthodes restreintes | `GET, POST, PUT, DELETE, OPTIONS, PATCH` (plus `*`) |
| Headers restreints | `Authorization, Content-Type, Accept, X-Requested-With` (plus `*`) |
| Hackathon | `CORS_ORIGINS=*` pour compatibilité tunnel Cloudflare |

### Génération du secret JWT

```bash
# Générer une clé sécurisée (64 caractères hexadécimaux)
openssl rand -hex 32

# Ajouter dans .env
JWT_SECRET_KEY=<output>
```

---

## Stack technique

### Backend

| Technologie | Version | Usage |
|---|---|---|
| **FastAPI** | 0.109 | API REST principale, orchestration IA |
| **PostgreSQL** | 15 | Base de données multi-tenant principale |
| **Redis** | 7 | Cache, queue d'alertes |
| **Celery + Beat** | 5.3 | Jobs planifiés (alertes horaires, rapports hebdo/mensuels) |
| **SQLAlchemy** | 2.0 | ORM multi-tenant avec requêtes paramétrées |
| **Alembic** | 1.13 | Migrations de base de données |
| **bcrypt** | 4.1 | Hashage des mots de passe |
| **python-jose** | 3.3 | JWT (authentification) |
| **slowapi** | 0.1.9 | Rate limiting par IP |
| **pydantic** | 2.6 | Validation des entrées, schémas |

### Intelligence artificielle

| Technologie | Version | Usage |
|---|---|---|
| **Groq API** | 0.4.2 | Chatbot NLP, rapports narratifs, insights domaines |
| **numpy / scipy** | 1.26 / 1.12 | Détection d'anomalies (Z-score) |
| **scikit-learn** | 1.4 | Prévision par régression linéaire |
| **pandas** | 2.2 | Traitement et normalisation des fichiers Excel/CSV |
| **pdfplumber** | 0.10 | Extraction texte depuis PDF natifs |
| **pytesseract** | 0.3.10 | OCR pour PDF scannés et images (fr+ar+en) |
| **Pillow** | 10.2 | Prétraitement des images avant OCR |

### Génération de rapports

| Technologie | Version | Usage |
|---|---|---|
| **ReportLab** | 4.1 | Génération PDF avec mise en page institutionnelle UCAR |
| **openpyxl** | 3.1 | Génération Excel multi-feuilles avec styles |

### Frontend

| Technologie | Version | Usage |
|---|---|---|
| **Next.js** | 14 | Framework React (App Router) |
| **Tailwind CSS** | 3 | Styling utilitaire |
| **Recharts** | 2 | Graphiques KPI (courbes, barres) |
| **Zustand** | 4 | State management (auth, institution) |
| **Axios** | 1.6 | Client HTTP avec intercepteur JWT |
| **lucide-react** | — | Icônes |
| **clsx** | — | Composition de classes CSS conditionnelles |

### Infrastructure

| Technologie | Usage |
|---|---|
| **Docker + Docker Compose** | Stack complète en un seul fichier |
| **Nginx 1.25** | Reverse proxy, security headers, `server_tokens off` |
| **Cloudflare Tunnel** | Accès public sans ouverture de port |

---

## Structure du projet

```
Hack4UCAR/
├── .env                            # Variables d'environnement (ne pas committer)
├── .env.example                    # Template de configuration
├── docker-compose.yml              # Stack complète (db, redis, backend, frontend, nginx)
├── nginx/
│   └── nginx.conf                  # Reverse proxy + security headers
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── auth.py             # Login (rate limited), JWT, /me
│   │   │   ├── institutions.py     # CRUD établissements (IDOR protégé)
│   │   │   ├── departments.py      # CRUD départements
│   │   │   ├── kpis.py             # KPIs + tendances + classement + health + insights
│   │   │   ├── alerts.py           # Alertes + règles (IDOR protégé)
│   │   │   ├── reports.py          # PDF/Excel (IDOR protégé + tenant check)
│   │   │   ├── chat.py             # Chatbot Groq streaming SSE (rate limited)
│   │   │   └── ingestion.py        # Excel/CSV + PDF/OCR (magic bytes + size check)
│   │   ├── ai/
│   │   │   ├── anomaly.py          # Z-score + prévision linéaire
│   │   │   ├── chatbot.py          # Intégration Groq API
│   │   │   └── insights.py         # Analyse IA par domaine
│   │   ├── core/
│   │   │   ├── config.py           # Settings (env vars + flag DEBUG)
│   │   │   ├── database.py         # Engine SQLAlchemy + session
│   │   │   ├── security.py         # bcrypt + JWT
│   │   │   └── limiter.py          # Rate limiter slowapi (IP réelle derrière proxy)
│   │   ├── dependencies/
│   │   │   └── auth.py             # get_current_user, RBAC, scoping tenant
│   │   ├── ingestion/
│   │   │   ├── pdf_extractor.py    # pdfplumber + pytesseract OCR
│   │   │   └── ai_extractor.py     # Groq KPI extraction + validation qualité
│   │   ├── models/                 # SQLAlchemy models (institution, user, kpi, alert, report, ingestion_job)
│   │   ├── schemas/                # Pydantic schemas avec validation (max_length, EmailStr)
│   │   ├── services/
│   │   │   ├── kpi_service.py      # Logique KPI, tendances, comparaison
│   │   │   ├── alert_service.py    # Vérification des règles d'alerte
│   │   │   ├── report_service.py   # Génération PDF/Excel (_xlsx_safe anti-injection)
│   │   │   └── ranking_service.py  # Indice de santé + classement institutions
│   │   ├── main.py                 # FastAPI app + middlewares sécurité + rate limiter
│   │   └── worker.py               # Celery tasks (alertes, rapports planifiés)
│   ├── alembic/                    # Migrations DB (001→004)
│   ├── scripts/
│   │   └── seed_demo_data.py       # Données de démonstration (5 établissements)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── login/page.tsx          # Page de connexion
│   │   ├── dashboard/page.tsx      # Tableau de bord KPI + health index + ranking
│   │   ├── alerts/page.tsx         # Gestion des alertes
│   │   ├── reports/page.tsx        # Rapports PDF/Excel
│   │   ├── chat/page.tsx           # Chatbot IA (streaming SSE + markdown)
│   │   └── ingestion/page.tsx      # Import données (drag-and-drop + job tracker)
│   ├── components/
│   │   ├── layout/                 # Sidebar, Header, DashboardLayout
│   │   ├── dashboard/              # KPICard, KPIChart, ComparisonChart, UploadButton
│   │   └── ui/
│   │       └── MarkdownText.tsx    # Rendu markdown sans dépendance externe
│   ├── lib/
│   │   ├── api.ts                  # Client Axios + intercepteur JWT (utilise ??)
│   │   └── types.ts                # Types TypeScript partagés
│   ├── store/
│   │   └── auth.ts                 # Zustand store (auth + hydratation)
│   ├── .dockerignore               # Exclut .env.local du build Docker
│   └── next.config.js              # Conditionnel static export / server
└── test_files/                     # Fichiers de test pour l'ingestion
    ├── 01_standard_format.xlsx     # Format standard (pas d'IA nécessaire)
    ├── 02_colonnes_francaises.xlsx # Colonnes en français → normalisation IA
    ├── 03_style_rapport.xlsx       # Style rapport avec en-têtes → extraction IA
    ├── 04_donnees_brutes.csv       # CSV avec séparateur point-virgule et commentaires
    └── 05_multi_feuilles.xlsx      # 4 feuilles avec colonnes différentes par domaine
```

---

## Installation & Démarrage

### Prérequis

- Docker & Docker Compose
- Clé API Groq (https://console.groq.com)

### 1. Cloner et configurer

```bash
git clone https://github.com/Akrem-Alamine/Hack4UCAR.git
cd Hack4UCAR

# Copier le fichier d'environnement
cp .env.example .env
```

Éditer `.env` et renseigner :

```env
GROQ_API_KEY=gsk_...           # Votre clé Groq
JWT_SECRET_KEY=<openssl rand -hex 32>   # Clé secrète forte
DEBUG=true                     # Exposer /docs en démo (mettre false en production)
```

### 2. Démarrer la stack complète

```bash
docker compose up -d --build
```

Ce démarrage lance automatiquement : PostgreSQL, Redis, Backend, Celery Worker, Celery Beat, Frontend, Nginx.

### 3. Initialiser la base de données

```bash
# Appliquer les migrations
docker compose exec backend alembic upgrade head

# Charger les données de démonstration
docker compose exec backend python -m scripts.seed_demo_data
```

### 4. Accéder à la plateforme

| Service | URL locale |
|---|---|
| Plateforme (via nginx) | http://localhost |
| API directe | http://localhost:8000 |
| Documentation Swagger | http://localhost/docs *(si DEBUG=true)* |
| Documentation ReDoc | http://localhost/redoc *(si DEBUG=true)* |

### 5. Rendre la plateforme accessible publiquement

```bash
# Installer Cloudflare Tunnel (une seule fois)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
  -o /usr/local/bin/cloudflared && chmod +x /usr/local/bin/cloudflared

# Lancer le tunnel (donne une URL publique instantanée)
cloudflared tunnel --url http://localhost:80
```

L'URL publique générée (ex : `https://xxx.trycloudflare.com`) est accessible depuis n'importe quel appareil ou réseau.

---

## Comptes de démonstration

> Mot de passe unique pour tous les comptes : **`demo1234`**

### Super Admin UCAR

| Email | Accès |
|---|---|
| `super@ucar.tn` | Vue consolidée de tous les établissements + classement + comparaison |

### Par établissement (même structure pour ENSTAB, IHEC, INSAT, ENIB, FSB, SUP'COM)

> Remplacer `<sigle>` par : `enstab`, `ihec`, `insat`, `enib`, `fsb`, `supcom`

| Email | Rôle | Données accessibles |
|---|---|---|
| `president@<sigle>.tn` | Président | Tous les domaines de l'établissement |
| `academique@<sigle>.tn` | Département | Académique uniquement |
| `finance@<sigle>.tn` | Département | Finance uniquement |
| `rh@<sigle>.tn` | Département | Ressources Humaines uniquement |
| `insertion@<sigle>.tn` | Département | Insertion Professionnelle uniquement |
| `esg@<sigle>.tn` | Département | ESG / RSE uniquement |
| `recherche@<sigle>.tn` | Département | Recherche uniquement |

**Règle de scoping** : un compte département ne peut ni voir, ni importer de données en dehors de son domaine — le backend l'applique côté serveur, indépendamment de ce que le frontend envoie.

---

## Import de données

### Fichiers structurés (Excel / CSV)

#### Format standard

| Colonne | Obligatoire | Description | Exemple |
|---|---|---|---|
| `domain` | Oui* | Domaine du KPI | `academic`, `finance`, `hr` |
| `indicator_key` | Oui | Identifiant snake_case | `success_rate`, `dropout_rate` |
| `value` | Oui | Valeur numérique | `82.5` |
| `unit` | Oui | Unité de mesure | `%`, `TND`, `kWh` |
| `period_label` | Oui | Libellé de la période | `2024-2025 S1` |
| `period_start` | Oui | Début de la période | `2024-09-01` |
| `period_end` | Oui | Fin de la période | `2025-01-31` |
| `department_code` | Non | Code du département | `FIN`, `RH`, `ACAD` |
| `notes` | Non | Commentaire libre | `Données validées` |

> *Pour les comptes département, la colonne `domain` est ignorée — le domaine est forcé à celui du compte.

#### Normalisation IA automatique

Si les colonnes du fichier ne correspondent pas au format standard, Groq analyse les colonnes et les données, puis les mappe automatiquement. Cela permet d'importer :
- Des fichiers avec des colonnes en français (`Indicateur`, `Valeur`, `Période`…)
- Des rapports structurés avec des sections et des en-têtes
- Des CSV avec des séparateurs non standards (`;`)

La réponse indique `"ai_normalized": true` si la normalisation IA a été utilisée.

#### Alias de domaine acceptés

| Valeur | Domaine reconnu |
|---|---|
| `academique`, `académique` | `academic` |
| `rh`, `ressources humaines` | `hr` |
| `recherche` | `research` |
| `partenariats` | `partnerships` |
| `rse`, `esg` | `esg` |
| `insertion professionnelle` | `insertion` |

### Documents non structurés (PDF / Images)

Les fichiers `.pdf`, `.png`, `.jpg` sont traités par le pipeline OCR + IA :

1. **Extraction texte** : pdfplumber (PDF natif) ou pytesseract (PDF scanné / image)
2. **Extraction KPIs** : Groq identifie les indicateurs dans le texte libre
3. **Validation** : score de qualité 0–100, seuls les KPIs avec confiance ≥ 50% sont importés
4. **Suivi** : job créé en base avec statut polling toutes les 3 secondes

### Endpoint template

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

Limite : **20 tentatives / minute par IP**.

Retourne un `access_token` JWT à inclure dans tous les appels suivants :

```http
Authorization: Bearer <access_token>
```

### KPIs

```http
# Liste des KPIs (dernier enregistrement par indicateur)
GET /api/v1/kpis/?institution_id=1&domain=academic

# Tendance historique + prévision IA
GET /api/v1/kpis/trend?institution_id=1&indicator_key=dropout_rate

# Comparaison inter-établissements (super_admin / president uniquement)
GET /api/v1/kpis/compare?indicator_key=success_rate

# Indice de santé d'un établissement
GET /api/v1/kpis/health?institution_id=1

# Classement de tous les établissements (super_admin uniquement)
GET /api/v1/kpis/ranking

# Insights IA par domaine
GET /api/v1/kpis/insights?institution_id=1&domain=academic

# Périodes disponibles
GET /api/v1/kpis/periods?institution_id=1

# Créer un enregistrement KPI
POST /api/v1/kpis/
```

### Alertes

```http
# Liste des alertes (filtrées par institution)
GET /api/v1/alerts/?unresolved_only=true

# Règles d'alerte
GET /api/v1/alerts/rules
POST /api/v1/alerts/rules

# Déclencher une vérification manuelle
POST /api/v1/alerts/check

# Acquitter une alerte (vérifie que l'alerte appartient à l'institution)
POST /api/v1/alerts/{id}/acknowledge
```

### Rapports

```http
# Demander la génération d'un rapport
POST /api/v1/reports/
{ "institution_id": 1, "type": "global", "period_label": "2024-2025 S1", "format": "pdf" }

# Liste des rapports
GET /api/v1/reports/

# Télécharger un rapport (vérifie que le rapport appartient à l'institution)
GET /api/v1/reports/{id}/download
```

### Chatbot IA

```http
POST /api/v1/chat/
Content-Type: application/json

# Mode standard
{ "question": "Quel est le taux d'abandon ?", "institution_id": 1, "stream": false }

# Mode streaming SSE
{ "question": "Analysez les KPIs financiers", "institution_id": 1, "stream": true }
```

Limite : **30 requêtes / minute par IP**.  
Taille de la question : maximum **2000 caractères**.

### Import de données

```http
# Import Excel / CSV (avec normalisation IA si besoin)
POST /api/v1/ingestion/upload
Content-Type: multipart/form-data
file=<fichier.xlsx>
institution_id=1
period_label_override=2024-2025 S1  (optionnel)

# Import PDF / Image (OCR + IA, asynchrone)
POST /api/v1/ingestion/upload-document
Content-Type: multipart/form-data
file=<document.pdf>
institution_id=1

# Statut d'un job
GET /api/v1/ingestion/jobs/{job_id}

# Liste des jobs
GET /api/v1/ingestion/jobs?institution_id=1

# Template de format attendu
GET /api/v1/ingestion/template
```

Contraintes : maximum **50 Mo** par fichier, magic bytes vérifiés.

---

## Déploiement public

### Stack locale avec accès internet

```bash
# 1. Démarrer la stack
docker compose up -d

# 2. Initialiser la base
docker compose exec backend alembic upgrade head
docker compose exec backend python -m scripts.seed_demo_data

# 3. Exposer publiquement avec Cloudflare Tunnel
cloudflared tunnel --url http://localhost:80
```

L'URL générée est accessible depuis n'importe quel appareil, réseau ou pays — sans configuration routeur.

### Variables d'environnement importantes

| Variable | Défaut | Description |
|---|---|---|
| `JWT_SECRET_KEY` | *(généré)* | Clé secrète JWT — générer avec `openssl rand -hex 32` |
| `GROQ_API_KEY` | *(requis)* | Clé API Groq (https://console.groq.com) |
| `DEBUG` | `false` | `true` pour exposer `/docs` et `/redoc` |
| `CORS_ORIGINS` | `*` | Origines autorisées — restreindre en production |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` | Durée de vie des tokens (8h) |

---

## Données de démonstration

Le script `seed_demo_data.py` génère des données réelles pour 5 établissements de l'**Université de Carthage** :

Le script `seed_demo_data.py` génère des données réelles pour 6 établissements de l'**Université de Carthage** :

| Établissement | Acronyme | Type | Ville |
|---|---|---|---|
| École Nationale des Sciences et Technologies Avancées de Borj Cédria | **ENSTAB** | École Nationale | Borj Cédria |
| Institut des Hautes Études Commerciales de Carthage | **IHEC** | Institut Supérieur | Carthage |
| Institut National des Sciences Appliquées et de Technologie | **INSAT** | Institut National | Tunis |
| École Nationale d'Ingénieurs de Bizerte | **ENIB** | École Nationale | Bizerte |
| Faculté des Sciences de Bizerte | **FSB** | Faculté | Bizerte |
| École Supérieure des Communications de Tunis | **SUP'COM** | École Supérieure | Ariana |

| Élément | Quantité |
|---|---|
| Établissements | 6 (ENSTAB, IHEC, INSAT, ENIB, FSB, SUP'COM) |
| Départements | 36 (6 par établissement) |
| Utilisateurs | 43 (1 super admin + 1 président + 6 départements × 6 établissements) |
| Enregistrements KPI | 396 (6 établissements × 6 domaines × ~4 indicateurs × 3 semestres) |
| Règles d'alerte | 4 (abandon critique, réussite faible, budget, absentéisme) |
| Alertes déclenchées | ~4 (1 critique ENSTAB, 1 avertissement ENIB, 1 info, 1 avertissement budget) |

**Scénarios de démonstration intégrés :**

- 🔴 **ENSTAB** : taux d'abandon passe de 7% → 8% → **22%** (anomalie Z-score + alerte critique)
- 🟡 **ENIB** : taux d'exécution budgétaire à **97.7%** (risque dépassement budgétaire)
- 📈 **INSAT** : meilleur établissement toutes catégories, 90%+ réussite (benchmark de référence)
- 🏦 **IHEC** : bon niveau général, légère baisse des conventions internationales (-6 pts sur 3 semestres)
- 📊 **FSB** : grande faculté stable, forte activité recherche (72+ publications)
- 📉 **SUP'COM** : profil en amélioration progressive sur 3 semestres (tendance positive)

---

## Critères de jugement HACK4UCAR

| Critère | Notre réponse |
|---|---|
| **Impact** | Couvre les 4 tracks, 6+ domaines KPI, 30+ établissements, 14 processus institutionnels |
| **Innovation** | IA au cœur : Z-score, régression linéaire, OCR, LLM streaming, ranking, health index |
| **Utilisabilité** | Interface 100% française, accès par rôle, import Excel/PDF sans code, chatbot naturel |
| **Scalabilité** | Architecture multi-tenant, Docker, API versionnée, Celery pour les jobs asynchrones |
| **Faisabilité** | Import Excel (workflow existant), PDF export, données réalistes tunisiennes |
| **Sécurité** | 14 vulnérabilités corrigées, défense en profondeur, rate limiting, IDOR protégé |

---

## Équipe

Développé pour **HACK4UCAR 2025** — Université de Carthage · ACM ENSTAB
