import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "UCAR — Plateforme Intelligente de Gestion Universitaire",
  description: "Gestion centralisée des indicateurs de performance des établissements universitaires",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body className="antialiased">{children}</body>
    </html>
  );
}
