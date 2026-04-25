"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";

export default function Home() {
  const router = useRouter();
  const { hydrate } = useAuthStore();

  useEffect(() => {
    hydrate();
    const token = localStorage.getItem("access_token");
    router.replace(token ? "/dashboard" : "/login");
  }, []);

  return null;
}
