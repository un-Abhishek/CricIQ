import os
import json
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
import builtins

# Set to True only if you want the detailed output for every match.
VERBOSE = False

def print(*args, **kwargs):
    if VERBOSE:
        builtins.print(*args, **kwargs)
        return

    message = " ".join(str(arg) for arg in args)

    important_markers = (
        "Connected to CricIQ database!",
        "Total IPL matches found:",
        "PROCESSING MATCH",
        "FILE:",
        "COMPLETED SUCCESSFULLY",
        "ERROR PROCESSING",
        "Rolled back",
        "IPL IMPORT COMPLETE",
        "Total matches found:",
        "Successfully processed:",
        "Failed:",
        "MySQL connection closed."
    )

    if any(marker in message for marker in important_markers) or message.strip().startswith("="):
        builtins.print(*args, **kwargs)


# -----------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------
load_dotenv()


# -----------------------------
# CONNECT TO MYSQL
# -----------------------------
connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = connection.cursor()

print("Connected to CricIQ database!")


# -----------------------------
# LOAD ONE IPL MATCH
# -----------------------------
DATASET_PATH = Path("Dataset/ipl_json")

json_files = sorted(DATASET_PATH.glob("*.json"))

print(f"Total IPL matches found: {len(json_files)}")
# -----------------------------
# IMPORT ALL IPL MATCHES
# -----------------------------

total_matches = len(json_files)
successful_matches = 0
failed_matches = 0

for index, match_file in enumerate(json_files, start=1):

    print("\n" + "=" * 60)
    print(f"PROCESSING MATCH {index}/{total_matches}")
    print(f"FILE: {match_file.name}")
    print("=" * 60)

    try:

        # Load match JSON
        with open(match_file, "r", encoding="utf-8") as file:
            match_data = json.load(file)
        
        # -----------------------------
        # EXTRACT BASIC MATCH INFO
        # -----------------------------
        info = match_data["info"]

        competition_name = info["event"]["name"]
        competition_type = "Domestic"

        season = info["season"]
        teams = info["teams"]
        match_date = info["dates"][0]


        # -----------------------------
        # INSERT COMPETITION
        # -----------------------------
        cursor.execute(
            """
            INSERT INTO competition (
                competition_name,
                competition_type
            )
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                competition_id = LAST_INSERT_ID(competition_id)
            """,
            (competition_name, competition_type)
        )

        competition_id = cursor.lastrowid

        connection.commit()

        print(f"\nCompetition inserted/found: {competition_name}")
        print(f"Competition Type: {competition_type}")
        print(f"Competition ID: {competition_id}")

        # -----------------------------
        # INSERT EDITION
        # -----------------------------
        edition_name = str(season)

        # Use the season from the dataset
        edition_season = str(season)

        # For now, use the match date as both dates.
        # Later, when importing all matches, we will calculate
        # the actual start and end dates for each season.
        start_date = match_date
        end_date = match_date

        cursor.execute(
            """
            INSERT INTO edition (
                competition_id,
                edition_name,
                season,
                start_date,
                end_date
            )
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                edition_id = LAST_INSERT_ID(edition_id)
            """,
            (
                competition_id,
                edition_name,
                edition_season,
                start_date,
                end_date
            )
        )

        edition_id = cursor.lastrowid

        connection.commit()

        print(f"\nEdition inserted/found: {edition_name}")
        print(f"Season: {edition_season}")
        print(f"Edition ID: {edition_id}")



        # -----------------------------
        # INSERT TEAMS
        # -----------------------------
        teams = info["teams"]

        team_type = "Franchise"
        country = "India"

        team_ids = {}

        for team_name in teams:

            cursor.execute(
                """
                INSERT INTO team (
                    team_name,
                    team_type,
                    country
                )
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    team_id = LAST_INSERT_ID(team_id)
                """,
                (
                    team_name,
                    team_type,
                    country
                )
            )

            team_ids[team_name] = cursor.lastrowid

        connection.commit()

        print("\n--- TEAMS INSERTED/FOUND ---")

        for team_name, team_id in team_ids.items():
            print(f"{team_name} -> Team ID: {team_id}")

        # -----------------------------
        # INSERT / FIND VENUE
        # -----------------------------
        venue_name = info.get("venue")
        city = info.get("city")
        country = "India"

        cursor.execute(
            """
            INSERT INTO venue (
                venue_name,
                city,
                country
            )
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                venue_id = LAST_INSERT_ID(venue_id)
            """,
            (
                venue_name,
                city,
                country
            )
        )

        venue_id = cursor.lastrowid

        connection.commit()

        print("\n--- VENUE INSERTED/FOUND ---")
        print(f"Venue: {venue_name}")
        print(f"City: {city}")
        print(f"Venue ID: {venue_id}")


        # -----------------------------
        # INSERT CRICKET MATCH
        # -----------------------------

        # Cricsheet match ID from the JSON filename
        cricsheet_match_id = match_file.stem

        # Match details
        match_format = info.get("match_type")
        gender = info.get("gender")

        # Match number
        event = info.get("event", {})
        match_type_number = event.get("match_number")

        # -----------------------------
        # TOSS INFORMATION
        # -----------------------------
        toss = info.get("toss", {})

        toss_winner_name = toss.get("winner")
        toss_decision = toss.get("decision")

        toss_winner_id = None

        if toss_winner_name in team_ids:
            toss_winner_id = team_ids[toss_winner_name]


        # -----------------------------
        # OUTCOME INFORMATION
        # -----------------------------
        outcome = info.get("outcome", {})

        winner_team_name = outcome.get("winner")

        winner_team_id = None

        if winner_team_name in team_ids:
            winner_team_id = team_ids[winner_team_name]


        # Result information
        result_by_type = None
        result_by_value = None

        if "by" in outcome:
            result_by = outcome["by"]

            if result_by:
                result_by_type = list(result_by.keys())[0]
                result_by_value = result_by[result_by_type]


        # Outcome type
        if winner_team_name:
            outcome_type = "winner"
        elif "result" in outcome:
            outcome_type = outcome["result"]
        else:
            outcome_type = None


        # Match method, for example D/L if applicable
        method = outcome.get("method")


        # -----------------------------
        # INSERT MATCH
        # -----------------------------
        cursor.execute(
            """
            INSERT INTO cricket_match (
                cricsheet_match_id,
                edition_id,
                venue_id,
                match_date,
                match_format,
                gender,
                match_type_number,
                toss_winner_id,
                toss_decision,
                winner_team_id,
                outcome_type,
                result_by_type,
                result_by_value,
                method
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON DUPLICATE KEY UPDATE
                match_id = LAST_INSERT_ID(match_id)
            """,
            (
                cricsheet_match_id,
                edition_id,
                venue_id,
                match_date,
                match_format,
                gender,
                match_type_number,
                toss_winner_id,
                toss_decision,
                winner_team_id,
                outcome_type,
                result_by_type,
                result_by_value,
                method
            )
        )

        match_id = cursor.lastrowid

        connection.commit()
        # -----------------------------
        # INSERT MATCH TEAMS
        # -----------------------------

        team_roles = ["team1", "team2"]

        for team_name, team_role in zip(teams, team_roles):
            team_id = team_ids[team_name]

            cursor.execute(
                """
                INSERT INTO match_team (
                    match_id,
                    team_id,
                    team_role
                )
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    team_role = VALUES(team_role)
                """,
                (
                    match_id,
                    team_id,
                    team_role
                )
            )

        connection.commit()

        print("\n--- MATCH TEAMS INSERTED/FOUND ---")

        for team_name, team_role in zip(teams, team_roles):
            print(
                f"{team_name} -> "
                f"Match ID: {match_id}, "
                f"Team ID: {team_ids[team_name]}, "
                f"Role: {team_role}"
            )


        # -----------------------------
        # INSERT INNINGS
        # -----------------------------

        print("\n--- INSERTING INNINGS ---")

        for innings_no, innings_data in enumerate(match_data["innings"], start=1):

            batting_team_name = innings_data["team"]
            batting_team_id = team_ids[batting_team_name]

            # Check if this innings is a Super Over
            is_super_over = 0

            if innings_data.get("super_over"):
                is_super_over = 1

            cursor.execute(
                """
                INSERT INTO innings (
                    match_id,
                    innings_no,
                    batting_team_id,
                    is_super_over
                )
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    batting_team_id = VALUES(batting_team_id),
                    is_super_over = VALUES(is_super_over)
                """,
                (
                    match_id,
                    innings_no,
                    batting_team_id,
                    is_super_over
                )
            )

        connection.commit()

        print("\n--- INNINGS INSERTED/FOUND ---")

        for innings_no, innings_data in enumerate(match_data["innings"], start=1):
            print(
                f"Innings {innings_no} -> "
                f"Batting Team: {innings_data['team']} "
                f"(Team ID: {team_ids[innings_data['team']]})"
            )

        # -----------------------------
        # INSERT PLAYERS
        # -----------------------------

        print("\n--- INSERTING PLAYERS ---")

        players_by_team = info["players"]

        # Get Cricsheet player IDs
        people_registry = info.get("registry", {}).get("people", {})

        player_ids = {}

        for team_name, players in players_by_team.items():

            for player_name in players:

                cricsheet_id = people_registry.get(player_name)

                cursor.execute(
                    """
                    INSERT INTO player (
                        cricsheet_id,
                        player_name
                    )
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE
                        player_id = LAST_INSERT_ID(player_id),
                        player_name = VALUES(player_name)
                    """,
                    (
                        cricsheet_id,
                        player_name
                    )
                )

                player_id = cursor.lastrowid

                # Store player name -> player ID
                player_ids[player_name] = player_id


        connection.commit()


        print("\n--- PLAYERS INSERTED/FOUND ---")

        for player_name, player_id in player_ids.items():
            print(f"{player_name} -> Player ID: {player_id}")

        # -----------------------------
        # INSERT TEAM-PLAYER RELATIONSHIPS
        # -----------------------------

        print("\n--- INSERTING TEAM PLAYERS ---")

        for team_name, players in players_by_team.items():

            team_id = team_ids[team_name]

            for player_name in players:

                player_id = player_ids[player_name]

                cursor.execute(
                    """
                    INSERT INTO team_player (
                        team_id,
                        player_id,
                        edition_id,
                        is_captain,
                        is_wicketkeeper
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        team_id = team_id
                    """,
                    (
                        team_id,
                        player_id,
                        edition_id,
                        0,
                        0
                    )
                )

        connection.commit()

        print("\n--- TEAM PLAYERS INSERTED/FOUND ---")

        for team_name, players in players_by_team.items():

            print(f"\n{team_name}:")

            for player_name in players:

                print(
                    f"{player_name} -> "
                    f"Team ID: {team_ids[team_name]}, "
                    f"Player ID: {player_ids[player_name]}, "
                    f"Edition ID: {edition_id}"
                )

        # -----------------------------
        # INSERT PLAYING XI
        # -----------------------------

        print("\n--- INSERTING PLAYING XI ---")

        playing_xi_count = 0

        # Get players grouped by team
        match_players = info.get("players", {})

        for team_name, players in match_players.items():

            # Get team ID
            team_id = team_ids[team_name]

            for player_name in players:

                # Get player ID
                player_id = player_ids[player_name]

                cursor.execute(
                    """
                    INSERT INTO playing_xi (
                        match_id,
                        player_id,
                        team_id,
                        is_captain,
                        is_wicketkeeper
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        team_id = VALUES(team_id)
                    """,
                    (
                        match_id,
                        player_id,
                        team_id,
                        False,
                        False
                    )
                )

                playing_xi_count += 1


        connection.commit()


        print("\n--- PLAYING XI INSERTED/FOUND ---")
        print(f"Total players in Playing XI: {playing_xi_count}")

        # -----------------------------
        # INSERT MATCH OFFICIALS
        # -----------------------------

        print("\n--- INSERTING MATCH OFFICIALS ---")

        official_count = 0

        # Get officials from match info
        officials = info.get("officials", {})

        for official_role, official_names in officials.items():

            # Sometimes the value may be a single name
            if isinstance(official_names, str):
                official_names = [official_names]

            for official_name in official_names:

                # -----------------------------
                # INSERT / FIND OFFICIAL
                # -----------------------------

                cursor.execute(
                    """
                    SELECT official_id
                    FROM official
                    WHERE official_name = %s
                    """,
                    (official_name,)
                )

                result = cursor.fetchone()

                if result:

                    official_id = result[0]

                else:

                    cursor.execute(
                        """
                        INSERT INTO official (
                            official_name
                        )
                        VALUES (%s)
                        """,
                        (official_name,)
                    )

                    official_id = cursor.lastrowid


                # -----------------------------
                # INSERT MATCH OFFICIAL
                # -----------------------------

                cursor.execute(
                    """
                    INSERT INTO match_official (
                        match_id,
                        official_id,
                        official_role
                    )
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        official_role = VALUES(official_role)
                    """,
                    (
                        match_id,
                        official_id,
                        official_role
                    )
                )

                official_count += 1


        connection.commit()


        print("\n--- MATCH OFFICIALS INSERTED/FOUND ---")
        print(f"Total officials processed: {official_count}")

        # -----------------------------
        # INSERT PLAYER AWARDS
        # -----------------------------

        print("\n--- INSERTING PLAYER AWARDS ---")

        award_count = 0

        # Get Player of the Match from JSON
        player_of_match_list = info.get("player_of_match", [])

        for player_name in player_of_match_list:

            # Check if player already exists in player_ids
            if player_name not in player_ids:

                cursor.execute(
                    """
                    SELECT player_id
                    FROM player
                    WHERE player_name = %s
                    """,
                    (player_name,)
                )

                result = cursor.fetchone()

                if result:
                    player_ids[player_name] = result[0]

                else:
                    cursor.execute(
                        """
                        INSERT INTO player (
                            player_name
                        )
                        VALUES (%s)
                        """,
                        (player_name,)
                    )

                    player_ids[player_name] = cursor.lastrowid


            player_id = player_ids[player_name]

            # Insert Player of the Match award
            cursor.execute(
                """
                INSERT INTO player_award (
                    match_id,
                    player_id,
                    award_type
                )
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    award_type = VALUES(award_type)
                """,
                (
                    match_id,
                    player_id,
                    "Player of the Match"
                )
            )

            award_count += 1


        connection.commit()


        print("\n--- PLAYER AWARDS INSERTED/FOUND ---")
        print(f"Total awards processed: {award_count}")

        # -----------------------------
        # INSERT DELIVERIES
        # -----------------------------

        print("\n--- INSERTING DELIVERIES ---")

        delivery_count = 0
        extra_count = 0
        wicket_count = 0
        fielder_count = 0


        for innings_no, innings_data in enumerate(match_data["innings"], start=1):

            # Get all overs in this innings
            overs = innings_data.get("overs", [])

            for over_data in overs:

                over_no = over_data["over"]

                # Get all deliveries in this over
                deliveries = over_data.get("deliveries", [])

                for delivery_sequence, delivery_data in enumerate(
                    deliveries,
                    start=1
                ):

                    batter_name = delivery_data["batter"]
                    non_striker_name = delivery_data["non_striker"]
                    bowler_name = delivery_data["bowler"]


                    # -----------------------------
                    # GET PLAYER IDs
                    # -----------------------------

                    batter_id = player_ids[batter_name]
                    non_striker_id = player_ids[non_striker_name]
                    bowler_id = player_ids[bowler_name]


                    # -----------------------------
                    # RUNS INFORMATION
                    # -----------------------------

                    runs = delivery_data.get("runs", {})

                    batter_runs = runs.get("batter", 0)
                    total_extras = runs.get("extras", 0)
                    total_runs = runs.get("total", 0)


                    # -----------------------------
                    # INSERT DELIVERY
                    # -----------------------------

                    cursor.execute(
                        """
                        INSERT INTO delivery (
                            match_id,
                            innings_no,
                            over_no,
                            delivery_sequence,
                            batter_id,
                            non_striker_id,
                            bowler_id,
                            batter_runs,
                            total_extras,
                            total_runs
                        )
                        VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s
                        )
                        ON DUPLICATE KEY UPDATE
                            delivery_id = LAST_INSERT_ID(delivery_id)
                        """,
                        (
                            match_id,
                            innings_no,
                            over_no,
                            delivery_sequence,
                            batter_id,
                            non_striker_id,
                            bowler_id,
                            batter_runs,
                            total_extras,
                            total_runs
                        )
                    )


                    # Get ID of inserted/found delivery
                    delivery_id = cursor.lastrowid

                    delivery_count += 1


                    # -----------------------------
                    # INSERT DELIVERY EXTRAS
                    # -----------------------------

                    extras = delivery_data.get("extras", {})

                    for extra_type, extra_runs in extras.items():

                        cursor.execute(
                            """
                            INSERT INTO delivery_extra (
                                delivery_id,
                                extra_type,
                                extra_runs
                            )
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                extra_runs = VALUES(extra_runs)
                            """,
                            (
                                delivery_id,
                                extra_type,
                                extra_runs
                            )
                        )

                        extra_count += 1


                    # -----------------------------
                    # INSERT WICKETS
                    # -----------------------------

                    wickets = delivery_data.get("wickets", [])

                    for wicket_data in wickets:

                        player_out_name = wicket_data["player_out"]
                        dismissal_kind = wicket_data["kind"]


                        # -----------------------------
                        # GET / INSERT PLAYER OUT
                        # -----------------------------

                        if player_out_name not in player_ids:

                            cursor.execute(
                                """
                                SELECT player_id
                                FROM player
                                WHERE player_name = %s
                                """,
                                (player_out_name,)
                            )

                            result = cursor.fetchone()

                            if result:

                                player_ids[player_out_name] = result[0]

                            else:

                                cursor.execute(
                                    """
                                    INSERT INTO player (
                                        player_name
                                    )
                                    VALUES (%s)
                                    """,
                                    (player_out_name,)
                                )

                                player_ids[player_out_name] = cursor.lastrowid


                        player_out_id = player_ids[player_out_name]


                        # -----------------------------
                        # INSERT WICKET
                        # -----------------------------

                        cursor.execute(
                            """
                            INSERT INTO wicket (
                                delivery_id,
                                player_out_id,
                                dismissal_kind
                            )
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                wicket_id = LAST_INSERT_ID(wicket_id)
                            """,
                            (
                                delivery_id,
                                player_out_id,
                                dismissal_kind
                            )
                        )


                        wicket_id = cursor.lastrowid

                        wicket_count += 1


                        # -----------------------------
                        # INSERT WICKET FIELDERS
                        # -----------------------------

                        fielders = wicket_data.get("fielders", [])

                        for fielder_data in fielders:

                            fielder_name = fielder_data["name"]


                            # -----------------------------
                            # GET / INSERT FIELDER
                            # -----------------------------

                            if fielder_name not in player_ids:

                                cursor.execute(
                                    """
                                    SELECT player_id
                                    FROM player
                                    WHERE player_name = %s
                                    """,
                                    (fielder_name,)
                                )

                                result = cursor.fetchone()


                                if result:

                                    player_ids[fielder_name] = result[0]


                                else:

                                    cursor.execute(
                                        """
                                        INSERT INTO player (
                                            player_name
                                        )
                                        VALUES (%s)
                                        """,
                                        (fielder_name,)
                                    )

                                    player_ids[fielder_name] = cursor.lastrowid


                            fielder_id = player_ids[fielder_name]


                            # -----------------------------
                            # INSERT WICKET FIELDER
                            # -----------------------------

                            cursor.execute(
                                """
                                INSERT INTO wicket_fielder (
                                    wicket_id,
                                    player_id
                                )
                                VALUES (%s, %s)
                                ON DUPLICATE KEY UPDATE
                                    player_id = VALUES(player_id)
                                """,
                                (
                                    wicket_id,
                                    fielder_id
                                )
                            )

                            fielder_count += 1


        # -----------------------------
        # COMMIT EVERYTHING
        # -----------------------------

        connection.commit()



        # -----------------------------
        # DISPLAY RESULTS
        # -----------------------------

        print("\n--- DELIVERIES INSERTED/FOUND ---")
        print(f"Total deliveries processed: {delivery_count}")

        print("\n--- DELIVERY EXTRAS INSERTED/FOUND ---")
        print(f"Total extras processed: {extra_count}")

        print("\n--- WICKETS INSERTED/FOUND ---")
        print(f"Total wickets processed: {wicket_count}")

        print("\n--- WICKET FIELDERS INSERTED/FOUND ---")
        print(f"Total wicket fielders processed: {fielder_count}")


        # -----------------------------
        # DISPLAY MATCH INFORMATION
        # -----------------------------
        print("\n--- MATCH INFORMATION ---")
        print(f"Competition: {competition_name}")
        print(f"Season: {season}")
        print(f"Teams: {teams[0]} vs {teams[1]}")
        print(f"Date: {match_date}")

        successful_matches += 1
        print(f"\nMATCH {index}/{total_matches} COMPLETED SUCCESSFULLY")

    except Exception as e:
        connection.rollback()
        failed_matches += 1
        print(f"\nERROR PROCESSING {match_file.name}: {e}")
        print("Rolled back the current transaction and continuing...")
        continue

# -----------------------------
# IMPORT SUMMARY
# -----------------------------
print("\n" + "=" * 60)
print("IPL IMPORT COMPLETE")
print("=" * 60)
print(f"Total matches found: {total_matches}")
print(f"Successfully processed: {successful_matches}")
print(f"Failed: {failed_matches}")
print("=" * 60)

# -----------------------------
# CLOSE CONNECTION
# -----------------------------
cursor.close()
connection.close()

print("\nMySQL connection closed.")
