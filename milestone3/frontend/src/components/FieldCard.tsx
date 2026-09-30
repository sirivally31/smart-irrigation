"use client";

import React, { useState } from "react";
import Link from "next/link";
import { FieldDetail } from "@/types";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { MoistureGauge } from "./MoistureGauge";
import { api } from "@/lib/api";
import { Sparkles, ArrowRight, Bell, Clock, Droplet } from "lucide-react";

interface FieldCardProps {
  field: FieldDetail;
  onRefresh?: () => void;
}

export function FieldCard({ field, onRefresh }: FieldCardProps) {
  const { t } = useTranslation();
  const [runningRec, setRunningRec] = useState(false);

  const handleRunRec = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setRunningRec(true);
    try {
      await api.runRecommendation(field.id);
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error(err);
    } finally {
      setRunningRec(false);
    }
  };

  const cropKey = `crop_${field.crop_type.toLowerCase()}` as any;
  const stageKey = `stage_${field.growth_stage.toLowerCase()}` as any;
  const cropLabel = t(cropKey) || field.crop_type;
  const stageLabel = t(stageKey) || field.growth_stage;

  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all hover:border-farm-leaf/40 flex flex-col justify-between">
      <div>
        {/* Header: Name and Status Badge */}
        <div className="flex items-start justify-between">
          <div>
            <span className="text-[10px] font-bold tracking-wider uppercase text-farm-emerald bg-farm-light px-2 py-0.5 rounded-md">
              {cropLabel} • {stageLabel}
            </span>
            <h4 className="text-base sm:text-lg font-bold text-gray-900 mt-1">
              {field.name}
            </h4>
            <p className="text-xs text-gray-500">
              {field.location || "Sector A"} • {field.area_acres} acres
            </p>
          </div>

          {field.active_alerts_count > 0 && (
            <span className="flex items-center space-x-1 px-2 py-0.5 bg-red-50 text-red-700 border border-red-200 rounded-full text-xs font-bold animate-pulse">
              <Bell className="w-3 h-3" />
              <span>{field.active_alerts_count}</span>
            </span>
          )}
        </div>

        {/* Moisture Gauge */}
        <div className="my-4 pt-1">
          <MoistureGauge
            value={field.latest_soil_moisture ?? 35}
            minTarget={field.target_moisture_min}
            maxTarget={field.target_moisture_max}
          />
        </div>

        {/* Today's Schedule Mini-Summary */}
        <div className="bg-farm-sand/80 rounded-xl p-3 border border-farm-light/60 my-2">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="font-semibold text-gray-700 flex items-center space-x-1">
              <Clock className="w-3.5 h-3.5 text-farm-primary" />
              <span>{t("today_irrigation")}</span>
            </span>
            <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${
              field.today_schedule_status === "completed"
                ? "bg-emerald-100 text-emerald-800"
                : field.today_schedule_status === "skipped"
                ? "bg-gray-200 text-gray-700"
                : "bg-amber-100 text-amber-800"
            }`}>
              {field.today_schedule_status === "completed"
                ? t("status_completed")
                : field.today_schedule_status === "skipped"
                ? t("status_skipped")
                : t("status_scheduled")}
            </span>
          </div>

          <div className="flex items-center justify-between text-xs text-gray-600 font-medium mt-1">
            <span>
              {field.today_recommended_time ? `${field.today_recommended_time}` : "--:--"}
            </span>
            <span className="flex items-center space-x-1 font-bold text-farm-dark">
              <Droplet className="w-3 h-3 text-farm-water" />
              <span>{field.today_recommended_liters ?? 0} L</span>
            </span>
          </div>

          {field.today_reason && (
            <p className="text-[11px] text-gray-500 mt-1.5 italic line-clamp-1">
              &ldquo;{field.today_reason}&rdquo;
            </p>
          )}
        </div>
      </div>

      {/* Card Footer Actions */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-100 mt-2">
        <button
          onClick={handleRunRec}
          disabled={runningRec}
          className="text-xs text-farm-primary font-semibold hover:text-farm-emerald flex items-center space-x-1 transition disabled:opacity-50"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>{runningRec ? "Evaluating..." : "Run ML Rec"}</span>
        </button>

        <Link
          href={`/fields/${field.id}`}
          className="text-xs font-bold text-farm-dark hover:text-farm-emerald flex items-center space-x-1 group/link"
        >
          <span>{t("view_details")}</span>
          <ArrowRight className="w-3.5 h-3.5 group-hover/link:translate-x-1 transition-transform" />
        </Link>
      </div>
    </div>
  );
}
