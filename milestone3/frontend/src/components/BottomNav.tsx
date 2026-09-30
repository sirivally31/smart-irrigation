"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslation } from "@/lib/i18n/LanguageContext";
import { api } from "@/lib/api";
import { LayoutDashboard, Trees, CalendarDays, Bell, UserCircle } from "lucide-react";

export function BottomNav() {
  const pathname = usePathname();
  const { t } = useTranslation();
  const [unreadAlerts, setUnreadAlerts] = useState(0);

  useEffect(() => {
    api.getAlertStats()
      .then((s) => setUnreadAlerts(s.unread))
      .catch(() => {});
  }, [pathname]);

  const navItems = [
    { href: "/", label: t("nav_dashboard"), icon: LayoutDashboard },
    { href: "/fields", label: t("nav_fields"), icon: Trees },
    { href: "/schedule", label: t("nav_schedule"), icon: CalendarDays },
    { href: "/alerts", label: t("nav_alerts"), icon: Bell, badge: unreadAlerts },
    { href: "/profile", label: t("nav_profile"), icon: UserCircle },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200 shadow-lg px-2 py-1.5 pb-safe">
      <div className="flex items-center justify-around">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`relative flex flex-col items-center justify-center min-w-[56px] py-1 px-2 rounded-xl transition ${
                isActive ? "text-farm-primary font-bold" : "text-gray-500 hover:text-farm-emerald"
              }`}
            >
              <div className="relative">
                <Icon className={`w-6 h-6 ${isActive ? "stroke-[2.5px] scale-110" : "stroke-2"} transition-transform`} />
                {item.badge && item.badge > 0 ? (
                  <span className="absolute -top-1.5 -right-2 bg-farm-dry text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center border border-white">
                    {item.badge > 9 ? "9+" : item.badge}
                  </span>
                ) : null}
              </div>
              <span className="text-[10px] sm:text-xs mt-0.5 tracking-tight truncate max-w-[64px]">
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
