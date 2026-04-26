"""
Seed script — 6 real Université de Carthage institutions, 3 semesters of KPI data.
Demo scenarios:
  ENSTAB  → dropout spike 7% → 8% → 22%  (anomalie critique)
  IHEC    → bon niveau, légère baisse insertion internationale
  INSAT   → top performer toutes catégories
  ENIB    → risque de dépassement budgétaire
  FSB     → profil stable, forte recherche
  SUP'COM → profil en amélioration progressive

Run: python -m scripts.seed_demo_data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.institution import Institution
from app.models.department import Department
from app.models.user import User, UserRole
from app.models.kpi import KPIRecord
from app.models.alert import AlertRule, Alert, AlertSeverity

db = SessionLocal()


def seed():
    print("🌱 Initialisation des données de démonstration UCAR...")

    _clear_data()

    institutions = _seed_institutions()
    _seed_departments(institutions)
    _seed_users(institutions)
    _seed_kpis(institutions)
    _seed_alert_rules()
    _run_alert_check()

    print("\n✅ Données de démonstration créées avec succès.")
    print("\n📋 Comptes de connexion:")
    print("  super@ucar.tn               / demo1234  (Super Admin UCAR)")
    for inst in institutions:
        key = inst.acronym.lower().replace("'", "").replace(" ", "")
        print(f"  president@{key}.tn  / demo1234  (Président {inst.acronym})")


def _clear_data():
    db.query(Alert).delete()
    db.query(AlertRule).delete()
    db.query(KPIRecord).delete()
    db.query(User).delete()
    db.query(Department).delete()
    db.query(Institution).delete()
    db.commit()
    print("  - Données existantes supprimées")


def _seed_institutions() -> list[Institution]:
    data = [
        {
            "name": "École Nationale des Sciences et Technologies Avancées de Borj Cédria",
            "acronym": "ENSTAB",
            "type": "École Nationale",
            "city": "Borj Cédria",
        },
        {
            "name": "Institut des Hautes Études Commerciales de Carthage",
            "acronym": "IHEC",
            "type": "Institut Supérieur",
            "city": "Carthage",
        },
        {
            "name": "Institut National des Sciences Appliquées et de Technologie",
            "acronym": "INSAT",
            "type": "Institut National",
            "city": "Tunis",
        },
        {
            "name": "École Nationale d'Ingénieurs de Bizerte",
            "acronym": "ENIB",
            "type": "École Nationale",
            "city": "Bizerte",
        },
        {
            "name": "Faculté des Sciences de Bizerte",
            "acronym": "FSB",
            "type": "Faculté",
            "city": "Bizerte",
        },
        {
            "name": "École Supérieure des Communications de Tunis",
            "acronym": "SUP'COM",
            "type": "École Supérieure",
            "city": "Ariana",
        },
    ]
    institutions = []
    for d in data:
        inst = Institution(**d)
        db.add(inst)
        institutions.append(inst)
    db.commit()
    for inst in institutions:
        db.refresh(inst)
    print(f"  - {len(institutions)} établissements créés")
    return institutions


DEPT_TEMPLATES = [
    {"name": "Académique",               "code": "ACAD",   "domain": "academic",  "email_prefix": "academique"},
    {"name": "Finance",                  "code": "FIN",    "domain": "finance",   "email_prefix": "finance"},
    {"name": "Ressources Humaines",      "code": "RH",     "domain": "hr",        "email_prefix": "rh"},
    {"name": "Insertion Professionnelle","code": "INSERT", "domain": "insertion", "email_prefix": "insertion"},
    {"name": "ESG / RSE",                "code": "ESG",    "domain": "esg",       "email_prefix": "esg"},
    {"name": "Recherche",                "code": "RECH",   "domain": "research",  "email_prefix": "recherche"},
]


def _seed_departments(institutions: list[Institution]):
    count = 0
    for inst in institutions:
        for t in DEPT_TEMPLATES:
            db.add(Department(
                institution_id=inst.id,
                name=t["name"],
                code=t["code"],
                domain=t["domain"],
            ))
            count += 1
    db.commit()
    print(f"  - {count} départements créés (6 par établissement)")


def _email_key(inst: Institution) -> str:
    return inst.acronym.lower().replace("'", "").replace(" ", "")


def _seed_users(institutions: list[Institution]):
    users = []

    super_admin = User(
        email="super@ucar.tn",
        hashed_password=hash_password("demo1234"),
        first_name="Ahmed",
        last_name="Ben Ali",
        role=UserRole.super_admin,
        institution_id=None,
    )
    db.add(super_admin)
    users.append(super_admin)

    for inst in institutions:
        key = _email_key(inst)
        president = User(
            email=f"president@{key}.tn",
            hashed_password=hash_password("demo1234"),
            first_name="Mohamed",
            last_name=f"Président {inst.acronym}",
            role=UserRole.president,
            institution_id=inst.id,
            domain_scope=None,
        )
        db.add(president)
        users.append(president)

        for t in DEPT_TEMPLATES:
            dept_user = User(
                email=f"{t['email_prefix']}@{key}.tn",
                hashed_password=hash_password("demo1234"),
                first_name=t["name"],
                last_name=inst.acronym,
                role=UserRole.department,
                institution_id=inst.id,
                domain_scope=t["domain"],
            )
            db.add(dept_user)
            users.append(dept_user)

    db.commit()
    print(f"  - {len(users)} utilisateurs créés (1 super admin + 1 président + 6 départements × {len(institutions)} établissements)")


PERIODS = [
    ("2023-2024 S1", date(2023, 9, 1),  date(2024, 1, 31)),
    ("2023-2024 S2", date(2024, 2, 1),  date(2024, 6, 30)),
    ("2024-2025 S1", date(2024, 9, 1),  date(2025, 1, 31)),
]


def _kpi(institution_id, domain, key, value, unit, period_idx):
    label, start, end = PERIODS[period_idx]
    return KPIRecord(
        institution_id=institution_id,
        domain=domain,
        indicator_key=key,
        value=value,
        unit=unit,
        period_label=label,
        period_start=start,
        period_end=end,
    )


def _seed_kpis(institutions: list[Institution]):
    records = []
    enstab, ihec, insat, enib, fsb, supcom = institutions

    # ─── ENSTAB ─── scénario : dropout_rate spike 7% → 8% → 22% (anomalie + alerte critique)
    # École technologique de Borj Cédria, ~1 200 étudiants
    for i, (sr, att, rep, drop) in enumerate([(82, 91, 9, 7), (84, 90, 8, 8), (78, 87, 11, 22)]):
        records += [
            _kpi(enstab.id, "academic", "success_rate",     sr,   "%", i),
            _kpi(enstab.id, "academic", "attendance_rate",  att,  "%", i),
            _kpi(enstab.id, "academic", "repetition_rate",  rep,  "%", i),
            _kpi(enstab.id, "academic", "dropout_rate",     drop, "%", i),
        ]
    for i, (alloc, cons) in enumerate([(2_800_000, 2_450_000), (2_800_000, 2_600_000), (2_800_000, 2_710_000)]):
        records += [
            _kpi(enstab.id, "finance", "budget_allocated",      alloc,                  "TND", i),
            _kpi(enstab.id, "finance", "budget_consumed",       cons,                   "TND", i),
            _kpi(enstab.id, "finance", "budget_execution_rate", round(cons/alloc*100,1), "%",  i),
            _kpi(enstab.id, "finance", "cost_per_student",      round(cons/1200, 1),    "TND", i),
        ]
    for i, (teach, admin, abs_, train) in enumerate([(120, 45, 4.2, 320), (120, 45, 3.8, 340), (122, 46, 5.1, 290)]):
        records += [
            _kpi(enstab.id, "hr", "teaching_headcount", teach,        "pers.", i),
            _kpi(enstab.id, "hr", "admin_headcount",    admin,        "pers.", i),
            _kpi(enstab.id, "hr", "total_staff",        teach + admin,"pers.", i),
            _kpi(enstab.id, "hr", "absenteeism_rate",   abs_,         "%",    i),
            _kpi(enstab.id, "hr", "training_hours",     train,        "h",    i),
        ]
    for i, (emp, nat, intl, delay) in enumerate([(72, 65, 18, 5.2), (74, 66, 20, 5.0), (71, 64, 19, 5.4)]):
        records += [
            _kpi(enstab.id, "insertion", "employability_rate",             emp,   "%",   i),
            _kpi(enstab.id, "insertion", "national_convention_rate",       nat,   "%",   i),
            _kpi(enstab.id, "insertion", "international_convention_rate",  intl,  "%",   i),
            _kpi(enstab.id, "insertion", "insertion_delay_months",         delay, "mois",i),
        ]
    for i, (kwh, co2, rec) in enumerate([(485_000, 142, 28), (472_000, 138, 31), (491_000, 144, 30)]):
        records += [
            _kpi(enstab.id, "esg", "energy_consumption_kwh", kwh, "kWh",  i),
            _kpi(enstab.id, "esg", "carbon_footprint_ton",   co2, "t CO₂",i),
            _kpi(enstab.id, "esg", "recycling_rate",         rec, "%",    i),
        ]
    for i, (pub, proj, fund) in enumerate([(38, 12, 420_000), (41, 13, 450_000), (39, 14, 480_000)]):
        records += [
            _kpi(enstab.id, "research", "publications_count", pub,  "pub.",   i),
            _kpi(enstab.id, "research", "active_projects",    proj, "projets",i),
            _kpi(enstab.id, "research", "funding_tnd",        fund, "TND",    i),
        ]

    # ─── IHEC Carthage ─── scénario : bon niveau général, légère baisse insertion internationale
    # École de commerce, ~3 000 étudiants
    for i, (sr, att, rep, drop) in enumerate([(85, 92, 7, 6), (86, 92, 7, 6), (84, 91, 8, 7)]):
        records += [
            _kpi(ihec.id, "academic", "success_rate",     sr,   "%", i),
            _kpi(ihec.id, "academic", "attendance_rate",  att,  "%", i),
            _kpi(ihec.id, "academic", "repetition_rate",  rep,  "%", i),
            _kpi(ihec.id, "academic", "dropout_rate",     drop, "%", i),
        ]
    for i, (alloc, cons) in enumerate([(3_500_000, 3_050_000), (3_500_000, 3_200_000), (3_500_000, 3_290_000)]):
        records += [
            _kpi(ihec.id, "finance", "budget_allocated",      alloc,                  "TND", i),
            _kpi(ihec.id, "finance", "budget_consumed",       cons,                   "TND", i),
            _kpi(ihec.id, "finance", "budget_execution_rate", round(cons/alloc*100,1), "%",  i),
            _kpi(ihec.id, "finance", "cost_per_student",      round(cons/3000, 1),    "TND", i),
        ]
    for i, (teach, admin, abs_, train) in enumerate([(180, 60, 3.5, 360), (181, 61, 3.4, 370), (182, 62, 3.6, 355)]):
        records += [
            _kpi(ihec.id, "hr", "teaching_headcount", teach,        "pers.", i),
            _kpi(ihec.id, "hr", "admin_headcount",    admin,        "pers.", i),
            _kpi(ihec.id, "hr", "total_staff",        teach + admin,"pers.", i),
            _kpi(ihec.id, "hr", "absenteeism_rate",   abs_,         "%",    i),
            _kpi(ihec.id, "hr", "training_hours",     train,        "h",    i),
        ]
    # Légère baisse des conventions internationales sur les 3 semestres
    for i, (emp, nat, intl, delay) in enumerate([(82, 75, 30, 4.2), (81, 74, 27, 4.4), (80, 73, 24, 4.6)]):
        records += [
            _kpi(ihec.id, "insertion", "employability_rate",             emp,   "%",   i),
            _kpi(ihec.id, "insertion", "national_convention_rate",       nat,   "%",   i),
            _kpi(ihec.id, "insertion", "international_convention_rate",  intl,  "%",   i),
            _kpi(ihec.id, "insertion", "insertion_delay_months",         delay, "mois",i),
        ]
    for i, (kwh, co2, rec) in enumerate([(420_000, 123, 32), (415_000, 121, 34), (418_000, 122, 33)]):
        records += [
            _kpi(ihec.id, "esg", "energy_consumption_kwh", kwh, "kWh",  i),
            _kpi(ihec.id, "esg", "carbon_footprint_ton",   co2, "t CO₂",i),
            _kpi(ihec.id, "esg", "recycling_rate",         rec, "%",    i),
        ]
    for i, (pub, proj, fund) in enumerate([(28, 9, 310_000), (31, 10, 340_000), (30, 11, 360_000)]):
        records += [
            _kpi(ihec.id, "research", "publications_count", pub,  "pub.",   i),
            _kpi(ihec.id, "research", "active_projects",    proj, "projets",i),
            _kpi(ihec.id, "research", "funding_tnd",        fund, "TND",    i),
        ]

    # ─── INSAT ─── top performer toutes catégories
    # Institut d'ingénierie & technologie, ~4 000 étudiants
    for i, (sr, att, rep, drop) in enumerate([(90, 94, 5, 4), (91, 95, 5, 3), (90, 94, 5, 4)]):
        records += [
            _kpi(insat.id, "academic", "success_rate",     sr,   "%", i),
            _kpi(insat.id, "academic", "attendance_rate",  att,  "%", i),
            _kpi(insat.id, "academic", "repetition_rate",  rep,  "%", i),
            _kpi(insat.id, "academic", "dropout_rate",     drop, "%", i),
        ]
    for i, (alloc, cons) in enumerate([(6_200_000, 5_700_000), (6_200_000, 5_850_000), (6_200_000, 5_780_000)]):
        records += [
            _kpi(insat.id, "finance", "budget_allocated",      alloc,                  "TND", i),
            _kpi(insat.id, "finance", "budget_consumed",       cons,                   "TND", i),
            _kpi(insat.id, "finance", "budget_execution_rate", round(cons/alloc*100,1), "%",  i),
            _kpi(insat.id, "finance", "cost_per_student",      round(cons/4000, 1),    "TND", i),
        ]
    for i, (teach, admin, abs_, train) in enumerate([(250, 85, 2.8, 680), (252, 86, 2.6, 710), (255, 88, 2.7, 730)]):
        records += [
            _kpi(insat.id, "hr", "teaching_headcount", teach,        "pers.", i),
            _kpi(insat.id, "hr", "admin_headcount",    admin,        "pers.", i),
            _kpi(insat.id, "hr", "total_staff",        teach + admin,"pers.", i),
            _kpi(insat.id, "hr", "absenteeism_rate",   abs_,         "%",    i),
            _kpi(insat.id, "hr", "training_hours",     train,        "h",    i),
        ]
    for i, (emp, nat, intl, delay) in enumerate([(88, 80, 38, 3.5), (90, 82, 40, 3.2), (89, 81, 39, 3.4)]):
        records += [
            _kpi(insat.id, "insertion", "employability_rate",             emp,   "%",   i),
            _kpi(insat.id, "insertion", "national_convention_rate",       nat,   "%",   i),
            _kpi(insat.id, "insertion", "international_convention_rate",  intl,  "%",   i),
            _kpi(insat.id, "insertion", "insertion_delay_months",         delay, "mois",i),
        ]
    for i, (kwh, co2, rec) in enumerate([(980_000, 286, 48), (970_000, 283, 50), (975_000, 285, 51)]):
        records += [
            _kpi(insat.id, "esg", "energy_consumption_kwh", kwh, "kWh",  i),
            _kpi(insat.id, "esg", "carbon_footprint_ton",   co2, "t CO₂",i),
            _kpi(insat.id, "esg", "recycling_rate",         rec, "%",    i),
        ]
    for i, (pub, proj, fund) in enumerate([(110, 34, 1_500_000), (118, 36, 1_650_000), (115, 38, 1_720_000)]):
        records += [
            _kpi(insat.id, "research", "publications_count", pub,  "pub.",   i),
            _kpi(insat.id, "research", "active_projects",    proj, "projets",i),
            _kpi(insat.id, "research", "funding_tnd",        fund, "TND",    i),
        ]

    # ─── ENIB ─── risque dépassement budgétaire (taux d'exécution → 97.7%)
    # École d'ingénieurs de Bizerte, ~3 000 étudiants
    for i, (sr, att, rep, drop) in enumerate([(81, 89, 10, 9), (82, 90, 9, 8), (80, 88, 10, 9)]):
        records += [
            _kpi(enib.id, "academic", "success_rate",     sr,   "%", i),
            _kpi(enib.id, "academic", "attendance_rate",  att,  "%", i),
            _kpi(enib.id, "academic", "repetition_rate",  rep,  "%", i),
            _kpi(enib.id, "academic", "dropout_rate",     drop, "%", i),
        ]
    for i, (alloc, cons) in enumerate([(4_000_000, 3_520_000), (4_000_000, 3_700_000), (4_000_000, 3_908_000)]):
        records += [
            _kpi(enib.id, "finance", "budget_allocated",      alloc,                  "TND", i),
            _kpi(enib.id, "finance", "budget_consumed",       cons,                   "TND", i),
            _kpi(enib.id, "finance", "budget_execution_rate", round(cons/alloc*100,1), "%",  i),
            _kpi(enib.id, "finance", "cost_per_student",      round(cons/3000, 1),    "TND", i),
        ]
    for i, (teach, admin, abs_, train) in enumerate([(175, 58, 4.5, 390), (177, 59, 4.8, 410), (180, 60, 5.2, 420)]):
        records += [
            _kpi(enib.id, "hr", "teaching_headcount", teach,        "pers.", i),
            _kpi(enib.id, "hr", "admin_headcount",    admin,        "pers.", i),
            _kpi(enib.id, "hr", "total_staff",        teach + admin,"pers.", i),
            _kpi(enib.id, "hr", "absenteeism_rate",   abs_,         "%",    i),
            _kpi(enib.id, "hr", "training_hours",     train,        "h",    i),
        ]
    for i, (emp, nat, intl, delay) in enumerate([(76, 68, 20, 5.0), (78, 70, 22, 4.7), (77, 69, 21, 4.8)]):
        records += [
            _kpi(enib.id, "insertion", "employability_rate",             emp,   "%",   i),
            _kpi(enib.id, "insertion", "national_convention_rate",       nat,   "%",   i),
            _kpi(enib.id, "insertion", "international_convention_rate",  intl,  "%",   i),
            _kpi(enib.id, "insertion", "insertion_delay_months",         delay, "mois",i),
        ]
    for i, (kwh, co2, rec) in enumerate([(580_000, 169, 34), (575_000, 168, 36), (585_000, 171, 35)]):
        records += [
            _kpi(enib.id, "esg", "energy_consumption_kwh", kwh, "kWh",  i),
            _kpi(enib.id, "esg", "carbon_footprint_ton",   co2, "t CO₂",i),
            _kpi(enib.id, "esg", "recycling_rate",         rec, "%",    i),
        ]
    for i, (pub, proj, fund) in enumerate([(45, 15, 520_000), (48, 16, 560_000), (47, 17, 590_000)]):
        records += [
            _kpi(enib.id, "research", "publications_count", pub,  "pub.",   i),
            _kpi(enib.id, "research", "active_projects",    proj, "projets",i),
            _kpi(enib.id, "research", "funding_tnd",        fund, "TND",    i),
        ]

    # ─── FSB ─── profil stable, grande faculté de sciences
    # ~6 000 étudiants, forte recherche
    for i, (sr, att, rep, drop) in enumerate([(76, 86, 13, 11), (77, 87, 12, 10), (76, 86, 12, 11)]):
        records += [
            _kpi(fsb.id, "academic", "success_rate",     sr,   "%", i),
            _kpi(fsb.id, "academic", "attendance_rate",  att,  "%", i),
            _kpi(fsb.id, "academic", "repetition_rate",  rep,  "%", i),
            _kpi(fsb.id, "academic", "dropout_rate",     drop, "%", i),
        ]
    for i, (alloc, cons) in enumerate([(5_500_000, 4_950_000), (5_500_000, 5_060_000), (5_500_000, 5_005_000)]):
        records += [
            _kpi(fsb.id, "finance", "budget_allocated",      alloc,                  "TND", i),
            _kpi(fsb.id, "finance", "budget_consumed",       cons,                   "TND", i),
            _kpi(fsb.id, "finance", "budget_execution_rate", round(cons/alloc*100,1), "%",  i),
            _kpi(fsb.id, "finance", "cost_per_student",      round(cons/6000, 1),    "TND", i),
        ]
    for i, (teach, admin, abs_, train) in enumerate([(310, 105, 5.0, 530), (312, 106, 4.8, 550), (315, 108, 4.9, 560)]):
        records += [
            _kpi(fsb.id, "hr", "teaching_headcount", teach,        "pers.", i),
            _kpi(fsb.id, "hr", "admin_headcount",    admin,        "pers.", i),
            _kpi(fsb.id, "hr", "total_staff",        teach + admin,"pers.", i),
            _kpi(fsb.id, "hr", "absenteeism_rate",   abs_,         "%",    i),
            _kpi(fsb.id, "hr", "training_hours",     train,        "h",    i),
        ]
    for i, (emp, nat, intl, delay) in enumerate([(66, 59, 13, 6.2), (67, 60, 13, 6.0), (67, 60, 14, 6.1)]):
        records += [
            _kpi(fsb.id, "insertion", "employability_rate",             emp,   "%",   i),
            _kpi(fsb.id, "insertion", "national_convention_rate",       nat,   "%",   i),
            _kpi(fsb.id, "insertion", "international_convention_rate",  intl,  "%",   i),
            _kpi(fsb.id, "insertion", "insertion_delay_months",         delay, "mois",i),
        ]
    for i, (kwh, co2, rec) in enumerate([(820_000, 240, 27), (815_000, 238, 28), (818_000, 239, 28)]):
        records += [
            _kpi(fsb.id, "esg", "energy_consumption_kwh", kwh, "kWh",  i),
            _kpi(fsb.id, "esg", "carbon_footprint_ton",   co2, "t CO₂",i),
            _kpi(fsb.id, "esg", "recycling_rate",         rec, "%",    i),
        ]
    for i, (pub, proj, fund) in enumerate([(72, 22, 820_000), (76, 24, 870_000), (74, 25, 900_000)]):
        records += [
            _kpi(fsb.id, "research", "publications_count", pub,  "pub.",   i),
            _kpi(fsb.id, "research", "active_projects",    proj, "projets",i),
            _kpi(fsb.id, "research", "funding_tnd",        fund, "TND",    i),
        ]

    # ─── SUP'COM ─── profil en amélioration progressive
    # École de télécommunications, ~2 000 étudiants, forte internationalisation
    for i, (sr, att, rep, drop) in enumerate([(72, 83, 14, 13), (74, 85, 13, 11), (76, 86, 12, 10)]):
        records += [
            _kpi(supcom.id, "academic", "success_rate",     sr,   "%", i),
            _kpi(supcom.id, "academic", "attendance_rate",  att,  "%", i),
            _kpi(supcom.id, "academic", "repetition_rate",  rep,  "%", i),
            _kpi(supcom.id, "academic", "dropout_rate",     drop, "%", i),
        ]
    for i, (alloc, cons) in enumerate([(2_800_000, 2_380_000), (2_800_000, 2_490_000), (2_800_000, 2_575_000)]):
        records += [
            _kpi(supcom.id, "finance", "budget_allocated",      alloc,                  "TND", i),
            _kpi(supcom.id, "finance", "budget_consumed",       cons,                   "TND", i),
            _kpi(supcom.id, "finance", "budget_execution_rate", round(cons/alloc*100,1), "%",  i),
            _kpi(supcom.id, "finance", "cost_per_student",      round(cons/2000, 1),    "TND", i),
        ]
    for i, (teach, admin, abs_, train) in enumerate([(115, 38, 6.0, 220), (117, 39, 5.5, 240), (120, 40, 5.0, 260)]):
        records += [
            _kpi(supcom.id, "hr", "teaching_headcount", teach,        "pers.", i),
            _kpi(supcom.id, "hr", "admin_headcount",    admin,        "pers.", i),
            _kpi(supcom.id, "hr", "total_staff",        teach + admin,"pers.", i),
            _kpi(supcom.id, "hr", "absenteeism_rate",   abs_,         "%",    i),
            _kpi(supcom.id, "hr", "training_hours",     train,        "h",    i),
        ]
    for i, (emp, nat, intl, delay) in enumerate([(68, 60, 28, 5.8), (71, 63, 31, 5.5), (74, 65, 34, 5.2)]):
        records += [
            _kpi(supcom.id, "insertion", "employability_rate",             emp,   "%",   i),
            _kpi(supcom.id, "insertion", "national_convention_rate",       nat,   "%",   i),
            _kpi(supcom.id, "insertion", "international_convention_rate",  intl,  "%",   i),
            _kpi(supcom.id, "insertion", "insertion_delay_months",         delay, "mois",i),
        ]
    for i, (kwh, co2, rec) in enumerate([(350_000, 102, 22), (345_000, 101, 24), (340_000, 99, 26)]):
        records += [
            _kpi(supcom.id, "esg", "energy_consumption_kwh", kwh, "kWh",  i),
            _kpi(supcom.id, "esg", "carbon_footprint_ton",   co2, "t CO₂",i),
            _kpi(supcom.id, "esg", "recycling_rate",         rec, "%",    i),
        ]
    for i, (pub, proj, fund) in enumerate([(35, 11, 390_000), (38, 13, 430_000), (42, 15, 480_000)]):
        records += [
            _kpi(supcom.id, "research", "publications_count", pub,  "pub.",   i),
            _kpi(supcom.id, "research", "active_projects",    proj, "projets",i),
            _kpi(supcom.id, "research", "funding_tnd",        fund, "TND",    i),
        ]

    db.bulk_save_objects(records)
    db.commit()
    print(f"  - {len(records)} enregistrements KPI créés")


def _seed_alert_rules():
    rules = [
        AlertRule(
            institution_id=None,
            name="Taux d'abandon critique (global)",
            indicator_key="dropout_rate",
            domain="academic",
            operator=">",
            threshold=15.0,
            severity=AlertSeverity.critical,
            description="Déclenché si le taux d'abandon dépasse 15% dans un établissement",
        ),
        AlertRule(
            institution_id=None,
            name="Taux de réussite faible",
            indicator_key="success_rate",
            domain="academic",
            operator="<",
            threshold=72.0,
            severity=AlertSeverity.warning,
            description="Alerte si le taux de réussite passe sous 72%",
        ),
        AlertRule(
            institution_id=None,
            name="Exécution budgétaire élevée",
            indicator_key="budget_execution_rate",
            domain="finance",
            operator=">=",
            threshold=97.0,
            severity=AlertSeverity.warning,
            description="Risque de dépassement budgétaire si l'exécution dépasse 97%",
        ),
        AlertRule(
            institution_id=None,
            name="Taux d'absentéisme enseignant",
            indicator_key="absenteeism_rate",
            domain="hr",
            operator=">",
            threshold=5.0,
            severity=AlertSeverity.info,
            description="Absentéisme enseignant supérieur à 5%",
        ),
    ]
    for rule in rules:
        db.add(rule)
    db.commit()
    print(f"  - {len(rules)} règles d'alerte créées")


def _run_alert_check():
    from app.services.alert_service import run_alert_check
    alerts = run_alert_check(db)
    print(f"  - {len(alerts)} alerte(s) déclenchée(s) sur les données de démonstration")


if __name__ == "__main__":
    try:
        seed()
    finally:
        db.close()
