export type UserRole = "super_admin" | "president" | "department";

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  institution_id: number | null;
  domain_scope: string | null;
}

export interface Institution {
  id: number;
  name: string;
  acronym: string;
  type: string;
  city: string;
  is_active: boolean;
}

export interface KPIRecord {
  id: number;
  institution_id: number;
  institution_name: string;
  institution_acronym: string;
  domain: string;
  indicator_key: string;
  value: number;
  unit: string;
  period_label: string;
  is_anomaly: boolean;
  z_score: number | null;
  anomaly_direction: string | null;
}

export interface KPITrend {
  institution_id: number;
  indicator_key: string;
  unit: string;
  historical_values: number[];
  historical_labels: string[];
  forecast_values: number[];
  forecast_labels: string[];
  trend: string;
  slope: number;
}

export type AlertSeverity = "info" | "warning" | "critical";

export interface AlertItem {
  id: number;
  rule_id: number;
  institution_id: number;
  institution_name: string;
  indicator_key: string;
  value_at_trigger: number;
  period_label: string;
  triggered_at: string;
  acknowledged_at: string | null;
  is_resolved: boolean;
  severity: AlertSeverity;
  rule_name: string;
  explanation: string | null;
}

export type ReportFormat = "pdf" | "excel";
export type ReportStatus = "pending" | "generating" | "ready" | "failed";

export interface Report {
  id: number;
  institution_id: number;
  type: string;
  period_label: string;
  format: ReportFormat;
  status: ReportStatus;
  file_path: string | null;
  narrative: string | null;
  generated_at: string | null;
  created_at: string;
}

export const DOMAIN_LABELS: Record<string, string> = {
  academic: "Académique",
  finance: "Finance",
  hr: "Ressources Humaines",
  esg: "ESG / RSE",
  insertion: "Insertion Professionnelle",
  research: "Recherche",
  infrastructure: "Infrastructure",
  partnerships: "Partenariats",
  student_life: "Vie Estudiantine",
};

// ─── Track 1: Ingestion Jobs ───────────────────────────────────────────────
export type JobStatus = "pending" | "processing" | "completed" | "failed";
export type JobSourceType = "pdf" | "image" | "excel" | "csv";

export interface IngestionJob {
  id: number;
  institution_id: number;
  source_type: JobSourceType;
  original_filename: string;
  status: JobStatus;
  kpi_count: number;
  quality_score: number;
  imported_count: number;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
  extracted_kpis: ExtractedKPI[];
}

export interface ExtractedKPI {
  domain: string;
  indicator_key: string;
  value: number;
  unit: string;
  period_label: string;
  confidence: number;
}

// ─── Track 2: Ranking & Health ─────────────────────────────────────────────
export interface InstitutionRanking {
  rank: number;
  institution_id: number;
  institution_name: string;
  institution_acronym: string;
  city: string;
  overall_score: number;
  domain_scores: Record<string, number>;
  risk_level: "low" | "medium" | "high";
  risk_label: string;
  kpi_count: number;
}

export interface InstitutionHealth {
  institution_id: number;
  institution_name?: string;
  institution_acronym?: string;
  overall_score: number;
  domain_scores: Record<string, number>;
  risk_level: "low" | "medium" | "high";
  risk_label: string;
  kpi_count: number;
}

export const INDICATOR_LABELS: Record<string, string> = {
  success_rate: "Taux de réussite",
  attendance_rate: "Taux de présence",
  dropout_rate: "Taux d'abandon",
  repetition_rate: "Taux de redoublement",
  budget_allocated: "Budget alloué",
  budget_consumed: "Budget consommé",
  budget_execution_rate: "Taux d'exécution budgétaire",
  cost_per_student: "Coût par étudiant",
  teaching_headcount: "Effectif enseignant",
  admin_headcount: "Effectif administratif",
  absenteeism_rate: "Taux d'absentéisme",
  training_hours: "Heures de formation",
  energy_consumption_kwh: "Consommation énergétique",
  carbon_footprint_ton: "Empreinte carbone",
  recycling_rate: "Taux de recyclage",
  employability_rate: "Taux d'employabilité",
  national_convention_rate: "Convention nationale",
  international_convention_rate: "Convention internationale",
  insertion_delay_months: "Délai d'insertion",
  publications_count: "Publications",
  active_projects: "Projets actifs",
  funding_tnd: "Financements (TND)",
};
