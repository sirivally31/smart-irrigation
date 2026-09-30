"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Bell, Check, Filter, RefreshCw, X } from "lucide-react";
import { api } from "@/lib/api";
import { AlertItem, FieldDetail } from "@/types";
import { useTranslation } from "@/lib/i18n/LanguageContext";

export default function AlertsPage() {
  const { t } = useTranslation();
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [fields, setFields] = useState<FieldDetail[]>([]);
  const [fieldId, setFieldId] = useState("");
  const [severity, setSeverity] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAlerts = async () => {
    setLoading(true);
    setError("");
    try {
      const [alertData, fieldData] = await Promise.all([
        api.getAlerts(fieldId || undefined, severity || undefined),
        fields.length ? Promise.resolve(fields) : api.getFields(),
      ]);
      setAlerts(alertData);
      setFields(fieldData);
    } catch (err: any) {
      setError(err.message || "Unable to load alerts.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadAlerts(); }, [fieldId, severity]);

  const updateStatus = async (id: number, status: "read" | "dismissed") => {
    await api.updateAlertStatus(id, status);
    await loadAlerts();
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 sm:text-3xl">{t("nav_alerts")}</h1>
          <p className="text-sm text-gray-500">Review field conditions and mark actions as complete.</p>
        </div>
        <button onClick={() => { api.evaluateAlerts().then(loadAlerts).catch(() => setError("Alert evaluation failed.")); }} className="inline-flex items-center gap-2 rounded-xl bg-farm-primary px-4 py-2.5 text-sm font-bold text-white hover:bg-farm-emerald">
          <RefreshCw className="h-4 w-4" /> Refresh conditions
        </button>
      </div>

      <div className="flex flex-col gap-3 rounded-2xl border border-gray-100 bg-white p-4 shadow-sm sm:flex-row">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700"><Filter className="h-4 w-4" /> Filter</div>
        <select value={fieldId} onChange={(e) => setFieldId(e.target.value)} className="rounded-xl border border-gray-200 px-3 py-2 text-sm">
          <option value="">All fields</option>
          {fields.map((field) => <option key={field.id} value={field.id}>{field.name}</option>)}
        </select>
        <select value={severity} onChange={(e) => setSeverity(e.target.value)} className="rounded-xl border border-gray-200 px-3 py-2 text-sm">
          <option value="">All severities</option><option value="critical">Critical</option><option value="warning">Warning</option><option value="info">Info</option>
        </select>
      </div>

      {error && <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">{error}</div>}
      {loading ? <div className="rounded-2xl bg-white p-10 text-center text-sm text-gray-500">Loading alerts...</div> : alerts.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-gray-300 bg-white p-12 text-center"><Bell className="mx-auto mb-3 h-10 w-10 text-gray-300" /><p className="text-sm font-semibold text-gray-600">No alerts match these filters.</p></div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <article key={alert.id} className={`rounded-2xl border bg-white p-5 shadow-sm ${alert.status === "unread" ? "border-amber-200" : "border-gray-100"}`}>
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="flex gap-3"><div className={`rounded-xl p-2 ${alert.severity === "critical" ? "bg-red-100 text-red-700" : alert.severity === "warning" ? "bg-amber-100 text-amber-700" : "bg-blue-100 text-blue-700"}`}><AlertTriangle className="h-5 w-5" /></div><div><div className="flex flex-wrap items-center gap-2"><h2 className="font-bold text-gray-900">{alert.title}</h2><span className="rounded-full bg-gray-100 px-2 py-0.5 text-[10px] font-bold uppercase text-gray-600">{alert.severity}</span><span className="text-xs text-gray-500">{alert.field_name || alert.field_id}</span></div><p className="mt-1 text-sm text-gray-700">{alert.message}</p>{alert.suggested_action && <p className="mt-2 text-xs font-semibold text-farm-primary">Suggested action: {alert.suggested_action}</p>}<p className="mt-2 text-xs text-gray-400">{new Date(alert.created_at).toLocaleString()}</p></div></div>
                <div className="flex shrink-0 gap-2"><button onClick={() => updateStatus(alert.id, "read")} disabled={alert.status !== "unread"} title="Mark as read" className="rounded-lg border border-gray-200 p-2 text-gray-600 hover:bg-gray-50 disabled:opacity-40"><Check className="h-4 w-4" /></button><button onClick={() => updateStatus(alert.id, "dismissed")} title="Dismiss alert" className="rounded-lg border border-gray-200 p-2 text-gray-600 hover:bg-gray-50"><X className="h-4 w-4" /></button></div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
