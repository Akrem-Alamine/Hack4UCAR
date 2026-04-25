"""
Seed script — 5 Tunisian universities, 3 semesters of KPI data,
one institution with a dropout spike to trigger the alert.

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
    users = _seed_users(institutions)
    _seed_kpis(institutions)
    _seed_alert_rules(institutions)
    _run_alert_check()

    print("✅ Données de démonstration créées avec succès.")
    print("\n📋 Comptes de connexion:")
    print("  super@ucar.tn          / demo1234  (Super Admin UCAR)")
    for inst in institutions:
        key = inst.acronym.lower()
        print(f"  president@{key}.tn       / demo1234  (Président {inst.acronym})")


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
        {"name": "École Nationale des Sciences et Technologies Avancées de Borj Cédria", "acronym": "ENSTAB", "type": "École Nationale", "city": "Tunis"},
        {"name": "École Nationale d'Ingénieurs de Tunis", "acronym": "ENIT", "type": "École Nationale", "city": "Tunis"},
        {"name": "École Supérieure Privée d'Ingénierie et de Technologies", "acronym": "ESPRIT", "type": "Établissement Privé", "city": "Tunis"},
        {"name": "Faculté des Sciences de Tunis", "acronym": "FST", "type": "Faculté", "city": "Tunis"},
        {"name": "Institut Supérieur des Études Technologiques de Sousse", "acronym": "ISETSOUSSE", "type": "Institut", "city": "Sousse"},
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
    {"name": "Académique",              "code": "ACAD",   "domain": "academic",  "email_prefix": "academique"},
    {"name": "Finance",                 "code": "FIN",    "domain": "finance",   "email_prefix": "finance"},
    {"name": "Ressources Humaines",     "code": "RH",     "domain": "hr",        "email_prefix": "rh"},
    {"name": "Insertion Professionnelle","code": "INSERT", "domain": "insertion", "email_prefix": "insertion"},
    {"name": "ESG / RSE",               "code": "ESG",    "domain": "esg",       "email_prefix": "esg"},
    {"name": "Recherche",               "code": "RECH",   "domain": "research",  "email_prefix": "recherche"},
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


def _seed_users(institutions: list[Institution]) -> list[User]:
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
        key = inst.acronym.lower()
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
    print(f"  - {len(users)} utilisateurs créés (1 président + 6 départements × {len(institutions)} établissements)")
    return users


PERIODS = [
    ("2023-2024 S1", date(2023, 9, 1), date(2024, 1, 31)),
    ("2023-2024 S2", date(2024, 2, 1), date(2024, 6, 30)),
    ("2024-2025 S1", date(2024, 9, 1), date(2025, 1, 31)),
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
    enstab, enit, esprit, fst, isetsousse = institutions

    # ─── ENSTAB ─── anomaly: dropout_rate spikes to 22% in S3
    for i, (sr, att, rep, drop) in enumerate([(82, 91, 9, 7), (84, 90, 8, 8), (78, 87, 11, 22)]):
        records += [
            _kpi(enstab.id, "academic", "success_rate", sr, "%", i),
            _kpi(enstab.id, "academic", "attendance_rate", att, "%", i),
            _kpi(enstab.id, "academic", "repetition_rate", rep, "%", i),
            _kpi(enstab.id, "academic", "dropout_rate", drop, "%", i),
        ]
    for i, (alloc, cons) in enumerate([(2_800_000, 2_450_000), (2_800_000, 2_600_000), (2_800_000, 2_710_000)]):
        records += [
            _kpi(enstab.id, "finance", "budget_allocated", alloc, "TND", i),
            _kpi(enstab.id, "finance", "budget_consumed", cons, "TND", i),
            _kpi(enstab.id, "finance", "budget_execution_rate", round(cons/alloc*100, 1), "%", i),
            _kpi(enstab.id, "finance", "cost_per_student", round(cons/1200, 1), "TND", i),
        ]
    for i, (teach, admin, abs_, train) in enumerate([(120, 45, 4.2, 320), (120, 45, 3.8, 340), (122, 46, 5.1, 290)]):
        records += [
            _kpi(enstab.id, "hr", "teaching_headcount", teach, "pers.", i),
            _kpi(enstab.id, "hr", "admin_headcount", admin, "pers.", i),
            _kpi(enstab.id, "hr", "absenteeism_rate", abs_, "%", i),
            _kpi(enstab.id, "hr", "training_hours", train, "h", i),
        ]
    for i, (emp, nat, intl, delay) in enumerate([(72, 65, 18, 5.2), (74, 66, 20, 5.0), (71, 64, 19, 5.4)]):
        records += [
            _kpi(enstab.id, "insertion", "employability_rate", emp, "%", i),
            _kpi(enstab.id, "insertion", "national_convention_rate", nat, "%", i),
            _kpi(enstab.id, "insertion", "international_convention_rate", intl, "%", i),
            _kpi(enstab.id, "insertion", "insertion_delay_months", delay, "mois", i),
        ]
    for i, (kwh, co2, rec) in enumerate([(485000, 142, 28), (472000, 138, 31), (491000, 144, 30)]):
        records += [
            _kpi(enstab.id, "esg", "energy_consumption_kwh", kwh, "kWh", i),
            _kpi(enstab.id, "esg", "carbon_footprint_ton", co2, "t CO₂", i),
            _kpi(enstab.id, "esg", "recycling_rate", rec, "%", i),
        ]
    for i, (pub, proj, fund) in enumerate([(38, 12, 420_000), (41, 13, 450_000), (39, 14, 480_000)]):
        records += [
            _kpi(enstab.id, "research", "publications_count", pub, "pub.", i),
            _kpi(enstab.id, "research", "active_projects", proj, "projets", i),
            _kpi(enstab.id, "research", "funding_tnd", fund, "TND", i),
        ]

    # ─── ENIT ─── high performer
    for i, (sr, att, rep, drop) in enumerate([(88, 93, 6, 5), (90, 94, 5, 4), (89, 93, 6, 5)]):
        records += [
            _kpi(enit.id, "academic", "success_rate", sr, "%", i),
            _kpi(enit.id, "academic", "attendance_rate", att, "%", i),
            _kpi(enit.id, "academic", "repetition_rate", rep, "%", i),
            _kpi(enit.id, "academic", "dropout_rate", drop, "%", i),
        ]
    for i, (alloc, cons) in enumerate([(5_200_000, 4_800_000), (5_200_000, 4_950_000), (5_200_000, 4_900_000)]):
        records += [
            _kpi(enit.id, "finance", "budget_allocated", alloc, "TND", i),
            _kpi(enit.id, "finance", "budget_consumed", cons, "TND", i),
            _kpi(enit.id, "finance", "budget_execution_rate", round(cons/alloc*100, 1), "%", i),
            _kpi(enit.id, "finance", "cost_per_student", round(cons/3200, 1), "TND", i),
        ]
    for i, (teach, admin, abs_, train) in enumerate([(280, 90, 3.1, 620), (280, 90, 2.9, 640), (285, 92, 3.0, 660)]):
        records += [
            _kpi(enit.id, "hr", "teaching_headcount", teach, "pers.", i),
            _kpi(enit.id, "hr", "admin_headcount", admin, "pers.", i),
            _kpi(enit.id, "hr", "absenteeism_rate", abs_, "%", i),
            _kpi(enit.id, "hr", "training_hours", train, "h", i),
        ]
    for i, (emp, nat, intl, delay) in enumerate([(85, 78, 32, 3.8), (87, 80, 35, 3.5), (86, 79, 34, 3.7)]):
        records += [
            _kpi(enit.id, "insertion", "employability_rate", emp, "%", i),
            _kpi(enit.id, "insertion", "national_convention_rate", nat, "%", i),
            _kpi(enit.id, "insertion", "international_convention_rate", intl, "%", i),
            _kpi(enit.id, "insertion", "insertion_delay_months", delay, "mois", i),
        ]
    for i, (kwh, co2, rec) in enumerate([(920000, 268, 42), (910000, 265, 44), (915000, 267, 45)]):
        records += [
            _kpi(enit.id, "esg", "energy_consumption_kwh", kwh, "kWh", i),
            _kpi(enit.id, "esg", "carbon_footprint_ton", co2, "t CO₂", i),
            _kpi(enit.id, "esg", "recycling_rate", rec, "%", i),
        ]
    for i, (pub, proj, fund) in enumerate([(95, 28, 1_200_000), (102, 30, 1_350_000), (98, 32, 1_400_000)]):
        records += [
            _kpi(enit.id, "research", "publications_count", pub, "pub.", i),
            _kpi(enit.id, "research", "active_projects", proj, "projets", i),
            _kpi(enit.id, "research", "funding_tnd", fund, "TND", i),
        ]

    # ─── ESPRIT ─── budget overspend risk
    for i, (sr, att, rep, drop) in enumerate([(80, 88, 10, 9), (81, 89, 10, 8), (79, 87, 11, 10)]):
        records += [
            _kpi(esprit.id, "academic", "success_rate", sr, "%", i),
            _kpi(esprit.id, "academic", "attendance_rate", att, "%", i),
            _kpi(esprit.id, "academic", "repetition_rate", rep, "%", i),
            _kpi(esprit.id, "academic", "dropout_rate", drop, "%", i),
        ]
    for i, (alloc, cons) in enumerate([(3_500_000, 3_100_000), (3_500_000, 3_250_000), (3_500_000, 3_420_000)]):
        records += [
            _kpi(esprit.id, "finance", "budget_allocated", alloc, "TND", i),
            _kpi(esprit.id, "finance", "budget_consumed", cons, "TND", i),
            _kpi(esprit.id, "finance", "budget_execution_rate", round(cons/alloc*100, 1), "%", i),
            _kpi(esprit.id, "finance", "cost_per_student", round(cons/2100, 1), "TND", i),
        ]
    for i, (teach, admin, abs_, train) in enumerate([(160, 55, 4.8, 380), (162, 56, 5.0, 400), (165, 58, 5.5, 410)]):
        records += [
            _kpi(esprit.id, "hr", "teaching_headcount", teach, "pers.", i),
            _kpi(esprit.id, "hr", "admin_headcount", admin, "pers.", i),
            _kpi(esprit.id, "hr", "absenteeism_rate", abs_, "%", i),
            _kpi(esprit.id, "hr", "training_hours", train, "h", i),
        ]
    for i, (emp, nat, intl, delay) in enumerate([(78, 70, 22, 4.5), (80, 72, 24, 4.2), (79, 71, 23, 4.3)]):
        records += [
            _kpi(esprit.id, "insertion", "employability_rate", emp, "%", i),
            _kpi(esprit.id, "insertion", "national_convention_rate", nat, "%", i),
            _kpi(esprit.id, "insertion", "international_convention_rate", intl, "%", i),
            _kpi(esprit.id, "insertion", "insertion_delay_months", delay, "mois", i),
        ]
    for i, (kwh, co2, rec) in enumerate([(620000, 181, 35), (615000, 179, 37), (630000, 184, 36)]):
        records += [
            _kpi(esprit.id, "esg", "energy_consumption_kwh", kwh, "kWh", i),
            _kpi(esprit.id, "esg", "carbon_footprint_ton", co2, "t CO₂", i),
            _kpi(esprit.id, "esg", "recycling_rate", rec, "%", i),
        ]
    for i, (pub, proj, fund) in enumerate([(22, 8, 280_000), (25, 9, 310_000), (24, 10, 330_000)]):
        records += [
            _kpi(esprit.id, "research", "publications_count", pub, "pub.", i),
            _kpi(esprit.id, "research", "active_projects", proj, "projets", i),
            _kpi(esprit.id, "research", "funding_tnd", fund, "TND", i),
        ]

    # ─── FST ─── stable performer
    for i, (sr, att, rep, drop) in enumerate([(75, 85, 13, 11), (76, 86, 12, 10), (74, 84, 13, 12)]):
        records += [
            _kpi(fst.id, "academic", "success_rate", sr, "%", i),
            _kpi(fst.id, "academic", "attendance_rate", att, "%", i),
            _kpi(fst.id, "academic", "repetition_rate", rep, "%", i),
            _kpi(fst.id, "academic", "dropout_rate", drop, "%", i),
        ]
    for i, (alloc, cons) in enumerate([(4_100_000, 3_700_000), (4_100_000, 3_820_000), (4_100_000, 3_780_000)]):
        records += [
            _kpi(fst.id, "finance", "budget_allocated", alloc, "TND", i),
            _kpi(fst.id, "finance", "budget_consumed", cons, "TND", i),
            _kpi(fst.id, "finance", "budget_execution_rate", round(cons/alloc*100, 1), "%", i),
            _kpi(fst.id, "finance", "cost_per_student", round(cons/4500, 1), "TND", i),
        ]
    for i, (teach, admin, abs_, train) in enumerate([(220, 75, 5.5, 480), (222, 76, 5.2, 500), (225, 77, 5.3, 510)]):
        records += [
            _kpi(fst.id, "hr", "teaching_headcount", teach, "pers.", i),
            _kpi(fst.id, "hr", "admin_headcount", admin, "pers.", i),
            _kpi(fst.id, "hr", "absenteeism_rate", abs_, "%", i),
            _kpi(fst.id, "hr", "training_hours", train, "h", i),
        ]
    for i, (emp, nat, intl, delay) in enumerate([(65, 58, 12, 6.5), (67, 60, 13, 6.2), (66, 59, 12, 6.3)]):
        records += [
            _kpi(fst.id, "insertion", "employability_rate", emp, "%", i),
            _kpi(fst.id, "insertion", "national_convention_rate", nat, "%", i),
            _kpi(fst.id, "insertion", "international_convention_rate", intl, "%", i),
            _kpi(fst.id, "insertion", "insertion_delay_months", delay, "mois", i),
        ]
    for i, (kwh, co2, rec) in enumerate([(750000, 219, 25), (742000, 217, 27), (755000, 221, 26)]):
        records += [
            _kpi(fst.id, "esg", "energy_consumption_kwh", kwh, "kWh", i),
            _kpi(fst.id, "esg", "carbon_footprint_ton", co2, "t CO₂", i),
            _kpi(fst.id, "esg", "recycling_rate", rec, "%", i),
        ]
    for i, (pub, proj, fund) in enumerate([(58, 18, 680_000), (62, 19, 720_000), (60, 20, 750_000)]):
        records += [
            _kpi(fst.id, "research", "publications_count", pub, "pub.", i),
            _kpi(fst.id, "research", "active_projects", proj, "projets", i),
            _kpi(fst.id, "research", "funding_tnd", fund, "TND", i),
        ]

    # ─── ISET Sousse ─── regional institute, lower but improving
    for i, (sr, att, rep, drop) in enumerate([(70, 82, 15, 13), (72, 83, 14, 12), (73, 84, 13, 11)]):
        records += [
            _kpi(isetsousse.id, "academic", "success_rate", sr, "%", i),
            _kpi(isetsousse.id, "academic", "attendance_rate", att, "%", i),
            _kpi(isetsousse.id, "academic", "repetition_rate", rep, "%", i),
            _kpi(isetsousse.id, "academic", "dropout_rate", drop, "%", i),
        ]
    for i, (alloc, cons) in enumerate([(1_800_000, 1_550_000), (1_800_000, 1_620_000), (1_800_000, 1_680_000)]):
        records += [
            _kpi(isetsousse.id, "finance", "budget_allocated", alloc, "TND", i),
            _kpi(isetsousse.id, "finance", "budget_consumed", cons, "TND", i),
            _kpi(isetsousse.id, "finance", "budget_execution_rate", round(cons/alloc*100, 1), "%", i),
            _kpi(isetsousse.id, "finance", "cost_per_student", round(cons/2200, 1), "TND", i),
        ]
    for i, (teach, admin, abs_, train) in enumerate([(85, 32, 6.2, 210), (87, 33, 5.8, 230), (88, 34, 5.5, 245)]):
        records += [
            _kpi(isetsousse.id, "hr", "teaching_headcount", teach, "pers.", i),
            _kpi(isetsousse.id, "hr", "admin_headcount", admin, "pers.", i),
            _kpi(isetsousse.id, "hr", "absenteeism_rate", abs_, "%", i),
            _kpi(isetsousse.id, "hr", "training_hours", train, "h", i),
        ]
    for i, (emp, nat, intl, delay) in enumerate([(62, 55, 8, 7.2), (64, 57, 9, 7.0), (65, 58, 10, 6.8)]):
        records += [
            _kpi(isetsousse.id, "insertion", "employability_rate", emp, "%", i),
            _kpi(isetsousse.id, "insertion", "national_convention_rate", nat, "%", i),
            _kpi(isetsousse.id, "insertion", "international_convention_rate", intl, "%", i),
            _kpi(isetsousse.id, "insertion", "insertion_delay_months", delay, "mois", i),
        ]
    for i, (kwh, co2, rec) in enumerate([(320000, 94, 20), (315000, 92, 22), (318000, 93, 23)]):
        records += [
            _kpi(isetsousse.id, "esg", "energy_consumption_kwh", kwh, "kWh", i),
            _kpi(isetsousse.id, "esg", "carbon_footprint_ton", co2, "t CO₂", i),
            _kpi(isetsousse.id, "esg", "recycling_rate", rec, "%", i),
        ]
    for i, (pub, proj, fund) in enumerate([(12, 4, 120_000), (14, 5, 135_000), (15, 5, 145_000)]):
        records += [
            _kpi(isetsousse.id, "research", "publications_count", pub, "pub.", i),
            _kpi(isetsousse.id, "research", "active_projects", proj, "projets", i),
            _kpi(isetsousse.id, "research", "funding_tnd", fund, "TND", i),
        ]

    db.bulk_save_objects(records)
    db.commit()
    print(f"  - {len(records)} enregistrements KPI créés")


def _seed_alert_rules(institutions: list[Institution]):
    enstab = institutions[0]

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
            description="Risque de dépassement budgétaire",
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
