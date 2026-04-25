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

export default function KPICard({
  indicator_key, value, unit, period_label,
  is_anomaly, z_score, anomaly_direction,
}: Props) {
  const label = INDICATOR_LABELS[indicator_key] || indicator_key.replace(/_/g, " ");

  // Only show a trend indicator when there's a real Z-score (not null, not zero)
  const hasTrend = z_score !== null && z_score !== 0;
  const absZ = z_score ? Math.abs(z_score) : 0;

  // Trend icon + colour based on direction and intensity
  let TrendIcon = Minus;
  let trendColor = "text-gray-400";
  let trendLabel = "";

  if (hasTrend) {
    if (z_score! > 0) {
      TrendIcon = TrendingUp;
      trendColor = is_anomaly ? "text-red-500" : "text-green-600";
      trendLabel = is_anomaly ? "Valeur anormalement élevée" : "Tendance à la hausse";
    } else {
      TrendIcon = TrendingDown;
      trendColor = is_anomaly ? "text-red-500" : "text-blue-500";
      trendLabel = is_anomaly ? "Valeur anormalement basse" : "Tendance à la baisse";
    }
  }

  return (
    <div className={clsx(
      "bg-white rounded-xl p-5 border transition-shadow hover:shadow-md",
      is_anomaly ? "border-red-300 shadow-sm shadow-red-50" : "border-gray-100"
    )}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide leading-tight pr-2">
          {label}
        </p>
        {is_anomaly && (
          <span className="flex items-center gap-1 bg-red-100 text-red-600 text-xs font-semibold px-2 py-0.5 rounded-full shrink-0">
            <AlertTriangle size={10} />
            Anomalie
          </span>
        )}
      </div>

      {/* Value */}
      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold text-ucar-blue">
          {typeof value === "number" && value >= 1000
            ? value.toLocaleString("fr-FR")
            : value}
        </span>
        <span className="text-sm text-gray-400 mb-0.5">{unit}</span>
      </div>

      {/* Footer: period + trend */}
      <div className="flex items-center justify-between mt-3">
        <span className="text-xs text-gray-400">{period_label}</span>

        {hasTrend && (
          <span
            className={clsx("flex items-center gap-1 text-xs font-medium", trendColor)}
            title={trendLabel}
          >
            <TrendIcon size={13} />
            {is_anomaly ? anomaly_direction || (z_score! > 0 ? "Élevé" : "Faible") : ""}
          </span>
        )}
      </div>
    </div>
  );
}
