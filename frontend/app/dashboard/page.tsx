"use client";
import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import KPICard from "@/components/dashboard/KPICard";
import KPIChart from "@/components/dashboard/KPIChart";
import ComparisonChart from "@/components/dashboard/ComparisonChart";
import UploadButton from "@/components/dashboard/UploadButton";
import { api } from "@/lib/api";
import { KPIRecord, KPITrend, DOMAIN_LABELS } from "@/lib/types";
import { useAuthStore } from "@/store/auth";
import { RefreshCw, AlertTriangle } from "lucide-react";
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

export default function DashboardPage() {
  const { user } = useAuthStore();

  // Department users are locked to their domain
  const isDeptUser = user?.role === "department";
  const lockedDomain = user?.domain_scope ?? null;

  const [selectedInstitution, setSelectedInstitution] = useState<number | null>(null);
  const [activeDomain, setActiveDomain] = useState(lockedDomain ?? "academic");
  const [kpis, setKpis] = useState<KPIRecord[]>([]);
  const [trends, setTrends] = useState<KPITrend[]>([]);
  const [comparisons, setComparisons] = useState<Record<string, any[]>>({});
  const [loading, setLoading] = useState(false);
  const [anomalyCount, setAnomalyCount] = useState(0);

  useEffect(() => {
    if (user?.institution_id) setSelectedInstitution(user.institution_id);
  }, [user]);

  // Keep domain locked for department users
  useEffect(() => {
    if (lockedDomain) setActiveDomain(lockedDomain);
  }, [lockedDomain]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = { domain: activeDomain };
      if (selectedInstitution) params.institution_id = selectedInstitution;

      const kpiRes = await api.get<KPIRecord[]>("/kpis/", { params });
      setKpis(kpiRes.data);
      setAnomalyCount(kpiRes.data.filter((k) => k.is_anomaly).length);

      const trendKeys = DOMAIN_TRENDS[activeDomain] ?? [];
      const compareKeys = DOMAIN_COMPARE[activeDomain] ?? [];

      if (selectedInstitution) {
        const trendResults = await Promise.all(
          trendKeys.map((key) =>
            api.get<KPITrend>("/kpis/trend", {
              params: { institution_id: selectedInstitution, indicator_key: key },
            }).catch(() => null)
          )
        );
        setTrends(
          trendResults
            .filter((r) => r && r.data?.historical_values?.length)
            .map((r) => r!.data)
        );
        setComparisons({});
      } else {
        setTrends([]);
        const compResults = await Promise.all(
          compareKeys.map((key) =>
            api.get<any[]>("/kpis/compare", { params: { indicator_key: key } }).catch(() => null)
          )
        );
        const compMap: Record<string, any[]> = {};
        compareKeys.forEach((key, i) => {
          if (compResults[i]?.data?.length) compMap[key] = compResults[i]!.data;
        });
        setComparisons(compMap);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) fetchData();
  }, [selectedInstitution, activeDomain, user]);

  const filteredKpis = kpis.filter((k) => k.domain === activeDomain);
  const visibleDomains = isDeptUser && lockedDomain ? [lockedDomain] : ALL_DOMAINS;

  return (
    <DashboardLayout
      selectedInstitution={selectedInstitution}
      onSelectInstitution={setSelectedInstitution}
    >
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

            {/* Upload button — visible to all users */}
            <UploadButton
              institutionId={selectedInstitution}
              onSuccess={fetchData}
            />

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

        {/* Domain tabs — locked for department users */}
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
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl p-5 border border-gray-100 animate-pulse h-32" />
            ))}
          </div>
        ) : filteredKpis.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-100 p-12 text-center">
            <p className="text-gray-400 text-sm">Aucune donnée disponible pour ce domaine.</p>
            <p className="text-gray-400 text-xs mt-1">Utilisez le bouton "Importer" pour charger vos données.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {filteredKpis.map((kpi) => (
              <KPICard key={`${kpi.institution_id}-${kpi.indicator_key}`} {...kpi} />
            ))}
          </div>
        )}

        {/* Trend charts — single institution */}
        {selectedInstitution && trends.length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-gray-700 mb-3">
              Tendances & Prévisions IA — {DOMAIN_LABELS[activeDomain]}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {trends.map((trend) => (
                <KPIChart key={trend.indicator_key} trend={trend} />
              ))}
            </div>
          </div>
        )}

        {/* Comparison charts — super admin consolidated view */}
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
      </div>
    </DashboardLayout>
  );
}
