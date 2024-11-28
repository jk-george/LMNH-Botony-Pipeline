"""Script to extract data from API to a .csv or .json file."""
import os
import requests
import csv
import json
import argparse

BASE_URL = "https://data-eng-plants-api.herokuapp.com/plants/"


def fetch_plant_data(plant_id: int) -> dict:
    """Feetech data for a specific plant by ID from the API specified."""
    url = f"{BASE_URL}{plant_id}"
    response = requests.get(url)
    if response.status_code == 200:
        plant_data = response.json()

        if "name" in plant_data:
            plant_data["plant_name"] = plant_data.pop("name")

        if "botanist" in plant_data and isinstance(plant_data["botanist"], dict):
            botanist_data = plant_data.pop("botanist")
            plant_data["botanist_email"] = botanist_data.get("email", "")
            full_name = botanist_data.get("name", "").split()
            plant_data["botanist_forename"] = full_name[0] if len(
                full_name) > 0 else ""
            plant_data["botanist_surname"] = full_name[1] if len(
                full_name) > 1 else ""
            plant_data["botanist_phone"] = botanist_data.get("phone", "")

        if "origin_location" in plant_data:
            origin_location = plant_data["origin_location"]
            if isinstance(origin_location, list) and len(origin_location) >= 4:
                plant_data["country_name"] = origin_location[3]
            del plant_data["origin_location"]

        return plant_data
    else:
        print(
            f"Failed to fetch: Plant ID {plant_id}. - (Status Code: {response.status_code})")
        return None


def get_all_keys(data: list) -> list:
    all_keys = set()
    for record in data:
        all_keys.update(record.keys())
    return list(all_keys)


def fetch_all_plants(start_id: int = 1, end_id: int = 10) -> list:
    """Fetch data for all plants within the given ID range."""
    plant_data = []

    for plant_id in range(start_id, end_id + 1):
        print(f"Fetching: Plant ID {plant_id}...")
        data = fetch_plant_data(plant_id)
        if data:
            plant_data.append(data)

    return plant_data


def export_to_csv(data: list, output_file: str = "./plants_data/plants_data.csv") -> None:
    """Export the plant data to a CSV file."""
    header_order = [
        "plant_id",
        "plant_name",
        "soil_moisture",
        "temperature",
        "last_watered",
        "botanist_email",
        "botanist_forename",
        "botanist_surname",
        "botanist_phone",
        "country_name"
    ]

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


def export_to_json(data: list, output_file: str = "./plants_data/plants_data.json") -> None:
    """Export the plant data to a JSON file."""
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data has been saved to '{output_file}'.")


def get_arguments() -> argparse.Namespace:
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch plant data and export to CSV or JSON.")
    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        help="Specify the export format (csv or json). Default is csv.",
    )

    return parser.parse_args()


def main_extract() -> None:
    """Main function to fetch all plant data and export it based on user argument."""
    os.makedirs("plants_data", exist_ok=True)

    args = get_arguments()

    plant_data = fetch_all_plants()

    if args.format == "csv":
        output_file = "./plants_data/plants_data.csv"
        print("Exporting to .csv:")
        export_to_csv(plant_data, output_file)
    elif args.format == "json":
        output_file = "./plants_data/plants_data.json"
        print("Exporting to .json:")
        export_to_json(plant_data, output_file)


if __name__ == "__main__":
    main_extract()
