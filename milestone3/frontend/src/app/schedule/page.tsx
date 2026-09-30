"use client";

import React, { useState, useEffect } from "react";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { api } from "@/lib/api";
import { IrrigationSchedule } from "@/types";
import {
  Clock, Droplets, CheckCircle2, AlertCircle, Sparkles,
  Calendar, Check, X
} from "lucide-react";

export default function SchedulePage() {
  const { t } = useTranslation();
  const [schedules, setSchedules] = useState<IrrigationSchedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [executingId, setExecutingId] = useState<number | null>(null);
  const [showExecuteModal, setShowExecuteModal] = useState<IrrigationSchedule | null>(null);
  const [executeData, setExecuteData] = useState({
    duration: 15,
    liters: 30,
    notes: ""
  });

  const loadSchedules = async () => {
    try {
      setLoading(true);
      const data = await api.getTodaySchedules();
      setSchedules(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSchedules();
  }, []);

  const openExecuteModal = (sched: IrrigationSchedule) => {
    setShowExecuteModal(sched);
    setExecuteData({
      duration: sched.duration_minutes || 15,
      liters: sched.water_quantity_liters || 30,
      notes: `Executed scheduled cycle for ${sched.field_name || sched.field_id}`
    });
  };

  const handleConfirmExecution = async () => {
    if (!showExecuteModal) return;
    try {
      setExecutingId(showExecuteModal.id);
      await api.executeSchedule(showExecuteModal.id, {
        actual_duration_minutes: executeData.duration,
        actual_water_liters: executeData.liters,
        notes: executeData.notes
      });
      setShowExecuteModal(null);
      await loadSchedules();
    } catch (err) {
      console.error(err);
    } finally {
      setExecutingId(null);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
          {t("today_schedule_title")}
        </h1>
        <p className="text-xs sm:text-sm text-gray-500">
          {t("schedule_subtitle")}
        </p>
      </div>

      {/* Legend / Distinction Card */}
      <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex flex-wrap gap-4 text-xs font-medium">
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-amber-400"></span>
          <span><b>ML Recommendation:</b> Calculated water deficit</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
          <span><b>Completed Event:</b> Valve opened & cycle verified</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-gray-400"></span>
          <span><b>Skipped:</b> Suppressed due to rain or high moisture</span>
        </div>
      </div>

      {/* Schedules List */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-28 bg-gray-200 animate-pulse rounded-2xl"></div>
          ))}
        </div>
      ) : schedules.length === 0 ? (
        <div className="bg-white p-12 text-center rounded-2xl border border-dashed border-gray-300">
          <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-semibold text-sm">{t("no_schedules_today")}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {schedules.map((sched) => {
            const isCompleted = sched.status === "completed";
            const isSkipped = sched.status === "skipped";

            return (
              <div
                key={sched.id}
                className={`bg-white rounded-2xl p-5 sm:p-6 border transition-all shadow-sm ${
                  isCompleted
                    ? "border-emerald-200 bg-emerald-50/20"
                    : isSkipped
                    ? "border-gray-200 bg-gray-50/40 opacity-80"
                    : "border-amber-200"
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold uppercase text-farm-primary tracking-wider">
                        {sched.field_id}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        isCompleted
                          ? "bg-emerald-100 text-emerald-800"
                          : isSkipped
                          ? "bg-gray-200 text-gray-700"
                          : "bg-amber-100 text-amber-800"
                      }`}>
                        {isCompleted ? t("status_completed") : isSkipped ? t("status_skipped") : t("status_scheduled")}
                      </span>
                    </div>

                    <h3 className="text-lg font-bold text-gray-900 mt-1">
                      {sched.field_name || sched.field_id.replace(/^./, (char) => char.toUpperCase())}
                    </h3>

                    <p className="text-xs text-gray-600 mt-1">
                      <b>{t("reason_label")}:</b> {sched.reason}
                    </p>
                  </div>

                  {/* Recommended Values & Status */}
                  <div className="flex flex-wrap items-center gap-3 sm:gap-6 self-start sm:self-auto text-xs">
                    <div className="bg-farm-sand/80 px-3 py-2 rounded-xl">
                      <span className="text-gray-500 block text-[10px]">{t("recommended_time")}</span>
                      <span className="font-extrabold text-sm text-gray-900">
                        {new Date(sched.recommended_start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>

                    <div className="bg-farm-sand/80 px-3 py-2 rounded-xl">
                      <span className="text-gray-500 block text-[10px]">{t("recommended_water")}</span>
                      <span className="font-extrabold text-sm text-farm-dark flex items-center space-x-1">
                        <Droplets className="w-3.5 h-3.5 text-farm-water" />
                        <span>{sched.water_quantity_liters} L</span>
                      </span>
                    </div>

                    <div className="bg-farm-sand/80 px-3 py-2 rounded-xl">
                      <span className="text-gray-500 block text-[10px]">{t("duration")}</span>
                      <span className="font-extrabold text-sm text-gray-900">
                        {sched.duration_minutes} min
                      </span>
                    </div>

                    {/* Action button */}
                    {!isCompleted && !isSkipped && (
                      <button
                        onClick={() => openExecuteModal(sched)}
                        className="px-4 py-2.5 bg-farm-primary hover:bg-farm-emerald text-white font-bold rounded-xl text-xs shadow-md transition flex items-center space-x-1"
                      >
                        <Check className="w-4 h-4" />
                        <span>{t("mark_as_executed")}</span>
                      </button>
                    )}

                    {isCompleted && (
                      <span className="flex items-center space-x-1 text-emerald-700 font-bold text-xs bg-emerald-100 px-3 py-2 rounded-xl">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Executed</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Execute Modal */}
      {showExecuteModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-farm-light animate-in fade-in">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-4">
              <h3 className="text-base font-bold text-gray-900">
                Confirm Irrigation Execution
              </h3>
              <button
                onClick={() => setShowExecuteModal(null)}
                className="p-1.5 text-gray-400 hover:text-gray-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-gray-600 mb-4">
              This will record an actual completed irrigation event for <b>{showExecuteModal.field_name || showExecuteModal.field_id}</b>.
            </p>

            <div className="space-y-3 text-xs sm:text-sm">
              <div>
                <label className="block font-semibold text-gray-700 mb-1">
                  Water Volume (Liters)
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={executeData.liters}
                  onChange={(e) => setExecuteData({ ...executeData, liters: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">
                  Duration (Minutes)
                </label>
                <input
                  type="number"
                  step="1"
                  value={executeData.duration}
                  onChange={(e) => setExecuteData({ ...executeData, duration: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">
                  Operational Notes
                </label>
                <textarea
                  rows={2}
                  value={executeData.notes}
                  onChange={(e) => setExecuteData({ ...executeData, notes: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                />
              </div>
            </div>

            <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-100 mt-5">
              <button
                type="button"
                onClick={() => setShowExecuteModal(null)}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-xl text-xs font-semibold"
              >
                {t("cancel")}
              </button>
              <button
                type="button"
                onClick={handleConfirmExecution}
                disabled={executingId !== null}
                className="px-5 py-2 bg-farm-primary hover:bg-farm-emerald text-white rounded-xl text-xs font-bold shadow-md"
              >
                {executingId !== null ? t("executing") : t("confirm")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
