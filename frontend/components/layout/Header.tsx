"use client";
import { useState, useEffect } from "react";
import { useAuthStore } from "@/store/auth";
import { api } from "@/lib/api";
import { Institution } from "@/lib/types";
import { ChevronDown, Building2 } from "lucide-react";

interface Props {
  selectedInstitution: number | null;
  onSelectInstitution: (id: number | null) => void;
}

export default function Header({ selectedInstitution, onSelectInstitution }: Props) {
  const { user } = useAuthStore();
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [open, setOpen] = useState(false);

  const isSuperAdmin = user?.role === "super_admin";

  useEffect(() => {
    if (!user) return;
    api.get<Institution[]>("/institutions/").then((r) => {
      setInstitutions(r.data);
      if (!isSuperAdmin && r.data.length === 1) {
        onSelectInstitution(r.data[0].id);
      }
    });
  }, [user]);

  const selected = institutions.find((i) => i.id === selectedInstitution);

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center px-6 gap-4">
      {isSuperAdmin && (
        <div className="relative">
          <button
            onClick={() => setOpen((v) => !v)}
            className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <Building2 size={16} className="text-ucar-blue" />
            {selected ? selected.acronym : "Tous les établissements"}
            <ChevronDown size={14} className="text-gray-400" />
          </button>

          {open && (
            <div className="absolute top-full left-0 mt-1 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
              <button
                onClick={() => { onSelectInstitution(null); setOpen(false); }}
                className="w-full px-4 py-3 text-left text-sm hover:bg-gray-50 border-b border-gray-100 font-medium text-ucar-blue"
              >
                Tous les établissements (vue consolidée)
              </button>
              {institutions.map((inst) => (
                <button
                  key={inst.id}
                  onClick={() => { onSelectInstitution(inst.id); setOpen(false); }}
                  className="w-full px-4 py-3 text-left text-sm hover:bg-gray-50 flex items-center gap-3"
                >
                  <span className="font-semibold text-ucar-blue w-24 shrink-0">{inst.acronym}</span>
                  <span className="text-gray-600 truncate">{inst.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="ml-auto flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-ucar-blue flex items-center justify-center">
          <span className="text-white text-xs font-bold">
            {user?.first_name?.[0]}{user?.last_name?.[0]}
          </span>
        </div>
      </div>
    </header>
  );
}
