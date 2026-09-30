"use client";

import React from "react";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { Droplets, AlertTriangle, CheckCircle2 } from "lucide-react";

interface MoistureGaugeProps {
  value: number;
  minTarget?: number;
  maxTarget?: number;
  size?: "sm" | "md" | "lg";
}

export function MoistureGauge({
  value,
  minTarget = 35,
  maxTarget = 70,
  size = "md"
}: MoistureGaugeProps) {
  const { t } = useTranslation();

  // Determine state
  const isDry = value < minTarget;
  const isWet = value > maxTarget;
  const isOptimal = !isDry && !isWet;

  // Status color
  const statusColor = isDry
    ? "text-red-600 bg-red-50 border-red-200"
    : isWet
    ? "text-blue-600 bg-blue-50 border-blue-200"
    : "text-emerald-700 bg-emerald-50 border-emerald-200";

  const barColor = isDry
    ? "bg-red-500"
    : isWet
    ? "bg-blue-500"
    : "bg-emerald-500";

  const statusText = isDry
    ? t("moisture_dry")
    : isWet
    ? t("moisture_wet")
    : t("moisture_optimal");

  const StatusIcon = isDry ? AlertTriangle : isWet ? Droplets : CheckCircle2;

  // Clamp percentage for progress bar width
  const clamped = Math.min(100, Math.max(0, value));

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center space-x-1.5">
          <Droplets className="w-4 h-4 text-farm-water" />
          <span className="text-xs font-semibold text-gray-700">
            {t("moisture_level")}
          </span>
        </div>
        <span className="text-lg font-black text-gray-900 tracking-tight">
          {value}%
        </span>
      </div>

      {/* Visual Multi-Segment Bar */}
      <div className="relative w-full h-3 bg-gray-200 rounded-full overflow-hidden">
        {/* Fill bar */}
        <div
          className={`h-full ${barColor} transition-all duration-500 rounded-full`}
          style={{ width: `${clamped}%` }}
        />
        {/* Optimal target range markers */}
        <div
          className="absolute top-0 bottom-0 border-l border-r border-dashed border-gray-400 pointer-events-none opacity-40"
          style={{ left: `${minTarget}%`, width: `${maxTarget - minTarget}%` }}
        />
      </div>

      {/* Target range and status indicator */}
      <div className="flex items-center justify-between mt-2">
        <span className="text-[11px] text-gray-500 font-medium">
          {t("target_range")}: {minTarget}% - {maxTarget}%
        </span>
        <div className={`px-2 py-0.5 rounded-full border text-[11px] font-bold flex items-center space-x-1 ${statusColor}`}>
          <StatusIcon className="w-3 h-3" />
          <span>{statusText}</span>
        </div>
      </div>
    </div>
  );
}
