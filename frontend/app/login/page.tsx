"use client";
import { useState, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { Building2, Lock, Mail, Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const { login, isLoading, hydrate } = useAuthStore();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    hydrate();
    const token = localStorage.getItem("access_token");
    if (token) router.replace("/dashboard");
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Identifiants incorrects. Veuillez réessayer.");
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left — branding */}
      <div className="hidden lg:flex w-1/2 bg-ucar-sidebar flex-col justify-center items-center p-12">
        <div className="max-w-sm text-center">
          <div className="w-16 h-16 bg-ucar-gold/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Building2 className="text-ucar-gold" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-white mb-3">UCAR</h1>
          <p className="text-white/60 text-base leading-relaxed">
            Plateforme Intelligente de Gestion des Établissements Universitaires
          </p>
          <div className="mt-10 grid grid-cols-2 gap-4 text-left">
            {[
              ["30+", "Établissements"],
              ["14", "Domaines KPI"],
              ["IA", "Au cœur du système"],
              ["100%", "Décisions basées sur les données"],
            ].map(([val, desc]) => (
              <div key={val} className="bg-white/5 rounded-xl p-4">
                <p className="text-ucar-gold text-xl font-bold">{val}</p>
                <p className="text-white/50 text-xs mt-1">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right — form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-ucar-bg">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <Building2 className="text-ucar-blue" size={24} />
            <span className="font-bold text-ucar-blue text-xl">UCAR</span>
          </div>

          <h2 className="text-2xl font-bold text-ucar-blue mb-1">Connexion</h2>
          <p className="text-gray-500 text-sm mb-8">Accédez à votre espace de gestion institutionnelle</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Adresse email</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="vous@etablissement.tn"
                  required
                  className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ucar-blue/20 focus:border-ucar-blue transition-colors bg-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Mot de passe</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type={showPass ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full pl-9 pr-10 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ucar-blue/20 focus:border-ucar-blue transition-colors bg-white"
                />
                <button
                  type="button"
                  onClick={() => setShowPass((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-ucar-blue text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-ucar-blue-light transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isLoading ? "Connexion en cours..." : "Se connecter"}
            </button>
          </form>

          <div className="mt-8 p-4 bg-white rounded-lg border border-gray-100">
            <p className="text-xs font-medium text-gray-500 mb-2">Comptes de démonstration :</p>
            <div className="space-y-1">
              <p className="text-xs text-gray-600"><span className="font-mono bg-gray-100 px-1 rounded">super@ucar.tn</span> — Super Admin UCAR</p>
              <p className="text-xs text-gray-600"><span className="font-mono bg-gray-100 px-1 rounded">president@enstab.tn</span> — Président ENSTAB (toutes données)</p>
              <p className="text-xs text-gray-600"><span className="font-mono bg-gray-100 px-1 rounded">academique@enstab.tn</span> — Département Académique</p>
              <p className="text-xs text-gray-600"><span className="font-mono bg-gray-100 px-1 rounded">finance@enstab.tn</span> — Département Finance</p>
              <p className="text-xs text-gray-600"><span className="font-mono bg-gray-100 px-1 rounded">rh@enstab.tn</span> — Département RH</p>
              <p className="text-xs text-gray-400 mt-1">Mot de passe : <span className="font-mono">demo1234</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
