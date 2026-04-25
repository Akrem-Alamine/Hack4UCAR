"use client";
import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { api } from "@/lib/api";
import { AlertItem, AlertSeverity, INDICATOR_LABELS } from "@/lib/types";
import { AlertTriangle, CheckCircle2, Clock, Filter } from "lucide-react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import clsx from "clsx";
import { useAuthStore } from "@/store/auth";

const SEVERITY_CONFIG: Record<AlertSeverity, { label: string; color: string; bg: string }> = {
  critical: { label: "Critique", color: "text-red-700", bg: "bg-red-100" },
  warning: { label: "Avertissement", color: "text-amber-700", bg: "bg-amber-100" },
  info: { label: "Information", color: "text-blue-700", bg: "bg-blue-100" },
};

export default function AlertsPage() {
  const { user } = useAuthStore();
  const [selectedInstitution, setSelectedInstitution] = useState<number | null>(user?.institution_id || null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterResolved, setFilterResolved] = useState<"all" | "open" | "resolved">("open");
  const [ackLoading, setAckLoading] = useState<number | null>(null);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (selectedInstitution) params.institution_id = selectedInstitution;
      if (filterResolved === "open") params.unresolved_only = true;
      const res = await api.get<AlertItem[]>("/alerts/", { params });
      let data = res.data;
      if (filterResolved === "resolved") data = data.filter((a) => a.is_resolved);
      setAlerts(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAlerts(); }, [selectedInstitution, filterResolved]);

  const runCheck = async () => {
    await api.post("/alerts/check");
    fetchAlerts();
  };

  const acknowledge = async (id: number) => {
    setAckLoading(id);
    try {
      await api.post(`/alerts/${id}/acknowledge`);
      fetchAlerts();
    } finally {
      setAckLoading(null);
    }
  };

  return (
    <DashboardLayout selectedInstitution={selectedInstitution} onSelectInstitution={setSelectedInstitution}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-ucar-blue">Alertes Intelligentes</h1>
            <p className="text-sm text-gray-500 mt-0.5">Suivi des anomalies et seuils critiques</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={runCheck} className="px-3 py-2 text-xs font-medium bg-ucar-blue text-white rounded-lg hover:bg-ucar-blue-light transition-colors">
              Vérifier les alertes
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2">
          {(["open", "all", "resolved"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilterResolved(f)}
              className={clsx(
                "px-4 py-1.5 rounded-full text-xs font-semibold transition-colors",
                filterResolved === f
                  ? "bg-ucar-blue text-white"
                  : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
              )}
            >
              {f === "open" ? "Non résolues" : f === "all" ? "Toutes" : "Résolues"}
            </button>
          ))}
          <span className="ml-auto text-xs text-gray-400 self-center">{alerts.length} alerte{alerts.length !== 1 ? "s" : ""}</span>
        </div>

        {/* Alert list */}
        {loading ? (
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl border border-gray-100 h-24 animate-pulse" />
            ))}
          </div>
        ) : alerts.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-100 p-12 text-center">
            <CheckCircle2 className="mx-auto text-green-400 mb-3" size={40} />
            <p className="text-gray-500 font-medium">Aucune alerte active</p>
            <p className="text-gray-400 text-sm mt-1">Tous les indicateurs sont dans les seuils normaux.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => {
              const sev = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.info;
              return (
                <div
                  key={alert.id}
                  className={clsx(
                    "bg-white rounded-xl border p-5 transition-all",
                    alert.is_resolved ? "border-gray-100 opacity-70" : "border-gray-200"
                  )}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <div className={clsx("p-2 rounded-lg shrink-0 mt-0.5", sev.bg)}>
                        <AlertTriangle size={14} className={sev.color} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={clsx("text-xs font-semibold px-2 py-0.5 rounded-full", sev.bg, sev.color)}>
                            {sev.label}
                          </span>
                          <span className="text-xs text-gray-500 font-medium">{alert.institution_name}</span>
                          {alert.is_resolved && (
                            <span className="text-xs text-green-600 font-medium flex items-center gap-1">
                              <CheckCircle2 size={10} /> Résolue
                            </span>
                          )}
                        </div>
                        <p className="text-sm font-semibold text-gray-800 mt-1">
                          {INDICATOR_LABELS[alert.indicator_key] || alert.indicator_key} : {alert.value_at_trigger}
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5">{alert.rule_name} · Période : {alert.period_label}</p>
                        {alert.explanation && (
                          <p className="text-xs text-gray-500 mt-2 leading-relaxed">{alert.explanation}</p>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col items-end gap-2 shrink-0">
                      <span className="flex items-center gap-1 text-xs text-gray-400">
                        <Clock size={10} />
                        {format(new Date(alert.triggered_at), "dd/MM/yyyy HH:mm", { locale: fr })}
                      </span>
                      {!alert.is_resolved && (
                        <button
                          onClick={() => acknowledge(alert.id)}
                          disabled={ackLoading === alert.id}
                          className="text-xs px-3 py-1.5 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors disabled:opacity-50"
                        >
                          {ackLoading === alert.id ? "..." : "Acquitter"}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
