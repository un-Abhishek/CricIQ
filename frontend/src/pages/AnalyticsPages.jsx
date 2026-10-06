import { useMemo, useState } from "react";
import { DataTable, PageHeader, SearchControls, Value, RankBadge, CustomChartTooltip } from "./shared";
import { useApi } from "./api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid, Legend } from "recharts";
import { Trophy, Shield, MapPin, Users } from "lucide-react";
import PageBackground from "../components/PageBackground";

const cell = (key, strong = false) => (r) => <Value value={r[key]} strong={strong} />;

// ----------------------------------------------------
// 1. BOWLING PAGE
// ----------------------------------------------------
export function Bowling() {
  const { data, loading, error } = useApi("/api/bowling");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("wickets");

  const rows = useMemo(
    () =>
      data
        .filter((r) => r.player_name?.toLowerCase().includes(search.toLowerCase()))
        .sort((a, b) => (+b[sort] || 0) - (+a[sort] || 0)),
    [data, search, sort]
  );

  const top10Bowlers = useMemo(
    () => [...data].sort((a, b) => b.wickets - a.wickets).slice(0, 10),
    [data]
  );

  const cols = [
    ["Rank", (_, i) => <RankBadge rank={i + 1} />],
    ["Bowler", (r) => <strong>{r.player_name}</strong>],
    ["M", cell("matches_played")],
    ["Wkts", (r) => cell("wickets", true)(r)],
    ["Runs", cell("runs_conceded")],
    ["Balls", cell("balls_bowled")],
    ["Econ", cell("economy_rate")],
    ["Avg", cell("bowling_average")],
    ["SR", cell("bowling_strike_rate")],
    ["Mdns", cell("maidens")],
    ["4W", (r) => <span style={{ color: "#38ef7d" }}>{r.four_wicket_hauls}</span>],
    ["5W", (r) => <span style={{ color: "#ffd700", fontWeight: "bold" }}>{r.five_wicket_hauls}</span>]
  ];

  return (
    <PageBackground bgImage="/backgrounds/Bowling_img.png">
      <main className="page">
        <PageHeader
          eyebrow="CRICIQ · BOWLING ANALYTICS"
          title={
            <>
              Bowling <em>Analysis</em>
            </>
          }
          description="Wickets, economy control, maidens and spell impact across match history."
        />

        {!loading && !error && top10Bowlers.length > 0 && (
          <div className="chart-card">
            <div className="chart-header">
              <h3>
                <Trophy size={18} /> Top 10 Wicket Takers (Purple Cap Benchmark)
              </h3>
              <span style={{ fontSize: 12, color: "var(--muted)", fontFamily: "var(--font-mono)" }}>
                Sorted by Total Wickets
              </span>
            </div>
            <div style={{ width: "100%", height: 260 }}>
              <ResponsiveContainer>
                <BarChart data={top10Bowlers} margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="player_name" stroke="#a0a7c4" fontSize={11} angle={-15} textAnchor="end" />
                  <YAxis stroke="#a0a7c4" fontSize={11} />
                  <Tooltip content={<CustomChartTooltip />} />
                  <Bar dataKey="wickets" name="Wickets" radius={[6, 6, 0, 0]}>
                    {top10Bowlers.map((_, index) => (
                      <Cell key={index} fill={index < 3 ? "#38ef7d" : "#00f2fe"} />
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
            ["wickets", "Most Wickets"],
            ["economy_rate", "Best Economy"],
            ["bowling_average", "Bowling Average"],
            ["five_wicket_hauls", "5-Wicket Hauls"],
            ["four_wicket_hauls", "4-Wicket Hauls"]
          ]}
        />
        <DataTable columns={cols} rows={rows} loading={loading} error={error} rowKey="player_id" />
      </main>
    </PageBackground>
  );
}

// ----------------------------------------------------
// 2. TEAMS PAGE
// ----------------------------------------------------
export function Teams() {
  const { data, loading, error } = useApi("/api/teams");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("wins");

  const rows = useMemo(
    () =>
      data
        .filter((r) => r.team_name?.toLowerCase().includes(search.toLowerCase()))
        .sort((a, b) => (+b[sort] || 0) - (+a[sort] || 0)),
    [data, search, sort]
  );

  const teamWinChartData = useMemo(() => {
    return [...data]
      .sort((a, b) => b.win_percentage - a.win_percentage)
      .map((t) => ({
        name: t.team_name,
        "Win %": t.win_percentage,
        Wins: t.wins,
        Losses: t.losses
      }));
  }, [data]);

  const cols = [
    ["Rank", (_, i) => <RankBadge rank={i + 1} />],
    ["Team", (r) => <strong>{r.team_name}</strong>],
    ["M", cell("matches_played")],
    ["W", (r) => cell("wins", true)(r)],
    ["L", cell("losses")],
    ["Win %", (r) => <Value value={r.win_percentage} suffix="%" strong />],
    ["Avg Score", cell("average_score")],
    ["Highest", (r) => <span style={{ color: "#ffd700", fontWeight: "bold" }}>{r.highest_score}</span>],
    ["Lowest", cell("lowest_score")],
    ["Bat 1st W", cell("batting_first_wins")],
    ["Chase W", cell("chasing_wins")]
  ];

  return (
    <PageBackground bgImage="/backgrounds/Teams_img.png">
      <main className="page">
        <PageHeader
          eyebrow="CRICIQ · TEAM ANALYTICS"
          title={
            <>
              Team <em>Performance</em>
            </>
          }
          description="Win ratios, scoring benchmarks and record totals for every IPL franchise."
        />

        {!loading && !error && teamWinChartData.length > 0 && (
          <div className="chart-card">
            <div className="chart-header">
              <h3>
                <Shield size={18} /> Team Win Ratios (% Win Rate)
              </h3>
              <span style={{ fontSize: 12, color: "var(--muted)", fontFamily: "var(--font-mono)" }}>
                Sorted by Win Percentage
              </span>
            </div>
            <div style={{ width: "100%", height: 260 }}>
              <ResponsiveContainer>
                <BarChart data={teamWinChartData} margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="#a0a7c4" fontSize={11} angle={-15} textAnchor="end" />
                  <YAxis stroke="#a0a7c4" fontSize={11} unit="%" />
                  <Tooltip content={<CustomChartTooltip />} />
                  <Bar dataKey="Win %" name="Win Ratio (%)" radius={[6, 6, 0, 0]}>
                    {teamWinChartData.map((_, index) => (
                      <Cell key={index} fill={index === 0 ? "#ffd700" : index === 1 ? "#38ef7d" : "#00f2fe"} />
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
            ["wins", "Most Wins"],
            ["win_percentage", "Highest Win %"],
            ["total_runs", "Total Runs"],
            ["average_score", "Average Score"],
            ["highest_score", "Highest Team Score"]
          ]}
        />
        <DataTable columns={cols} rows={rows} loading={loading} error={error} rowKey="team_id" />
      </main>
    </PageBackground>
  );
}

// ----------------------------------------------------
// 3. VENUES PAGE
// ----------------------------------------------------
export function Venues() {
  const { data, loading, error } = useApi("/api/venues");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("matches_played");

  const rows = useMemo(
    () =>
      data
        .filter((r) => r.venue_name?.toLowerCase().includes(search.toLowerCase()))
        .sort((a, b) => (+b[sort] || 0) - (+a[sort] || 0)),
    [data, search, sort]
  );

  const venueChartData = useMemo(() => {
    return [...data]
      .sort((a, b) => b.matches_played - a.matches_played)
      .slice(0, 8)
      .map((v) => ({
        name: v.venue_name.split(",")[0],
        "1st Innings Avg": v.average_first_innings_score,
        "2nd Innings Avg": v.average_second_innings_score
      }));
  }, [data]);

  const cols = [
    ["Rank", (_, i) => <RankBadge rank={i + 1} />],
    [
      "Venue",
      (r) => (
        <>
          <strong>{r.venue_name}</strong>
          <small>{[r.city, r.country].filter(Boolean).join(", ")}</small>
        </>
      )
    ],
    ["Matches", cell("matches_played", true)],
    ["Avg Innings", cell("average_innings_score")],
    ["1st Inn Avg", (r) => <span style={{ color: "#38ef7d" }}>{r.average_first_innings_score}</span>],
    ["2nd Inn Avg", (r) => <span style={{ color: "#00f2fe" }}>{r.average_second_innings_score}</span>],
    ["High Score", (r) => <span style={{ color: "#ffd700", fontWeight: "bold" }}>{r.highest_team_score}</span>],
    ["Bat 1st %", (r) => <Value value={r.batting_first_win_percentage} suffix="%" />],
    ["Chase %", (r) => <Value value={r.chasing_win_percentage} suffix="%" />]
  ];

  return (
    <PageBackground bgImage="/backgrounds/Venue_img.png">
      <main className="page">
        <PageHeader
          eyebrow="CRICIQ · GROUND ANALYTICS"
          title={
            <>
              Venue <em>Insights</em>
            </>
          }
          description="How scoring trends, pitch behavior, and chasing win ratios vary across stadiums."
        />

        {!loading && !error && venueChartData.length > 0 && (
          <div className="chart-card">
            <div className="chart-header">
              <h3>
                <MapPin size={18} /> 1st vs 2nd Innings Average Score Comparison
              </h3>
              <span style={{ fontSize: 12, color: "var(--muted)", fontFamily: "var(--font-mono)" }}>
                Top Stadiums by Matches Played
              </span>
            </div>
            <div style={{ width: "100%", height: 260 }}>
              <ResponsiveContainer>
                <BarChart data={venueChartData} margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="#a0a7c4" fontSize={11} angle={-15} textAnchor="end" />
                  <YAxis stroke="#a0a7c4" fontSize={11} domain={[100, 220]} />
                  <Tooltip content={<CustomChartTooltip />} />
                  <Legend wrapperStyle={{ paddingTop: 10, fontSize: 12 }} />
                  <Bar dataKey="1st Innings Avg" fill="#38ef7d" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="2nd Innings Avg" fill="#00f2fe" radius={[4, 4, 0, 0]} />
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
            ["matches_played", "Most Matches"],
            ["average_innings_score", "Highest Average Score"],
            ["highest_team_score", "Highest Team Score"],
            ["batting_first_win_percentage", "Highest Bat 1st Win %"]
          ]}
        />
        <DataTable columns={cols} rows={rows} loading={loading} error={error} rowKey="venue_id" />
      </main>
    </PageBackground>
  );
}

// ----------------------------------------------------
// 4. HEAD-TO-HEAD PAGE
// ----------------------------------------------------
export function HeadToHead() {
  const { data, loading, error } = useApi("/api/head-to-head");
  const [search, setSearch] = useState("");

  const rows = useMemo(
    () => data.filter((r) => `${r.team1} ${r.team2}`.toLowerCase().includes(search.toLowerCase())),
    [data, search]
  );

  const cols = [
    [
      "Matchup",
      (r) => (
        <strong>
          {r.team1} <em style={{ color: "var(--accent)" }}>vs</em> {r.team2}
        </strong>
      )
    ],
    ["Matches", cell("matches_played")],
    ["Team 1 Wins", (r) => <Value value={r.team1_wins} strong />],
    ["Team 2 Wins", (r) => <Value value={r.team2_wins} strong />],
    ["T1 Win %", (r) => <Value value={r.team1_win_percentage} suffix="%" />],
    ["T2 Win %", (r) => <Value value={r.team2_win_percentage} suffix="%" />],
    ["Bat 1st Wins", cell("batting_first_wins")],
    ["Chasing Wins", cell("chasing_wins")]
  ];

  return (
    <PageBackground bgImage="/backgrounds/Head_to_head_img.png">
      <main className="page">
        <PageHeader
          eyebrow="CRICIQ · RIVALRY ANALYTICS"
          title={
            <>
              Head-to-<em>Head</em>
            </>
          }
          description="Historical match results and rivalry dominance across every team pairing."
        />
        <SearchControls search={search} onSearch={setSearch} />
        <DataTable columns={cols} rows={rows} loading={loading} error={error} rowKey="team1_id" empty="No matchups match your search query." />
      </main>
    </PageBackground>
  );
}

// ----------------------------------------------------
// 5. PLAYERS (PLAYER MATCHUPS) PAGE
// ----------------------------------------------------
export function Players() {
  const { data, loading, error } = useApi("/api/player-vs-opponent");
  const [search, setSearch] = useState("");
  const [player, setPlayer] = useState("");

  const names = useMemo(() => [...new Set(data.map((r) => r.player_name))].sort(), [data]);
  const selected = player || names[0];

  const rows = useMemo(
    () =>
      data.filter(
        (r) => r.player_name === selected && r.opponent.toLowerCase().includes(search.toLowerCase())
      ),
    [data, selected, search]
  );

  const totals = useMemo(
    () =>
      rows.reduce(
        (acc, r) => ({
          runs: acc.runs + (+r.runs || 0),
          wickets: acc.wickets + (+r.wickets || 0),
          balls: acc.balls + (+r.balls_faced || 0)
        }),
        { runs: 0, wickets: 0, balls: 0 }
      ),
    [rows]
  );

  const chartData = useMemo(() => {
    return rows.map((r) => ({
      name: r.opponent,
      Runs: r.runs,
      Wickets: r.wickets
    }));
  }, [rows]);

  const cols = [
    ["Opponent", (r) => <strong>{r.opponent}</strong>],
    ["Runs", (r) => cell("runs", true)(r)],
    ["Balls", cell("balls_faced")],
    ["SR", cell("strike_rate")],
    ["Highest", (r) => <span style={{ color: "#ffd700", fontWeight: "bold" }}>{r.highest_score}</span>],
    ["4s", (r) => <span style={{ color: "#38ef7d" }}>{r.fours}</span>],
    ["6s", (r) => <span style={{ color: "#ffd700", fontWeight: "bold" }}>{r.sixes}</span>],
    ["Wkts", (r) => cell("wickets", true)(r)],
    ["Conceded", cell("runs_conceded")],
    ["Econ", cell("economy_rate")]
  ];

  return (
    <PageBackground bgImage="/backgrounds/player_img.png">
      <main className="page">
        <PageHeader
          eyebrow="CRICIQ · PLAYER MATCHUPS"
          title={
            <>
              Player <em>Discovery</em>
            </>
          }
          description="Inspect any player's career batting and bowling performance broken down against every opponent team."
        />

        {!loading && !error && (
          <div className="profile-strip">
            <label>
              Select Player:
              <select value={selected} onChange={(e) => setPlayer(e.target.value)}>
                {names.map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </label>
            <div>
              <small>Runs vs Opponents</small>
              <strong>{totals.runs.toLocaleString()}</strong>
            </div>
            <div>
              <small>Wickets vs Opponents</small>
              <strong>{totals.wickets}</strong>
            </div>
            <div>
              <small>Opponents Faced</small>
              <strong>{rows.length}</strong>
            </div>
          </div>
        )}

        {!loading && !error && chartData.length > 0 && (
          <div className="chart-card">
            <div className="chart-header">
              <h3>
                <Users size={18} /> Performance breakdown for <em style={{ color: "#ffd700", fontStyle: "normal", marginLeft: 6 }}>{selected}</em>
              </h3>
            </div>
            <div style={{ width: "100%", height: 240 }}>
              <ResponsiveContainer>
                <BarChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="#a0a7c4" fontSize={11} angle={-15} textAnchor="end" />
                  <YAxis stroke="#a0a7c4" fontSize={11} />
                  <Tooltip content={<CustomChartTooltip />} />
                  <Bar dataKey="Runs" fill="#ffd700" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Wickets" fill="#38ef7d" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        <SearchControls search={search} onSearch={setSearch} />
        <DataTable columns={cols} rows={rows} loading={loading} error={error} rowKey="opponent_team_id" empty="No opponent records match this search." />
      </main>
    </PageBackground>
  );
}
