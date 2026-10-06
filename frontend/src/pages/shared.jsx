import { Search, TriangleAlert, Award, ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";

export function Value({ value, strong = false, prefix = "", suffix = "" }) {
  if (value === null || value === undefined || value === "") return "—";
  const num = Number(value);
  const formatted = Number.isFinite(num) && !Number.isInteger(num)
    ? num.toFixed(2)
    : Number.isFinite(num)
    ? num.toLocaleString()
    : value;

  return (
    <span className={strong ? "accent-value" : ""}>
      {prefix}{formatted}{suffix}
    </span>
  );
}

export function RankBadge({ rank }) {
  if (rank === 1) return <span className="rank-badge rank-1" title="1st Rank">🥇</span>;
  if (rank === 2) return <span className="rank-badge rank-2" title="2nd Rank">🥈</span>;
  if (rank === 3) return <span className="rank-badge rank-3" title="3rd Rank">🥉</span>;
  return <span style={{ color: "#91a196", fontWeight: "bold" }}>{rank}</span>;
}

export function PageHeader({ eyebrow, title, description, children }) {
  return (
    <header className="page-header">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {children}
    </header>
  );
}

export function SearchControls({ search, onSearch, sort, onSort, options, extra }) {
  return (
    <div className="controls">
      <label className="search-field">
        <Search size={18} />
        <input
          value={search}
          onChange={(e) => onSearch(e.target.value)}
          placeholder="Search records or players…"
        />
      </label>
      {onSort && options && (
        <select value={sort} onChange={(e) => onSort(e.target.value)}>
          {options.map(([val, label]) => (
            <option key={val} value={val}>
              Sort by: {label}
            </option>
          ))}
        </select>
      )}
      {extra}
    </div>
  );
}

export function DataTable({
  columns,
  rows,
  loading,
  error,
  rowKey,
  empty = "No records found in database.",
  pageSize = 15
}) {
  const [currentPage, setCurrentPage] = useState(1);

  if (loading) return <State type="loading" text="Analyzing live cricket data from database…" />;
  if (error) return <State type="error" text={error} />;
  if (!rows || rows.length === 0) return <State type="empty" text={empty} />;

  const totalPages = Math.ceil(rows.length / pageSize);
  const startIdx = (currentPage - 1) * pageSize;
  const paginatedRows = rows.slice(startIdx, startIdx + pageSize);

  return (
    <div className="table-card">
      <div className="table-count" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span>Showing {rows.length.toLocaleString()} matches & players</span>
        {totalPages > 1 && (
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="control-btn"
              style={{ width: 30, height: 30, opacity: currentPage === 1 ? 0.4 : 1 }}
            >
              <ChevronLeft size={16} />
            </button>
            <span style={{ fontSize: 12, fontFamily: "var(--font-mono)" }}>
              Page {currentPage} of {totalPages}
            </span>
            <button
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              className="control-btn"
              style={{ width: 30, height: 30, opacity: currentPage === totalPages ? 0.4 : 1 }}
            >
              <ChevronRight size={16} />
            </button>
          </div>
        )}
      </div>

      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              {columns.map(([name]) => (
                <th key={name}>{name}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedRows.map((row, index) => {
              const globalIndex = startIdx + index;
              return (
                <tr key={row[rowKey] ?? globalIndex}>
                  {columns.map(([name, render]) => (
                    <td key={name}>{render(row, globalIndex)}</td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function State({ type, text }) {
  return (
    <div className={`state-card ${type}`}>
      {type === "error" && <TriangleAlert size={26} />}
      <strong>
        {type === "loading"
          ? "Connecting to Cricket Database"
          : type === "error"
          ? "Database Query Error"
          : "No Matching Records"}
      </strong>
      <span>{text}</span>
    </div>
  );
}

// Recharts Custom Tooltip
export function CustomChartTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          background: "rgba(10, 18, 14, 0.92)",
          border: "1px solid rgba(229, 184, 66, 0.4)",
          borderRadius: "8px",
          padding: "10px 14px",
          boxShadow: "0 10px 25px rgba(0,0,0,0.5)",
          color: "#ece5d4",
          fontSize: "12px"
        }}
      >
        <strong style={{ display: "block", color: "#e5b842", marginBottom: 6 }}>{label}</strong>
        {payload.map((entry, idx) => (
          <div key={idx} style={{ display: "flex", justifyContent: "space-between", gap: 14, marginTop: 3 }}>
            <span style={{ color: entry.color || "#91a196" }}>{entry.name}:</span>
            <strong style={{ fontFamily: "var(--font-mono)" }}>
              {Number(entry.value).toLocaleString()}
            </strong>
          </div>
        ))}
      </div>
    );
  }
  return null;
}
