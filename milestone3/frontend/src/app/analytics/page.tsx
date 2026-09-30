"use client";

import React, { useState, useEffect } from "react";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { api } from "@/lib/api";
import { SensorReading, FieldDetail, IrrigationRecord } from "@/types";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Legend
} from "recharts";
import {
  TrendingUp, Droplets, CloudRain, Thermometer, Filter
} from "lucide-react";

export default function AnalyticsPage() {
  const { t } = useTranslation();
  const [fields, setFields] = useState<FieldDetail[]>([]);
  const [selectedField, setSelectedField] = useState<string>("north");
  const [selectedDays, setSelectedDays] = useState<number>(7);
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [history, setHistory] = useState<IrrigationRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getFields().then((data) => {
      setFields(data);
      if (data.length > 0 && !selectedField) {
        setSelectedField(data[0].id);
      }
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedField) return;
    setLoading(true);
    Promise.all([
      api.getSensorHistory(selectedField, selectedDays).catch(() => []),
      api.getIrrigationHistory(selectedField, selectedDays).catch(() => [])
    ]).then(([sensorData, histData]) => {
      setReadings(sensorData);
      setHistory(histData);
    }).finally(() => {
      setLoading(false);
    });
  }, [selectedField, selectedDays]);

  const targetField = fields.find((f) => f.id === selectedField);

  // Recharts formatted data
  const sensorChartData = readings.map((r) => ({
    time: new Date(r.timestamp).toLocaleDateString([], { month: "short", day: "numeric", hour: "2-digit" }),
    moisture: r.soil_moisture_pct,
    minTarget: targetField?.target_moisture_min || 35,
    maxTarget: targetField?.target_moisture_max || 75,
    temp: r.temperature_c,
    humidity: r.humidity_pct,
    rain: r.rainfall_mm
  }));

  // Group water usage by date
  const waterUsageMap: Record<string, number> = {};
  history.forEach((h) => {
    const d = new Date(h.timestamp).toLocaleDateString([], { month: "short", day: "numeric" });
    waterUsageMap[d] = (waterUsageMap[d] || 0) + h.water_quantity_liters;
  });
  const waterChartData = Object.entries(waterUsageMap).map(([date, liters]) => ({
    date,
    liters
  }));

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
          {t("sensor_analytics")}
        </h1>
        <p className="text-xs sm:text-sm text-gray-500">
          Telemetry trends, soil retention profiles, and agricultural evapotranspiration demand
        </p>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-gray-400" />
          <span className="text-xs font-semibold text-gray-700">{t("filter_by_field")}:</span>
          <select
            value={selectedField}
            onChange={(e) => setSelectedField(e.target.value)}
            className="px-3 py-2 rounded-xl border border-gray-200 bg-white focus:ring-2 focus:ring-farm-emerald focus:outline-none text-xs sm:text-sm"
          >
            {fields.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name} ({f.crop_type})
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-1.5 w-full sm:w-auto justify-end">
          {[7, 14, 30].map((d) => (
            <button
              key={d}
              onClick={() => setSelectedDays(d)}
              className={`px-3.5 py-1.5 rounded-xl font-semibold text-xs transition ${
                selectedDays === d
                  ? "bg-farm-primary text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {d} Days
            </button>
          ))}
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Soil Moisture Trend vs Target */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-gray-800 flex items-center space-x-1.5">
                <Droplets className="w-4 h-4 text-farm-emerald" />
                <span>{t("moisture_trend")}</span>
              </h3>
              <p className="text-[11px] text-gray-500">
                Target Zone: {targetField?.target_moisture_min}% - {targetField?.target_moisture_max}%
              </p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sensorChartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="time" tick={{ fontSize: 9 }} stroke="#888" />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} stroke="#888" />
                <Tooltip contentStyle={{ backgroundColor: "#1B4D3E", borderRadius: "10px", color: "#fff", fontSize: "12px", border: "none" }} />
                <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                <Line type="monotone" dataKey="moisture" name="Actual Moisture (%)" stroke="#2D7A4D" strokeWidth={3} dot={false} />
                <Line type="monotone" dataKey="minTarget" name="Min Threshold" stroke="#EF4444" strokeDasharray="4 4" dot={false} strokeWidth={1.5} />
                <Line type="monotone" dataKey="maxTarget" name="Max Threshold" stroke="#3B82F6" strokeDasharray="4 4" dot={false} strokeWidth={1.5} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. Temperature & Humidity Trend */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-gray-800 flex items-center space-x-1.5">
                <Thermometer className="w-4 h-4 text-amber-500" />
                <span>{t("weather_trend")}</span>
              </h3>
              <p className="text-[11px] text-gray-500">Ambient Temperature vs Relative Humidity</p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sensorChartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="time" tick={{ fontSize: 9 }} stroke="#888" />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} stroke="#888" />
                <Tooltip contentStyle={{ backgroundColor: "#1E293B", borderRadius: "10px", color: "#fff", fontSize: "12px", border: "none" }} />
                <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                <Line type="monotone" dataKey="temp" name="Temperature (°C)" stroke="#D97706" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="humidity" name="Humidity (%)" stroke="#0284C7" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. Rainfall Trend */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-gray-800 flex items-center space-x-1.5">
                <CloudRain className="w-4 h-4 text-blue-500" />
                <span>Measured Rainfall (mm)</span>
              </h3>
              <p className="text-[11px] text-gray-500">Precipitation events impacting irrigation suppression</p>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sensorChartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="time" tick={{ fontSize: 9 }} stroke="#888" />
                <YAxis tick={{ fontSize: 10 }} stroke="#888" />
                <Tooltip contentStyle={{ backgroundColor: "#0284C7", borderRadius: "10px", color: "#fff", fontSize: "12px", border: "none" }} />
                <Bar dataKey="rain" name="Rainfall (mm)" fill="#0284C7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 4. Cumulative Water Usage */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-gray-800 flex items-center space-x-1.5">
                <TrendingUp className="w-4 h-4 text-farm-primary" />
                <span>{t("water_usage_chart")}</span>
              </h3>
              <p className="text-[11px] text-gray-500">Actual water volume consumed by irrigation cycles</p>
            </div>
          </div>

          <div className="h-64 w-full">
            {waterChartData.length === 0 ? (
              <div className="flex items-center justify-center h-full text-xs text-gray-400 italic">
                No water consumption logged during this period.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={waterChartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="#888" />
                  <YAxis tick={{ fontSize: 10 }} stroke="#888" />
                  <Tooltip contentStyle={{ backgroundColor: "#1B4D3E", borderRadius: "10px", color: "#fff", fontSize: "12px", border: "none" }} />
                  <Bar dataKey="liters" name="Water (Liters)" fill="#2D7A4D" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
