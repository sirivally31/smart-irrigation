"use client";

import React, { useState, useEffect } from "react";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { Download, X } from "lucide-react";

export function PWAInstallPrompt() {
  const { t } = useTranslation();
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Check if user already dismissed recently
    const isDismissed = sessionStorage.getItem("pwa_prompt_dismissed");
    if (isDismissed) {
      setDismissed(true);
    }

    const handler = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };

    window.addEventListener("beforeinstallprompt", handler);

    // Register service worker if supported
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker
        .register("/sw.js")
        .then(() => console.log("PWA Service Worker registered"))
        .catch((err) => console.warn("PWA SW registration failed:", err));
    }

    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") {
      setDeferredPrompt(null);
    }
  };

  const handleDismiss = () => {
    setDismissed(true);
    sessionStorage.setItem("pwa_prompt_dismissed", "true");
  };

  if (!deferredPrompt || dismissed) return null;

  return (
    <div className="fixed top-18 left-4 right-4 md:left-auto md:right-6 md:max-w-md z-40 bg-farm-dark text-white p-3.5 rounded-2xl shadow-2xl border border-farm-leaf flex items-center justify-between animate-in fade-in slide-in-from-top-4">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-farm-leaf rounded-xl">
          <Download className="w-5 h-5 text-white" />
        </div>
        <div>
          <h4 className="text-xs font-bold leading-tight">Install Farmer PWA</h4>
          <p className="text-[11px] text-farm-light/80">Add to home screen for offline access</p>
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <button
          onClick={handleInstall}
          className="px-3 py-1.5 bg-white text-farm-dark hover:bg-farm-light text-xs font-bold rounded-lg transition"
        >
          Install
        </button>
        <button
          onClick={handleDismiss}
          className="p-1 text-gray-400 hover:text-white transition"
          aria-label="Dismiss install prompt"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
