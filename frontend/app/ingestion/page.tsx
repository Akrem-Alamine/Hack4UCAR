"use client";
import { useState, useEffect, useRef } from "react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { IngestionJob, DOMAIN_LABELS, INDICATOR_LABELS } from "@/lib/types";
import { Upload, FileText, Image, FileSpreadsheet, CheckCircle, XCircle, Loader2, Eye, RefreshCw, AlertTriangle } from "lucide-react";
import clsx from "clsx";

interface DryRunResult {
  imported: number;
  errors: number;
  warnings: string[];
  ai_normalized: boolean;
  rows: { row: number; domain: string; indicator_key: string; value: number; unit: string }[];
  error_details: { row: number; error: string }[];
  message: string;
}

const STATUS_CONFIG = {
  pending:    { label: "En attente",    color: "text-gray-500",  bg: "bg-gray-100",  icon: Loader2 },
  processing: { label: "Traitement IA", color: "text-blue-600",  bg: "bg-blue-50",   icon: Loader2 },
  completed:  { label: "Terminé",       color: "text-green-600", bg: "bg-green-50",  icon: CheckCircle },
  failed:     { label: "Échec",         color: "text-red-600",   bg: "bg-red-50",    icon: XCircle },
};

const SOURCE_ICON = {
  pdf:   FileText,
  image: Image,
  excel: FileSpreadsheet,
  csv:   FileSpreadsheet,
};

const CONFIDENCE_COLOR = (c: number) =>
  c >= 0.8 ? "text-green-600" : c >= 0.6 ? "text-yellow-600" : "text-red-500";

export default function IngestionPage() {
  const { user } = useAuthStore();
  const [selectedInstitution, setSelectedInstitution] = useState<number | null>(
    user?.institution_id || null
  );
  const [jobs, setJobs] = useState<IngestionJob[]>([]);
  const [selectedJob, setSelectedJob] = useState<IngestionJob | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [uploadResult, setUploadResult] = useState<{ success: boolean; message: string } | null>(null);
  const [pendingUpload, setPendingUpload] = useState<{ file: File; dryRun: DryRunResult } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  const fetchJobs = async () => {
    setLoadingJobs(true);
    try {
      const params: Record<string, any> = {};
      if (selectedInstitution) params.institution_id = selectedInstitution;
      const res = await api.get<IngestionJob[]>("/ingestion/jobs", { params });
      setJobs(res.data);
    } catch {
      // silent
    } finally {
      setLoadingJobs(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [selectedInstitution]);

  // Poll every 3s while a job is processing/pending
  useEffect(() => {
    const hasPending = jobs.some((j) => j.status === "pending" || j.status === "processing");
    if (hasPending) {
      pollRef.current = setTimeout(fetchJobs, 3000);
    }
    return () => { if (pollRef.current) clearTimeout(pollRef.current); };
  }, [jobs]);

  const commitUpload = async (file: File) => {
    const ext = file.name.split(".").pop()?.toLowerCase() || "";
    const isDocument = ["pdf", "png", "jpg", "jpeg", "tiff", "bmp"].includes(ext);
    const endpoint = isDocument ? "/ingestion/upload-document" : "/ingestion/upload";

    const formData = new FormData();
    formData.append("file", file);
    formData.append("institution_id", String(selectedInstitution!));
    if (!isDocument) formData.append("dry_run", "false");

    setUploading(true);
    try {
      const res = await api.post(endpoint, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadResult({
        success: true,
        message: isDocument
          ? `${file.name} — Extraction IA démarrée (job #${res.data.job_id})`
          : `✓ ${file.name} — ${res.data.message}`,
      });
    } catch (err: any) {
      setUploadResult({
        success: false,
        message: `Erreur : ${err.response?.data?.detail || err.message}`,
      });
    } finally {
      setUploading(false);
      setPendingUpload(null);
      fetchJobs();
    }
  };

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    if (!selectedInstitution) {
      setUploadResult({ success: false, message: "Veuillez sélectionner un établissement." });
      return;
    }

    setUploadResult(null);

    for (const file of Array.from(files)) {
      const ext = file.name.split(".").pop()?.toLowerCase() || "";
      const isDocument = ["pdf", "png", "jpg", "jpeg", "tiff", "bmp"].includes(ext);

      if (isDocument) {
        await commitUpload(file);
        continue;
      }

      // Dry-run first for structured files
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);
      formData.append("institution_id", String(selectedInstitution));
      formData.append("dry_run", "true");

      try {
        const res = await api.post<DryRunResult>("/ingestion/upload", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        const dryResult = res.data;

        const hasWarnings = dryResult.warnings.length > 0 || dryResult.errors > 0;
        if (hasWarnings) {
          setUploading(false);
          setPendingUpload({ file, dryRun: dryResult });
        } else {
          setUploading(false);
          await commitUpload(file);
        }
      } catch (err: any) {
        setUploading(false);
        setUploadResult({
          success: false,
          message: `Erreur : ${err.response?.data?.detail || err.message}`,
        });
      }
    }
  };

  const openJob = async (job: IngestionJob) => {
    try {
      const res = await api.get<IngestionJob>(`/ingestion/jobs/${job.id}`);
      setSelectedJob(res.data);
    } catch {
      setSelectedJob(job);
    }
  };

  return (
    <DashboardLayout selectedInstitution={selectedInstitution} onSelectInstitution={setSelectedInstitution}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-ucar-blue">Ingestion de données</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Track 1 — Import Excel, CSV, PDF et images avec extraction IA
            </p>
          </div>
          <button
            onClick={fetchJobs}
            disabled={loadingJobs}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <RefreshCw size={14} className={loadingJobs ? "animate-spin" : ""} />
            Actualiser
          </button>
        </div>

        {/* Upload zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files); }}
          onClick={() => fileInputRef.current?.click()}
          className={clsx(
            "border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors",
            dragOver ? "border-ucar-blue bg-ucar-blue/5" : "border-gray-300 hover:border-ucar-blue/50 hover:bg-gray-50"
          )}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".xlsx,.xls,.csv,.pdf,.png,.jpg,.jpeg,.tiff"
            className="hidden"
            onChange={(e) => handleFiles(e.target.files)}
          />
          {uploading ? (
            <div className="flex flex-col items-center gap-2">
              <Loader2 className="text-ucar-blue animate-spin" size={32} />
              <p className="text-sm text-ucar-blue font-medium">Envoi en cours...</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <Upload className="text-gray-400" size={32} />
              <div>
                <p className="text-sm font-semibold text-gray-700">
                  Glissez vos fichiers ici ou cliquez pour parcourir
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  Excel / CSV → import direct &nbsp;|&nbsp; PDF / Image → OCR + extraction IA
                </p>
              </div>
              <div className="flex gap-2 mt-1">
                {["XLSX", "CSV", "PDF", "PNG", "JPG"].map((f) => (
                  <span key={f} className="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs rounded">
                    {f}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Upload result */}
        {uploadResult && (
          <div className={clsx(
            "px-4 py-3 rounded-lg text-sm",
            uploadResult.success ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"
          )}>
            {uploadResult.message}
          </div>
        )}

        {/* Format guide */}
        <div className="bg-ucar-blue/5 border border-ucar-blue/10 rounded-xl p-4">
          <p className="text-xs font-semibold text-ucar-blue mb-2">Format Excel/CSV requis :</p>
          <p className="text-xs text-gray-600 font-mono">
            domain | indicator_key | value | unit | period_label | period_start | period_end | department_code (opt) | notes (opt)
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Exemples de domaines : <span className="font-mono">academic, finance, hr, esg, insertion, research</span>
          </p>
        </div>

        {/* Jobs list */}
        <div>
          <h2 className="text-sm font-semibold text-gray-700 mb-3">
            Historique des imports ({jobs.length})
          </h2>

          {jobs.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-100 p-12 text-center">
              <p className="text-gray-400 text-sm">Aucun import pour le moment.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {jobs.map((job) => {
                const status = STATUS_CONFIG[job.status];
                const StatusIcon = status.icon;
                const FileIcon = SOURCE_ICON[job.source_type] || FileText;
                const isPendingOrProcessing = job.status === "pending" || job.status === "processing";

                return (
                  <div
                    key={job.id}
                    className="bg-white rounded-xl border border-gray-100 p-4 flex items-center gap-4"
                  >
                    <div className="w-9 h-9 rounded-lg bg-gray-100 flex items-center justify-center shrink-0">
                      <FileIcon size={16} className="text-gray-500" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">
                        {job.original_filename}
                      </p>
                      <div className="flex items-center gap-3 mt-0.5">
                        <span className="text-xs text-gray-400">
                          {new Date(job.created_at).toLocaleString("fr-FR")}
                        </span>
                        {job.status === "completed" && (
                          <>
                            <span className="text-xs text-gray-400">
                              {job.kpi_count} KPIs extraits
                            </span>
                            <span className="text-xs text-gray-400">
                              Qualité : {job.quality_score}%
                            </span>
                            <span className="text-xs text-green-600 font-medium">
                              {job.imported_count} importés
                            </span>
                          </>
                        )}
                        {job.error_message && (
                          <span className="text-xs text-red-500 truncate max-w-xs">
                            {job.error_message}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className={clsx("flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium shrink-0", status.bg, status.color)}>
                      <StatusIcon size={11} className={isPendingOrProcessing ? "animate-spin" : ""} />
                      {status.label}
                    </div>

                    {(job.status === "completed" || job.status === "failed") && (
                      <button
                        onClick={() => openJob(job)}
                        className="p-2 text-gray-400 hover:text-ucar-blue hover:bg-gray-50 rounded-lg transition-colors"
                        title="Voir les détails"
                      >
                        <Eye size={15} />
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Dry-run warning modal */}
      {pendingUpload && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg shadow-xl" onClick={(e) => e.stopPropagation()}>
            <div className="p-6 border-b border-gray-100 flex items-start gap-3">
              <div className="w-9 h-9 rounded-full bg-amber-100 flex items-center justify-center shrink-0">
                <AlertTriangle size={18} className="text-amber-600" />
              </div>
              <div>
                <h3 className="font-bold text-gray-800">Avertissement avant import</h3>
                <p className="text-xs text-gray-500 mt-0.5">{pendingUpload.file.name}</p>
              </div>
            </div>

            <div className="p-6 space-y-4">
              {/* Warnings */}
              {pendingUpload.dryRun.warnings.length > 0 && (
                <div className="space-y-2">
                  {pendingUpload.dryRun.warnings.map((w, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm text-amber-700 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2">
                      <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                      {w}
                    </div>
                  ))}
                </div>
              )}

              {/* Row errors preview */}
              {pendingUpload.dryRun.error_details.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 mb-1.5">
                    Lignes avec erreurs ({pendingUpload.dryRun.error_details.length}) :
                  </p>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {pendingUpload.dryRun.error_details.map((e, i) => (
                      <div key={i} className="text-xs text-red-600 bg-red-50 rounded px-2 py-1">
                        Ligne {e.row} — {e.error}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Summary */}
              <p className="text-sm text-gray-600">
                <span className="font-semibold text-gray-800">{pendingUpload.dryRun.imported}</span> indicateur(s) seraient importé(s),{" "}
                <span className="font-semibold text-red-600">{pendingUpload.dryRun.errors}</span> ligne(s) ignorée(s).
              </p>
              <p className="text-sm text-gray-500">Voulez-vous continuer l'import ?</p>
            </div>

            <div className="px-6 pb-6 flex gap-3 justify-end">
              <button
                onClick={() => { setPendingUpload(null); setUploadResult(null); }}
                className="px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                Annuler
              </button>
              <button
                onClick={() => commitUpload(pendingUpload.file)}
                className="px-4 py-2 text-sm font-medium text-white bg-ucar-blue rounded-lg hover:bg-ucar-blue/90"
              >
                Continuer quand même
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Job detail modal */}
      {selectedJob && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setSelectedJob(null)}>
          <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="p-6 border-b border-gray-100 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-gray-800">{selectedJob.original_filename}</h3>
                <p className="text-xs text-gray-400 mt-0.5">
                  {selectedJob.kpi_count} KPIs extraits · Qualité : {selectedJob.quality_score}% · {selectedJob.imported_count} importés
                </p>
              </div>
              <button onClick={() => setSelectedJob(null)} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
            </div>

            <div className="p-6 space-y-5">
              {selectedJob.extracted_kpis?.length > 0 ? (
                <>
                  <p className="text-sm font-semibold text-gray-700">KPIs extraits par l'IA :</p>
                  <div className="space-y-2">
                    {selectedJob.extracted_kpis.map((kpi, i) => (
                      <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-medium text-gray-800">
                              {INDICATOR_LABELS[kpi.indicator_key] || kpi.indicator_key}
                            </span>
                            <span className="text-xs px-1.5 py-0.5 bg-ucar-blue/10 text-ucar-blue rounded">
                              {DOMAIN_LABELS[kpi.domain] || kpi.domain}
                            </span>
                          </div>
                          <p className="text-sm font-bold text-gray-700 mt-0.5">
                            {kpi.value} {kpi.unit}
                            <span className="text-xs text-gray-400 font-normal ml-2">({kpi.period_label})</span>
                          </p>
                        </div>
                        <div className={clsx("text-xs font-medium", CONFIDENCE_COLOR(kpi.confidence))}>
                          {Math.round(kpi.confidence * 100)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="bg-amber-50 border border-amber-100 rounded-lg p-4">
                  <p className="text-sm font-semibold text-amber-700 mb-1">Aucun KPI extrait</p>
                  <p className="text-xs text-amber-600">
                    Le document ne contient pas de données chiffrées reconnues comme indicateurs de performance.
                    Vérifiez le texte extrait ci-dessous pour comprendre ce qui a été lu.
                  </p>
                </div>
              )}

              {/* Raw extracted text */}
              {selectedJob.extracted_text && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 mb-2">Texte extrait par OCR / lecture PDF :</p>
                  <pre className="text-xs text-gray-500 bg-gray-50 rounded-lg p-3 max-h-48 overflow-y-auto whitespace-pre-wrap font-mono border border-gray-100">
                    {selectedJob.extracted_text}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
