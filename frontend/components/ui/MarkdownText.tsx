"use client";
import React from "react";

/**
 * Renders basic markdown into styled JSX.
 * Handles: **bold**, *italic*, ## headings, - bullets, 1. numbered lists.
 * No external dependency needed.
 */
export default function MarkdownText({ text, className = "" }: { text: string; className?: string }) {
  if (!text) return null;

  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let listBuffer: { type: "ul" | "ol"; items: React.ReactNode[] } | null = null;

  const flushList = () => {
    if (!listBuffer) return;
    if (listBuffer.type === "ul") {
      elements.push(
        <ul key={elements.length} className="list-disc list-inside space-y-1 my-1 text-gray-700">
          {listBuffer.items.map((item, i) => <li key={i}>{item}</li>)}
        </ul>
      );
    } else {
      elements.push(
        <ol key={elements.length} className="list-decimal list-inside space-y-1 my-1 text-gray-700">
          {listBuffer.items.map((item, i) => <li key={i}>{item}</li>)}
        </ol>
      );
    }
    listBuffer = null;
  };

  const parseInline = (raw: string): React.ReactNode => {
    // Split on **bold** and *italic* markers
    const parts = raw.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={i} className="font-semibold text-gray-800">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith("*") && part.endsWith("*")) {
        return <em key={i}>{part.slice(1, -1)}</em>;
      }
      return part;
    });
  };

  lines.forEach((line, idx) => {
    const trimmed = line.trim();

    // Skip empty lines — flush any open list
    if (!trimmed) {
      flushList();
      elements.push(<div key={`gap-${idx}`} className="h-1" />);
      return;
    }

    // ## Heading
    if (trimmed.startsWith("### ")) {
      flushList();
      elements.push(
        <h4 key={idx} className="font-bold text-ucar-blue text-sm mt-3 mb-1">
          {parseInline(trimmed.slice(4))}
        </h4>
      );
      return;
    }
    if (trimmed.startsWith("## ")) {
      flushList();
      elements.push(
        <h3 key={idx} className="font-bold text-ucar-blue text-sm mt-3 mb-1">
          {parseInline(trimmed.slice(3))}
        </h3>
      );
      return;
    }
    if (trimmed.startsWith("# ")) {
      flushList();
      elements.push(
        <h2 key={idx} className="font-bold text-ucar-blue text-base mt-3 mb-1">
          {parseInline(trimmed.slice(2))}
        </h2>
      );
      return;
    }

    // - Bullet list item
    if (trimmed.startsWith("- ") || trimmed.startsWith("• ")) {
      const content = parseInline(trimmed.slice(2));
      if (!listBuffer || listBuffer.type !== "ul") {
        flushList();
        listBuffer = { type: "ul", items: [] };
      }
      listBuffer.items.push(content);
      return;
    }

    // 1. Numbered list item
    const numberedMatch = trimmed.match(/^(\d+)\.\s+(.+)$/);
    if (numberedMatch) {
      const content = parseInline(numberedMatch[2]);
      if (!listBuffer || listBuffer.type !== "ol") {
        flushList();
        listBuffer = { type: "ol", items: [] };
      }
      listBuffer.items.push(content);
      return;
    }

    // Regular paragraph line
    flushList();
    elements.push(
      <p key={idx} className="text-sm text-gray-700 leading-relaxed">
        {parseInline(trimmed)}
      </p>
    );
  });

  flushList();

  return <div className={className}>{elements}</div>;
}
