import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "Smart Irrigation System", description: "Week 1 development environment" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}