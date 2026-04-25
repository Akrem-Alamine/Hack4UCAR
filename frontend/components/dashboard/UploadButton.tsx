"use client";
import { useRef, useState } from "react";
import { Upload, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";

interface Props {
  institutionId: number | null;
  onSuccess: () => void;
}

type Status = "idle" | "uploading" | "success" | "error";

export default function UploadButton({ institutionId, onSuccess }: Props) {
  const { user } = useAuthStore();
  const inputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [result, setResult] = useState<{ imported: number; errors: number; message: string } | null>(null);
  const [showResult, setShowResult] = useState(false);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const targetId = institutionId ?? user?.institution_id;
    if (!targetId) {
      alert("Sélectionnez d'abord un établissement.");
      return;
    }

    setStatus("uploading");
    setShowResult(false);

    const form = new FormData();
    form.append("file", file);
    form.append("institution_id", String(targetId));

    try {
      const res = await api.post("/ingestion/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
      setStatus("success");
      setShowResult(true);
      onSuccess();
      setTimeout(() => { setStatus("idle"); setShowResult(false); }, 5000);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || "Erreur lors de l'import.";
      setResult({ imported: 0, errors: 1, message: detail });
      setStatus("error");
      setShowResult(true);
      setTimeout(() => { setStatus("idle"); setShowResult(false); }, 6000);
    } finally {
      // Reset file input so same file can be re-uploaded
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  const icons: Record<Status, React.ReactNode> = {
    idle: <Upload size={14} />,
    uploading: <Loader2 size={14} className="animate-spin" />,
    success: <CheckCircle2 size={14} />,
    error: <XCircle size={14} />,
  };

  const colors: Record<Status, string> = {
    idle: "text-gray-600 border-gray-200 hover:bg-gray-50",
    uploading: "text-blue-600 border-blue-200 bg-blue-50 cursor-not-allowed",
    success: "text-green-600 border-green-200 bg-green-50",
    error: "text-red-600 border-red-200 bg-red-50",
  };

  const labels: Record<Status, string> = {
    idle: "Importer",
    uploading: "Importation...",
    success: "Importé",
    error: "Échec",
  };

  return (
    <div className="relative">
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx,.xls,.csv"
        className="hidden"
        onChange={handleFile}
      />
      <button
        onClick={() => status === "idle" && inputRef.current?.click()}
        disabled={status === "uploading"}
        className={`flex items-center gap-2 px-3 py-2 text-sm border rounded-lg transition-colors ${colors[status]}`}
      >
        {icons[status]}
        {labels[status]}
      </button>

      {showResult && result && (
        <div
          className={`absolute top-full right-0 mt-2 w-72 rounded-xl border p-4 shadow-lg z-50 text-sm ${
            status === "success"
              ? "bg-green-50 border-green-200"
              : "bg-red-50 border-red-200"
          }`}
        >
          <p className="font-medium mb-1">
            {status === "success" ? "✅ Import réussi" : "❌ Erreur d'import"}
          </p>
          <p className="text-xs text-gray-600">{result.message}</p>
          {result.imported > 0 && (
            <p className="text-xs text-gray-500 mt-1">
              {result.imported} indicateur{result.imported > 1 ? "s" : ""} ajouté{result.imported > 1 ? "s" : ""} — tableau de bord actualisé.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
