"use client";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine
} from "recharts";
import { KPITrend, INDICATOR_LABELS } from "@/lib/types";

interface Props {
  trend: KPITrend;
}

export default function KPIChart({ trend }: Props) {
  const label = INDICATOR_LABELS[trend.indicator_key] || trend.indicator_key;

  const data = [
    ...trend.historical_labels.map((l, i) => ({
      label: l,
      valeur: trend.historical_values[i],
      prévision: null,
    })),
    ...trend.forecast_labels.map((l, i) => ({
      label: l,
      valeur: null,
      prévision: parseFloat(trend.forecast_values[i].toFixed(1)),
    })),
  ];

  const trendColors: Record<string, string> = {
    croissant: "#16a34a",
    décroissant: "#dc2626",
    stable: "#2563eb",
  };

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-800">{label}</h3>
          <p className="text-xs text-gray-400 mt-0.5">Historique + prévision</p>
        </div>
        <span
          className="text-xs font-medium px-2 py-1 rounded-full"
          style={{
            color: trendColors[trend.trend] || "#6b7280",
            backgroundColor: (trendColors[trend.trend] || "#6b7280") + "18",
          }}
        >
          Tendance : {trend.trend}
        </span>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#9ca3af" }} />
          <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} unit={trend.unit} />
          <Tooltip
            formatter={(val, name) => [
              `${val} ${trend.unit}`,
              name === "valeur" ? "Réel" : "Prévision",
            ]}
            contentStyle={{ borderRadius: 8, border: "1px solid #e5e7eb", fontSize: 12 }}
          />
          <Legend formatter={(v) => (v === "valeur" ? "Réel" : "Prévision")} />
          <ReferenceLine
            x={trend.historical_labels[trend.historical_labels.length - 1]}
            stroke="#d1d5db"
            strokeDasharray="4 4"
          />
          <Line type="monotone" dataKey="valeur" stroke="#1B3A6B" strokeWidth={2} dot={{ r: 4 }} connectNulls={false} />
          <Line type="monotone" dataKey="prévision" stroke="#D4A017" strokeWidth={2} strokeDasharray="6 3" dot={{ r: 4 }} connectNulls={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
