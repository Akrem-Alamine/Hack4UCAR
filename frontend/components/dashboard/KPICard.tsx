import { INDICATOR_LABELS } from "@/lib/types";
import { AlertTriangle, TrendingUp, TrendingDown, Minus } from "lucide-react";
import clsx from "clsx";

interface Props {
  indicator_key: string;
  value: number;
  unit: string;
  period_label: string;
  is_anomaly: boolean;
  z_score: number | null;
  anomaly_direction: string | null;
}

export default function KPICard({ indicator_key, value, unit, period_label, is_anomaly, z_score, anomaly_direction }: Props) {
  const label = INDICATOR_LABELS[indicator_key] || indicator_key;

  const trendIcon = !z_score ? <Minus size={14} /> : z_score > 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />;
  const trendColor = !z_score ? "text-gray-400" : Math.abs(z_score) > 2 ? "text-red-500" : "text-green-600";

  return (
    <div className={clsx(
      "bg-white rounded-xl p-5 border transition-shadow hover:shadow-md",
      is_anomaly ? "border-red-300 shadow-red-50" : "border-gray-100"
    )}>
      <div className="flex items-start justify-between mb-3">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide leading-tight">{label}</p>
        {is_anomaly && (
          <span className="flex items-center gap-1 bg-red-100 text-red-600 text-xs font-medium px-2 py-0.5 rounded-full">
            <AlertTriangle size={10} />
            Anomalie
          </span>
        )}
      </div>

      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold text-ucar-blue">
          {typeof value === "number" && value >= 1000
            ? value.toLocaleString("fr-FR")
            : value}
        </span>
        <span className="text-sm text-gray-400 mb-0.5">{unit}</span>
      </div>

      <div className="flex items-center justify-between mt-3">
        <span className="text-xs text-gray-400">{period_label}</span>
        {z_score !== null && (
          <span className={clsx("flex items-center gap-1 text-xs font-medium", trendColor)}>
            {trendIcon}
            Z={z_score}
          </span>
        )}
      </div>
    </div>
  );
}
