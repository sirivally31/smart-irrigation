"use client";

import React, { useState, useEffect } from "react";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { api } from "@/lib/api";
import { IrrigationRecord, FieldDetail } from "@/types";
import {
  Calendar, Droplets, Clock, Filter, Plus, X, Search
} from "lucide-react";

export default function HistoryPage() {
  const { t } = useTranslation();
  const [records, setRecords] = useState<IrrigationRecord[]>([]);
  const [fields, setFields] = useState<FieldDetail[]>([]);
  const [selectedField, setSelectedField] = useState<string>("");
  const [selectedDays, setSelectedDays] = useState<number>(30);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<any>(null);

  // Manual Log Modal
  const [showLogModal, setShowLogModal] = useState(false);
  const [manualData, setManualData] = useState({
    field_id: "north",
    duration_minutes: 15,
    water_quantity_liters: 30,
    notes: ""
  });

  const loadHistory = async () => {
    try {
      setLoading(true);
      const [historyData, fieldsData, summaryData] = await Promise.all([
        api.getIrrigationHistory(selectedField || undefined, selectedDays),
        api.getFields().catch(() => []),
        api.getIrrigationSummary(selectedField || undefined, selectedDays).catch(() => null)
      ]);
      setRecords(historyData);
      setFields(fieldsData);
      setSummary(summaryData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [selectedField, selectedDays]);

  const handleManualLog = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.logIrrigation(manualData);
      setShowLogModal(false);
      setManualData({
        field_id: fields[0]?.id || "north",
        duration_minutes: 15,
        water_quantity_liters: 30,
        notes: ""
      });
      await loadHistory();
    } catch (err: any) {
      alert(`Failed to log irrigation: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
            {t("irrigation_history_title")}
          </h1>
          <p className="text-xs sm:text-sm text-gray-500">
            Audit trail of verified irrigation cycles, water consumption, and field applications
          </p>
        </div>

        <button
          onClick={() => setShowLogModal(true)}
          className="px-4 py-2.5 bg-farm-primary hover:bg-farm-emerald text-white font-bold rounded-xl text-xs sm:text-sm flex items-center space-x-1.5 shadow-md transition self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>{t("manual_entry")}</span>
        </button>
      </div>

      {/* Summary KPI Cards */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white p-4 sm:p-5 rounded-2xl border border-gray-100 shadow-sm flex items-center space-x-3">
            <div className="p-3 rounded-xl bg-farm-light text-farm-primary">
              <Droplets className="w-6 h-6 text-farm-water" />
            </div>
            <div>
              <span className="text-xs text-gray-500 font-semibold">{t("total_water_applied")}</span>
              <div className="text-xl font-extrabold text-gray-900">
                {summary.total_water_liters} Liters
              </div>
            </div>
          </div>

          <div className="bg-white p-4 sm:p-5 rounded-2xl border border-gray-100 shadow-sm flex items-center space-x-3">
            <div className="p-3 rounded-xl bg-farm-light text-farm-primary">
              <Calendar className="w-6 h-6 text-farm-emerald" />
            </div>
            <div>
              <span className="text-xs text-gray-500 font-semibold">{t("total_cycles")}</span>
              <div className="text-xl font-extrabold text-gray-900">
                {summary.total_events} events
              </div>
            </div>
          </div>

          <div className="bg-white p-4 sm:p-5 rounded-2xl border border-gray-100 shadow-sm flex items-center space-x-3">
            <div className="p-3 rounded-xl bg-farm-light text-farm-primary">
              <Clock className="w-6 h-6 text-amber-500" />
            </div>
            <div>
              <span className="text-xs text-gray-500 font-semibold">Total Operation Time</span>
              <div className="text-xl font-extrabold text-gray-900">
                {summary.total_duration_minutes} mins
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters Row */}
      <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3 text-xs sm:text-sm">
        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-gray-400" />
          <span className="font-semibold text-gray-700">{t("filter_by_field")}:</span>
          <select
            value={selectedField}
            onChange={(e) => setSelectedField(e.target.value)}
            className="px-3 py-2 rounded-xl border border-gray-200 bg-white focus:ring-2 focus:ring-farm-emerald focus:outline-none text-xs sm:text-sm"
          >
            <option value="">{t("all_fields")}</option>
            {fields.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name} ({f.crop_type})
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-1.5 w-full sm:w-auto justify-end">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setSelectedDays(d)}
              className={`px-3 py-1.5 rounded-xl font-semibold text-xs transition ${
                selectedDays === d
                  ? "bg-farm-primary text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {d === 7 ? t("last_7_days") : d === 30 ? t("last_30_days") : t("last_90_days")}
            </button>
          ))}
        </div>
      </div>

      {/* History Log Table */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-sm text-gray-400">Loading history...</div>
        ) : records.length === 0 ? (
          <div className="p-12 text-center text-sm text-gray-500 italic">
            No irrigation records found for this timeframe.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-farm-sand/70 text-gray-700 font-bold border-b border-gray-200">
                <tr>
                  <th className="p-3.5">{t("date_time")}</th>
                  <th className="p-3.5">Field</th>
                  <th className="p-3.5">{t("duration")}</th>
                  <th className="p-3.5">Water Volume</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5">{t("notes")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 font-medium">
                {records.map((r) => (
                  <tr key={r.id} className="hover:bg-gray-50/80 transition">
                    <td className="p-3.5 text-gray-900">
                      {new Date(r.timestamp).toLocaleString([], { dateStyle: "medium", timeStyle: "short" })}
                    </td>
                    <td className="p-3.5 text-farm-dark font-bold">
                      {r.field_name || r.field_id.replace(/^./, (char) => char.toUpperCase())}
                    </td>
                    <td className="p-3.5 text-gray-600">
                      {r.duration_minutes} min
                    </td>
                    <td className="p-3.5 font-bold text-farm-primary">
                      {r.water_quantity_liters} Liters
                    </td>
                    <td className="p-3.5">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                        {r.status}
                      </span>
                    </td>
                    <td className="p-3.5 text-gray-500 text-xs">
                      {r.notes || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Manual Entry Modal */}
      {showLogModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-farm-light animate-in fade-in">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100 mb-4">
              <h3 className="text-base font-bold text-gray-900">
                {t("manual_entry")}
              </h3>
              <button
                onClick={() => setShowLogModal(false)}
                className="p-1.5 text-gray-400 hover:text-gray-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleManualLog} className="space-y-3.5 text-xs sm:text-sm">
              <div>
                <label className="block font-semibold text-gray-700 mb-1">
                  Select Field
                </label>
                <select
                  value={manualData.field_id}
                  onChange={(e) => setManualData({ ...manualData, field_id: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none bg-white"
                >
                  {fields.map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.name} ({f.crop_type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">
                  Duration (Minutes)
                </label>
                <input
                  type="number"
                  min="1"
                  required
                  value={manualData.duration_minutes}
                  onChange={(e) => setManualData({ ...manualData, duration_minutes: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">
                  Water Quantity (Liters)
                </label>
                <input
                  type="number"
                  step="0.5"
                  min="0.5"
                  required
                  value={manualData.water_quantity_liters}
                  onChange={(e) => setManualData({ ...manualData, water_quantity_liters: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">
                  Notes
                </label>
                <input
                  type="text"
                  placeholder="e.g. Manual furrow watering"
                  value={manualData.notes}
                  onChange={(e) => setManualData({ ...manualData, notes: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-gray-200 focus:ring-2 focus:ring-farm-emerald focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowLogModal(false)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-xl font-semibold"
                >
                  {t("cancel")}
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-farm-primary hover:bg-farm-emerald text-white rounded-xl font-bold shadow-md"
                >
                  Save Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
