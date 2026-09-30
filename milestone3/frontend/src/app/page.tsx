"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { api } from "@/lib/api";
import { FieldDetail, IrrigationSchedule, AlertItem, FarmerProfile } from "@/types";
import { FieldCard } from "@/components/FieldCard";
import { AlertBanner } from "@/components/AlertBanner";
import {
  Trees, Clock, Droplets, AlertTriangle, Sparkles, Plus,
  FileDown, CloudRain, Sun, Wind, Compass
} from "lucide-react";

export default function DashboardPage() {
  const { t, language } = useTranslation();
  const [fields, setFields] = useState<FieldDetail[]>([]);
  const [todaySchedules, setTodaySchedules] = useState<IrrigationSchedule[]>([]);
  const [alertStats, setAlertStats] = useState({ total: 0, unread: 0, critical_unread: 0, warning_unread: 0 });
  const [farmer, setFarmer] = useState<FarmerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [runningAll, setRunningAll] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [fieldsData, schedData, statsData, farmerData] = await Promise.all([
        api.getFields().catch(() => []),
        api.getTodaySchedules().catch(() => []),
        api.getAlertStats().catch(() => ({ total: 0, unread: 0, critical_unread: 0, warning_unread: 0 })),
        api.getFarmerProfile().catch(() => null),
      ]);
      setFields(fieldsData);
      setTodaySchedules(schedData);
      setAlertStats(statsData);
      setFarmer(farmerData);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunAllRecs = async () => {
    setRunningAll(true);
    try {
      await api.runAllRecommendations();
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setRunningAll(false);
    }
  };

  // Compute summary stats
  const totalWaterScheduled = todaySchedules
    .filter((s) => s.status === "scheduled")
    .reduce((sum, s) => sum + s.water_quantity_liters, 0);

  const avgMoisture = fields.length > 0
    ? Math.round(
        fields.reduce((acc, f) => acc + (f.latest_soil_moisture || 35), 0) / fields.length
      )
    : 0;

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Critical Alert Banner */}
      <AlertBanner criticalCount={alertStats.critical_unread} />

      {/* Hero Welcome & Quick Stats Banner */}
      <div className="bg-gradient-to-r from-farm-dark to-farm-primary text-white rounded-3xl p-6 sm:p-8 shadow-xl relative overflow-hidden">
        {/* Background Subtle Leaf Deco */}
        <div className="absolute right-0 top-0 bottom-0 w-1/3 opacity-10 pointer-events-none flex items-center justify-center">
          <Droplets className="w-64 h-64" />
        </div>

        <div className="relative z-10">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="text-xs sm:text-sm font-semibold text-farm-light/80 tracking-wide uppercase">
                {farmer?.location || "Dharwad, Karnataka"}
              </span>
              <h1 className="text-2xl sm:text-3xl font-extrabold mt-1 tracking-tight">
                {t("welcome_farmer")}, {farmer?.name || "Farmer"}!
              </h1>
              <p className="text-xs sm:text-sm text-farm-light/90 max-w-xl mt-1">
                IoT soil sensors and ML models are actively monitoring your crop water demand.
              </p>
            </div>

            {/* Quick action button on Hero */}
            <div className="flex items-center space-x-2">
              <button
                onClick={handleRunAllRecs}
                disabled={runningAll}
                className="px-4 py-2.5 bg-white text-farm-dark hover:bg-farm-light font-bold rounded-xl text-xs sm:text-sm shadow-md transition flex items-center space-x-2 disabled:opacity-75"
              >
                <Sparkles className={`w-4 h-4 text-farm-emerald ${runningAll ? "animate-spin" : ""}`} />
                <span>{runningAll ? "Updating..." : t("run_all_recs")}</span>
              </button>
            </div>
          </div>

          {/* KPI Metric Cards Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mt-6">
            <div className="bg-white/10 backdrop-blur-md p-3.5 sm:p-4 rounded-2xl border border-white/15">
              <div className="flex items-center space-x-2 text-farm-light/80 text-xs font-semibold">
                <Trees className="w-4 h-4" />
                <span>{t("total_fields")}</span>
              </div>
              <div className="text-xl sm:text-2xl font-black mt-1 text-white">
                {fields.length}
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-md p-3.5 sm:p-4 rounded-2xl border border-white/15">
              <div className="flex items-center space-x-2 text-farm-light/80 text-xs font-semibold">
                <Droplets className="w-4 h-4 text-sky-300" />
                <span>{t("avg_soil_moisture")}</span>
              </div>
              <div className="text-xl sm:text-2xl font-black mt-1 text-white">
                {avgMoisture}%
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-md p-3.5 sm:p-4 rounded-2xl border border-white/15">
              <div className="flex items-center space-x-2 text-farm-light/80 text-xs font-semibold">
                <Clock className="w-4 h-4 text-amber-300" />
                <span>{t("today_irrigation")}</span>
              </div>
              <div className="text-xl sm:text-2xl font-black mt-1 text-white">
                {totalWaterScheduled} L
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-md p-3.5 sm:p-4 rounded-2xl border border-white/15">
              <div className="flex items-center space-x-2 text-farm-light/80 text-xs font-semibold">
                <AlertTriangle className="w-4 h-4 text-rose-300" />
                <span>{t("active_alerts")}</span>
              </div>
              <div className="text-xl sm:text-2xl font-black mt-1 text-white">
                {alertStats.unread}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Field Cards Grid Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg sm:text-xl font-extrabold text-gray-900 tracking-tight">
              {t("nav_fields")}
            </h2>
            <p className="text-xs text-gray-500">Live soil conditions & today&apos;s recommendations</p>
          </div>

          <div className="flex items-center space-x-2">
            <Link
              href="/fields"
              className="text-xs font-bold text-farm-primary hover:text-farm-emerald bg-farm-light/60 hover:bg-farm-light px-3 py-1.5 rounded-lg transition"
            >
              {t("field_management")}
            </Link>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-64 bg-gray-200 animate-pulse rounded-2xl"></div>
            ))}
          </div>
        ) : fields.length === 0 ? (
          <div className="bg-white p-8 rounded-2xl text-center border border-dashed border-gray-300">
            <p className="text-gray-500 text-sm">No fields registered yet.</p>
            <Link
              href="/fields"
              className="mt-3 inline-flex items-center space-x-1 px-4 py-2 bg-farm-primary text-white text-xs font-bold rounded-xl"
            >
              <Plus className="w-4 h-4" />
              <span>{t("add_new_field")}</span>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {fields.map((field) => (
              <FieldCard key={field.id} field={field} onRefresh={loadData} />
            ))}
          </div>
        )}
      </section>

      {/* Today's Schedule Overview + Weather Snapshot Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Schedule Widget */}
        <div className="lg:col-span-2 bg-white p-5 sm:p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base sm:text-lg font-bold text-gray-900">
                {t("today_schedule_title")}
              </h3>
              <p className="text-xs text-gray-500">{t("schedule_subtitle")}</p>
            </div>
            <Link
              href="/schedule"
              className="text-xs font-bold text-farm-emerald hover:underline"
            >
              View Full Schedule →
            </Link>
          </div>

          {todaySchedules.length === 0 ? (
            <p className="text-xs text-gray-500 py-4 italic">{t("no_schedules_today")}</p>
          ) : (
            <div className="space-y-3">
              {todaySchedules.map((sched) => (
                <div
                  key={sched.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 bg-farm-sand/70 rounded-xl border border-farm-light/50 gap-2"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-9 h-9 rounded-lg bg-farm-light text-farm-primary flex items-center justify-center font-bold text-xs uppercase">
                      {sched.field_id.slice(0, 2)}
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-gray-900">
                        {sched.field_name || sched.field_id.replace(/^./, (char) => char.toUpperCase())}
                      </h4>
                      <p className="text-xs text-gray-500 line-clamp-1">
                        {sched.reason}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 self-end sm:self-auto text-xs">
                    <span className="font-semibold text-gray-700">
                      {new Date(sched.recommended_start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    <span className="font-bold text-farm-dark bg-white px-2 py-1 rounded-md border border-gray-200">
                      {sched.water_quantity_liters} L ({sched.duration_minutes}m)
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      sched.status === "completed"
                        ? "bg-emerald-100 text-emerald-800"
                        : sched.status === "skipped"
                        ? "bg-gray-200 text-gray-700"
                        : "bg-amber-100 text-amber-800"
                    }`}>
                      {sched.status === "completed" ? t("status_completed") : sched.status === "skipped" ? t("status_skipped") : t("status_scheduled")}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Live Weather Widget */}
        <div className="bg-white p-5 sm:p-6 rounded-2xl border border-gray-100 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base sm:text-lg font-bold text-gray-900">
                {t("weather_overview")}
              </h3>
              <Sun className="w-5 h-5 text-amber-500" />
            </div>

            <div className="flex items-center space-x-4 my-2">
              <span className="text-4xl font-black text-gray-900">
                {fields[0]?.latest_temperature ?? 26.5}°C
              </span>
              <div>
                <span className="text-sm font-bold text-farm-primary block">
                  {t("condition_sunny")}
                </span>
                <span className="text-xs text-gray-500">
                  Humidity: {fields[0]?.latest_humidity ?? 58}%
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-gray-100 text-xs">
              <div className="flex items-center space-x-2 text-gray-600">
                <CloudRain className="w-4 h-4 text-sky-500" />
                <span>Rain: {fields[0]?.latest_rainfall ?? 0} mm</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600">
                <Wind className="w-4 h-4 text-teal-600" />
                <span>Wind: 2.1 m/s</span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-gray-100">
            <Link
              href="/reports"
              className="w-full py-2.5 px-3 bg-farm-sand hover:bg-farm-light text-farm-primary font-bold text-xs rounded-xl flex items-center justify-center space-x-1.5 transition"
            >
              <FileDown className="w-4 h-4" />
              <span>{t("reports_title")}</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
