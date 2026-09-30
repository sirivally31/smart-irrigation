"use client";

import { FormEvent, useEffect, useState } from "react";
import { Bell, Check, Mail, MessageSquare, Save, Smartphone, User } from "lucide-react";
import { api } from "@/lib/api";
import { FarmerProfile, Language, NotificationPreferences } from "@/types";
import { useTranslation } from "@/lib/i18n/LanguageContext";

export default function ProfilePage() {
  const { language, setLanguage } = useTranslation();
  const [profile, setProfile] = useState<FarmerProfile | null>(null);
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [pushLoading, setPushLoading] = useState(false);

  useEffect(() => {
    Promise.all([api.getFarmerProfile(), api.getPreferences()]).then(([farmer, prefs]) => {
      setProfile(farmer); setPreferences(prefs); setLanguage(farmer.preferred_language);
    }).catch((err) => setError(err.message || "Unable to load profile."));
  }, [setLanguage]);

  const saveProfile = async (event: FormEvent) => {
    event.preventDefault(); if (!profile) return;
    try { const saved = await api.updateFarmerProfile({ name: profile.name, phone: profile.phone, email: profile.email, location: profile.location, preferred_language: profile.preferred_language }); setProfile(saved); setLanguage(saved.preferred_language); setMessage("Profile saved."); setError(""); } catch (err: any) { setError(err.message || "Profile could not be saved."); }
  };

  const savePreferences = async () => {
    if (!preferences) return;
    try { setPreferences(await api.updatePreferences(preferences)); setMessage("Notification preferences saved."); setError(""); } catch (err: any) { setError(err.message || "Preferences could not be saved."); }
  };

  const togglePreference = (key: keyof NotificationPreferences) => setPreferences((current) => current ? { ...current, [key]: !current[key] } : current);

  const enablePushNotifications = async () => {
    if (!("Notification" in window) || !("serviceWorker" in navigator)) {
      setError("This browser does not support web push notifications.");
      return;
    }
    setPushLoading(true);
    try {
      const permission = await Notification.requestPermission();
      if (permission !== "granted") throw new Error("Notification permission was not granted.");
      const { vapid_public_key: vapidKey } = await api.getVapidKey();
      if (!vapidKey || vapidKey.startsWith("BExample")) throw new Error("Web push is not configured on this backend.");
      const registration = await navigator.serviceWorker.ready;
      const applicationServerKey = Uint8Array.from(atob(vapidKey.replace(/-/g, "+").replace(/_/g, "/")), (char) => char.charCodeAt(0));
      const subscription = await registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey });
      const json = subscription.toJSON();
      if (!json.endpoint || !json.keys?.p256dh || !json.keys.auth) throw new Error("The browser returned an incomplete push subscription.");
      await api.subscribePush({ endpoint: json.endpoint, keys: { p256dh: json.keys.p256dh, auth: json.keys.auth } });
      setPreferences((current) => current ? { ...current, enable_push: true } : current);
      setMessage("Browser push notifications enabled.");
      setError("");
    } catch (err: any) {
      setError(err.message || "Could not enable browser notifications.");
    } finally {
      setPushLoading(false);
    }
  };

  if (!profile || !preferences) return <div className="rounded-2xl bg-white p-10 text-center text-sm text-gray-500">Loading profile...</div>;

  return (
    <div className="mx-auto max-w-3xl space-y-6 animate-in fade-in duration-300">
      <div><h1 className="text-2xl font-extrabold text-gray-900 sm:text-3xl">Farmer profile</h1><p className="text-sm text-gray-500">Manage contact details, language, and notification channels.</p></div>
      {message && <div className="flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800"><Check className="h-4 w-4" />{message}</div>}
      {error && <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</div>}

      <form onSubmit={saveProfile} className="space-y-4 rounded-2xl border border-gray-100 bg-white p-5 shadow-sm sm:p-6">
        <h2 className="flex items-center gap-2 font-bold text-gray-900"><User className="h-5 w-5 text-farm-primary" /> Personal details</h2>
        <div className="grid gap-4 sm:grid-cols-2">{([['name','Name'],['phone','Phone'],['email','Email'],['location','Location']] as const).map(([key,label]) => <label key={key} className="text-sm font-semibold text-gray-700">{label}<input value={profile[key]} onChange={(e) => setProfile({ ...profile, [key]: e.target.value })} className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2.5 font-normal outline-none focus:ring-2 focus:ring-farm-emerald" /></label>)}<label className="text-sm font-semibold text-gray-700">Preferred language<select value={profile.preferred_language} onChange={(e) => setProfile({ ...profile, preferred_language: e.target.value as Language })} className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 font-normal"><option value="en">English</option><option value="hi">Hindi</option><option value="kn">Kannada</option></select></label></div>
        <button className="inline-flex items-center gap-2 rounded-xl bg-farm-primary px-4 py-2.5 text-sm font-bold text-white hover:bg-farm-emerald"><Save className="h-4 w-4" /> Save profile</button>
      </form>

      <section className="space-y-4 rounded-2xl border border-gray-100 bg-white p-5 shadow-sm sm:p-6"><h2 className="flex items-center gap-2 font-bold text-gray-900"><Bell className="h-5 w-5 text-farm-primary" /> Notification preferences</h2><div className="grid gap-3 sm:grid-cols-2">{([['enable_push','Browser push notifications',Bell],['enable_sms','SMS alerts',Smartphone],['enable_email','Email alerts',Mail],['enable_reminders','Irrigation reminders',MessageSquare],['enable_weather_alerts','Weather alerts',Bell],['enable_moisture_alerts','Soil moisture alerts',Bell]] as const).map(([key,label,Icon]) => <label key={key} className="flex cursor-pointer items-center justify-between rounded-xl border border-gray-100 p-3 text-sm font-semibold text-gray-700"><span className="flex items-center gap-2"><Icon className="h-4 w-4 text-farm-emerald" />{label}</span><input type="checkbox" checked={Boolean(preferences[key])} onChange={() => togglePreference(key)} className="h-4 w-4 accent-farm-primary" /></label>)}</div><button onClick={enablePushNotifications} disabled={pushLoading} className="rounded-xl border border-farm-primary px-4 py-2.5 text-sm font-bold text-farm-primary hover:bg-farm-light disabled:opacity-50">{pushLoading ? "Connecting..." : "Enable browser push"}</button><div className="grid gap-4 sm:grid-cols-2"><label className="text-sm font-semibold text-gray-700">Quiet hours start<input type="time" value={preferences.quiet_hours_start} onChange={(e) => setPreferences({ ...preferences, quiet_hours_start: e.target.value })} className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2.5 font-normal" /></label><label className="text-sm font-semibold text-gray-700">Quiet hours end<input type="time" value={preferences.quiet_hours_end} onChange={(e) => setPreferences({ ...preferences, quiet_hours_end: e.target.value })} className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2.5 font-normal" /></label></div><button onClick={savePreferences} className="inline-flex items-center gap-2 rounded-xl bg-farm-primary px-4 py-2.5 text-sm font-bold text-white hover:bg-farm-emerald"><Save className="h-4 w-4" /> Save preferences</button></section>
    </div>
  );
}
