import { useMemo, useState } from "react";
import { DataTable, PageHeader, SearchControls, Value, RankBadge, CustomChartTooltip } from "./shared";
import { useApi } from "./api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid } from "recharts";
import { Target, Award } from "lucide-react";
import PageBackground from "../components/PageBackground";

export default function Batting() {
  const { data, loading, error } = useApi("/api/batting");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("total_runs");
  const [minRuns, setMinRuns] = useState(0);

  const filteredRows = useMemo(() => {
    return data
      .filter((p) => p.player_name?.toLowerCase().includes(search.toLowerCase()) && +p.total_runs >= minRuns)
      .sort((a, b) => (+b[sort] || 0) - (+a[sort] || 0));
  }, [data, search, sort, minRuns]);

  const top10Batters = useMemo(() => {
    return [...data].sort((a, b) => b.total_runs - a.total_runs).slice(0, 10);
  }, [data]);

  const columns = [
    ["Rank", (_, i) => <RankBadge rank={i + 1} />],
    ["Player", (p) => <strong>{p.player_name}</strong>],
    ["M", (p) => p.matches_played],
    ["Runs", (p) => <Value value={p.total_runs} strong />],
    ["Avg", (p) => <Value value={p.batting_average} />],
    ["SR", (p) => <Value value={p.strike_rate} />],
    ["HS", (p) => p.highest_score],
    ["4s", (p) => <span style={{ color: "#2bd980" }}>{p.fours}</span>],
    ["6s", (p) => <span style={{ color: "#ffd700", fontWeight: "bold" }}>{p.sixes}</span>]
  ];

  return (
    <PageBackground bgImage="/backgrounds/Batting_img.png">
      <main className="page">
        <PageHeader
          eyebrow="CRICIQ · BATTING ANALYTICS"
          title={
            <>
              Batting <em>Analysis</em>
            </>
          }
          description="Career batting performance, boundary stats, averages and strike rates from your match database."
        />

        {!loading && !error && top10Batters.length > 0 && (
          <div className="chart-card">
            <div className="chart-header">
              <h3>
                <Award size={18} /> Top 10 Run Scorers (Overall)
              </h3>
              <span style={{ fontSize: 12, color: "var(--muted)", fontFamily: "var(--font-mono)" }}>
                Sorted by Total Runs
              </span>
            </div>
            <div style={{ width: "100%", height: 260 }}>
              <ResponsiveContainer>
                <BarChart data={top10Batters} margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="player_name" stroke="#a0a7c4" fontSize={11} angle={-15} textAnchor="end" />
                  <YAxis stroke="#a0a7c4" fontSize={11} />
                  <Tooltip content={<CustomChartTooltip />} />
                  <Bar dataKey="total_runs" name="Total Runs" radius={[6, 6, 0, 0]}>
                    {top10Batters.map((_, index) => (
                      <Cell key={index} fill={index < 3 ? "#ffd700" : "#00f2fe"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        <SearchControls
          search={search}
          onSearch={setSearch}
          sort={sort}
          onSort={setSort}
          options={[
            ["total_runs", "Total Runs"],
            ["batting_average", "Batting Average"],
            ["strike_rate", "Strike Rate"],
            ["highest_score", "Highest Score"],
            ["sixes", "Most Sixes"],
            ["fours", "Most Fours"]
          ]}
          extra={
            <select value={minRuns} onChange={(e) => setMinRuns(+e.target.value)}>
              <option value="0">All Runs</option>
              <option value="500">500+ Runs</option>
              <option value="1000">1,000+ Runs</option>
              <option value="2000">2,000+ Runs</option>
            </select>
          }
        />

        <DataTable
          columns={columns}
          rows={filteredRows}
          loading={loading}
          error={error}
          rowKey="player_id"
          empty="No batters match the selected filter criteria."
        />
      </main>
    </PageBackground>
  );
}
