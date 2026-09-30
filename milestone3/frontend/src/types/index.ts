export type Language = 'en' | 'hi' | 'kn';

export interface FarmerProfile {
  id: number;
  name: string;
  phone: string;
  email: string;
  location: string;
  preferred_language: Language;
  created_at: string;
}

export interface FieldDetail {
  id: string;
  name: string;
  crop_type: string;
  growth_stage: string;
  soil_type: string;
  area_acres: number;
  location?: string;
  target_moisture_min: number;
  target_moisture_max: number;
  is_active: boolean;
  created_at: string;
  latest_soil_moisture?: number;
  latest_temperature?: number;
  latest_humidity?: number;
  latest_rainfall?: number;
  today_schedule_status?: string;
  today_recommended_liters?: number;
  today_recommended_time?: string;
  today_reason?: string;
  active_alerts_count: number;
}

export interface SensorReading {
  id: number;
  field_id: string;
  timestamp: string;
  soil_moisture_pct: number;
  temperature_c: number;
  humidity_pct: number;
  rainfall_mm: number;
  wind_speed_mps: number;
  solar_radiation_wm2: number;
  is_simulated: boolean;
}

export interface IrrigationSchedule {
  id: number;
  field_id: string;
  field_name?: string;
  crop_type?: string;
  schedule_date: string;
  recommended_start: string;
  duration_minutes: number;
  water_quantity_liters: number;
  status: 'scheduled' | 'completed' | 'skipped';
  reason: string;
  ml_recommendation_needed: boolean;
  created_at: string;
}

export interface IrrigationRecord {
  id: number;
  field_id: string;
  field_name?: string;
  timestamp: string;
  duration_minutes: number;
  water_quantity_liters: number;
  status: string;
  notes?: string;
  created_at: string;
}

export interface AlertItem {
  id: number;
  field_id: string;
  field_name?: string;
  alert_type: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  suggested_action?: string;
  status: 'unread' | 'read' | 'dismissed';
  created_at: string;
}

export interface NotificationPreferences {
  enable_push: boolean;
  enable_sms: boolean;
  enable_email: boolean;
  enable_weather_alerts: boolean;
  enable_moisture_alerts: boolean;
  enable_reminders: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
  low_moisture_threshold: number;
  high_rain_threshold: number;
}

export interface WeatherData {
  field_id: string;
  temperature_c: number;
  humidity_pct: number;
  rainfall_mm: number;
  condition: string;
  wind_speed_mps: number;
  solar_radiation_wm2: number;
  forecast_24h: {
    expected_rain_mm: number;
    max_temp_c: number;
    min_temp_c: number;
    evapotranspiration_risk: string;
  };
}

export interface AIExplanation {
  field_id: string;
  language: string;
  headline: string;
  explanation: string;
  farmer_tip: string;
  source: string;
}

export interface VoiceQueryResponse {
  query: string;
  language: string;
  answer: string;
  audio_base64?: string;
  relevant_fields: string[];
  source: string;
}
