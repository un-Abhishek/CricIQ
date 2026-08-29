import json
from pathlib import Path

# Path to IPL dataset
DATASET_PATH = Path("Dataset/ipl_json")

# Get one JSON match file
json_files = list(DATASET_PATH.glob("*.json"))

print(f"Total IPL JSON files: {len(json_files)}")

# Read the first match
with open(json_files[0], "r", encoding="utf-8") as file:
    match_data = json.load(file)

print("\nTop-level keys:")
print(match_data.keys())

print("\nMatch info keys:")
print(match_data["info"].keys())

print("\nFirst few match info values:")
for key, value in list(match_data["info"].items())[:10]:
    print(f"{key}: {value}")

print("\n--- INNINGS STRUCTURE ---")

print(f"Total innings: {len(match_data['innings'])}")

first_innings = match_data["innings"][0]

print("\nFirst innings keys:")
print(first_innings.keys())

print("\nFirst innings team:")
print(first_innings["team"])

print("\nFirst innings overs count:")
print(len(first_innings["overs"]))

first_over = first_innings["overs"][0]

print("\nFirst over keys:")
print(first_over.keys())

print("\nFirst over number:")
print(first_over["over"])

print("\nNumber of deliveries in first over:")
print(len(first_over["deliveries"]))

first_delivery = first_over["deliveries"][0]

print("\nFirst delivery keys:")
print(first_delivery.keys())

print("\nFirst delivery:")
print(first_delivery)


print("\n--- SPECIAL DELIVERY EXAMPLES ---")

extra_example = None
wicket_example = None

for innings in match_data["innings"]:
    for over in innings["overs"]:
        for delivery in over["deliveries"]:

            if "extras" in delivery and extra_example is None:
                extra_example = delivery

            if "wickets" in delivery and wicket_example is None:
                wicket_example = delivery

            if extra_example and wicket_example:
                break

        if extra_example and wicket_example:
            break

    if extra_example and wicket_example:
        break


print("\nDelivery with extras:")
print(extra_example)

print("\nDelivery with wicket:")
print(wicket_example)