"use client";
import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import KPICard from "@/components/dashboard/KPICard";
import KPIChart from "@/components/dashboard/KPIChart";
import ComparisonChart from "@/components/dashboard/ComparisonChart";
import { api } from "@/lib/api";
import { KPIRecord, KPITrend, InstitutionRanking, InstitutionHealth, DOMAIN_LABELS } from "@/lib/types";
import { useAuthStore } from "@/store/auth";
import { RefreshCw, AlertTriangle, Brain, Trophy, TrendingUp, TrendingDown, Minus, ChevronRight } from "lucide-react";
import MarkdownText from "@/components/ui/MarkdownText";
import clsx from "clsx";

const ALL_DOMAINS = ["academic", "finance", "hr", "insertion", "esg", "research"];

const DOMAIN_TRENDS: Record<string, string[]> = {
  academic:  ["success_rate", "dropout_rate", "attendance_rate"],
  finance:   ["budget_execution_rate", "budget_consumed", "cost_per_student"],
  hr:        ["absenteeism_rate", "teaching_headcount", "training_hours"],
  insertion: ["employability_rate", "national_convention_rate", "insertion_delay_months"],
  esg:       ["energy_consumption_kwh", "recycling_rate", "carbon_footprint_ton"],
  research:  ["publications_count", "active_projects", "funding_tnd"],
};

const DOMAIN_COMPARE: Record<string, string[]> = {
  academic:  ["success_rate", "dropout_rate", "attendance_rate"],
  finance:   ["budget_execution_rate", "cost_per_student", "budget_consumed"],
  hr:        ["absenteeism_rate", "teaching_headcount", "training_hours"],
  insertion: ["employability_rate", "national_convention_rate", "insertion_delay_months"],
  esg:       ["energy_consumption_kwh", "recycling_rate", "carbon_footprint_ton"],
  research:  ["publications_count", "active_projects", "funding_tnd"],
};

const RISK_CONFIG = {
  low:    { label: "Risque faible",  color: "text-green-600",  bg: "bg-green-50",  border: "border-green-200" },
  medium: { label: "Risque modéré", color: "text-yellow-600", bg: "bg-yellow-50", border: "border-yellow-200" },
  high:   { label: "Risque élevé",  color: "text-red-600",    bg: "bg-red-50",    border: "border-red-200" },
};

function ScoreBadge({ score }: { score: number }) {
  const color = score >= 75 ? "bg-green-500" : score >= 50 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div className={clsx("h-full rounded-full transition-all", color)} style={{ width: `${score}%` }} />
      </div>
      <span className="text-xs font-bold text-gray-700 w-8 text-right">{score}</span>
    </div>
  );
}

function TrendIcon({ trend }: { trend: string }) {
  if (trend === "croissant") return <TrendingUp size={12} className="text-green-500" />;
  if (trend === "décroissant") return <TrendingDown size={12} className="text-red-500" />;
  return <Minus size={12} className="text-gray-400" />;
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const isDeptUser = user?.role === "department";
  const lockedDomain = user?.domain_scope ?? null;
  const isSuperAdmin = user?.role === "super_admin";

  const [selectedInstitution, setSelectedInstitution] = useState<number | null>(null);
  const [activeDomain, setActiveDomain] = useState(lockedDomain ?? "academic");
  const [kpis, setKpis] = useState<KPIRecord[]>([]);
  const [trends, setTrends] = useState<KPITrend[]>([]);
  const [comparisons, setComparisons] = useState<Record<string, any[]>>({});
  const [ranking, setRanking] = useState<InstitutionRanking[]>([]);
  const [health, setHealth] = useState<InstitutionHealth | null>(null);
  const [insights, setInsights] = useState<string>("");
  const [loadingInsights, setLoadingInsights] = useState(false);
  const [loading, setLoading] = useState(false);
  const [anomalyCount, setAnomalyCount] = useState(0);
  const [showInsights, setShowInsights] = useState(false);

  useEffect(() => {
    if (user?.institution_id) setSelectedInstitution(user.institution_id);
  }, [user]);

  useEffect(() => {
    if (lockedDomain) setActiveDomain(lockedDomain);
  }, [lockedDomain]);

  const fetchData = async () => {
    setLoading(true);
    setInsights("");
    setShowInsights(false);
    try {
      const params: Record<string, any> = { domain: activeDomain };
      if (selectedInstitution) params.institution_id = selectedInstitution;

      const kpiRes = await api.get<KPIRecord[]>("/kpis/", { params });
      setKpis(kpiRes.data);
      setAnomalyCount(kpiRes.data.filter((k) => k.is_anomaly).length);

      const trendKeys = DOMAIN_TRENDS[activeDomain] ?? [];
      const compareKeys = DOMAIN_COMPARE[activeDomain] ?? [];

      if (selectedInstitution) {
        const [trendResults, healthRes] = await Promise.all([
          Promise.all(
            trendKeys.map((key) =>
              api.get<KPITrend>("/kpis/trend", {
                params: { institution_id: selectedInstitution, indicator_key: key },
              }).catch(() => null)
            )
          ),
          api.get<InstitutionHealth>("/kpis/health", {
            params: { institution_id: selectedInstitution },
          }).catch(() => null),
        ]);

        setTrends(
          trendResults
            .filter((r) => r && r.data?.historical_values?.length)
            .map((r) => r!.data)
        );
        setHealth(healthRes?.data || null);
        setComparisons({});
      } else {
        setTrends([]);
        setHealth(null);

        const [compResults, rankingRes] = await Promise.all([
          Promise.all(
            compareKeys.map((key) =>
              api.get<any[]>("/kpis/compare", { params: { indicator_key: key } }).catch(() => null)
            )
          ),
          isSuperAdmin
            ? api.get<InstitutionRanking[]>("/kpis/ranking").catch(() => null)
            : Promise.resolve(null),
        ]);

        const compMap: Record<string, any[]> = {};
        compareKeys.forEach((key, i) => {
          if (compResults[i]?.data?.length) compMap[key] = compResults[i]!.data;
        });
        setComparisons(compMap);
        setRanking(rankingRes?.data || []);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchInsights = async () => {
    if (!selectedInstitution) return;
    setLoadingInsights(true);
    setShowInsights(true);
    try {
      const res = await api.get("/kpis/insights", {
        params: { institution_id: selectedInstitution, domain: activeDomain },
      });
      setInsights(res.data.insights || "");
    } catch {
      setInsights("Analyse temporairement indisponible.");
    } finally {
      setLoadingInsights(false);
    }
  };

  useEffect(() => {
    if (user) fetchData();
  }, [selectedInstitution, activeDomain, user]);

  const filteredKpis = kpis.filter((k) => k.domain === activeDomain);
  const visibleDomains = isDeptUser && lockedDomain ? [lockedDomain] : ALL_DOMAINS;

  return (
    <DashboardLayout selectedInstitution={selectedInstitution} onSelectInstitution={setSelectedInstitution}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-ucar-blue">Tableau de bord</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              {isDeptUser
                ? `Département ${DOMAIN_LABELS[activeDomain] || activeDomain}`
                : selectedInstitution
                ? `Vue établissement — ${DOMAIN_LABELS[activeDomain] || activeDomain}`
                : "Vue consolidée — Tous les établissements"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {anomalyCount > 0 && (
              <span className="flex items-center gap-1.5 bg-red-100 text-red-700 text-xs font-medium px-3 py-1.5 rounded-full">
                <AlertTriangle size={12} />
                {anomalyCount} anomalie{anomalyCount > 1 ? "s" : ""}
              </span>
            )}
            <button
              onClick={fetchData}
              disabled={loading}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
              Actualiser
            </button>
          </div>
        </div>

        {/* Health index bar — when viewing a single institution */}
        {health && (
          <div className={clsx(
            "rounded-xl border p-4",
            RISK_CONFIG[health.risk_level]?.bg,
            RISK_CONFIG[health.risk_level]?.border,
          )}>
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="text-sm font-bold text-gray-800">
                  Indice de santé institutionnel — {health.overall_score}/100
                </p>
                <p className={clsx("text-xs font-medium mt-0.5", RISK_CONFIG[health.risk_level]?.color)}>
                  {RISK_CONFIG[health.risk_level]?.label}
                </p>
              </div>
              <button
                onClick={fetchInsights}
                disabled={loadingInsights}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-ucar-blue text-white text-xs font-medium rounded-lg hover:bg-ucar-blue-light transition-colors disabled:opacity-60"
              >
                <Brain size={12} className={loadingInsights ? "animate-pulse" : ""} />
                Analyse IA
              </button>
            </div>
            <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
              {Object.entries(health.domain_scores).map(([domain, score]) => (
                <div key={domain} className="bg-white/70 rounded-lg p-2">
                  <p className="text-xs text-gray-500 mb-1 truncate">{DOMAIN_LABELS[domain] || domain}</p>
                  <ScoreBadge score={score} />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Insights panel */}
        {showInsights && (
          <div className="bg-ucar-blue/5 border border-ucar-blue/20 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Brain size={16} className="text-ucar-blue" />
              <p className="text-sm font-bold text-ucar-blue">
                Analyse IA — {DOMAIN_LABELS[activeDomain]}
              </p>
            </div>
            {loadingInsights ? (
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <RefreshCw size={14} className="animate-spin" />
                Génération de l'analyse en cours...
              </div>
            ) : (
              <MarkdownText text={insights} />
            )}
          </div>
        )}

        {/* Domain tabs */}
        <div className="flex gap-1.5 flex-wrap">
          {visibleDomains.map((domain) => (
            <button
              key={domain}
              onClick={() => !isDeptUser && setActiveDomain(domain)}
              disabled={isDeptUser}
              className={clsx(
                "px-4 py-1.5 rounded-full text-xs font-semibold transition-colors",
                activeDomain === domain
                  ? "bg-ucar-blue text-white"
                  : "bg-white text-gray-600 border border-gray-200",
                !isDeptUser && activeDomain !== domain && "hover:bg-gray-50",
                isDeptUser && "cursor-default"
              )}
            >
              {DOMAIN_LABELS[domain] || domain}
            </button>
          ))}
        </div>

        {/* KPI Cards */}
        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl p-5 border border-gray-100 animate-pulse h-32" />
            ))}
          </div>
        ) : filteredKpis.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-100 p-12 text-center">
            <p className="text-gray-400 text-sm">Aucune donnée disponible pour ce domaine.</p>
            <p className="text-gray-400 text-xs mt-1">Accédez à la page "Ingestion" pour importer vos données.</p>
          </div>
        ) : selectedInstitution ? (
          /* Single institution — flat grid */
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {filteredKpis.map((kpi) => (
              <KPICard key={`${kpi.institution_id}-${kpi.indicator_key}`} {...kpi} />
            ))}
          </div>
        ) : (
          /* Consolidated view — grouped by institution */
          <div className="space-y-6">
            {Object.entries(
              filteredKpis.reduce((acc, kpi) => {
                if (!acc[kpi.institution_id]) {
                  acc[kpi.institution_id] = {
                    name: kpi.institution_name,
                    acronym: kpi.institution_acronym,
                    kpis: [],
                  };
                }
                acc[kpi.institution_id].kpis.push(kpi);
                return acc;
              }, {} as Record<number, { name: string; acronym: string; kpis: KPIRecord[] }>)
            ).map(([instId, group]) => {
              const anomalies = group.kpis.filter((k) => k.is_anomaly).length;
              return (
                <div key={instId} className="bg-white rounded-xl border border-gray-100 p-4">
                  {/* Institution header */}
                  <div className="flex items-center gap-3 mb-4 pb-3 border-b border-gray-100">
                    <span className="text-xs font-bold text-white bg-ucar-blue px-2.5 py-1 rounded-lg tracking-wide">
                      {group.acronym}
                    </span>
                    <span className="text-sm font-semibold text-gray-700 flex-1">{group.name}</span>
                    {anomalies > 0 && (
                      <span className="flex items-center gap-1 text-xs font-medium text-red-600 bg-red-50 border border-red-100 px-2.5 py-1 rounded-full">
                        <AlertTriangle size={10} />
                        {anomalies} anomalie{anomalies > 1 ? "s" : ""}
                      </span>
                    )}
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {group.kpis.map((kpi) => (
                      <KPICard key={`${kpi.institution_id}-${kpi.indicator_key}`} {...kpi} />
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Trend charts */}
        {selectedInstitution && trends.length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <TrendingUp size={14} className="text-ucar-blue" />
              Tendances & Prévisions IA — {DOMAIN_LABELS[activeDomain]}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {trends.map((trend) => (
                <KPIChart key={trend.indicator_key} trend={trend} />
              ))}
            </div>
          </div>
        )}

        {/* Cross-institution comparison */}
        {!selectedInstitution && Object.keys(comparisons).length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-gray-700 mb-3">
              Comparaison inter-établissements — {DOMAIN_LABELS[activeDomain]}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(comparisons).map(([key, data]) =>
                data?.length > 0 ? <ComparisonChart key={key} indicatorKey={key} data={data} /> : null
              )}
            </div>
          </div>
        )}

        {/* Track 4: Institution ranking table */}
        {!selectedInstitution && isSuperAdmin && ranking.length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <Trophy size={14} className="text-ucar-gold" />
              Classement & Indice de santé — Tous les établissements
            </h2>
            <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-100">
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider w-10">#</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Établissement</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider w-40">Score global</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Acad.</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Finance</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">RH</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Risque</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {ranking.map((inst) => {
                    const risk = RISK_CONFIG[inst.risk_level];
                    return (
                      <tr key={inst.institution_id} className="hover:bg-gray-50/50 transition-colors">
                        <td className="px-4 py-3">
                          <span className={clsx(
                            "text-sm font-bold",
                            inst.rank === 1 ? "text-yellow-500" :
                            inst.rank === 2 ? "text-gray-400" :
                            inst.rank === 3 ? "text-amber-700" : "text-gray-400"
                          )}>
                            {inst.rank === 1 ? "🥇" : inst.rank === 2 ? "🥈" : inst.rank === 3 ? "🥉" : inst.rank}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <p className="font-medium text-gray-800">{inst.institution_acronym}</p>
                          <p className="text-xs text-gray-400">{inst.city}</p>
                        </td>
                        <td className="px-4 py-3">
                          <ScoreBadge score={inst.overall_score} />
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-600">
                          {inst.domain_scores["academic"]?.toFixed(0) ?? "—"}
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-600">
                          {inst.domain_scores["finance"]?.toFixed(0) ?? "—"}
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-600">
                          {inst.domain_scores["hr"]?.toFixed(0) ?? "—"}
                        </td>
                        <td className="px-4 py-3">
                          <span className={clsx("text-xs font-medium px-2 py-0.5 rounded-full", risk?.bg, risk?.color)}>
                            {inst.risk_label}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
