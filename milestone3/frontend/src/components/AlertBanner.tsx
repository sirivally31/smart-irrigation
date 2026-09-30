"use client";

import React from "react";
import Link from "next/link";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { AlertTriangle, ArrowRight } from "lucide-react";

interface AlertBannerProps {
  criticalCount: number;
}

export function AlertBanner({ criticalCount }: AlertBannerProps) {
  const { t } = useTranslation();

  if (criticalCount <= 0) return null;

  return (
    <div className="bg-red-600 text-white px-4 py-2.5 rounded-xl shadow-md mb-6 flex items-center justify-between animate-pulse">
      <div className="flex items-center space-x-2.5 text-sm font-semibold">
        <AlertTriangle className="w-5 h-5 flex-shrink-0" />
        <span>
          {criticalCount} {t("severity_critical")} {t("nav_alerts").toLowerCase()}: Immediate attention required.
        </span>
      </div>
      <Link
        href="/alerts"
        className="bg-white/20 hover:bg-white/30 text-white text-xs font-bold px-3 py-1.5 rounded-lg flex items-center space-x-1 transition"
      >
        <span>View</span>
        <ArrowRight className="w-3.5 h-3.5" />
      </Link>
    </div>
  );
}
