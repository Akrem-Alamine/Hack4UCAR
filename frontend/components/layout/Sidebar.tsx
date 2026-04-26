"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Bell, FileText, MessageSquare, LogOut, Building2, Upload, Database } from "lucide-react";
import { useAuthStore } from "@/store/auth";
import { useRouter } from "next/navigation";
import clsx from "clsx";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Tableau de bord", icon: LayoutDashboard },
  { href: "/ingestion", label: "Import de données", icon: Upload },
  { href: "/alerts", label: "Alertes", icon: Bell },
  { href: "/reports", label: "Rapports", icon: FileText },
  { href: "/chat", label: "Assistant IA", icon: MessageSquare },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <aside className="fixed inset-y-0 left-0 w-64 bg-ucar-sidebar flex flex-col z-30">
      <div className="px-6 py-5 border-b border-white/10">
        <div className="flex items-center gap-2">
          <Building2 className="text-ucar-gold" size={22} />
          <div>
            <p className="text-white font-bold text-sm leading-none">UCAR</p>
            <p className="text-white/50 text-xs">Plateforme Intelligente</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                active
                  ? "bg-ucar-blue text-white"
                  : "text-white/60 hover:bg-white/10 hover:text-white"
              )}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="px-3 pb-2">
        {(() => {
          const href = "/database";
          const active = pathname.startsWith(href);
          return (
            <Link
              href={href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                active
                  ? "bg-ucar-blue text-white"
                  : "text-white/60 hover:bg-white/10 hover:text-white"
              )}
            >
              <Database size={18} />
              Base de données
            </Link>
          );
        })()}
      </div>

      <div className="px-3 py-4 border-t border-white/10">
        <div className="px-3 py-2 mb-2">
          <p className="text-white text-sm font-medium truncate">
            {user?.first_name} {user?.last_name}
          </p>
          <p className="text-white/40 text-xs truncate">{user?.email}</p>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 w-full rounded-lg text-sm text-white/60 hover:bg-white/10 hover:text-white transition-colors"
        >
          <LogOut size={18} />
          Déconnexion
        </button>
      </div>
    </aside>
  );
}
