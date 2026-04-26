"use client";
import { useState, useEffect, useCallback } from "react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { Database, Table, Search, ChevronLeft, ChevronRight, RefreshCw, X, Hash, AlignLeft } from "lucide-react";
import clsx from "clsx";

interface TableMeta {
  name: string;
  row_count: number;
  columns: { name: string; type: string }[];
}

interface TableData {
  table: string;
  columns: string[];
  rows: Record<string, unknown>[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

const TABLE_LABELS: Record<string, string> = {
  institutions: "Établissements",
  users: "Utilisateurs",
  kpi_records: "Indicateurs KPI",
  alert_rules: "Règles d'alerte",
  alerts: "Alertes déclenchées",
  reports: "Rapports",
  ingestion_jobs: "Jobs d'ingestion",
  departments: "Départements",
};

function formatValue(val: unknown): string {
  if (val === null || val === undefined) return "—";
  if (typeof val === "boolean") return val ? "Oui" : "Non";
  if (typeof val === "object") return JSON.stringify(val);
  const s = String(val);
  if (s.length > 80) return s.slice(0, 80) + "…";
  return s;
}

function isNumericType(type: string) {
  return /int|float|decimal|numeric|double|real/i.test(type);
}

export default function DatabasePage() {
  const { user } = useAuthStore();
  const [tables, setTables] = useState<TableMeta[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [data, setData] = useState<TableData | null>(null);
  const [loading, setLoading] = useState(false);
  const [tablesLoading, setTablesLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [page, setPage] = useState(1);
  const [sortCol, setSortCol] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [selectedRow, setSelectedRow] = useState<Record<string, unknown> | null>(null);

  const fetchTables = async () => {
    setTablesLoading(true);
    try {
      const res = await api.get<TableMeta[]>("/db-explorer/tables");
      setTables(res.data);
    } finally {
      setTablesLoading(false);
    }
  };

  const fetchRows = useCallback(async (table: string, p: number, q: string, col: string | null, dir: string) => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = { page: p, page_size: 50 };
      if (q) params.search = q;
      if (col) { params.sort_col = col; params.sort_dir = dir; }
      const res = await api.get<TableData>(`/db-explorer/tables/${table}/rows`, { params });
      setData(res.data);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTables(); }, []);

  useEffect(() => {
    if (!selectedTable) return;
    fetchRows(selectedTable, page, search, sortCol, sortDir);
  }, [selectedTable, page, search, sortCol, sortDir, fetchRows]);

  const selectTable = (name: string) => {
    setSelectedTable(name);
    setPage(1);
    setSearch("");
    setSearchInput("");
    setSortCol(null);
    setSortDir("desc");
    setData(null);
    setSelectedRow(null);
  };

  const handleSort = (col: string) => {
    if (sortCol === col) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortCol(col);
      setSortDir("desc");
    }
    setPage(1);
  };

  const handleSearch = () => {
    setSearch(searchInput);
    setPage(1);
  };

  const clearSearch = () => {
    setSearchInput("");
    setSearch("");
    setPage(1);
  };

  if (user?.role !== "super_admin") {
    return (
      <DashboardLayout selectedInstitution={null} onSelectInstitution={() => {}}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Database size={40} className="text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">Accès réservé au super administrateur</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout selectedInstitution={null} onSelectInstitution={() => {}}>
      <div className="flex gap-4 h-[calc(100vh-7rem)]">

        {/* Left panel — table list */}
        <div className="w-56 shrink-0 bg-white rounded-xl border border-gray-100 flex flex-col overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database size={14} className="text-ucar-blue" />
              <span className="text-xs font-bold text-gray-700">Tables</span>
            </div>
            <button onClick={fetchTables} className="p-1 text-gray-400 hover:text-ucar-blue">
              <RefreshCw size={12} className={tablesLoading ? "animate-spin" : ""} />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto py-1">
            {tablesLoading ? (
              [...Array(6)].map((_, i) => (
                <div key={i} className="mx-3 my-1 h-9 rounded-lg bg-gray-100 animate-pulse" />
              ))
            ) : (
              tables.map((t) => (
                <button
                  key={t.name}
                  onClick={() => selectTable(t.name)}
                  className={clsx(
                    "w-full text-left px-3 py-2 mx-0 flex items-center justify-between gap-2 transition-colors text-xs",
                    selectedTable === t.name
                      ? "bg-ucar-blue/10 text-ucar-blue font-semibold border-r-2 border-ucar-blue"
                      : "text-gray-600 hover:bg-gray-50"
                  )}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <Table size={11} className="shrink-0 opacity-60" />
                    <span className="truncate">{TABLE_LABELS[t.name] || t.name}</span>
                  </div>
                  <span className="text-gray-400 shrink-0 font-mono text-[10px]">
                    {t.row_count.toLocaleString()}
                  </span>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Main panel */}
        <div className="flex-1 flex flex-col min-w-0 gap-3">
          {!selectedTable ? (
            <div className="flex-1 bg-white rounded-xl border border-gray-100 flex items-center justify-center">
              <div className="text-center">
                <Database size={48} className="text-gray-200 mx-auto mb-4" />
                <p className="text-gray-400 text-sm font-medium">Sélectionnez une table</p>
                <p className="text-gray-300 text-xs mt-1">{tables.length} tables disponibles</p>
              </div>
            </div>
          ) : (
            <>
              {/* Toolbar */}
              <div className="bg-white rounded-xl border border-gray-100 px-4 py-3 flex items-center gap-3">
                <div className="flex items-center gap-2 flex-1">
                  <Table size={14} className="text-ucar-blue shrink-0" />
                  <span className="text-sm font-bold text-gray-800">
                    {TABLE_LABELS[selectedTable] || selectedTable}
                  </span>
                  <span className="text-xs text-gray-400 font-mono">({selectedTable})</span>
                  {data && (
                    <span className="text-xs text-gray-400">
                      — {data.total.toLocaleString()} enregistrements
                    </span>
                  )}
                </div>

                {/* Search */}
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      value={searchInput}
                      onChange={(e) => setSearchInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                      placeholder="Rechercher…"
                      className="pl-8 pr-7 py-1.5 text-xs border border-gray-200 rounded-lg w-48 focus:outline-none focus:ring-2 focus:ring-ucar-blue/20"
                    />
                    {searchInput && (
                      <button onClick={clearSearch} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                        <X size={11} />
                      </button>
                    )}
                  </div>
                  <button
                    onClick={handleSearch}
                    className="px-3 py-1.5 text-xs font-medium bg-ucar-blue text-white rounded-lg hover:bg-ucar-blue/90"
                  >
                    OK
                  </button>
                </div>

                <button
                  onClick={() => fetchRows(selectedTable, page, search, sortCol, sortDir)}
                  className="p-1.5 text-gray-400 hover:text-ucar-blue border border-gray-200 rounded-lg"
                >
                  <RefreshCw size={13} className={loading ? "animate-spin" : ""} />
                </button>
              </div>

              {/* Table */}
              <div className="flex-1 bg-white rounded-xl border border-gray-100 overflow-hidden flex flex-col">
                {loading && !data ? (
                  <div className="flex-1 flex items-center justify-center">
                    <RefreshCw size={24} className="text-gray-300 animate-spin" />
                  </div>
                ) : data && data.columns.length > 0 ? (
                  <>
                    <div className="flex-1 overflow-auto">
                      <table className="w-full text-xs border-collapse min-w-max">
                        <thead className="sticky top-0 z-10">
                          <tr className="bg-gray-50 border-b border-gray-200">
                            {data.columns.map((col) => {
                              const isSorted = sortCol === col;
                              const meta = tables.find((t) => t.name === selectedTable);
                              const colMeta = meta?.columns.find((c) => c.name === col);
                              const isNum = colMeta ? isNumericType(colMeta.type) : false;
                              return (
                                <th
                                  key={col}
                                  onClick={() => handleSort(col)}
                                  className="px-3 py-2.5 text-left font-semibold text-gray-600 cursor-pointer hover:bg-gray-100 whitespace-nowrap select-none"
                                >
                                  <div className="flex items-center gap-1.5">
                                    {isNum
                                      ? <Hash size={10} className="text-blue-400 shrink-0" />
                                      : <AlignLeft size={10} className="text-gray-400 shrink-0" />
                                    }
                                    {col}
                                    {isSorted && (
                                      <span className="text-ucar-blue">{sortDir === "asc" ? "↑" : "↓"}</span>
                                    )}
                                  </div>
                                </th>
                              );
                            })}
                          </tr>
                        </thead>
                        <tbody>
                          {data.rows.map((row, ri) => (
                            <tr
                              key={ri}
                              onClick={() => setSelectedRow(row)}
                              className={clsx(
                                "border-b border-gray-50 cursor-pointer transition-colors",
                                ri % 2 === 0 ? "bg-white" : "bg-gray-50/50",
                                "hover:bg-ucar-blue/5"
                              )}
                            >
                              {data.columns.map((col) => (
                                <td key={col} className="px-3 py-2 whitespace-nowrap text-gray-700 font-mono">
                                  {row[col] === null || row[col] === undefined ? (
                                    <span className="text-gray-300 italic text-[10px]">null</span>
                                  ) : (
                                    formatValue(row[col])
                                  )}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Pagination */}
                    <div className="border-t border-gray-100 px-4 py-2.5 flex items-center justify-between">
                      <span className="text-xs text-gray-400">
                        Page {data.page} / {data.pages} —{" "}
                        {((data.page - 1) * data.page_size + 1).toLocaleString()}–
                        {Math.min(data.page * data.page_size, data.total).toLocaleString()} sur{" "}
                        {data.total.toLocaleString()}
                      </span>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => setPage((p) => Math.max(1, p - 1))}
                          disabled={page === 1}
                          className="p-1.5 rounded border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40"
                        >
                          <ChevronLeft size={13} />
                        </button>
                        {Array.from({ length: Math.min(5, data.pages) }, (_, i) => {
                          const start = Math.max(1, Math.min(page - 2, data.pages - 4));
                          const p = start + i;
                          if (p > data.pages) return null;
                          return (
                            <button
                              key={p}
                              onClick={() => setPage(p)}
                              className={clsx(
                                "px-2.5 py-1 rounded text-xs border",
                                p === page
                                  ? "bg-ucar-blue text-white border-ucar-blue font-bold"
                                  : "border-gray-200 text-gray-600 hover:bg-gray-50"
                              )}
                            >
                              {p}
                            </button>
                          );
                        })}
                        <button
                          onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                          disabled={page === data.pages}
                          className="p-1.5 rounded border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-40"
                        >
                          <ChevronRight size={13} />
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
                    Aucun enregistrement trouvé.
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Row detail panel */}
        {selectedRow && (
          <div className="w-64 shrink-0 bg-white rounded-xl border border-gray-100 flex flex-col overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
              <span className="text-xs font-bold text-gray-700">Détail</span>
              <button onClick={() => setSelectedRow(null)} className="text-gray-400 hover:text-gray-600">
                <X size={13} />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto divide-y divide-gray-50">
              {Object.entries(selectedRow).map(([key, val]) => (
                <div key={key} className="px-4 py-2.5">
                  <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-0.5">{key}</p>
                  <p className={clsx(
                    "text-xs break-all font-mono",
                    val === null || val === undefined ? "text-gray-300 italic" : "text-gray-700"
                  )}>
                    {val === null || val === undefined ? "null" : String(val)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
