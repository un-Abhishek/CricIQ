import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, BarChart3, MapPin, Shield, Swords, Target, Users, Trophy, Award, Sparkles } from "lucide-react";
import { State, Value } from "./shared";
import { useApi } from "./api";
import TrophyVideoBackground from "../components/TrophyVideoBackground";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const modules = [
  ["/batting", "Batting analysis", Target, "Runs, efficiency, boundaries, 4s & 6s breakdown."],
  ["/bowling", "Bowling analysis", BarChart3, "Wickets, economy rates, maidens and spell impact."],
  ["/teams", "Team performance", Shield, "Wins, highest/lowest scores and win ratios."],
  ["/head-to-head", "Head-to-head", Swords, "Rivalry records, head-to-head wins and match trends."],
  ["/venues", "Venue analytics", MapPin, "Ground scoring patterns, 1st vs 2nd innings trends."],
  ["/players", "Player matchups", Users, "Detailed breakdown against every opposing team."]
];

export default function Dashboard() {
  const matches = useApi("/api/matches");
  const batting = useApi("/api/batting");
  const bowling = useApi("/api/bowling");
  const teams = useApi("/api/teams");
  const venues = useApi("/api/venues");

  const [leaderTab, setLeaderTab] = useState("batting"); // "batting" | "bowling"

  const loading = matches.loading || batting.loading || teams.loading || venues.loading || bowling.loading;
  const error = matches.error || batting.error || teams.error || venues.error || bowling.error;

  const topBatters = useMemo(
    () => [...batting.data].sort((a, b) => b.total_runs - a.total_runs).slice(0, 5),
    [batting.data]
  );

  const topBowlers = useMemo(
    () => [...bowling.data].sort((a, b) => b.wickets - a.wickets).slice(0, 5),
    [bowling.data]
  );

  const chartData = useMemo(() => {
    if (leaderTab === "batting") {
      return topBatters.map((p) => ({
        name: p.player_name,
        value: p.total_runs
      }));
    } else {
      return topBowlers.map((p) => ({
        name: p.player_name,
        value: p.wickets
      }));
    }
  }, [leaderTab, topBatters, topBowlers]);

  return (
    <TrophyVideoBackground videoSpeed={1.0}>
      <main className="dashboard">
        {/* Full-width Transparent Hero Panel */}
        <section className="hero-glass-panel">
          <p className="eyebrow">
            <Trophy size={15} style={{ display: "inline-block", verticalAlign: "middle", marginRight: 6 }} />
            CRICIQ · CRICKET ANALYTICS
          </p>
          <h1>
            Understand the game.<br />
            <em>Beyond the scoreboard.</em>
          </h1>
          <p>
            Explore data-driven cricket insights from your ball-by-ball database: player benchmarks, team dominance, venue scoring patterns, and historical rivalries.
          </p>
          <div style={{ display: "flex", gap: 14, marginTop: 28, flexWrap: "wrap" }}>
            <Link className="button primary" to="/batting">
              Explore Analytics <ArrowRight size={17} />
            </Link>
            <Link className="button secondary" to="/players">
              View Player Matchups
            </Link>
          </div>
        </section>

        {error ? (
          <State type="error" text={error} />
        ) : (
          <>
            {/* Database Metrics */}
            <section className="metric-grid">
              <Metric label="Total Matches" value={matches.data.length} loading={loading} subtitle="Imported IPL Fixtures" />
              <Metric label="Total Batters" value={batting.data.length} loading={loading} subtitle="Active Career Profiles" />
              <Metric label="Total Teams" value={teams.data.length} loading={loading} subtitle="Franchises Analyzed" />
              <Metric label="Total Venues" value={venues.data.length} loading={loading} subtitle="Stadium Grounds" />
            </section>

            {/* Spacious Leaderboard & Visualizer Section */}
            <section className="dashboard-section">
              <div
                className="section-title"
                style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: 16 }}
              >
                <div>
                  <p className="eyebrow">CAREER BENCHMARKS</p>
                  <h2>Leaderboard <em>At a Glance</em></h2>
                </div>
                <div style={{ display: "flex", gap: 10 }}>
                  <button
                    className={`button ${leaderTab === "batting" ? "primary" : "secondary"}`}
                    onClick={() => setLeaderTab("batting")}
                    style={{ padding: "10px 20px", fontSize: 13 }}
                  >
                    <Award size={15} /> Runs
                  </button>
                  <button
                    className={`button ${leaderTab === "bowling" ? "primary" : "secondary"}`}
                    onClick={() => setLeaderTab("bowling")}
                    style={{ padding: "10px 20px", fontSize: 13 }}
                  >
                    <Trophy size={15} /> Wickets
                  </button>
                </div>
              </div>

              <div className="dashboard-grid" style={{ gridTemplateColumns: "1.1fr 0.9fr", gap: 24 }}>
                {/* Spacious Leader List */}
                <div className="leader-list-container">
                  <div className="leader-header">
                    <span>RANK</span>
                    <span>PLAYER</span>
                    <span style={{ textAlign: "right" }}>MATCHES</span>
                    <span style={{ textAlign: "right" }}>{leaderTab === "batting" ? "RUNS" : "WICKETS"}</span>
                    <span style={{ textAlign: "right" }}>{leaderTab === "batting" ? "AVG" : "ECON"}</span>
                  </div>

                  {loading ? (
                    <State type="loading" text="Calculating leaders…" />
                  ) : leaderTab === "batting" ? (
                    topBatters.map((p, i) => (
                      <div key={p.player_id} className="leader-row">
                        <span className={`rank-badge rank-${i + 1}`}>0{i + 1}</span>
                        <div className="player-info">
                          <strong>{p.player_name}</strong>
                          <small>Career Batting</small>
                        </div>
                        <span className="col-stat">{p.matches_played} M</span>
                        <strong className="col-primary">{p.total_runs.toLocaleString()}</strong>
                        <span className="col-stat"><Value value={p.batting_average} /></span>
                      </div>
                    ))
                  ) : (
                    topBowlers.map((p, i) => (
                      <div key={p.player_id} className="leader-row">
                        <span className={`rank-badge rank-${i + 1}`}>0{i + 1}</span>
                        <div className="player-info">
                          <strong>{p.player_name}</strong>
                          <small>Career Bowling</small>
                        </div>
                        <span className="col-stat">{p.matches_played} M</span>
                        <strong className="col-primary">{p.wickets} wkts</strong>
                        <span className="col-stat"><Value value={p.economy_rate} /></span>
                      </div>
                    ))
                  )}
                </div>

                {/* Chart Visualizer */}
                <div className="chart-card" style={{ margin: 0, padding: 28, display: "flex", flexDirection: "column", justifyContent: "center" }}>
                  <div className="chart-header" style={{ marginBottom: 24 }}>
                    <h3>
                      <Sparkles size={18} /> Top 5 {leaderTab === "batting" ? "Run Scorers" : "Wicket Takers"}
                    </h3>
                  </div>
                  <div style={{ width: "100%", height: 260 }}>
                    <ResponsiveContainer>
                      <BarChart data={chartData} layout="vertical" margin={{ left: 10, right: 20, top: 10, bottom: 10 }}>
                        <XAxis type="number" stroke="#a0a7c4" fontSize={12} />
                        <YAxis type="category" dataKey="name" stroke="#f1f3f9" fontSize={13} width={120} tickLine={false} />
                        <Tooltip
                          contentStyle={{ background: "#060813", borderColor: "#ffd700", borderRadius: 8, color: "#f1f3f9" }}
                          formatter={(val) => [val, leaderTab === "batting" ? "Total Runs" : "Wickets"]}
                        />
                        <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={22}>
                          {chartData.map((_, index) => (
                            <Cell key={index} fill={index === 0 ? "#ffd700" : index === 1 ? "#00f2fe" : "#9d4edd"} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </section>
          </>
        )}

        {/* Analytics Feature Modules Grid */}
        <section className="dashboard-section">
          <div className="section-title">
            <p className="eyebrow">EXPLORE CRICIQ ANALYTICS</p>
            <h2>Analytics <em>Modules</em></h2>
          </div>
          <div className="module-grid">
            {modules.map(([to, title, Icon, copy]) => (
              <Link to={to} key={to} className="module-card">
                <Icon size={24} />
                <h3>{title}</h3>
                <p>{copy}</p>
                <ArrowRight size={18} />
              </Link>
            ))}
          </div>
        </section>
      </main>
    </TrophyVideoBackground>
  );
}

function Metric({ label, value, loading, subtitle }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{loading ? "…" : Number(value).toLocaleString()}</strong>
      <small>{subtitle}</small>
    </div>
  );
}
