"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { api } from "@/lib/api";
import { FieldDetail, SensorReading, IrrigationRecord, AIExplanation } from "@/types";
import { MoistureGauge } from "@/components/MoistureGauge";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";
import {
  ArrowLeft, Sparkles, Clock, Droplets, Thermometer, Wind,
  Sun, CloudRain, Calendar, ShieldCheck
} from "lucide-react";

export default function FieldDetailPage() {
  const params = useParams();
  const fieldId = params.id as string;
  const router = useRouter();
  const { t, language } = useTranslation();

  const [field, setField] = useState<FieldDetail | null>(null);
  const [sensors, setSensors] = useState<SensorReading[]>([]);
  const [history, setHistory] = useState<IrrigationRecord[]>([]);
  const [aiExp, setAiExp] = useState<AIExplanation | null>(null);
  const [loading, setLoading] = useState(true);
  const [runningRec, setRunningRec] = useState(false);

  const loadFieldData = async () => {
    try {
      setLoading(true);
      const [fData, sData, hData, aiData] = await Promise.all([
        api.getField(fieldId),
        api.getSensorHistory(fieldId, 7).catch(() => []),
        api.getIrrigationHistory(fieldId, 30).catch(() => []),
        api.explainAI(fieldId, language).catch(() => null),
      ]);
      setField(fData);
      setSensors(sData);
      setHistory(hData);
      setAiExp(aiData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (fieldId) {
      loadFieldData();
    }
  }, [fieldId, language]);

  const handleTriggerRec = async () => {
    setRunningRec(true);
    try {
      await api.runRecommendation(fieldId);
      await loadFieldData();
    } catch (err) {
      console.error(err);
    } finally {
      setRunningRec(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-40 bg-gray-200 animate-pulse rounded-lg"></div>
        <div className="h-64 bg-gray-200 animate-pulse rounded-2xl"></div>
      </div>
    );
  }

  if (!field) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 font-semibold">Field not found.</p>
        <Link href="/fields" className="text-farm-primary underline text-sm mt-2 block">
          Return to Fields
        </Link>
      </div>
    );
  }

  // Format sensor data for Recharts
  const chartData = sensors.map((s) => ({
    time: new Date(s.timestamp).toLocaleDateString([], { month: "short", day: "numeric", hour: "2-digit" }),
    moisture: s.soil_moisture_pct,
    temp: s.temperature_c,
    humidity: s.humidity_pct
  }));

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <Link
            href="/fields"
            className="p-2 rounded-xl bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <span className="text-[10px] font-bold tracking-wider uppercase text-farm-emerald bg-farm-light px-2 py-0.5 rounded-md">
              {field.crop_type} • {field.growth_stage}
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 mt-1">
              {field.name}
            </h1>
          </div>
        </div>

        <button
          onClick={handleTriggerRec}
          disabled={runningRec}
          className="px-4 py-2.5 bg-farm-primary hover:bg-farm-emerald text-white text-xs sm:text-sm font-bold rounded-xl shadow-md transition flex items-center space-x-2 self-start sm:self-auto disabled:opacity-50"
        >
          <Sparkles className={`w-4 h-4 ${runningRec ? "animate-spin" : ""}`} />
          <span>{runningRec ? "Evaluating..." : "Run ML Recommendation"}</span>
        </button>
      </div>

      {/* Main Grid: Status Gauge, Telemetry, and AI Explanation */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Gauge and Field Info */}
        <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-3">
              Field Telemetry
            </h3>
            <MoistureGauge
              value={field.latest_soil_moisture ?? 35}
              minTarget={field.target_moisture_min}
              maxTarget={field.target_moisture_max}
            />

            <div className="grid grid-cols-2 gap-3 mt-6 pt-4 border-t border-gray-100 text-xs">
              <div className="flex items-center space-x-2 text-gray-700">
                <Thermometer className="w-4 h-4 text-amber-500" />
                <span>Temp: <b>{field.latest_temperature ?? 26.5}°C</b></span>
              </div>
              <div className="flex items-center space-x-2 text-gray-700">
                <Droplets className="w-4 h-4 text-sky-500" />
                <span>Humidity: <b>{field.latest_humidity ?? 60}%</b></span>
              </div>
              <div className="flex items-center space-x-2 text-gray-700">
                <CloudRain className="w-4 h-4 text-blue-500" />
                <span>Rain: <b>{field.latest_rainfall ?? 0} mm</b></span>
              </div>
              <div className="flex items-center space-x-2 text-gray-700">
                <Wind className="w-4 h-4 text-teal-600" />
                <span>Area: <b>{field.area_acres} ac</b></span>
              </div>
            </div>
          </div>

          {/* Today's Recommendation Box */}
          <div className="mt-6 pt-4 border-t border-gray-100 bg-farm-sand/80 p-4 rounded-xl">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="font-bold text-farm-primary flex items-center space-x-1">
                <Clock className="w-3.5 h-3.5" />
                <span>{t("today_irrigation")}</span>
              </span>
              <span className="font-bold text-[10px] bg-white px-2 py-0.5 rounded border border-gray-200">
                {field.today_schedule_status?.toUpperCase() || "SCHEDULED"}
              </span>
            </div>
            <div className="text-sm font-extrabold text-gray-900 mt-1">
              {field.today_recommended_liters ?? 0} Liters ({Math.round((field.today_recommended_liters ?? 0) / 2)} mins)
            </div>
            {field.today_reason && (
              <p className="text-xs text-gray-600 mt-1 italic">
                &ldquo;{field.today_reason}&rdquo;
              </p>
            )}
          </div>
        </div>

        {/* Center & Right: Sarvam AI Advisory + Sensor Trend Chart */}
        <div className="lg:col-span-2 space-y-6">
          {/* Sarvam AI Multilingual Advisory Box */}
          {aiExp && (
            <div className="bg-gradient-to-br from-white to-farm-light/30 rounded-2xl p-6 border border-farm-light shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2 text-farm-primary">
                  <Sparkles className="w-5 h-5 text-farm-emerald" />
                  <h3 className="font-bold text-base text-farm-dark">
                    {aiExp.headline}
                  </h3>
                </div>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 bg-farm-primary text-white rounded">
                  {aiExp.source === "sarvam_ai" ? "Sarvam AI" : "Agronomic AI"}
                </span>
              </div>

              <p className="text-sm text-gray-800 leading-relaxed font-medium">
                {aiExp.explanation}
              </p>

              <div className="mt-4 p-3 bg-white rounded-xl border border-farm-leaf/20 flex items-start space-x-2 text-xs text-farm-emerald font-semibold">
                <ShieldCheck className="w-4 h-4 flex-shrink-0 mt-0.5 text-farm-leaf" />
                <span><b>Farmer Tip:</b> {aiExp.farmer_tip}</span>
              </div>
            </div>
          )}

          {/* Interactive Recharts 7-Day Trend Chart */}
          <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
            <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-4">
              {t("moisture_trend")}
            </h3>
            {chartData.length === 0 ? (
              <p className="text-xs text-gray-400 py-12 text-center">No telemetry recorded yet.</p>
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="time" tick={{ fontSize: 10 }} stroke="#888" />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} stroke="#888" />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#1B4D3E", borderRadius: "12px", border: "none", color: "#fff", fontSize: "12px" }}
                    />
                    <Line
                      type="monotone"
                      dataKey="moisture"
                      name="Moisture (%)"
                      stroke="#2D7A4D"
                      strokeWidth={3}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Field Irrigation Records Table */}
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
        <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider mb-4 flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-farm-primary" />
          <span>Past Irrigation Cycles for this Field</span>
        </h3>

        {history.length === 0 ? (
          <p className="text-xs text-gray-400 py-6 text-center italic">
            No completed irrigation cycles recorded for this field.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-farm-sand/70 text-gray-700 font-bold border-b border-gray-200">
                <tr>
                  <th className="p-3">Date & Time</th>
                  <th className="p-3">Duration</th>
                  <th className="p-3">Water Applied</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {history.map((record) => (
                  <tr key={record.id} className="hover:bg-gray-50/80 transition">
                    <td className="p-3 font-medium text-gray-900">
                      {new Date(record.timestamp).toLocaleString([], { dateStyle: "medium", timeStyle: "short" })}
                    </td>
                    <td className="p-3 text-gray-600">{record.duration_minutes} mins</td>
                    <td className="p-3 font-bold text-farm-dark">{record.water_quantity_liters} Liters</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full text-[10px] font-bold">
                        {record.status}
                      </span>
                    </td>
                    <td className="p-3 text-gray-500">{record.notes || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
