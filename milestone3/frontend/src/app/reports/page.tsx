"use client";

import { useEffect, useState } from "react";
import { BarChart3, Download, FileText } from "lucide-react";
import { api } from "@/lib/api";
import { FieldDetail } from "@/types";

export default function ReportsPage() {
  const [fields, setFields] = useState<FieldDetail[]>([]);
  const [fieldId, setFieldId] = useState("");
  const [days, setDays] = useState(7);

  useEffect(() => { api.getFields().then(setFields).catch(() => setFields([])); }, []);

  return (
    <div className="mx-auto max-w-3xl space-y-6 animate-in fade-in duration-300">
      <div><h1 className="text-2xl font-extrabold text-gray-900 sm:text-3xl">Irrigation reports</h1><p className="text-sm text-gray-500">Download recorded history, sensor readings, and alert history for a selected period.</p></div>
      <section className="space-y-4 rounded-2xl border border-gray-100 bg-white p-5 shadow-sm sm:p-6"><div className="grid gap-4 sm:grid-cols-2"><label className="text-sm font-semibold text-gray-700">Field<select value={fieldId} onChange={(e) => setFieldId(e.target.value)} className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 font-normal"><option value="">All fields</option>{fields.map((field) => <option key={field.id} value={field.id}>{field.name}</option>)}</select></label><label className="text-sm font-semibold text-gray-700">Reporting period<select value={days} onChange={(e) => setDays(Number(e.target.value))} className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 font-normal"><option value={7}>Last 7 days</option><option value={30}>Last 30 days</option><option value={90}>Last 90 days</option></select></label></div><div className="grid gap-3 sm:grid-cols-2"><a href={api.getPdfReportUrl(fieldId || undefined, days)} target="_blank" rel="noreferrer" className="inline-flex items-center justify-center gap-2 rounded-xl bg-farm-primary px-4 py-3 text-sm font-bold text-white hover:bg-farm-emerald"><FileText className="h-4 w-4" /> Download PDF report</a><a href={api.getCsvReportUrl("irrigation", fieldId || undefined)} download className="inline-flex items-center justify-center gap-2 rounded-xl border border-farm-primary px-4 py-3 text-sm font-bold text-farm-primary hover:bg-farm-light"><Download className="h-4 w-4" /> Irrigation CSV</a><a href={api.getCsvReportUrl("sensors", fieldId || undefined)} download className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-200 px-4 py-3 text-sm font-bold text-gray-700 hover:bg-gray-50"><BarChart3 className="h-4 w-4" /> Sensor CSV</a><a href={api.getCsvReportUrl("alerts", fieldId || undefined)} download className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-200 px-4 py-3 text-sm font-bold text-gray-700 hover:bg-gray-50"><FileText className="h-4 w-4" /> Alert CSV</a></div><p className="text-xs text-gray-500">Reports contain recorded backend data. Sensor readings marked simulated remain labeled by the API.</p></section>
    </div>
  );
}
