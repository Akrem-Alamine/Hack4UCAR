"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { INDICATOR_LABELS } from "@/lib/types";

interface CompEntry {
  institution_acronym: string;
  value: number;
  unit: string;
}

interface Props {
  indicatorKey: string;
  data: CompEntry[];
}

const COLORS = ["#1B3A6B", "#2A5298", "#D4A017", "#4B6CB7", "#8B9DC3"];

export default function ComparisonChart({ indicatorKey, data }: Props) {
  const label = INDICATOR_LABELS[indicatorKey] || indicatorKey;
  const unit = data[0]?.unit || "";

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-800">{label} — Comparaison inter-établissements</h3>
        <p className="text-xs text-gray-400 mt-0.5">Dernière période disponible</p>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="institution_acronym" tick={{ fontSize: 11, fill: "#6b7280" }} />
          <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} unit={unit} />
          <Tooltip
            formatter={(val) => [`${val} ${unit}`, label]}
            contentStyle={{ borderRadius: 8, border: "1px solid #e5e7eb", fontSize: 12 }}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
