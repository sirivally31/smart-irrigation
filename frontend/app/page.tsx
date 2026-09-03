"use client";

import { useEffect, useState } from "react";

type Reading = { id: number; sensor_id: number; field_id: number; soil_moisture: number; timestamp: string };
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [readings, setReadings] = useState<Reading[]>([]);
  const [status, setStatus] = useState("Checking API...");

  useEffect(() => {
    fetch(`${apiUrl}/health`).then((response) => { if (!response.ok) throw new Error(); return response.json(); })
      .then(() => { setStatus("API connected"); return fetch(`${apiUrl}/api/v1/sensors/readings?limit=10`); })
      .then((response) => response.json()).then(setReadings).catch(() => setStatus("API unavailable"));
  }, []);

  return <main><p className="eyebrow">WEEK 1 FOUNDATION</p><h1>Smart Irrigation System</h1><p className="status">{status}</p><section><h2>Latest sensor readings</h2>{readings.length === 0 ? <p>No readings stored yet.</p> : <ul>{readings.map((reading) => <li key={reading.id}>Sensor {reading.sensor_id}: {reading.soil_moisture}% soil moisture <small>{new Date(reading.timestamp).toLocaleString()}</small></li>)}</ul>}</section></main>;
}