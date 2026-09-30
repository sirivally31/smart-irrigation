import {
  FarmerProfile, FieldDetail, SensorReading, IrrigationSchedule,
  IrrigationRecord, AlertItem, NotificationPreferences, WeatherData,
  AIExplanation, VoiceQueryResponse
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function fetchJson<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      }
    });
    if (!res.ok) {
      let errDetail = `HTTP ${res.status}`;
      try {
        const errJson = await res.json();
        errDetail = errJson.detail || errDetail;
      } catch (e) {
        // fallback
      }
      throw new Error(errDetail);
    }
    return await res.json();
  } catch (err: any) {
    console.error(`API Fetch Error [${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  // Fields
  getFields: () => fetchJson<FieldDetail[]>("/api/fields"),
  getField: (id: string) => fetchJson<FieldDetail>(`/api/fields/${id}`),
  createField: (data: any) => fetchJson<FieldDetail>("/api/fields", { method: "POST", body: JSON.stringify(data) }),
  updateField: (id: string, data: any) => fetchJson<FieldDetail>(`/api/fields/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteField: (id: string) => fetchJson<{ status: string; message: string }>(`/api/fields/${id}`, { method: "DELETE" }),
  getCurrentSensors: (fieldId: string) => fetchJson<SensorReading>(`/api/fields/${fieldId}/sensors/current`),
  getSensorHistory: (fieldId: string, days = 7) => fetchJson<SensorReading[]>(`/api/fields/${fieldId}/sensors/history?days=${days}`),
  getFieldWeather: (fieldId: string) => fetchJson<WeatherData>(`/api/fields/${fieldId}/weather`),

  // Schedules & Recommendations
  getTodaySchedules: () => fetchJson<IrrigationSchedule[]>("/api/recommendations/today"),
  runRecommendation: (fieldId: string) => fetchJson<IrrigationSchedule>(`/api/recommendations/field/${fieldId}`, { method: "POST" }),
  runAllRecommendations: () => fetchJson<IrrigationSchedule[]>("/api/recommendations/run-all", { method: "POST" }),
  executeSchedule: (id: number, data: { actual_duration_minutes?: number; actual_water_liters?: number; notes?: string }) =>
    fetchJson<any>(`/api/recommendations/schedule/${id}/execute`, { method: "POST", body: JSON.stringify(data) }),

  // History
  getIrrigationHistory: (fieldId?: string, days = 30) =>
    fetchJson<IrrigationRecord[]>(`/api/history/irrigation?${fieldId ? `field_id=${fieldId}&` : ''}days=${days}`),
  getIrrigationSummary: (fieldId?: string, days = 30) =>
    fetchJson<any>(`/api/history/summary?${fieldId ? `field_id=${fieldId}&` : ''}days=${days}`),
  logIrrigation: (data: { field_id: string; duration_minutes: number; water_quantity_liters: number; status?: string; notes?: string }) =>
    fetchJson<IrrigationRecord>("/api/history/irrigation", { method: "POST", body: JSON.stringify(data) }),

  // Alerts
  getAlerts: (fieldId?: string, severity?: string, status?: string) => {
    const params = new URLSearchParams();
    if (fieldId) params.append("field_id", fieldId);
    if (severity) params.append("severity", severity);
    if (status) params.append("status", status);
    return fetchJson<AlertItem[]>(`/api/alerts?${params.toString()}`);
  },
  evaluateAlerts: () => fetchJson<AlertItem[]>("/api/alerts/evaluate", { method: "POST" }),
  updateAlertStatus: (id: number, status: "read" | "unread" | "dismissed") =>
    fetchJson<AlertItem>(`/api/alerts/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),
  getAlertStats: () => fetchJson<{ total: number; unread: number; critical_unread: number; warning_unread: number }>("/api/alerts/stats"),

  // Farmer & Preferences
  getFarmerProfile: () => fetchJson<FarmerProfile>("/api/farmer/profile"),
  updateFarmerProfile: (data: Partial<FarmerProfile>) => fetchJson<FarmerProfile>("/api/farmer/profile", { method: "PUT", body: JSON.stringify(data) }),
  getPreferences: () => fetchJson<NotificationPreferences>("/api/farmer/preferences"),
  updatePreferences: (data: Partial<NotificationPreferences>) => fetchJson<NotificationPreferences>("/api/farmer/preferences", { method: "PUT", body: JSON.stringify(data) }),

  // Notifications
  getVapidKey: () => fetchJson<{ vapid_public_key: string }>("/api/notifications/vapid-public-key"),
  subscribePush: (data: { endpoint: string; keys: { p256dh: string; auth: string } }) =>
    fetchJson<any>("/api/notifications/push/subscribe", { method: "POST", body: JSON.stringify(data) }),
  testPush: () => fetchJson<any>("/api/notifications/push/test", { method: "POST" }),
  testSms: () => fetchJson<any>("/api/notifications/sms/test", { method: "POST" }),
  testEmail: () => fetchJson<any>("/api/notifications/email/test", { method: "POST" }),

  // Sarvam AI & Voice
  explainAI: (fieldId: string, language: string) =>
    fetchJson<AIExplanation>("/api/ai/explain", { method: "POST", body: JSON.stringify({ field_id: fieldId, language }) }),
  voiceQuery: (query: string, language: string, fieldId?: string) =>
    fetchJson<VoiceQueryResponse>("/api/ai/voice-query", { method: "POST", body: JSON.stringify({ query, language, field_id: fieldId }) }),

  // Reports
  getPdfReportUrl: (fieldId?: string, days = 7) =>
    `${API_BASE}/api/reports/pdf?${fieldId ? `field_id=${fieldId}&` : ''}days=${days}`,
  getCsvReportUrl: (type: 'irrigation' | 'sensors' | 'alerts', fieldId?: string) =>
    `${API_BASE}/api/reports/csv?type=${type}${fieldId ? `&field_id=${fieldId}` : ''}`,
};
