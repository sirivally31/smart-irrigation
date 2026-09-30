"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { Language } from "@/types";
import { api } from "@/lib/api";
import { Sprout, Bell, Globe, User, LogIn } from "lucide-react";

export function Navbar() {
  const { language, setLanguage, t } = useTranslation();
  const [unreadAlerts, setUnreadAlerts] = useState<number>(0);
  const [langDropdownOpen, setLangDropdownOpen] = useState(false);

  useEffect(() => {
    // Fetch active alert count
    api.getAlertStats()
      .then((stats) => setUnreadAlerts(stats.unread))
      .catch(() => setUnreadAlerts(0));

    // Refresh every 30 seconds
    const interval = setInterval(() => {
      api.getAlertStats().then((s) => setUnreadAlerts(s.unread)).catch(() => {});
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const languages: { code: Language; label: string; flag: string }[] = [
    { code: "en", label: "English", flag: "EN" },
    { code: "hi", label: "हिन्दी", flag: "HI" },
    { code: "kn", label: "ಕನ್ನಡ", flag: "KN" }
  ];

  return (
    <header className="sticky top-0 z-40 bg-farm-dark text-white shadow-md border-b border-farm-primary">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl bg-farm-leaf flex items-center justify-center shadow-inner group-hover:scale-105 transition-transform">
            <Sprout className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg sm:text-xl tracking-tight text-white block leading-tight">
              {t("app_title")}
            </span>
            <span className="text-xs text-farm-light/70 hidden sm:block">
              {t("app_tagline")}
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center space-x-1 lg:space-x-4 text-sm font-medium">
          <Link href="/" className="px-3 py-2 rounded-lg hover:bg-farm-primary transition">
            {t("nav_dashboard")}
          </Link>
          <Link href="/fields" className="px-3 py-2 rounded-lg hover:bg-farm-primary transition">
            {t("nav_fields")}
          </Link>
          <Link href="/schedule" className="px-3 py-2 rounded-lg hover:bg-farm-primary transition">
            {t("nav_schedule")}
          </Link>
          <Link href="/history" className="px-3 py-2 rounded-lg hover:bg-farm-primary transition">
            {t("nav_history")}
          </Link>
          <Link href="/analytics" className="px-3 py-2 rounded-lg hover:bg-farm-primary transition">
            {t("nav_analytics")}
          </Link>
          <Link href="/reports" className="px-3 py-2 rounded-lg hover:bg-farm-primary transition">
            {t("nav_reports")}
          </Link>
        </nav>

        {/* Right Controls */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Language Switcher */}
          <div className="relative">
            <button
              onClick={() => setLangDropdownOpen(!langDropdownOpen)}
              className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-farm-primary hover:bg-farm-emerald text-xs sm:text-sm font-semibold border border-farm-leaf/30 transition"
              aria-label="Select Language"
            >
              <Globe className="w-4 h-4 text-farm-light" />
              <span className="uppercase">{language}</span>
            </button>

            {langDropdownOpen && (
              <div
                className="absolute right-0 mt-2 w-36 bg-white text-gray-800 rounded-xl shadow-2xl border border-gray-100 py-1.5 z-50 animate-in fade-in zoom-in-95 duration-150"
                onMouseLeave={() => setLangDropdownOpen(false)}
              >
                {languages.map((l) => (
                  <button
                    key={l.code}
                    onClick={() => {
                      setLanguage(l.code);
                      setLangDropdownOpen(false);
                    }}
                    className={`w-full text-left px-4 py-2.5 text-sm flex items-center justify-between hover:bg-farm-light/60 transition ${
                      language === l.code ? "font-bold text-farm-primary bg-farm-light/30" : "text-gray-700"
                    }`}
                  >
                    <span>{l.label}</span>
                    <span className="text-xs bg-gray-100 text-gray-500 rounded px-1.5 py-0.5 font-mono">
                      {l.flag}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Alerts Bell */}
          <Link
            href="/alerts"
            className="relative p-2 rounded-lg bg-farm-primary hover:bg-farm-emerald text-white transition"
            aria-label="View Alerts"
          >
            <Bell className="w-5 h-5" />
            {unreadAlerts > 0 && (
              <span className="absolute -top-1 -right-1 bg-farm-dry text-white text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center border-2 border-farm-dark animate-pulse">
                {unreadAlerts > 9 ? "9+" : unreadAlerts}
              </span>
            )}
          </Link>

          <Link
            href="/login"
            className="flex items-center gap-2 rounded-lg bg-farm-primary px-2.5 py-2 text-white transition hover:bg-farm-emerald sm:px-3"
            aria-label="Sign in"
          >
            <LogIn className="h-5 w-5" />
            <span className="hidden text-sm font-semibold sm:inline">Sign in</span>
          </Link>

          {/* Profile */}
          <Link
            href="/profile"
            className="p-2 rounded-lg bg-farm-primary hover:bg-farm-emerald text-white transition flex items-center"
            aria-label="Farmer Profile"
          >
            <User className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </header>
  );
}
