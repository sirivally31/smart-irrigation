"use client";

import { useEffect, useState } from "react";

type Reading = { id: number; sensor_id: number; field_id: number; soil_moisture: number; timestamp: string };
type Field = { id: number; name: string; location?: string; latitude: number; longitude: number };
type Weather = { temperature: number; humidity: number; rainfall: number; rain_probability: number };
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [readings, setReadings] = useState<Reading[]>([]);
  const [fields, setFields] = useState<Field[]>([]);
  const [weather, setWeather] = useState<Weather | null>(null);
  const [status, setStatus] = useState("Checking API...");

  useEffect(() => {
    fetch(`${apiUrl}/health`).then((response) => { if (!response.ok) throw new Error(); return response.json(); })
      .then(() => { setStatus("API connected"); return Promise.all([fetch(`${apiUrl}/api/v1/sensors/readings?limit=10`), fetch(`${apiUrl}/api/v1/fields`)]); })
      .then(async ([readingsResponse, fieldsResponse]) => { const nextReadings = await readingsResponse.json(); const nextFields = await fieldsResponse.json(); setReadings(nextReadings); setFields(nextFields); if (nextFields[0]?.latitude != null) { const weatherResponse = await fetch(`${apiUrl}/api/v1/fields/${nextFields[0].id}/weather`); if (weatherResponse.ok) setWeather(await weatherResponse.json()); } })
      .catch(() => setStatus("API unavailable"));
  }, []);

  return <main><p className="eyebrow">MILESTONE 1</p><h1>Smart Irrigation System</h1><p className="status">{status}</p><section><h2>Configured fields</h2>{fields.length === 0 ? <p>No fields configured.</p> : <ul>{fields.map((field) => <li key={field.id}>{field.name} <small>{field.location ?? "No location"}</small></li>)}</ul>}</section><section><h2>Current weather</h2>{weather ? <p>{weather.temperature} C, {weather.humidity}% humidity, {weather.rainfall} mm rain, {weather.rain_probability}% rain probability</p> : <p>Weather unavailable or not configured.</p>}</section><section><h2>Latest sensor readings</h2>{readings.length === 0 ? <p>No readings stored yet.</p> : <ul>{readings.map((reading) => <li key={reading.id}>Sensor {reading.sensor_id}: {reading.soil_moisture}% soil moisture <small>{new Date(reading.timestamp).toLocaleString()}</small></li>)}</ul>}</section></main>;
}