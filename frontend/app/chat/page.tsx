"use client";
import { useState, useRef, useEffect } from "react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { useAuthStore } from "@/store/auth";
import { Send, Bot, User, Lightbulb, Zap } from "lucide-react";
import MarkdownText from "@/components/ui/MarkdownText";
import clsx from "clsx";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

interface Message {
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
}

const SUGGESTIONS = [
  "Quel est le taux d'abandon pour ce semestre ?",
  "Comparez les taux de réussite entre les établissements.",
  "Quel est l'état d'exécution du budget ?",
  "Y a-t-il des anomalies dans les données académiques ?",
  "Quelles sont les recommandations pour l'employabilité ?",
  "Quel établissement a le meilleur taux de réussite ?",
];

export default function ChatPage() {
  const { user } = useAuthStore();
  const [selectedInstitution, setSelectedInstitution] = useState<number | null>(
    user?.institution_id || null
  );
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Bonjour ! Je suis votre assistant IA spécialisé en gestion universitaire UCAR. Posez-moi vos questions sur les données de performance — KPIs, tendances, anomalies, recommandations. Je réponds en temps réel.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamingMode, setStreamingMode] = useState(true);
  const endRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;
    const question = text.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: question }]);
    setLoading(true);

    if (streamingMode) {
      await sendStreaming(question);
    } else {
      await sendDirect(question);
    }
  };

  const sendDirect = async (question: string) => {
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const res = await fetch(`${API_URL}/api/v1/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ question, institution_id: selectedInstitution, stream: false }),
      });
      const data = await res.json();
      setMessages((m) => [...m, { role: "assistant", content: data.answer || "Pas de réponse." }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "Erreur de connexion au service IA." }]);
    } finally {
      setLoading(false);
    }
  };

  const sendStreaming = async (question: string) => {
    abortRef.current = new AbortController();
    // Add an empty streaming message placeholder
    setMessages((m) => [...m, { role: "assistant", content: "", streaming: true }]);

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const res = await fetch(`${API_URL}/api/v1/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ question, institution_id: selectedInstitution, stream: true }),
        signal: abortRef.current.signal,
      });

      if (!res.ok || !res.body) {
        throw new Error("Streaming non disponible");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let accumulated = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const raw = decoder.decode(value, { stream: true });
        const lines = raw.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const chunk = line.slice(6);
            if (chunk === "[DONE]") break;
            // Decode escaped newlines and backslashes sent by the backend
            const decoded = chunk.replace(/\\n/g, "\n").replace(/\\\\/g, "\\");
            accumulated += decoded;
            setMessages((m) => {
              const updated = [...m];
              updated[updated.length - 1] = { role: "assistant", content: accumulated, streaming: true };
              return updated;
            });
          }
        }
      }

      // Mark streaming as done
      setMessages((m) => {
        const updated = [...m];
        updated[updated.length - 1] = { role: "assistant", content: accumulated, streaming: false };
        return updated;
      });
    } catch (err: any) {
      if (err.name !== "AbortError") {
        setMessages((m) => {
          const updated = [...m];
          updated[updated.length - 1] = {
            role: "assistant",
            content: "Désolé, une erreur s'est produite. Essayez en mode standard.",
            streaming: false,
          };
          return updated;
        });
      }
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  };

  const stopStreaming = () => {
    abortRef.current?.abort();
    setLoading(false);
  };

  return (
    <DashboardLayout selectedInstitution={selectedInstitution} onSelectInstitution={setSelectedInstitution}>
      <div className="h-[calc(100vh-8rem)] flex flex-col">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-ucar-blue">Assistant IA</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Track 3 — Interrogez les données institutionnelles en langage naturel
            </p>
          </div>
          {/* Streaming toggle */}
          <button
            onClick={() => setStreamingMode((v) => !v)}
            className={clsx(
              "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-colors",
              streamingMode
                ? "bg-ucar-blue text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            )}
          >
            <Zap size={11} />
            {streamingMode ? "Temps réel activé" : "Temps réel désactivé"}
          </button>
        </div>

        <div className="flex-1 flex gap-6 min-h-0">
          {/* Chat area */}
          <div className="flex-1 flex flex-col bg-white rounded-xl border border-gray-100 overflow-hidden">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, i) => (
                <div key={i} className={clsx("flex gap-3", msg.role === "user" && "justify-end")}>
                  {msg.role === "assistant" && (
                    <div className="w-8 h-8 rounded-full bg-ucar-blue flex items-center justify-center shrink-0 mt-0.5">
                      <Bot size={14} className="text-white" />
                    </div>
                  )}
                  <div
                    className={clsx(
                      "max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed",
                      msg.role === "assistant"
                        ? "bg-gray-50 text-gray-800 rounded-tl-sm"
                        : "bg-ucar-blue text-white rounded-tr-sm"
                    )}
                  >
                    {msg.role === "assistant" ? (
                      msg.content ? (
                        <>
                          <MarkdownText text={msg.content} />
                          {msg.streaming && (
                            <span className="inline-block w-1.5 h-4 bg-ucar-blue/60 ml-0.5 animate-pulse rounded-sm align-middle" />
                          )}
                        </>
                      ) : (
                        <span className="text-gray-400 italic">…</span>
                      )
                    ) : (
                      msg.content
                    )}
                  </div>
                  {msg.role === "user" && (
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center shrink-0 mt-0.5">
                      <User size={14} className="text-gray-600" />
                    </div>
                  )}
                </div>
              ))}

              {loading && !messages[messages.length - 1]?.streaming && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-ucar-blue flex items-center justify-center shrink-0">
                    <Bot size={14} className="text-white" />
                  </div>
                  <div className="bg-gray-50 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
                    {[0, 1, 2].map((i) => (
                      <div key={i} className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                    ))}
                  </div>
                </div>
              )}
              <div ref={endRef} />
            </div>

            {/* Input */}
            <div className="border-t border-gray-100 p-4">
              <div className="flex gap-2">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage(input)}
                  placeholder="Posez votre question sur les données institutionnelles..."
                  disabled={loading}
                  className="flex-1 px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ucar-blue/20 focus:border-ucar-blue disabled:bg-gray-50"
                />
                {loading && streamingMode ? (
                  <button
                    onClick={stopStreaming}
                    className="p-2.5 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                  >
                    ✕
                  </button>
                ) : (
                  <button
                    onClick={() => sendMessage(input)}
                    disabled={!input.trim() || loading}
                    className="p-2.5 bg-ucar-blue text-white rounded-lg hover:bg-ucar-blue-light transition-colors disabled:opacity-50"
                  >
                    <Send size={16} />
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Suggestions panel */}
          <div className="w-64 shrink-0 space-y-4">
            <div className="bg-white rounded-xl border border-gray-100 p-4">
              <div className="flex items-center gap-2 mb-3">
                <Lightbulb size={14} className="text-ucar-gold" />
                <p className="text-xs font-semibold text-gray-700">Questions suggérées</p>
              </div>
              <div className="space-y-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => sendMessage(s)}
                    disabled={loading}
                    className="w-full text-left text-xs text-gray-600 px-3 py-2 rounded-lg bg-gray-50 hover:bg-ucar-blue/5 hover:text-ucar-blue transition-colors disabled:opacity-50"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-ucar-blue/5 rounded-xl border border-ucar-blue/10 p-4">
              <p className="text-xs font-semibold text-ucar-blue mb-2">Capacités IA</p>
              <ul className="space-y-1.5 text-xs text-gray-600">
                <li>✓ Réponses en temps réel (streaming)</li>
                <li>✓ Analyse des KPIs contextuelle</li>
                <li>✓ Détection et explication d'anomalies</li>
                <li>✓ Comparaisons inter-établissements</li>
                <li>✓ Recommandations stratégiques</li>
                <li>✓ Réponses en français</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
