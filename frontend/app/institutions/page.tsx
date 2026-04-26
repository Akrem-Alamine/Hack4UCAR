"use client";
import { useState, useEffect, useCallback } from "react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { Building2, Plus, MapPin, Tag, Copy, Check, X, RefreshCw, Users } from "lucide-react";
import clsx from "clsx";

interface Institution {
  id: number;
  name: string;
  acronym: string;
  type: string;
  city: string;
  is_active: boolean;
  created_at: string;
}

interface CreatedAccount {
  email: string;
  role: string;
  domain: string | null;
}

interface CreationResult {
  institution: Institution;
  password: string;
  accounts: CreatedAccount[];
}

const DOMAIN_LABELS: Record<string, string> = {
  academic: "Académique",
  finance: "Finance",
  hr: "Ressources Humaines",
  insertion: "Insertion Professionnelle",
  esg: "ESG / RSE",
  research: "Recherche",
};

const INST_TYPE_OPTIONS = [
  "École Nationale",
  "École Supérieure",
  "Institut National",
  "Institut Supérieur",
  "Faculté",
  "Centre de Recherche",
  "Autre",
];

export default function InstitutionsPage() {
  const { user } = useAuthStore();
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [result, setResult] = useState<CreationResult | null>(null);
  const [copied, setCopied] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({ name: "", acronym: "", type: INST_TYPE_OPTIONS[0], city: "" });

  const fetchInstitutions = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get<Institution[]>("/institutions/");
      setInstitutions(res.data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchInstitutions(); }, [fetchInstitutions]);

  const openModal = () => {
    setForm({ name: "", acronym: "", type: INST_TYPE_OPTIONS[0], city: "" });
    setError(null);
    setResult(null);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.acronym.trim() || !form.city.trim()) {
      setError("Tous les champs sont obligatoires.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.post<CreationResult>("/institutions/", {
        name: form.name.trim(),
        acronym: form.acronym.trim().toUpperCase(),
        type: form.type,
        city: form.city.trim(),
      });
      setResult(res.data);
      fetchInstitutions();
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Une erreur est survenue.");
    } finally {
      setSubmitting(false);
    }
  };

  const copyPassword = () => {
    if (!result) return;
    navigator.clipboard.writeText(result.password);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (user?.role !== "super_admin") {
    return (
      <DashboardLayout selectedInstitution={null} onSelectInstitution={() => {}}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Building2 size={40} className="text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">Accès réservé au super administrateur</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout selectedInstitution={null} onSelectInstitution={() => {}}>
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold text-gray-800">Établissements</h1>
            <p className="text-sm text-gray-400 mt-0.5">{institutions.length} établissement(s) actif(s)</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={fetchInstitutions} className="p-2 text-gray-400 hover:text-ucar-blue border border-gray-200 rounded-lg bg-white">
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            </button>
            <button
              onClick={openModal}
              className="flex items-center gap-2 px-4 py-2 bg-ucar-blue text-white text-sm font-medium rounded-lg hover:bg-ucar-blue/90 transition-colors"
            >
              <Plus size={15} />
              Nouvel établissement
            </button>
          </div>
        </div>

        {/* Institution grid */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-36 bg-white rounded-xl border border-gray-100 animate-pulse" />
            ))}
          </div>
        ) : institutions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 bg-white rounded-xl border border-gray-100">
            <Building2 size={40} className="text-gray-200 mb-3" />
            <p className="text-gray-400 text-sm">Aucun établissement. Créez-en un.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {institutions.map((inst) => (
              <div key={inst.id} className="bg-white rounded-xl border border-gray-100 p-4 hover:shadow-sm transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-lg bg-ucar-blue/10 flex items-center justify-center shrink-0">
                    <Building2 size={18} className="text-ucar-blue" />
                  </div>
                  <span className="text-xs font-bold text-ucar-blue bg-ucar-blue/10 px-2 py-0.5 rounded-full">
                    {inst.acronym}
                  </span>
                </div>
                <p className="text-sm font-semibold text-gray-800 leading-snug mb-2">{inst.name}</p>
                <div className="space-y-1">
                  <div className="flex items-center gap-1.5 text-xs text-gray-400">
                    <Tag size={10} />
                    <span>{inst.type}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-gray-400">
                    <MapPin size={10} />
                    <span>{inst.city}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-gray-400">
                    <Users size={10} />
                    <span>7 comptes créés (président + 6 départements)</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 overflow-hidden">

            {result ? (
              /* Success view */
              <>
                <div className="bg-green-50 border-b border-green-100 px-6 py-4 flex items-center justify-between">
                  <div>
                    <p className="font-bold text-green-800">Établissement créé !</p>
                    <p className="text-xs text-green-600 mt-0.5">{result.institution.name} · {result.institution.acronym}</p>
                  </div>
                  <button onClick={closeModal} className="text-green-500 hover:text-green-700">
                    <X size={16} />
                  </button>
                </div>

                <div className="px-6 py-4 space-y-4 max-h-[70vh] overflow-y-auto">
                  {/* Password */}
                  <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                    <p className="text-xs font-semibold text-amber-700 mb-2">Mot de passe temporaire (affiché une seule fois)</p>
                    <div className="flex items-center gap-2">
                      <code className="flex-1 text-sm font-mono font-bold text-amber-900 bg-white border border-amber-200 rounded-lg px-3 py-2">
                        {result.password}
                      </code>
                      <button
                        onClick={copyPassword}
                        className={clsx(
                          "p-2 rounded-lg border text-sm transition-colors",
                          copied
                            ? "bg-green-50 border-green-200 text-green-600"
                            : "bg-white border-amber-200 text-amber-600 hover:bg-amber-50"
                        )}
                      >
                        {copied ? <Check size={15} /> : <Copy size={15} />}
                      </button>
                    </div>
                  </div>

                  {/* Accounts */}
                  <div>
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Comptes créés ({result.accounts.length})</p>
                    <div className="space-y-1">
                      {result.accounts.map((acc) => (
                        <div key={acc.email} className="flex items-center justify-between py-1.5 px-3 rounded-lg bg-gray-50">
                          <span className="text-xs font-mono text-gray-700">{acc.email}</span>
                          <span className={clsx(
                            "text-[10px] font-semibold px-2 py-0.5 rounded-full",
                            acc.role === "president"
                              ? "bg-ucar-blue/10 text-ucar-blue"
                              : "bg-gray-200 text-gray-600"
                          )}>
                            {acc.role === "president" ? "Président" : DOMAIN_LABELS[acc.domain ?? ""] ?? acc.domain}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="px-6 py-4 border-t border-gray-100">
                  <button
                    onClick={closeModal}
                    className="w-full py-2 text-sm font-medium bg-ucar-blue text-white rounded-xl hover:bg-ucar-blue/90 transition-colors"
                  >
                    Fermer
                  </button>
                </div>
              </>
            ) : (
              /* Form view */
              <form onSubmit={handleSubmit}>
                <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                  <p className="font-bold text-gray-800">Nouvel établissement</p>
                  <button type="button" onClick={closeModal} className="text-gray-400 hover:text-gray-600">
                    <X size={16} />
                  </button>
                </div>

                <div className="px-6 py-5 space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-600 mb-1">Nom complet *</label>
                    <input
                      value={form.name}
                      onChange={(e) => setForm({ ...form, name: e.target.value })}
                      placeholder="ex: École Nationale des Sciences de Tunis"
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ucar-blue/20"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-gray-600 mb-1">Sigle (acronyme) *</label>
                      <input
                        value={form.acronym}
                        onChange={(e) => setForm({ ...form, acronym: e.target.value.toUpperCase() })}
                        placeholder="ex: ENST"
                        maxLength={20}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm font-mono uppercase focus:outline-none focus:ring-2 focus:ring-ucar-blue/20"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-gray-600 mb-1">Ville *</label>
                      <input
                        value={form.city}
                        onChange={(e) => setForm({ ...form, city: e.target.value })}
                        placeholder="ex: Tunis"
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ucar-blue/20"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-gray-600 mb-1">Type d'établissement</label>
                    <select
                      value={form.type}
                      onChange={(e) => setForm({ ...form, type: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ucar-blue/20"
                    >
                      {INST_TYPE_OPTIONS.map((t) => <option key={t}>{t}</option>)}
                    </select>
                  </div>

                  {/* Preview of what will be created */}
                  <div className="bg-blue-50 border border-blue-100 rounded-xl p-3 text-xs text-blue-700 space-y-1">
                    <p className="font-semibold mb-1">Ce qui sera créé automatiquement :</p>
                    <p>· 6 départements (Académique, Finance, RH, Insertion, ESG, Recherche)</p>
                    <p>· 1 compte Président <span className="font-mono">president@{form.acronym ? form.acronym.toLowerCase().replace(/'/g, "") : "sigle"}.tn</span></p>
                    <p>· 6 comptes département (academique, finance, rh, insertion, esg, recherche)</p>
                    <p>· Un mot de passe temporaire commun affiché une seule fois</p>
                  </div>

                  {error && (
                    <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</p>
                  )}
                </div>

                <div className="px-6 py-4 border-t border-gray-100 flex gap-3">
                  <button
                    type="button"
                    onClick={closeModal}
                    className="flex-1 py-2 text-sm font-medium border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50 transition-colors"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="flex-1 py-2 text-sm font-medium bg-ucar-blue text-white rounded-xl hover:bg-ucar-blue/90 disabled:opacity-60 transition-colors flex items-center justify-center gap-2"
                  >
                    {submitting ? <><RefreshCw size={13} className="animate-spin" /> Création…</> : "Créer l'établissement"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
