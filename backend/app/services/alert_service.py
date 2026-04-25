from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.alert import AlertRule, Alert, AlertSeverity
from app.models.kpi import KPIRecord
from app.models.institution import Institution


OPERATORS = {
    ">": lambda v, t: v > t,
    "<": lambda v, t: v < t,
    ">=": lambda v, t: v >= t,
    "<=": lambda v, t: v <= t,
    "==": lambda v, t: v == t,
}

SEVERITY_LABELS = {
    AlertSeverity.info: "Information",
    AlertSeverity.warning: "Avertissement",
    AlertSeverity.critical: "Critique",
}

INDICATOR_LABELS = {
    "dropout_rate": "Taux d'abandon",
    "success_rate": "Taux de réussite",
    "attendance_rate": "Taux de présence",
    "budget_execution_rate": "Taux d'exécution budgétaire",
    "absenteeism_rate": "Taux d'absentéisme",
}


def run_alert_check(db: Session) -> list[Alert]:
    rules = db.query(AlertRule).filter(AlertRule.is_active == True).all()
    new_alerts = []

    for rule in rules:
        institution_ids = (
            [rule.institution_id]
            if rule.institution_id
            else [i.id for i in db.query(Institution).filter(Institution.is_active == True).all()]
        )

        for inst_id in institution_ids:
            latest = (
                db.query(KPIRecord)
                .filter(
                    KPIRecord.institution_id == inst_id,
                    KPIRecord.indicator_key == rule.indicator_key,
                )
                .order_by(KPIRecord.period_start.desc())
                .first()
            )

            if not latest:
                continue

            op_fn = OPERATORS.get(rule.operator)
            if not op_fn:
                continue

            if op_fn(latest.value, rule.threshold):
                # avoid duplicate alerts for same rule+institution+period
                existing = (
                    db.query(Alert)
                    .filter(
                        Alert.rule_id == rule.id,
                        Alert.institution_id == inst_id,
                        Alert.period_label == latest.period_label,
                        Alert.is_resolved == False,
                    )
                    .first()
                )
                if existing:
                    continue

                indicator_label = INDICATOR_LABELS.get(rule.indicator_key, rule.indicator_key)
                severity_label = SEVERITY_LABELS.get(rule.severity, rule.severity)
                explanation = (
                    f"L'indicateur '{indicator_label}' a atteint {latest.value} {latest.unit} "
                    f"pour la période {latest.period_label}, "
                    f"dépassant le seuil {rule.operator} {rule.threshold} {latest.unit}. "
                    f"Niveau de sévérité: {severity_label}. "
                    f"Une action correctrice est recommandée."
                )

                alert = Alert(
                    rule_id=rule.id,
                    institution_id=inst_id,
                    indicator_key=rule.indicator_key,
                    value_at_trigger=latest.value,
                    period_label=latest.period_label,
                    triggered_at=datetime.now(timezone.utc),
                    explanation=explanation,
                )
                db.add(alert)
                new_alerts.append(alert)

    db.commit()
    return new_alerts


def get_alerts(db: Session, institution_id: int | None, unresolved_only: bool = False) -> list[dict]:
    query = (
        db.query(Alert, AlertRule.severity, AlertRule.name, Institution.name.label("inst_name"))
        .join(AlertRule, Alert.rule_id == AlertRule.id)
        .join(Institution, Alert.institution_id == Institution.id)
    )

    if institution_id:
        query = query.filter(Alert.institution_id == institution_id)
    if unresolved_only:
        query = query.filter(Alert.is_resolved == False)

    rows = query.order_by(Alert.triggered_at.desc()).all()

    return [
        {
            "id": alert.id,
            "rule_id": alert.rule_id,
            "institution_id": alert.institution_id,
            "institution_name": inst_name,
            "indicator_key": alert.indicator_key,
            "value_at_trigger": alert.value_at_trigger,
            "period_label": alert.period_label,
            "triggered_at": alert.triggered_at,
            "acknowledged_at": alert.acknowledged_at,
            "is_resolved": alert.is_resolved,
            "severity": severity,
            "rule_name": rule_name,
            "explanation": alert.explanation,
        }
        for alert, severity, rule_name, inst_name in rows
    ]


def acknowledge_alert(db: Session, alert_id: int, user_id: int) -> Alert | None:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None
    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.acknowledged_by = user_id
    alert.is_resolved = True
    db.commit()
    db.refresh(alert)
    return alert
