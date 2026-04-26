"use client";
import React from "react";

export default function MarkdownText({ text, className = "" }: { text: string; className?: string }) {
  if (!text) return null;

  const parseInline = (raw: string): React.ReactNode => {
    const parts = raw.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**"))
        return <strong key={i} className="font-semibold text-gray-800">{part.slice(2, -2)}</strong>;
      if (part.startsWith("*") && part.endsWith("*"))
        return <em key={i}>{part.slice(1, -1)}</em>;
      return part;
    });
  };

  type Block = { type: "table"; rows: string[][] } | { type: "lines"; lines: string[] };

  // Split into logical blocks: table runs vs everything else
  const lines = text.split("\n");
  const blocks: Block[] = [];

  let i = 0;
  while (i < lines.length) {
    const line = lines[i].trim();
    // Detect table: line contains | and next line is a separator row (|---|)
    if (
      line.startsWith("|") &&
      lines[i + 1] !== undefined &&
      /^\|[\s\-|:]+\|/.test(lines[i + 1].trim())
    ) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      const rows = tableLines
        .filter((l) => !/^\|[\s\-|:]+\|/.test(l.trim())) // drop separator rows
        .map((l) =>
          l
            .trim()
            .replace(/^\|/, "")
            .replace(/\|$/, "")
            .split("|")
            .map((c) => c.trim())
        );
      blocks.push({ type: "table", rows });
    } else {
      const last = blocks[blocks.length - 1];
      if (!last || last.type !== "lines") {
        blocks.push({ type: "lines", lines: [lines[i]] });
      } else {
        last.lines.push(lines[i]);
      }
      i++;
    }
  }

  const renderLines = (rawLines: string[]) => {
    const elements: React.ReactNode[] = [];
    let listBuffer: { type: "ul" | "ol"; items: React.ReactNode[] } | null = null;

    const flushList = () => {
      if (!listBuffer) return;
      if (listBuffer.type === "ul") {
        elements.push(
          <ul key={elements.length} className="list-disc list-inside space-y-1 my-1 text-gray-700">
            {listBuffer.items.map((item, j) => <li key={j}>{item}</li>)}
          </ul>
        );
      } else {
        elements.push(
          <ol key={elements.length} className="list-decimal list-inside space-y-1 my-1 text-gray-700">
            {listBuffer.items.map((item, j) => <li key={j}>{item}</li>)}
          </ol>
        );
      }
      listBuffer = null;
    };

    rawLines.forEach((line, idx) => {
      const trimmed = line.trim();
      if (!trimmed) {
        flushList();
        elements.push(<div key={`gap-${idx}`} className="h-1" />);
        return;
      }
      if (trimmed.startsWith("#### ")) {
        flushList();
        elements.push(<h5 key={idx} className="font-semibold text-gray-700 text-sm mt-2 mb-0.5">{parseInline(trimmed.slice(5))}</h5>);
        return;
      }
      if (trimmed.startsWith("### ")) {
        flushList();
        elements.push(<h4 key={idx} className="font-bold text-ucar-blue text-sm mt-3 mb-1">{parseInline(trimmed.slice(4))}</h4>);
        return;
      }
      if (trimmed.startsWith("## ")) {
        flushList();
        elements.push(<h3 key={idx} className="font-bold text-ucar-blue text-sm mt-3 mb-1">{parseInline(trimmed.slice(3))}</h3>);
        return;
      }
      if (trimmed.startsWith("# ")) {
        flushList();
        elements.push(<h2 key={idx} className="font-bold text-ucar-blue text-base mt-3 mb-1">{parseInline(trimmed.slice(2))}</h2>);
        return;
      }
      if (trimmed.startsWith("- ") || trimmed.startsWith("• ")) {
        const content = parseInline(trimmed.slice(2));
        if (!listBuffer || listBuffer.type !== "ul") { flushList(); listBuffer = { type: "ul", items: [] }; }
        listBuffer.items.push(content);
        return;
      }
      const numbered = trimmed.match(/^(\d+)\.\s+(.+)$/);
      if (numbered) {
        const content = parseInline(numbered[2]);
        if (!listBuffer || listBuffer.type !== "ol") { flushList(); listBuffer = { type: "ol", items: [] }; }
        listBuffer.items.push(content);
        return;
      }
      flushList();
      elements.push(<p key={idx} className="text-sm text-gray-700 leading-relaxed">{parseInline(trimmed)}</p>);
    });

    flushList();
    return elements;
  };

  return (
    <div className={className}>
      {blocks.map((block, bi) => {
        if (block.type === "table") {
          const [header, ...body] = block.rows;
          if (!header) return null;
          return (
            <div key={bi} className="overflow-x-auto my-3 rounded-lg border border-gray-200">
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="bg-ucar-blue text-white">
                    {header.map((cell, ci) => (
                      <th key={ci} className="px-3 py-2 text-left font-semibold whitespace-nowrap">
                        {parseInline(cell)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {body.map((row, ri) => (
                    <tr key={ri} className={ri % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                      {row.map((cell, ci) => (
                        <td key={ci} className="px-3 py-2 border-t border-gray-100">
                          {parseInline(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }
        return <React.Fragment key={bi}>{renderLines(block.lines)}</React.Fragment>;
      })}
    </div>
  );
}
