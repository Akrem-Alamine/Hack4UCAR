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
- **Génère** des rapports PDF avec résumés narratifs IA
- **Répond** aux questions en langage naturel via un chatbot streaming avec rendu Markdown complet
- **Sécurise** les accès par tenant, par rôle et par domaine
- **Ingère** des données depuis des fichiers Excel, CSV, PDF et images
- **Explore** la base de données en temps réel via une interface SGBD intégrée

---

## Couverture des 4 Tracks

### Track 1 — Digitalisation & Structuration des données

| Fonctionnalité | Détails |
|---|---|
| Import Excel / CSV standard | Colonnes standard avec validation ligne par ligne |
| Normalisation IA automatique | Si les colonnes ne correspondent pas, Groq les mappe vers le schéma standard — le prompt liste explicitement les 27 clés canoniques autorisées et demande à l'IA d'ignorer les lignes non mappables |
| Mode dry-run avant import | Validation et aperçu sans sauvegarder — popup de confirmation si anomalies |
| Upsert intelligent | Re-importer un fichier met à jour les valeurs existantes, jamais de doublons |
| Normalisation des clés indicateur | Regex multilingue avec strip des accents : "Taux d'abandon étudiants" → `dropout_rate` automatiquement ; appliquée aussi après normalisation IA comme filet de sécurité |
| Allowlist canonique | Seuls 27 indicateurs connus sont acceptés — toute clé non résolue (de l'IA ou du fichier) est rejetée avec message d'erreur par ligne |
| Import PDF & images (OCR) | pdfplumber + pytesseract (`fra+ara+eng`) |
| Extraction de KPIs depuis PDF | Groq identifie et structure les indicateurs depuis du texte libre |
| Récupération automatique des jobs | Au redémarrage, les jobs bloqués en `processing` sont relancés automatiquement |
| Historique des imports | Chaque import Excel/CSV/PDF/image crée un enregistrement traçable |
| Validation de qualité IA | Score de confiance 0–100 par indicateur extrait |
| File d'attente asynchrone | Jobs d'ingestion trackés en base (pending → processing → completed) |
| Texte OCR visible | Le texte brut extrait est affiché dans le détail du job pour vérification |
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
| Rendu Markdown complet | Tableaux, titres `#` à `####`, listes, gras, italique — rendu natif sans dépendance |
| Encodage SSE correct | Les sauts de ligne dans les chunks sont encodés `\n` → pas de perte de contenu |
| Arrêt du streaming | Bouton ✕ pour interrompre la réponse en cours |
| Rapport PDF institutionnel | ReportLab avec mise en page UCAR + résumé exécutif IA |
| Format PDF uniquement | Les rapports sont toujours générés en PDF |
| Téléchargement authentifié | Le téléchargement utilise le token Bearer (pas de lien nu) |
| Auto-polling rapports | La page se rafraîchit automatiquement tant qu'un rapport est en cours de génération |
| Narration automatique | Groq génère le résumé narratif de chaque rapport |
| Insights par domaine | Analyse contextuelle `GET /api/v1/kpis/insights` |
| Explications des anomalies | Groq explique chaque anomalie en langage naturel |

### Track 4 — Plateforme End-to-End

| Fonctionnalité | Détails |
|---|---|
| Multi-tenancy | `institution_id` sur chaque table, isolation garantie côté serveur |
| RBAC 4 niveaux | Super Admin → Président → Doyen → Staff département |
| Tableau de bord consolidé | Vue globale UCAR groupée par établissement + drill-down institution |
| Vue consolidée groupée | En mode "tous établissements", les KPIs sont regroupés par institution avec badge anomalies |
| Alertes intelligentes | Seuils configurables, niveaux Info / Warning / Critical |
| Explorateur de base de données | Interface SGBD intégrée (super admin uniquement) : navigation, tri, recherche, pagination, détail enregistrement |
| Provisionnement d'établissement | Super admin crée un établissement en un formulaire → 6 départements + 1 président + 6 comptes département créés automatiquement avec un mot de passe temporaire affiché une seule fois |
| Sélecteur d'institution | Changement de contexte sans rechargement |
| Accès public via tunnel | Cloudflare Tunnel → accessible depuis n'importe quel appareil |
| API versionnée | `/api/v1/` avec documentation Swagger intégrée |
| Déploiement Docker | Un seul `docker compose up` lance l'ensemble de la stack |

---

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE TUNNEL (public)                     │
│              https://<slug>.trycloudflare.com                     │
└──────────────────────────────┬────────────────────────────────────┘
                               │
┌──────────────────────────────▼────────────────────────────────────┐
│                    NGINX REVERSE PROXY (:80)                      │
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
│  /api/v1/ingestion          │   │  /database  (SGBD explorer)   │
│  /api/v1/departments        │   └───────────────────────────────┘
│  /api/v1/db-explorer        │
│  Celery Worker + Beat       │
└────────┬───────────┬────────┘
         │           │
    PostgreSQL     Redis
    (multi-tenant) (cache + queue)
         │
    ┌────┴──────────────────────────────┐
    │           COUCHE IA               │
    │  Groq LLM (chatbot + rapports)    │
    │  Z-score → anomalies              │
    │  Régression linéaire → prévision  │
    │  pdfplumber + pytesseract (OCR)   │
    │  ReportLab (exports PDF)          │
    └───────────────────────────────────┘
```

### Multi-tenancy

- Chaque établissement est un **tenant isolé** via `institution_id` sur chaque table
- Les comptes **Super Admin UCAR** voient tous les établissements (vue consolidée groupée)
- Les **Présidents** voient toutes les données de leur établissement
- Les comptes **département** sont strictement limités à leur domaine de données
- Toute tentative d'accès cross-tenant est bloquée par le backend (HTTP 403)

---

## Fonctionnalités

### 1. Tableau de bord consolidé multi-établissements

- Vue globale UCAR avec agrégation de tous les KPIs
- **Mode "tous établissements"** : KPIs groupés par institution, chacun dans sa propre section avec badge d'anomalies
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

### 3. Rapports automatiques PDF

- Génération à la demande par période et domaine (format PDF uniquement)
- Mise en page institutionnelle UCAR avec résumé exécutif généré par Groq
- Téléchargement authentifié via Bearer token (aucun lien public exposé)
- Auto-polling : la page se rafraîchit toutes les 3 secondes pendant la génération
- Génération en arrière-plan (non-bloquant)
- Rapports hebdomadaires et mensuels générés automatiquement par Celery

### 4. Moteur d'analyse prédictive

- Tendance historique sur 3 semestres affichée en graphique
- Prévision par régression linéaire sur les 3 prochaines périodes
- Indicateur de tendance : croissant · décroissant · stable
- Anomalie Z-score avec seuil combiné (Z > 3 ET déviation absolue > 15%)
- Indice de santé institutionnel par domaine + score global

### 5. Chatbot IA streaming avec Markdown complet

- Questions en langage naturel (français)
- Réponse en streaming temps réel (Server-Sent Events)
- **Encodage correct des sauts de ligne SSE** : les `\n` dans les chunks sont encodés côté serveur et décodés côté client — les tableaux et titres arrivent intacts
- **Rendu Markdown natif** sans dépendance externe :
  - Titres `#`, `##`, `###`, `####`
  - Tableaux avec entête bleue et lignes alternées
  - Listes à puces et numérotées
  - Texte en gras et italique
- Contexte KPI injecté dynamiquement depuis la base de données
- Suggestions de questions pré-définies
- Mode standard (non-streaming) disponible en bascule

### 6. Pipeline d'ingestion de données

#### Fichiers structurés (Excel / CSV)

- **Mode dry-run** : validation et aperçu avant sauvegarde — popup de confirmation si erreurs ou normalisation IA
- **Upsert** : re-importer un fichier met à jour les valeurs, jamais de doublons
- **Normalisation des clés** : regex multilingue avec strip des accents — "Taux de réussite global" → `success_rate`
- **Allowlist stricte** : 27 clés canoniques autorisées, toute clé non reconnue est rejetée avec message d'erreur par ligne
- Normalisation automatique des colonnes via Groq si le format ne correspond pas — le prompt inclut explicitement la liste des 27 clés canoniques, l'IA ne génère que des clés valides et ignore les lignes non mappables
- Double filet de sécurité : normalisation regex appliquée après la sortie IA avant la vérification de l'allowlist
- Historique de chaque import visible dans la page Ingestion

#### Documents non structurés (PDF / Images)

- OCR via pdfplumber (PDF natif) ou pytesseract (PDF scanné / image)
- Support multilingue : français + arabe + anglais
- Extraction KPIs via Groq avec score de confiance — uniquement les clés canoniques sont sauvegardées
- **Récupération automatique** : jobs bloqués au redémarrage relancés automatiquement
- Interface de suivi avec statut en temps réel + texte OCR brut consultable
- Seuls les KPIs avec confiance ≥ 50% sont importés automatiquement

### 7. Gestion des établissements — provisionnement automatique

Accessible via **Établissements** dans la barre de navigation (super admin uniquement).

- **Liste des institutions** : grille de toutes les institutions actives (nom, sigle, type, ville)
- **Formulaire de création** : 4 champs seulement — Nom complet, Sigle, Ville, Type d'établissement
- **Provisionnement automatique en un clic** :
  - 6 départements créés (Académique, Finance, RH, Insertion Professionnelle, ESG, Recherche)
  - 1 compte Président (`president@<sigle>.tn`)
  - 6 comptes département (`academique@`, `finance@`, `rh@`, `insertion@`, `esg@`, `recherche@`)
  - Un mot de passe temporaire aléatoire généré et affiché **une seule fois** avec bouton de copie
- **Sécurité** : 409 si le sigle est déjà utilisé, accès super admin uniquement (HTTP 403 sinon)

### 8. Explorateur de base de données (SGBD intégré)

Accessible via **Base de données** dans la barre de navigation (super admin uniquement).

- **Liste des tables** avec nombre de lignes en temps réel (8 tables exposées)
- **Grille de données** : 50 lignes par page, défilement horizontal, toutes les colonnes
- **Tri par colonne** : clic sur l'entête pour trier, re-clic pour inverser (↑/↓)
- **Recherche textuelle** : filtrage ILIKE sur toutes les colonnes texte
- **Pagination** : navigateur de pages avec numéros
- **Panneau de détail** : clic sur une ligne → panneau latéral avec toutes les valeurs complètes (non tronquées)
- **Sécurité** : lecture seule, allowlist explicite des tables, accès super admin uniquement (HTTP 403 sinon)

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
| Explorateur DB — `GET /db-explorer/*` | 403 pour tout rôle autre que `super_admin` |
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
| ORM SQLAlchemy exclusif | Zéro requête SQL brute dans le code applicatif |
| Paramétrage automatique | SQLAlchemy envoie les valeurs comme paramètres liés à PostgreSQL |
| Explorateur DB — requêtes paramétrées | `text()` avec `:param` liés, table validée contre allowlist avant exécution |

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
│   │   │   ├── institutions.py     # CRUD établissements + POST / provisionnement complet (IDOR protégé)
│   │   │   ├── departments.py      # CRUD départements
│   │   │   ├── kpis.py             # KPIs + tendances + classement + health + insights
│   │   │   ├── alerts.py           # Alertes + règles (IDOR protégé)
│   │   │   ├── reports.py          # PDF (IDOR protégé + tenant check)
│   │   │   ├── chat.py             # Chatbot Groq streaming SSE (rate limited, newlines encodés)
│   │   │   ├── ingestion.py        # Excel/CSV + PDF/OCR (upsert, allowlist, dry-run, récupération jobs)
│   │   │   └── database_explorer.py# Explorateur SGBD lecture seule (super admin, allowlist tables)
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
│   │   │   └── ai_extractor.py     # Groq KPI extraction + validation qualité (prompt strict)
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                # Pydantic schemas avec validation
│   │   ├── services/
│   │   │   ├── kpi_service.py      # Logique KPI, tendances, comparaison
│   │   │   ├── alert_service.py    # Vérification des règles d'alerte
│   │   │   ├── report_service.py   # Génération PDF (_xlsx_safe anti-injection)
│   │   │   └── ranking_service.py  # Indice de santé + classement institutions
│   │   ├── main.py                 # FastAPI app + middlewares sécurité + récupération jobs au démarrage
│   │   └── worker.py               # Celery tasks (alertes, rapports planifiés)
│   ├── alembic/                    # Migrations DB
│   ├── scripts/
│   │   └── seed_demo_data.py       # Données de démonstration (6 établissements UCAR)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── login/page.tsx          # Page de connexion
│   │   ├── dashboard/page.tsx      # Tableau de bord KPI + health index + ranking (groupé par institution)
│   │   ├── alerts/page.tsx         # Gestion des alertes
│   │   ├── reports/page.tsx        # Rapports PDF (auto-polling, téléchargement authentifié)
│   │   ├── chat/page.tsx           # Chatbot IA (streaming SSE + rendu Markdown complet)
│   │   ├── ingestion/page.tsx      # Import données (dry-run + modal avertissement + job tracker)
│   │   ├── institutions/page.tsx   # Gestion établissements + provisionnement automatique (super admin)
│   │   └── database/page.tsx       # Explorateur SGBD (tri, recherche, pagination, détail)
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx         # Navigation (Établissements + Base de données, super admin uniquement)
│   │   │   └── DashboardLayout.tsx
│   │   ├── dashboard/              # KPICard, KPIChart, ComparisonChart
│   │   └── ui/
│   │       └── MarkdownText.tsx    # Rendu Markdown natif : tableaux, titres #–####, listes, gras
│   ├── lib/
│   │   ├── api.ts                  # Client Axios + intercepteur JWT
│   │   └── types.ts                # Types TypeScript partagés
│   ├── store/
│   │   └── auth.ts                 # Zustand store (auth + hydratation)
│   └── next.config.js
└── test_files/                     # Fichiers de test pour l'ingestion
    ├── 01_standard_format.xlsx
    ├── 02_colonnes_francaises.xlsx
    ├── 03_style_rapport.xlsx
    ├── 04_donnees_brutes.csv
    └── 05_multi_feuilles.xlsx
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

cp .env.example .env
```

Éditer `.env` et renseigner :

```env
GROQ_API_KEY=gsk_...                    # Votre clé Groq
JWT_SECRET_KEY=<openssl rand -hex 32>   # Clé secrète forte
DEBUG=true                              # Exposer /docs en démo (false en production)
```

### 2. Démarrer la stack complète

```bash
docker compose up -d --build
```

Lance automatiquement : PostgreSQL, Redis, Backend, Celery Worker, Celery Beat, Frontend, Nginx.

### 3. Initialiser la base de données

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m scripts.seed_demo_data
```

### 4. Accéder à la plateforme

| Service | URL locale |
|---|---|
| Plateforme (via nginx) | http://localhost |
| API directe | http://localhost:8000 |
| Documentation Swagger | http://localhost/docs *(si DEBUG=true)* |

### 5. Rendre la plateforme accessible publiquement

```bash
cloudflared tunnel --url http://localhost:80
```

---

## Comptes de démonstration

> Mot de passe unique pour tous les comptes : **`demo1234`**

### Super Admin UCAR

| Email | Accès |
|---|---|
| `super@ucar.tn` | Vue consolidée de tous les établissements + classement + comparaison + explorateur DB + gestion établissements |

### Par établissement

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

---

## Import de données

### Fichiers structurés (Excel / CSV)

#### Format standard

| Colonne | Obligatoire | Description | Exemple |
|---|---|---|---|
| `domain` | Oui* | Domaine du KPI | `academic`, `finance`, `hr` |
| `indicator_key` | Oui | Identifiant (normalisé automatiquement) | `success_rate`, `Taux de réussite` |
| `value` | Oui | Valeur numérique | `82.5` |
| `unit` | Oui | Unité de mesure | `%`, `TND`, `kWh` |
| `period_label` | Oui | Libellé de la période | `2024-2025 S1` |
| `period_start` | Oui | Début de la période | `2024-09-01` |
| `period_end` | Oui | Fin de la période | `2025-01-31` |
| `department_code` | Non | Code du département | `FIN`, `RH` |
| `notes` | Non | Commentaire libre | `Données validées` |

#### Clés d'indicateurs acceptées (allowlist canonique)

| Domaine | Clés acceptées |
|---|---|
| Académique | `success_rate`, `attendance_rate`, `dropout_rate`, `repetition_rate`, `enrolled_students` |
| Finance | `budget_allocated`, `budget_consumed`, `budget_execution_rate`, `cost_per_student` |
| RH | `teaching_headcount`, `admin_headcount`, `total_staff`, `absenteeism_rate`, `training_hours` |
| ESG | `energy_consumption_kwh`, `carbon_footprint_ton`, `recycling_rate` |
| Insertion | `employability_rate`, `national_convention_rate`, `international_convention_rate`, `insertion_delay_months` |
| Recherche | `publications_count`, `active_projects`, `funding_tnd` |
| Infrastructure | `equipment_count`, `classroom_occupancy_rate` |

> Les variantes françaises (`Taux de réussite`, `taux d abandon etudiants`…) sont normalisées automatiquement par regex avant la vérification.

#### Mode dry-run

Chaque import Excel/CSV passe d'abord par une validation sans sauvegarde. Si des avertissements sont détectés (normalisation IA, erreurs de format), une popup apparaît avec le détail avant de demander confirmation.

---

## KPIs & Domaines

### Académique (`academic`)

| Indicateur | Unité |
|---|---|
| `success_rate` — Taux de réussite | % |
| `attendance_rate` — Taux de présence | % |
| `dropout_rate` — Taux d'abandon | % |
| `repetition_rate` — Taux de redoublement | % |
| `enrolled_students` — Étudiants inscrits | nombre |

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
| `total_staff` — Effectif total | pers. |
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

### Infrastructure (`infrastructure`)

| Indicateur | Unité |
|---|---|
| `equipment_count` — Nombre d'équipements | nombre |
| `classroom_occupancy_rate` — Taux d'occupation salles | % |

---

## API Reference

### Authentification

```http
POST /api/v1/auth/login
{ "email": "president@enstab.tn", "password": "demo1234" }
```

Limite : **20 tentatives / minute par IP**. Retourne un `access_token` JWT.

```http
Authorization: Bearer <access_token>
```

### KPIs

```http
GET /api/v1/kpis/?institution_id=1&domain=academic
GET /api/v1/kpis/trend?institution_id=1&indicator_key=dropout_rate
GET /api/v1/kpis/compare?indicator_key=success_rate
GET /api/v1/kpis/health?institution_id=1
GET /api/v1/kpis/ranking
GET /api/v1/kpis/insights?institution_id=1&domain=academic
```

### Alertes

```http
GET  /api/v1/alerts/?unresolved_only=true
POST /api/v1/alerts/rules
POST /api/v1/alerts/check
POST /api/v1/alerts/{id}/acknowledge
```

### Rapports

```http
POST /api/v1/reports/
{ "institution_id": 1, "type": "global", "period_label": "2024-2025 S1", "format": "pdf" }

GET  /api/v1/reports/
GET  /api/v1/reports/{id}/download   # Bearer token requis
```

### Chatbot IA

```http
POST /api/v1/chat/
{ "question": "Analysez les KPIs financiers", "institution_id": 1, "stream": true }
```

Limite : **30 requêtes / minute par IP**. Question : max **2000 caractères**.

### Import de données

```http
# Dry-run (validation sans sauvegarde)
POST /api/v1/ingestion/upload
  file=<fichier.xlsx>  institution_id=1  dry_run=true

# Import réel
POST /api/v1/ingestion/upload
  file=<fichier.xlsx>  institution_id=1  dry_run=false

# PDF / Image (OCR + IA asynchrone)
POST /api/v1/ingestion/upload-document
  file=<document.pdf>  institution_id=1

GET /api/v1/ingestion/jobs/{job_id}
GET /api/v1/ingestion/jobs?institution_id=1
GET /api/v1/ingestion/template
```

### Établissements (super admin)

```http
GET  /api/v1/institutions/
POST /api/v1/institutions/
{
  "name": "École Nationale des Sciences de Tunis",
  "acronym": "ENST",
  "type": "École Nationale",
  "city": "Tunis"
}
# → crée l'institution + 6 départements + 1 président + 6 comptes département
# → retourne { institution, password, accounts[] }
```

### Explorateur base de données (super admin)

```http
GET /api/v1/db-explorer/tables
GET /api/v1/db-explorer/tables/{table}/rows?page=1&page_size=50&search=...&sort_col=id&sort_dir=desc
GET /api/v1/db-explorer/tables/{table}/row/{id}
```

---

## Déploiement public

```bash
docker compose up -d
docker compose exec backend alembic upgrade head
docker compose exec backend python -m scripts.seed_demo_data
cloudflared tunnel --url http://localhost:80
```

### Variables d'environnement

| Variable | Défaut | Description |
|---|---|---|
| `JWT_SECRET_KEY` | *(généré)* | Clé secrète JWT — `openssl rand -hex 32` |
| `GROQ_API_KEY` | *(requis)* | Clé API Groq (https://console.groq.com) |
| `DEBUG` | `false` | `true` pour exposer `/docs` et `/redoc` |
| `CORS_ORIGINS` | `*` | Origines autorisées — restreindre en production |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` | Durée de vie des tokens (8h) |

---

## Données de démonstration

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
| Utilisateurs | 43 (1 super admin + (1 président + 6 départements) × 6 établissements) |
| Enregistrements KPI | ~396 (6 établissements × 6 domaines × ~4 indicateurs × 3 semestres) |
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
| **Impact** | Couvre les 4 tracks, 7 domaines KPI, 27 indicateurs, 30+ établissements, 14 processus institutionnels |
| **Innovation** | IA au cœur : Z-score, régression linéaire, OCR, LLM streaming, ranking, health index, DB explorer |
| **Utilisabilité** | Interface 100% française, accès par rôle, import Excel/PDF sans code, chatbot Markdown, provisionnement établissement en 1 clic |
| **Scalabilité** | Architecture multi-tenant, Docker, API versionnée, Celery pour les jobs asynchrones, ajout d'établissement sans redéploiement |
| **Faisabilité** | Import Excel (workflow existant), PDF export, données réalistes tunisiennes, upsert intelligent |
| **Sécurité** | 15+ mesures de sécurité, défense en profondeur, rate limiting, IDOR protégé, allowlist stricte |

---

## Équipe

KawKab Zoumoroda
Développé pour **HACK4UCAR 2025** — Université de Carthage · ACM ENSTAB
