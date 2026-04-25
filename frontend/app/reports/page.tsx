"use client";
import { useState, useEffect } from "react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { api } from "@/lib/api";
import { Report, ReportFormat, ReportStatus } from "@/lib/types";
import { FileText, Download, RefreshCw, Plus, CheckCircle2, Clock, XCircle, Loader2 } from "lucide-react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import clsx from "clsx";
import { useAuthStore } from "@/store/auth";

const STATUS_CONFIG: Record<ReportStatus, { label: string; icon: React.ReactNode; color: string }> = {
  pending: { label: "En attente", icon: <Clock size={12} />, color: "text-gray-500" },
  generating: { label: "Génération...", icon: <Loader2 size={12} className="animate-spin" />, color: "text-blue-500" },
  ready: { label: "Prêt", icon: <CheckCircle2 size={12} />, color: "text-green-600" },
  failed: { label: "Échec", icon: <XCircle size={12} />, color: "text-red-500" },
};

const REPORT_TYPES = [
  { value: "global", label: "Rapport Global" },
  { value: "academic", label: "Académique" },
  { value: "finance", label: "Finance" },
  { value: "hr", label: "Ressources Humaines" },
  { value: "research", label: "Recherche" },
];

export default function ReportsPage() {
  const { user } = useAuthStore();
  const [selectedInstitution, setSelectedInstitution] = useState<number | null>(user?.institution_id || null);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ type: "global", period_label: "2024-2025 S1", format: "pdf" as ReportFormat });
  const [generating, setGenerating] = useState(false);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (selectedInstitution) params.institution_id = selectedInstitution;
      const res = await api.get<Report[]>("/reports/", { params });
      setReports(res.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchReports(); }, [selectedInstitution]);

  const requestReport = async () => {
    if (!selectedInstitution) return;
    setGenerating(true);
    try {
      await api.post("/reports/", { ...form, institution_id: selectedInstitution });
      setShowForm(false);
      setTimeout(fetchReports, 1500);
    } finally {
      setGenerating(false);
    }
  };

  const download = (reportId: number) => {
    const token = localStorage.getItem("access_token");
    const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/reports/${reportId}/download`;
    const a = document.createElement("a");
    a.href = url;
    a.click();
  };

  return (
    <DashboardLayout selectedInstitution={selectedInstitution} onSelectInstitution={setSelectedInstitution}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-ucar-blue">Rapports</h1>
            <p className="text-sm text-gray-500 mt-0.5">Génération et export des rapports institutionnels (PDF / Excel)</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={fetchReports} className="p-2 text-gray-500 border border-gray-200 rounded-lg hover:bg-gray-50">
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            </button>
            <button
              onClick={() => setShowForm((v) => !v)}
              disabled={!selectedInstitution}
              className="flex items-center gap-2 px-3 py-2 text-xs font-medium bg-ucar-blue text-white rounded-lg hover:bg-ucar-blue-light transition-colors disabled:opacity-50"
            >
              <Plus size={14} />
              Nouveau rapport
            </button>
          </div>
        </div>

        {!selectedInstitution && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-700">
            Sélectionnez un établissement pour générer un rapport.
          </div>
        )}

        {/* Report form */}
        {showForm && selectedInstitution && (
          <div className="bg-white rounded-xl border border-gray-100 p-6">
            <h3 className="text-sm font-semibold text-gray-800 mb-4">Paramètres du rapport</h3>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1.5">Type</label>
                <select
                  value={form.type}
                  onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ucar-blue/20"
                >
                  {REPORT_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1.5">Période</label>
                <select
                  value={form.period_label}
                  onChange={(e) => setForm((f) => ({ ...f, period_label: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ucar-blue/20"
                >
                  {["2023-2024 S1", "2023-2024 S2", "2024-2025 S1"].map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1.5">Format</label>
                <select
                  value={form.format}
                  onChange={(e) => setForm((f) => ({ ...f, format: e.target.value as ReportFormat }))}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ucar-blue/20"
                >
                  <option value="pdf">PDF</option>
                  <option value="excel">Excel</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-4">
              <button onClick={() => setShowForm(false)} className="px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50">
                Annuler
              </button>
              <button onClick={requestReport} disabled={generating} className="px-4 py-2 text-sm font-medium bg-ucar-blue text-white rounded-lg hover:bg-ucar-blue-light disabled:opacity-60">
                {generating ? "Génération..." : "Générer"}
              </button>
            </div>
          </div>
        )}

        {/* Reports list */}
        {loading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl border border-gray-100 h-20 animate-pulse" />
            ))}
          </div>
        ) : reports.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-100 p-12 text-center">
            <FileText className="mx-auto text-gray-300 mb-3" size={40} />
            <p className="text-gray-500 font-medium">Aucun rapport généré</p>
            <p className="text-gray-400 text-sm mt-1">Sélectionnez un établissement et créez votre premier rapport.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {reports.map((report) => {
              const s = STATUS_CONFIG[report.status];
              return (
                <div key={report.id} className="bg-white rounded-xl border border-gray-100 p-5 flex items-center gap-4">
                  <div className="p-2.5 bg-ucar-blue/5 rounded-lg">
                    <FileText size={20} className="text-ucar-blue" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-800">
                      Rapport {report.type} — {report.period_label}
                    </p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      Format : {report.format.toUpperCase()} · Demandé le{" "}
                      {format(new Date(report.created_at), "dd/MM/yyyy HH:mm", { locale: fr })}
                    </p>
                  </div>
                  <div className={clsx("flex items-center gap-1 text-xs font-medium", s.color)}>
                    {s.icon} {s.label}
                  </div>
                  {report.status === "ready" && (
                    <button
                      onClick={() => download(report.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-ucar-blue border border-ucar-blue/20 rounded-lg hover:bg-ucar-blue/5 transition-colors"
                    >
                      <Download size={12} />
                      Télécharger
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
