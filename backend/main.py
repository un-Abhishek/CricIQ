from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_db_connection

app = FastAPI(
    title="CricIQ API",
    description="Cricket Analytics API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Welcome to CricIQ API",
        "status": "running"
    }


@app.get("/test-db")
def test_database():
    connection = get_db_connection()

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM cricket_match")

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return {
        "database": "connected",
        "matches": result[0]
    }


@app.get("/api/batting")
def get_batting_stats():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    WITH player_innings AS (
        SELECT
            d.match_id,
            d.innings_no,
            d.batter_id,
            SUM(d.batter_runs) AS innings_runs,
            COUNT(d.delivery_id)
            - COUNT(de.delivery_id) AS balls_faced,
            SUM(
                CASE
                    WHEN d.batter_runs = 4 THEN 1
                    ELSE 0
                END
            ) AS fours,
            SUM(
                CASE
                    WHEN d.batter_runs = 6 THEN 1
                    ELSE 0
                END
            ) AS sixes
        FROM delivery d
        LEFT JOIN delivery_extra de
            ON d.delivery_id = de.delivery_id
            AND de.extra_type = 'wides'
        GROUP BY
            d.match_id,
            d.innings_no,
            d.batter_id
    ),

    player_dismissals AS (
        SELECT
            w.player_out_id AS player_id,
            COUNT(*) AS times_dismissed
        FROM wicket w
        GROUP BY w.player_out_id
    )

    SELECT
        p.player_id,
        p.player_name,
        COUNT(DISTINCT pi.match_id) AS matches_played,
        SUM(pi.innings_runs) AS total_runs,
        SUM(pi.balls_faced) AS balls_faced,

        ROUND(
            SUM(pi.innings_runs) * 100.0 /
            NULLIF(SUM(pi.balls_faced), 0),
            2
        ) AS strike_rate,

        MAX(pi.innings_runs) AS highest_score,

        ROUND(
            SUM(pi.innings_runs) /
            NULLIF(pd.times_dismissed, 0),
            2
        ) AS batting_average,

        SUM(pi.fours) AS fours,
        SUM(pi.sixes) AS sixes

    FROM player_innings pi

    JOIN player p
        ON pi.batter_id = p.player_id

    LEFT JOIN player_dismissals pd
        ON p.player_id = pd.player_id

    GROUP BY
        p.player_id,
        p.player_name,
        pd.times_dismissed

    ORDER BY total_runs DESC;
    """

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result


@app.get("/api/bowling")
def get_bowling_stats():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    WITH delivery_stats AS (
        SELECT
            d.delivery_id,
            d.match_id,
            d.innings_no,
            d.over_no,
            d.bowler_id,
            d.total_runs,

            COALESCE(SUM(
                CASE
                    WHEN de.extra_type IN ('byes', 'legbyes', 'penalty')
                    THEN de.extra_runs
                    ELSE 0
                END
            ), 0) AS non_bowler_extras,

            COALESCE(SUM(
                CASE
                    WHEN de.extra_type IN ('wides', 'noballs')
                    THEN de.extra_runs
                    ELSE 0
                END
            ), 0) AS illegal_delivery_extras

        FROM delivery d

        LEFT JOIN delivery_extra de
            ON d.delivery_id = de.delivery_id

        GROUP BY
            d.delivery_id,
            d.match_id,
            d.innings_no,
            d.over_no,
            d.bowler_id,
            d.total_runs
    ),

    bowler_stats AS (
        SELECT
            ds.bowler_id,

            COUNT(DISTINCT ds.match_id) AS matches_played,

            SUM(
                ds.total_runs - ds.non_bowler_extras
            ) AS runs_conceded,

            SUM(
                CASE
                    WHEN ds.illegal_delivery_extras = 0
                    THEN 1
                    ELSE 0
                END
            ) AS balls_bowled

        FROM delivery_stats ds

        GROUP BY ds.bowler_id
    ),

    bowler_wickets AS (
        SELECT
            ds.bowler_id,
            COUNT(w.wicket_id) AS wickets

        FROM delivery_stats ds

        LEFT JOIN wicket w
            ON ds.delivery_id = w.delivery_id

        GROUP BY ds.bowler_id
    ),

    over_stats AS (
        SELECT
            ds.match_id,
            ds.innings_no,
            ds.over_no,
            ds.bowler_id,

            SUM(
                ds.total_runs - ds.non_bowler_extras
            ) AS runs_conceded

        FROM delivery_stats ds

        GROUP BY
            ds.match_id,
            ds.innings_no,
            ds.over_no,
            ds.bowler_id
    ),

    bowler_hauls AS (
        SELECT
            os.bowler_id,

            SUM(
                CASE
                    WHEN os.wickets_in_match >= 4
                    THEN 1
                    ELSE 0
                END
            ) AS four_wicket_hauls,

            SUM(
                CASE
                    WHEN os.wickets_in_match >= 5
                    THEN 1
                    ELSE 0
                END
            ) AS five_wicket_hauls

        FROM (
            SELECT
                os.match_id,
                os.bowler_id,
                COUNT(w.wicket_id) AS wickets_in_match

            FROM over_stats os

            LEFT JOIN delivery_stats ds
                ON os.match_id = ds.match_id
                AND os.innings_no = ds.innings_no
                AND os.over_no = ds.over_no
                AND os.bowler_id = ds.bowler_id

            LEFT JOIN wicket w
                ON ds.delivery_id = w.delivery_id

            GROUP BY
                os.match_id,
                os.bowler_id
        ) os

        GROUP BY os.bowler_id
    ),

    bowler_overs AS (
        SELECT
            os.bowler_id,

            COUNT(*) AS overs_bowled,

            SUM(
                CASE
                    WHEN os.runs_conceded = 0
                    THEN 1
                    ELSE 0
                END
            ) AS maidens

        FROM over_stats os

        GROUP BY os.bowler_id
    )

    SELECT
        p.player_id,
        p.player_name,

        bs.matches_played,

        bw.wickets,

        bs.runs_conceded,

        bs.balls_bowled,

        bo.overs_bowled,

        bo.maidens,

        ROUND(
            bs.runs_conceded * 6.0 /
            NULLIF(bs.balls_bowled, 0),
            2
        ) AS economy_rate,

        ROUND(
            bs.runs_conceded * 1.0 /
            NULLIF(bw.wickets, 0),
            2
        ) AS bowling_average,

        ROUND(
            bs.balls_bowled * 1.0 /
            NULLIF(bw.wickets, 0),
            2
        ) AS bowling_strike_rate,

        bh.four_wicket_hauls,

        bh.five_wicket_hauls

    FROM bowler_stats bs

    JOIN player p
        ON bs.bowler_id = p.player_id

    JOIN bowler_wickets bw
        ON bs.bowler_id = bw.bowler_id

    JOIN bowler_overs bo
        ON bs.bowler_id = bo.bowler_id

    JOIN bowler_hauls bh
        ON bs.bowler_id = bh.bowler_id

    ORDER BY bw.wickets DESC;
    """

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result


@app.get("/api/matches")
def get_match_stats():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    WITH match_teams AS (
        SELECT
            mt.match_id,
            MAX(
                CASE
                    WHEN mt.team_role = 'team1'
                    THEN mt.team_id
                END
            ) AS team1_id,
            MAX(
                CASE
                    WHEN mt.team_role = 'team2'
                    THEN mt.team_id
                END
            ) AS team2_id
        FROM match_team mt
        GROUP BY mt.match_id
    ),

    innings_scores AS (
        SELECT
            i.match_id,
            i.innings_no,
            i.batting_team_id,
            SUM(d.total_runs) AS total_runs
        FROM innings i
        JOIN delivery d
            ON i.match_id = d.match_id
            AND i.innings_no = d.innings_no
        WHERE i.is_super_over = FALSE
        GROUP BY
            i.match_id,
            i.innings_no,
            i.batting_team_id
    ),

    first_innings AS (
        SELECT
            match_id,
            batting_team_id AS first_batting_team_id,
            total_runs AS first_innings_score
        FROM innings_scores
        WHERE innings_no = 1
    ),

    second_innings AS (
        SELECT
            match_id,
            batting_team_id AS chasing_team_id,
            total_runs AS second_innings_score
        FROM innings_scores
        WHERE innings_no = 2
    )

    SELECT
        cm.match_id,
        cm.match_date,
        cm.match_format,
        cm.gender,

        c.competition_name,
        e.edition_name,
        e.season,

        v.venue_name,
        v.city,
        v.country AS venue_country,

        t1.team_name AS team1,
        t2.team_name AS team2,

        toss.team_name AS toss_winner,
        cm.toss_decision,

        winner.team_name AS winner,

        cm.outcome_type,
        cm.result_by_type,
        cm.result_by_value,
        cm.method,

        fi.first_batting_team_id,
        first_team.team_name AS first_batting_team,

        fi.first_innings_score,
        si.second_innings_score,

        CASE
            WHEN cm.winner_team_id IS NULL
                THEN 'No Result / Tie'

            WHEN cm.winner_team_id = fi.first_batting_team_id
                THEN 'Batting First'

            WHEN cm.winner_team_id = si.chasing_team_id
                THEN 'Chasing'

            ELSE 'Other'
        END AS winning_strategy

    FROM cricket_match cm

    LEFT JOIN match_teams mt
        ON cm.match_id = mt.match_id

    LEFT JOIN team t1
        ON mt.team1_id = t1.team_id

    LEFT JOIN team t2
        ON mt.team2_id = t2.team_id

    LEFT JOIN team toss
        ON cm.toss_winner_id = toss.team_id

    LEFT JOIN team winner
        ON cm.winner_team_id = winner.team_id

    LEFT JOIN edition e
        ON cm.edition_id = e.edition_id

    LEFT JOIN competition c
        ON e.competition_id = c.competition_id

    LEFT JOIN venue v
        ON cm.venue_id = v.venue_id

    LEFT JOIN first_innings fi
        ON cm.match_id = fi.match_id

    LEFT JOIN second_innings si
        ON cm.match_id = si.match_id

    LEFT JOIN team first_team
        ON fi.first_batting_team_id = first_team.team_id

    ORDER BY cm.match_date DESC;
    """

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result


@app.get("/api/teams")
def get_team_stats():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    WITH team_matches AS (
        SELECT
            mt.team_id,
            mt.match_id
        FROM match_team mt
    ),

    team_results AS (
        SELECT
            tm.team_id,
            tm.match_id,

            CASE
                WHEN cm.winner_team_id = tm.team_id
                    THEN 1
                ELSE 0
            END AS win,

            CASE
                WHEN cm.winner_team_id IS NULL
                    THEN 1
                ELSE 0
            END AS no_result_or_tie

        FROM team_matches tm

        JOIN cricket_match cm
            ON tm.match_id = cm.match_id
    ),

    innings_scores AS (
        SELECT
            i.match_id,
            i.batting_team_id AS team_id,
            i.innings_no,

            SUM(d.total_runs) AS runs_scored

        FROM innings i

        JOIN delivery d
            ON i.match_id = d.match_id
            AND i.innings_no = d.innings_no

        WHERE i.is_super_over = FALSE

        GROUP BY
            i.match_id,
            i.batting_team_id,
            i.innings_no
    ),

    team_scoring AS (
        SELECT
            team_id,

            COUNT(DISTINCT match_id) AS matches_batted,

            SUM(runs_scored) AS total_runs,

            ROUND(
                AVG(runs_scored),
                2
            ) AS average_score,

            MAX(runs_scored) AS highest_score,

            MIN(runs_scored) AS lowest_score

        FROM innings_scores

        GROUP BY team_id
    ),

    runs_conceded AS (
        SELECT
            i.batting_team_id AS batting_team_id,
            mt.team_id AS bowling_team_id,
            i.match_id,

            SUM(d.total_runs) AS runs_conceded

        FROM innings i

        JOIN delivery d
            ON i.match_id = d.match_id
            AND i.innings_no = d.innings_no

        JOIN match_team mt
            ON i.match_id = mt.match_id
            AND mt.team_id <> i.batting_team_id

        WHERE i.is_super_over = FALSE

        GROUP BY
            i.batting_team_id,
            mt.team_id,
            i.match_id
    ),

    team_conceding AS (
        SELECT
            bowling_team_id AS team_id,

            SUM(runs_conceded) AS total_runs_conceded,

            ROUND(
                AVG(runs_conceded),
                2
            ) AS average_runs_conceded

        FROM runs_conceded

        GROUP BY bowling_team_id
    ),

    batting_first_results AS (
        SELECT
            first_innings.team_id,

            COUNT(*) AS batting_first_matches,

            SUM(
                CASE
                    WHEN cm.winner_team_id = first_innings.team_id
                        THEN 1
                    ELSE 0
                END
            ) AS batting_first_wins

        FROM innings_scores first_innings

        JOIN cricket_match cm
            ON first_innings.match_id = cm.match_id

        WHERE first_innings.innings_no = 1

        GROUP BY first_innings.team_id
    ),

    chasing_results AS (
        SELECT
            second_innings.team_id,

            COUNT(*) AS chasing_matches,

            SUM(
                CASE
                    WHEN cm.winner_team_id = second_innings.team_id
                        THEN 1
                    ELSE 0
                END
            ) AS chasing_wins

        FROM innings_scores second_innings

        JOIN cricket_match cm
            ON second_innings.match_id = cm.match_id

        WHERE second_innings.innings_no = 2

        GROUP BY second_innings.team_id
    )

    SELECT
        t.team_id,
        t.team_name,
        t.team_type,
        t.country,

        COUNT(DISTINCT tr.match_id) AS matches_played,

        SUM(tr.win) AS wins,

        COUNT(DISTINCT tr.match_id)
            - SUM(tr.win)
            - SUM(tr.no_result_or_tie) AS losses,

        SUM(tr.no_result_or_tie) AS no_result_or_tie,

        ROUND(
            SUM(tr.win) * 100.0 /
            NULLIF(COUNT(DISTINCT tr.match_id), 0),
            2
        ) AS win_percentage,

        COALESCE(ts.matches_batted, 0)
            AS matches_batted,

        COALESCE(ts.total_runs, 0)
            AS total_runs,

        COALESCE(ts.average_score, 0)
            AS average_score,

        COALESCE(ts.highest_score, 0)
            AS highest_score,

        COALESCE(ts.lowest_score, 0)
            AS lowest_score,

        COALESCE(tc.total_runs_conceded, 0)
            AS total_runs_conceded,

        COALESCE(tc.average_runs_conceded, 0)
            AS average_runs_conceded,

        COALESCE(bfr.batting_first_matches, 0)
            AS batting_first_matches,

        COALESCE(bfr.batting_first_wins, 0)
            AS batting_first_wins,

        COALESCE(cr.chasing_matches, 0)
            AS chasing_matches,

        COALESCE(cr.chasing_wins, 0)
            AS chasing_wins

    FROM team t

    LEFT JOIN team_results tr
        ON t.team_id = tr.team_id

    LEFT JOIN team_scoring ts
        ON t.team_id = ts.team_id

    LEFT JOIN team_conceding tc
        ON t.team_id = tc.team_id

    LEFT JOIN batting_first_results bfr
        ON t.team_id = bfr.team_id

    LEFT JOIN chasing_results cr
        ON t.team_id = cr.team_id

    GROUP BY
        t.team_id,
        t.team_name,
        t.team_type,
        t.country,
        ts.matches_batted,
        ts.total_runs,
        ts.average_score,
        ts.highest_score,
        ts.lowest_score,
        tc.total_runs_conceded,
        tc.average_runs_conceded,
        bfr.batting_first_matches,
        bfr.batting_first_wins,
        cr.chasing_matches,
        cr.chasing_wins

    ORDER BY wins DESC;
    """

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result


@app.get("/api/head-to-head")
def get_head_to_head_stats():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    WITH team_pairs AS (
        SELECT
            mt1.match_id,
            mt1.team_id AS team1_id,
            mt2.team_id AS team2_id
        FROM match_team mt1
        JOIN match_team mt2
            ON mt1.match_id = mt2.match_id
            AND mt1.team_id < mt2.team_id
    ),

    h2h_results AS (
        SELECT
            tp.team1_id,
            tp.team2_id,

            COUNT(*) AS matches_played,

            SUM(
                CASE
                    WHEN cm.winner_team_id = tp.team1_id
                    THEN 1
                    ELSE 0
                END
            ) AS team1_wins,

            SUM(
                CASE
                    WHEN cm.winner_team_id = tp.team2_id
                    THEN 1
                    ELSE 0
                END
            ) AS team2_wins,

            SUM(
                CASE
                    WHEN cm.winner_team_id IS NULL
                    THEN 1
                    ELSE 0
                END
            ) AS no_result_or_tie

        FROM team_pairs tp

        JOIN cricket_match cm
            ON tp.match_id = cm.match_id

        GROUP BY
            tp.team1_id,
            tp.team2_id
    ),

    innings_scores AS (
        SELECT
            i.match_id,
            i.innings_no,
            i.batting_team_id AS team_id,

            SUM(d.total_runs) AS runs_scored

        FROM innings i

        JOIN delivery d
            ON i.match_id = d.match_id
            AND i.innings_no = d.innings_no

        WHERE i.is_super_over = FALSE

        GROUP BY
            i.match_id,
            i.innings_no,
            i.batting_team_id
    ),

    team1_scores AS (
        SELECT
            tp.team1_id,
            tp.team2_id,

            AVG(iscore.runs_scored)
                AS team1_average_score,

            MAX(iscore.runs_scored)
                AS team1_highest_score,

            MIN(iscore.runs_scored)
                AS team1_lowest_score

        FROM team_pairs tp

        JOIN innings_scores iscore
            ON tp.match_id = iscore.match_id
            AND iscore.team_id = tp.team1_id

        GROUP BY
            tp.team1_id,
            tp.team2_id
    ),

    team2_scores AS (
        SELECT
            tp.team1_id,
            tp.team2_id,

            AVG(iscore.runs_scored)
                AS team2_average_score,

            MAX(iscore.runs_scored)
                AS team2_highest_score,

            MIN(iscore.runs_scored)
                AS team2_lowest_score

        FROM team_pairs tp

        JOIN innings_scores iscore
            ON tp.match_id = iscore.match_id
            AND iscore.team_id = tp.team2_id

        GROUP BY
            tp.team1_id,
            tp.team2_id
    ),

    batting_first AS (
        SELECT
            tp.team1_id,
            tp.team2_id,

            COUNT(*) AS batting_first_matches,

            SUM(
                CASE
                    WHEN cm.winner_team_id = first_innings.team_id
                    THEN 1
                    ELSE 0
                END
            ) AS batting_first_wins

        FROM team_pairs tp

        JOIN innings_scores first_innings
            ON tp.match_id = first_innings.match_id
            AND first_innings.innings_no = 1

        JOIN cricket_match cm
            ON tp.match_id = cm.match_id

        GROUP BY
            tp.team1_id,
            tp.team2_id
    ),

    chasing AS (
        SELECT
            tp.team1_id,
            tp.team2_id,

            COUNT(*) AS chasing_matches,

            SUM(
                CASE
                    WHEN cm.winner_team_id = second_innings.team_id
                    THEN 1
                    ELSE 0
                END
            ) AS chasing_wins

        FROM team_pairs tp

        JOIN innings_scores second_innings
            ON tp.match_id = second_innings.match_id
            AND second_innings.innings_no = 2

        JOIN cricket_match cm
            ON tp.match_id = cm.match_id

        GROUP BY
            tp.team1_id,
            tp.team2_id
    )

    SELECT
        t1.team_id AS team1_id,
        t1.team_name AS team1,

        t2.team_id AS team2_id,
        t2.team_name AS team2,

        hr.matches_played,

        hr.team1_wins,
        hr.team2_wins,

        hr.team2_wins AS team1_losses,
        hr.team1_wins AS team2_losses,

        hr.no_result_or_tie,

        ROUND(
            hr.team1_wins * 100.0 /
            NULLIF(
                hr.matches_played - hr.no_result_or_tie,
                0
            ),
            2
        ) AS team1_win_percentage,

        ROUND(
            hr.team2_wins * 100.0 /
            NULLIF(
                hr.matches_played - hr.no_result_or_tie,
                0
            ),
            2
        ) AS team2_win_percentage,

        ROUND(ts1.team1_average_score, 2)
            AS team1_average_score,

        ts1.team1_highest_score,
        ts1.team1_lowest_score,

        ROUND(ts2.team2_average_score, 2)
            AS team2_average_score,

        ts2.team2_highest_score,
        ts2.team2_lowest_score,

        COALESCE(
            bf.batting_first_matches,
            0
        ) AS batting_first_matches,

        COALESCE(
            bf.batting_first_wins,
            0
        ) AS batting_first_wins,

        COALESCE(
            ch.chasing_matches,
            0
        ) AS chasing_matches,

        COALESCE(
            ch.chasing_wins,
            0
        ) AS chasing_wins

    FROM h2h_results hr

    JOIN team t1
        ON hr.team1_id = t1.team_id

    JOIN team t2
        ON hr.team2_id = t2.team_id

    LEFT JOIN team1_scores ts1
        ON hr.team1_id = ts1.team1_id
        AND hr.team2_id = ts1.team2_id

    LEFT JOIN team2_scores ts2
        ON hr.team1_id = ts2.team1_id
        AND hr.team2_id = ts2.team2_id

    LEFT JOIN batting_first bf
        ON hr.team1_id = bf.team1_id
        AND hr.team2_id = bf.team2_id

    LEFT JOIN chasing ch
        ON hr.team1_id = ch.team1_id
        AND hr.team2_id = ch.team2_id

    ORDER BY hr.matches_played DESC;
    """

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result


@app.get("/api/venues")
def get_venue_stats():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    WITH innings_scores AS (
        SELECT
            i.match_id,
            i.innings_no,
            i.batting_team_id,
            cm.venue_id,
            SUM(d.total_runs) AS runs_scored
        FROM innings i
        JOIN delivery d
            ON i.match_id = d.match_id
            AND i.innings_no = d.innings_no
        JOIN cricket_match cm
            ON i.match_id = cm.match_id
        WHERE i.is_super_over = FALSE
        GROUP BY
            i.match_id,
            i.innings_no,
            i.batting_team_id,
            cm.venue_id
    ),

    venue_scoring AS (
        SELECT
            venue_id,
            SUM(runs_scored) AS total_runs_scored,

            ROUND(
                AVG(runs_scored),
                2
            ) AS average_innings_score,

            MAX(runs_scored) AS highest_team_score,

            MIN(runs_scored) AS lowest_team_score

        FROM innings_scores
        GROUP BY venue_id
    ),

    venue_innings_average AS (
        SELECT
            venue_id,

            ROUND(
                AVG(
                    CASE
                        WHEN innings_no = 1
                        THEN runs_scored
                    END
                ),
                2
            ) AS average_first_innings_score,

            ROUND(
                AVG(
                    CASE
                        WHEN innings_no = 2
                        THEN runs_scored
                    END
                ),
                2
            ) AS average_second_innings_score

        FROM innings_scores
        GROUP BY venue_id
    ),

    venue_matches AS (
        SELECT
            cm.venue_id,

            COUNT(DISTINCT cm.match_id) AS matches_played,

            SUM(
                CASE
                    WHEN cm.winner_team_id IS NOT NULL
                    AND fi.batting_team_id = cm.winner_team_id
                    THEN 1
                    ELSE 0
                END
            ) AS batting_first_wins,

            SUM(
                CASE
                    WHEN cm.winner_team_id IS NOT NULL
                    AND si.batting_team_id = cm.winner_team_id
                    THEN 1
                    ELSE 0
                END
            ) AS chasing_wins

        FROM cricket_match cm

        LEFT JOIN innings_scores fi
            ON cm.match_id = fi.match_id
            AND fi.innings_no = 1

        LEFT JOIN innings_scores si
            ON cm.match_id = si.match_id
            AND si.innings_no = 2

        GROUP BY cm.venue_id
    )

    SELECT
        v.venue_id,
        v.venue_name,
        v.city,
        v.country,

        vm.matches_played,

        COALESCE(
            vs.total_runs_scored,
            0
        ) AS total_runs_scored,

        COALESCE(
            vs.average_innings_score,
            0
        ) AS average_innings_score,

        COALESCE(
            vs.highest_team_score,
            0
        ) AS highest_team_score,

        COALESCE(
            vs.lowest_team_score,
            0
        ) AS lowest_team_score,

        COALESCE(
            via.average_first_innings_score,
            0
        ) AS average_first_innings_score,

        COALESCE(
            via.average_second_innings_score,
            0
        ) AS average_second_innings_score,

        vm.batting_first_wins,

        vm.chasing_wins,

        ROUND(
            vm.batting_first_wins * 100.0 /
            NULLIF(
                vm.batting_first_wins +
                vm.chasing_wins,
                0
            ),
            2
        ) AS batting_first_win_percentage,

        ROUND(
            vm.chasing_wins * 100.0 /
            NULLIF(
                vm.batting_first_wins +
                vm.chasing_wins,
                0
            ),
            2
        ) AS chasing_win_percentage

    FROM venue v

    LEFT JOIN venue_matches vm
        ON v.venue_id = vm.venue_id

    LEFT JOIN venue_scoring vs
        ON v.venue_id = vs.venue_id

    LEFT JOIN venue_innings_average via
        ON v.venue_id = via.venue_id

    WHERE vm.matches_played IS NOT NULL

    ORDER BY vm.matches_played DESC;
    """

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result


@app.get("/api/player-vs-opponent")
def get_player_vs_opponent_stats():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    WITH batting_stats AS (
        SELECT
            d.batter_id AS player_id,
            mt.team_id AS opponent_team_id,
            d.match_id,

            SUM(d.batter_runs) AS runs,

            COUNT(d.delivery_id)
            - COUNT(
                CASE
                    WHEN de.extra_type = 'wides'
                    THEN d.delivery_id
                    ELSE NULL
                END
            ) AS balls_faced,

            SUM(
                CASE
                    WHEN d.batter_runs = 4
                    THEN 1
                    ELSE 0
                END
            ) AS fours,

            SUM(
                CASE
                    WHEN d.batter_runs = 6
                    THEN 1
                    ELSE 0
                END
            ) AS sixes

        FROM delivery d

        JOIN innings i
            ON d.match_id = i.match_id
            AND d.innings_no = i.innings_no

        JOIN match_team mt
            ON d.match_id = mt.match_id
            AND mt.team_id <> i.batting_team_id

        LEFT JOIN delivery_extra de
            ON d.delivery_id = de.delivery_id
            AND de.extra_type = 'wides'

        GROUP BY
            d.batter_id,
            mt.team_id,
            d.match_id
    ),

    batting_dismissals AS (
        SELECT
            d.batter_id AS player_id,
            mt.team_id AS opponent_team_id,
            d.match_id,

            COUNT(w.wicket_id) AS dismissals

        FROM delivery d

        JOIN innings i
            ON d.match_id = i.match_id
            AND d.innings_no = i.innings_no

        JOIN match_team mt
            ON d.match_id = mt.match_id
            AND mt.team_id <> i.batting_team_id

        LEFT JOIN wicket w
            ON d.delivery_id = w.delivery_id
            AND w.player_out_id = d.batter_id

        GROUP BY
            d.batter_id,
            mt.team_id,
            d.match_id
    ),

    bowling_stats AS (
        SELECT
            d.bowler_id AS player_id,
            i.batting_team_id AS opponent_team_id,
            d.match_id,

            SUM(
                d.total_runs -
                COALESCE(
                    (
                        SELECT SUM(de2.extra_runs)
                        FROM delivery_extra de2
                        WHERE de2.delivery_id = d.delivery_id
                        AND de2.extra_type IN (
                            'byes',
                            'legbyes',
                            'penalty'
                        )
                    ),
                    0
                )
            ) AS runs_conceded,

            COUNT(
                CASE
                    WHEN NOT EXISTS (
                        SELECT 1
                        FROM delivery_extra de3
                        WHERE de3.delivery_id = d.delivery_id
                        AND de3.extra_type IN (
                            'wides',
                            'noballs'
                        )
                    )
                    THEN d.delivery_id
                END
            ) AS balls_bowled

        FROM delivery d

        JOIN innings i
            ON d.match_id = i.match_id
            AND d.innings_no = i.innings_no

        GROUP BY
            d.bowler_id,
            i.batting_team_id,
            d.match_id
    ),

    bowling_wickets AS (
        SELECT
            d.bowler_id AS player_id,
            i.batting_team_id AS opponent_team_id,
            d.match_id,

            COUNT(w.wicket_id) AS wickets

        FROM delivery d

        JOIN innings i
            ON d.match_id = i.match_id
            AND d.innings_no = i.innings_no

        LEFT JOIN wicket w
            ON d.delivery_id = w.delivery_id

        GROUP BY
            d.bowler_id,
            i.batting_team_id,
            d.match_id
    ),

    combined_batting AS (
        SELECT
            bs.player_id,
            bs.opponent_team_id,

            COUNT(DISTINCT bs.match_id)
                AS batting_matches,

            SUM(bs.runs)
                AS total_runs,

            SUM(bs.balls_faced)
                AS balls_faced,

            MAX(bs.runs)
                AS highest_score,

            SUM(bs.fours)
                AS fours,

            SUM(bs.sixes)
                AS sixes,

            SUM(bd.dismissals)
                AS times_dismissed

        FROM batting_stats bs

        LEFT JOIN batting_dismissals bd
            ON bs.player_id = bd.player_id
            AND bs.opponent_team_id = bd.opponent_team_id
            AND bs.match_id = bd.match_id

        GROUP BY
            bs.player_id,
            bs.opponent_team_id
    ),

    combined_bowling AS (
        SELECT
            bs.player_id,
            bs.opponent_team_id,

            COUNT(DISTINCT bs.match_id)
                AS bowling_matches,

            SUM(bs.runs_conceded)
                AS runs_conceded,

            SUM(bs.balls_bowled)
                AS balls_bowled,

            SUM(bw.wickets)
                AS wickets

        FROM bowling_stats bs

        LEFT JOIN bowling_wickets bw
            ON bs.player_id = bw.player_id
            AND bs.opponent_team_id = bw.opponent_team_id
            AND bs.match_id = bw.match_id

        GROUP BY
            bs.player_id,
            bs.opponent_team_id
    ),

    player_opponents AS (
        SELECT
            player_id,
            opponent_team_id
        FROM combined_batting

        UNION

        SELECT
            player_id,
            opponent_team_id
        FROM combined_bowling
    )

    SELECT
        p.player_id,
        p.player_name,

        t.team_id AS opponent_team_id,
        t.team_name AS opponent,

        COALESCE(
            cb.batting_matches,
            0
        ) AS batting_matches,

        COALESCE(
            cb.total_runs,
            0
        ) AS runs,

        COALESCE(
            cb.balls_faced,
            0
        ) AS balls_faced,

        ROUND(
            COALESCE(cb.total_runs, 0) * 100.0 /
            NULLIF(cb.balls_faced, 0),
            2
        ) AS strike_rate,

        COALESCE(
            cb.highest_score,
            0
        ) AS highest_score,

        ROUND(
            COALESCE(cb.total_runs, 0) * 1.0 /
            NULLIF(cb.times_dismissed, 0),
            2
        ) AS batting_average,

        COALESCE(
            cb.fours,
            0
        ) AS fours,

        COALESCE(
            cb.sixes,
            0
        ) AS sixes,

        COALESCE(
            cbow.bowling_matches,
            0
        ) AS bowling_matches,

        COALESCE(
            cbow.wickets,
            0
        ) AS wickets,

        COALESCE(
            cbow.runs_conceded,
            0
        ) AS runs_conceded,

        COALESCE(
            cbow.balls_bowled,
            0
        ) AS balls_bowled,

        ROUND(
            COALESCE(cbow.runs_conceded, 0) * 6.0 /
            NULLIF(cbow.balls_bowled, 0),
            2
        ) AS economy_rate,

        ROUND(
            COALESCE(cbow.runs_conceded, 0) * 1.0 /
            NULLIF(cbow.wickets, 0),
            2
        ) AS bowling_average,

        ROUND(
            COALESCE(cbow.balls_bowled, 0) * 1.0 /
            NULLIF(cbow.wickets, 0),
            2
        ) AS bowling_strike_rate

    FROM player_opponents po

    JOIN player p
        ON po.player_id = p.player_id

    JOIN team t
        ON po.opponent_team_id = t.team_id

    LEFT JOIN combined_batting cb
        ON po.player_id = cb.player_id
        AND po.opponent_team_id = cb.opponent_team_id

    LEFT JOIN combined_bowling cbow
        ON po.player_id = cbow.player_id
        AND po.opponent_team_id = cbow.opponent_team_id

    ORDER BY
        p.player_name,
        t.team_name;
    """

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result