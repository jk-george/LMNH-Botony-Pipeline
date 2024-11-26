import requests
import csv
import json
import argparse

# Define the base URL for the API
BASE_URL = "https://data-eng-plants-api.herokuapp.com/plants/"

def fetch_plant_data(plant_id):
    url = f"{BASE_URL}{plant_id}"
    response = requests.get(url)
    if response.status_code == 200:
        plant_data = response.json()

        if "origin_location" in plant_data:
            origin_location = plant_data["origin_location"]
            if isinstance(origin_location, list) and len(origin_location) >= 4:
                plant_data["origin_location"] = origin_location[3]

        return plant_data
    else:
        print(f"Failed to fetch: Plant ID {plant_id}. - (Status Code: {response.status_code})")
        return None

def get_all_keys(data):
    all_keys = set()
    for record in data:
        all_keys.update(record.keys())
    return list(all_keys)

def fetch_all_plants(start_id=1, end_id=50):
    plant_data = []

    for plant_id in range(start_id, end_id + 1):
        print(f"Fetching: Plant ID {plant_id}...")
        data = fetch_plant_data(plant_id)
        if data:
            plant_data.append(data)

    return plant_data

def export_to_csv(data, output_file="./data/plants_data.csv"):
    header_order = ["plant_id", "name", "soil_moisture", "temperature", "last_watered"]

    keys = get_all_keys(data)
    ordered_keys = [key for key in header_order if key in keys]
    unordered_keys = [key for key in keys if key not in ordered_keys]
    reordered_keys = ordered_keys + unordered_keys

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=reordered_keys)
        writer.writeheader()
        for plant in data:
            writer.writerow(plant)

    print(f"Data has been saved to '{output_file}'.")

def export_to_json(data, output_file="./data/plants_data.json"):
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data has been saved to '{output_file}'.")

def get_arguments():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(description="Fetch plant data and export to CSV or JSON.")
    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        help="Specify the export format (csv or json). Default is csv.",
    )

    return parser.parse_args()

def main():
    args = get_arguments()

    plant_data = fetch_all_plants()

    output_file="./data/plants_data.json"

    if args.format == "csv":
        output_file = "./data/plants_data.csv"
        print("Exporting to .csv:")
        export_to_csv(plant_data, output_file)
    elif args.format == "json":
        output_file = "./data/plants_data.json"
        print("Exporting to .json:")
        export_to_json(plant_data, output_file)

if __name__ == "__main__":
    main()