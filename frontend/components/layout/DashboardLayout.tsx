"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import Sidebar from "./Sidebar";
import Header from "./Header";

interface Props {
  children: React.ReactNode;
  selectedInstitution: number | null;
  onSelectInstitution: (id: number | null) => void;
}

export default function DashboardLayout({ children, selectedInstitution, onSelectInstitution }: Props) {
  const { user, hydrate } = useAuthStore();
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    hydrate();
    setReady(true);
  }, []);

  useEffect(() => {
    if (ready && !useAuthStore.getState().user) {
      router.push("/login");
    }
  }, [ready]);

  if (!ready || !user) return null;

  return (
    <div className="min-h-screen bg-ucar-bg flex">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        <Header selectedInstitution={selectedInstitution} onSelectInstitution={onSelectInstitution} />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
